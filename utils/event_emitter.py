from typing import Callable, Dict, List
import asyncio

class AsyncEventEmitter:
    def __init__(self):
        self._events: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    async def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._events:
            for callback in self._events[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)

event_emitter = AsyncEventEmitter()