from typing import Callable, Dict, TypeVar

T = TypeVar("T")


class IdempotencyRegistry:
    def __init__(self) -> None:
        self._results: Dict[str, object] = {}

    def execute_once(self, key: str, operation: Callable[[], T]) -> T:
        if key in self._results:
            return self._results[key]  # type: ignore[return-value]
        result = operation()
        self._results[key] = result
        return result
