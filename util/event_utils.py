from collections import defaultdict
from typing import Callable, Any


class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = defaultdict(list)
        self._once: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, listener: Callable) -> None:
        self._listeners[event].append(listener)

    def once(self, event: str, listener: Callable) -> None:
        self._once[event].append(listener)

    def off(self, event: str, listener: Callable) -> bool:
        if listener in self._listeners[event]:
            self._listeners[event].remove(listener)
            return True
        return False

    def emit(self, event: str, *args: Any, **kwargs: Any) -> int:
        called = 0
        for listener in list(self._listeners[event]):
            listener(*args, **kwargs)
            called += 1
        for listener in list(self._once[event]):
            listener(*args, **kwargs)
            called += 1
        self._once[event].clear()
        return called

    def listeners(self, event: str) -> list[Callable]:
        return self._listeners[event] + self._once[event]

    def clear(self, event: str | None = None) -> None:
        if event:
            self._listeners[event].clear()
            self._once[event].clear()
        else:
            self._listeners.clear()
            self._once.clear()

    def __repr__(self) -> str:
        events = set(self._listeners) | set(self._once)
        return f"EventEmitter(events={list(events)})"


if __name__ == "__main__":
    emitter = EventEmitter()

    def on_login(user: str):
        print(f"  [on]   user logged in: {user}")

    def on_login_once(user: str):
        print(f"  [once] welcome message for: {user}")

    emitter.on("login", on_login)
    emitter.once("login", on_login_once)

    print("emit #1:")
    emitter.emit("login", "Grzegorz")

    print("emit #2 (once listener should not fire):")
    emitter.emit("login", "Grzegorz")

    emitter.off("login", on_login)
    print("emit #3 (all listeners removed):")
    count = emitter.emit("login", "Grzegorz")
    print(f"  listeners called: {count}")

    print(emitter)
