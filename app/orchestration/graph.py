from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.orchestration.nodes import (
    dedupe_jobs_node,
    dedupe_urls_node,
    error_handler_node,
    extraction_agent_node,
    filter_rules_node,
    finalize_node,
    load_preferences_node,
    persist_node,
    rank_jobs_node,
    research_agent_node,
)
from app.orchestration.state import NodeName, OrchestrationState


RESUME_ORDER: list[NodeName] = [
    "load_preferences",
    "research_agent",
    "dedupe_urls",
    "extraction_agent",
    "filter_rules",
    "dedupe_jobs",
    "rank_jobs",
    "persist",
    "finalize",
]


def _next_unfinished_step(state: OrchestrationState) -> NodeName:
    if state.get("current_step") and state["current_step"] in RESUME_ORDER:
        return state["current_step"]
    completed = set(state.get("completed_steps", []))
    for step in RESUME_ORDER:
        if step not in completed:
            return step
    return "finalize"


def _route_resume(state: OrchestrationState) -> str:
    return _next_unfinished_step(state)


def _route_after_node(state: OrchestrationState, success_target: str) -> str:
    if state.get("errors"):
        return "error_handler"
    return success_target


def build_pipeline_graph(research_adapter, extraction_adapter, persistence_adapter):
    graph = StateGraph(OrchestrationState)

    graph.add_node("load_preferences", load_preferences_node)
    graph.add_node("research_agent", lambda state: research_agent_node(state, research_adapter))
    graph.add_node("dedupe_urls", dedupe_urls_node)
    graph.add_node("extraction_agent", lambda state: extraction_agent_node(state, extraction_adapter))
    graph.add_node("filter_rules", filter_rules_node)
    graph.add_node("dedupe_jobs", dedupe_jobs_node)
    graph.add_node("rank_jobs", rank_jobs_node)
    graph.add_node("persist", lambda state: persist_node(state, persistence_adapter))
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("finalize", finalize_node)

    graph.add_conditional_edges(
        START,
        _route_resume,
        {
            "load_preferences": "load_preferences",
            "research_agent": "research_agent",
            "dedupe_urls": "dedupe_urls",
            "extraction_agent": "extraction_agent",
            "filter_rules": "filter_rules",
            "dedupe_jobs": "dedupe_jobs",
            "rank_jobs": "rank_jobs",
            "persist": "persist",
            "finalize": "finalize",
        },
    )

    graph.add_conditional_edges(
        "load_preferences",
        lambda state: _route_after_node(state, "research_agent"),
        {"research_agent": "research_agent", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "research_agent",
        lambda state: _route_after_node(state, "dedupe_urls"),
        {"dedupe_urls": "dedupe_urls", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "dedupe_urls",
        lambda state: _route_after_node(state, "extraction_agent"),
        {"extraction_agent": "extraction_agent", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "extraction_agent",
        lambda state: _route_after_node(state, "filter_rules"),
        {"filter_rules": "filter_rules", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "filter_rules",
        lambda state: _route_after_node(state, "dedupe_jobs"),
        {"dedupe_jobs": "dedupe_jobs", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "dedupe_jobs",
        lambda state: _route_after_node(state, "rank_jobs"),
        {"rank_jobs": "rank_jobs", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "rank_jobs",
        lambda state: _route_after_node(state, "persist"),
        {"persist": "persist", "error_handler": "error_handler"},
    )
    graph.add_conditional_edges(
        "persist",
        lambda state: _route_after_node(state, "finalize"),
        {"finalize": "finalize", "error_handler": "error_handler"},
    )

    graph.add_edge("error_handler", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()

