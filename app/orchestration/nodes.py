from __future__ import annotations

from copy import deepcopy

from app.orchestration.retry import NodeExecutionError, execute_with_retry_and_timeout
from app.orchestration.state import NodeName, OrchestrationState, PipelineError, utc_now_iso


def _append_completed(state: OrchestrationState, node: NodeName) -> None:
    if node not in state["completed_steps"]:
        state["completed_steps"].append(node)


def _fail_state(
    state: OrchestrationState,
    *,
    node: NodeName,
    error: Exception,
    attempts: int = 1,
    retryable: bool = False,
) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = node
    next_state["status"] = "failed"
    next_state["errors"].append(
        PipelineError(
            node=node,
            error_type=type(error).__name__,
            message=str(error),
            retryable=retryable,
            attempts=attempts,
            timestamp=utc_now_iso(),
        )
    )
    return next_state


def load_preferences_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "load_preferences"
    if not next_state["preferences"]:
        next_state["preferences"] = {
            "roles": ["AI Solutions Engineer", "LLM Engineer"],
            "keywords": ["python", "automation", "langgraph"],
            "work_modes": ["remote"],
            "preferred_locations": ["US"],
            "fresher_friendly": True,
            "salary_min": 50000,
            "companies_to_avoid": [],
        }
    _append_completed(next_state, "load_preferences")
    return next_state


def research_agent_node(state: OrchestrationState, research_adapter) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "research_agent"
    cfg = state["config"]
    try:
        urls = execute_with_retry_and_timeout(
            lambda: research_adapter.discover_urls(next_state["preferences"]),
            max_retries=cfg["max_retries"],
            timeout_seconds=cfg["node_timeout_seconds"],
        )
        next_state["candidate_urls"] = urls
        _append_completed(next_state, "research_agent")
        return next_state
    except NodeExecutionError as exc:
        return _fail_state(
            next_state,
            node="research_agent",
            error=exc,
            attempts=exc.attempts,
            retryable=exc.retryable,
        )


def dedupe_urls_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "dedupe_urls"
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in next_state["candidate_urls"]:
        key = item.get("canonical_url", item.get("source_url", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    next_state["candidate_urls"] = deduped
    _append_completed(next_state, "dedupe_urls")
    return next_state


def extraction_agent_node(state: OrchestrationState, extraction_adapter) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "extraction_agent"
    cfg = state["config"]
    try:
        jobs = execute_with_retry_and_timeout(
            lambda: extraction_adapter.extract_jobs(
                next_state["candidate_urls"], next_state["preferences"]
            ),
            max_retries=cfg["max_retries"],
            timeout_seconds=cfg["node_timeout_seconds"],
        )
        next_state["extracted_jobs"] = jobs
        _append_completed(next_state, "extraction_agent")
        return next_state
    except NodeExecutionError as exc:
        return _fail_state(
            next_state,
            node="extraction_agent",
            error=exc,
            attempts=exc.attempts,
            retryable=exc.retryable,
        )


def filter_rules_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "filter_rules"
    roles = {r.lower() for r in next_state["preferences"].get("roles", [])}
    companies_to_avoid = {c.lower() for c in next_state["preferences"].get("companies_to_avoid", [])}

    filtered: list[dict] = []
    for job in next_state["extracted_jobs"]:
        title = str(job.get("title", "")).lower()
        company = str(job.get("company", "")).lower()
        if companies_to_avoid and company in companies_to_avoid:
            continue
        if roles and not any(role in title or title in role for role in roles):
            continue
        filtered.append(job)
    next_state["filtered_jobs"] = filtered
    _append_completed(next_state, "filter_rules")
    return next_state


def dedupe_jobs_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "dedupe_jobs"
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict] = []
    for job in next_state["filtered_jobs"]:
        key = (
            str(job.get("title", "")).strip().lower(),
            str(job.get("company", "")).strip().lower(),
            str(job.get("location", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    next_state["deduped_jobs"] = deduped
    _append_completed(next_state, "dedupe_jobs")
    return next_state


def rank_jobs_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "rank_jobs"
    keywords = [k.lower() for k in next_state["preferences"].get("keywords", [])]

    ranked: list[dict] = []
    for job in next_state["deduped_jobs"]:
        title = str(job.get("title", "")).lower()
        summary = str(job.get("summary", "")).lower()
        score = 0.0
        for keyword in keywords:
            if keyword in title or keyword in summary:
                score += 1.0
        ranked_job = dict(job)
        ranked_job["fit_score"] = round(score, 2)
        ranked_job["match_reasons"] = [kw for kw in keywords if kw in title or kw in summary]
        ranked.append(ranked_job)

    ranked.sort(key=lambda item: item.get("fit_score", 0.0), reverse=True)
    next_state["ranked_jobs"] = ranked
    _append_completed(next_state, "rank_jobs")
    return next_state


def persist_node(state: OrchestrationState, persistence_adapter) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "persist"
    cfg = state["config"]
    try:
        count = execute_with_retry_and_timeout(
            lambda: persistence_adapter.persist_jobs(
                next_state["ranked_jobs"], next_state["pipeline_run_id"]
            ),
            max_retries=cfg["max_retries"],
            timeout_seconds=cfg["node_timeout_seconds"],
        )
        next_state["persisted_count"] = int(count)
        _append_completed(next_state, "persist")
        return next_state
    except NodeExecutionError as exc:
        return _fail_state(
            next_state,
            node="persist",
            error=exc,
            attempts=exc.attempts,
            retryable=exc.retryable,
        )


def error_handler_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "error_handler"
    _append_completed(next_state, "error_handler")
    return next_state


def finalize_node(state: OrchestrationState) -> OrchestrationState:
    next_state = deepcopy(state)
    next_state["current_step"] = "finalize"
    if next_state["errors"]:
        next_state["status"] = "failed"
    else:
        next_state["status"] = "completed"
    _append_completed(next_state, "finalize")
    return next_state

