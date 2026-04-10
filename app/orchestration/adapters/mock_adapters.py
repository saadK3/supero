from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class MockResearchAdapter:
    fail_times: int = 0
    sleep_seconds: float = 0.0
    _attempts: int = 0

    def discover_urls(self, preferences: dict) -> list[dict]:
        import time

        self._attempts += 1
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        if self._attempts <= self.fail_times:
            raise RuntimeError("Mock research adapter forced failure.")

        roles = preferences.get("roles", ["LLM Engineer"])
        urls: list[dict] = []
        for idx, role in enumerate(roles, start=1):
            slug = role.lower().replace(" ", "-")
            urls.append(
                {
                    "source": "mock_board",
                    "source_url": f"https://jobs.example.com/{slug}-{idx}",
                    "canonical_url": f"https://jobs.example.com/{slug}-{idx}",
                    "discovery_query": role,
                }
            )
        return urls


@dataclass
class MockExtractionAdapter:
    fail_times: int = 0
    sleep_seconds: float = 0.0
    _attempts: int = 0

    def extract_jobs(self, candidate_urls: list[dict], preferences: dict) -> list[dict]:
        import time

        self._attempts += 1
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        if self._attempts <= self.fail_times:
            raise RuntimeError("Mock extraction adapter forced failure.")

        jobs: list[dict] = []
        for item in candidate_urls:
            query = item.get("discovery_query") or "LLM Engineer"
            jobs.append(
                {
                    "title": query,
                    "company": "Mock Company",
                    "location": "Remote",
                    "remote_type": "remote",
                    "experience_level": "junior",
                    "salary_text": "$80,000 - $120,000",
                    "apply_url": item["source_url"] + "/apply",
                    "source": item["source"],
                    "source_url": item["source_url"],
                    "posted_date": str(date.today()),
                    "summary": f"Opportunity for {query}",
                    "raw_text": f"Raw listing for {query}",
                }
            )
        return jobs


@dataclass
class MockPersistenceAdapter:
    persisted: list[dict] | None = None

    def persist_jobs(self, jobs: list[dict], pipeline_run_id: str) -> int:
        self.persisted = list(jobs)
        return len(jobs)

