from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Callable


class NodeExecutionError(Exception):
    def __init__(self, message: str, *, attempts: int, retryable: bool) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.retryable = retryable


def execute_with_retry_and_timeout(
    fn: Callable[[], Any],
    *,
    max_retries: int,
    timeout_seconds: float,
) -> Any:
    attempts = 0
    last_exception: Exception | None = None

    for _ in range(max_retries + 1):
        attempts += 1
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fn)
                return future.result(timeout=timeout_seconds)
        except FutureTimeout as exc:
            last_exception = exc
            if attempts > max_retries:
                raise NodeExecutionError(
                    f"Node execution timed out after {timeout_seconds}s.",
                    attempts=attempts,
                    retryable=True,
                ) from exc
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            if attempts > max_retries:
                raise NodeExecutionError(
                    f"Node execution failed: {exc}",
                    attempts=attempts,
                    retryable=True,
                ) from exc

    raise NodeExecutionError(
        f"Node execution failed after {attempts} attempts: {last_exception}",
        attempts=attempts,
        retryable=True,
    )

