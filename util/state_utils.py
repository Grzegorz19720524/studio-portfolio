from typing import Any, Callable


class Store:
    def __init__(self, initial: dict):
        self._state = dict(initial)
        self._subscribers: list[Callable] = []
        self._history: list[dict] = [dict(initial)]

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value
        self._history.append(dict(self._state))
        self._notify()

    def update(self, data: dict) -> None:
        self._state.update(data)
        self._history.append(dict(self._state))
        self._notify()

    def reset(self) -> None:
        self._state = dict(self._history[0])
        self._history.append(dict(self._state))
        self._notify()

    def undo(self) -> bool:
        if len(self._history) < 2:
            return False
        self._history.pop()
        self._state = dict(self._history[-1])
        self._notify()
        return True

    def subscribe(self, fn: Callable) -> None:
        self._subscribers.append(fn)

    def _notify(self) -> None:
        for fn in self._subscribers:
            fn(dict(self._state))

    @property
    def state(self) -> dict:
        return dict(self._state)

    def __repr__(self) -> str:
        return f"Store(state={self._state}, history={len(self._history)})"


class StateMachine:
    def __init__(self, initial: str, transitions: dict[str, list[str]]):
        self._state = initial
        self._transitions = transitions
        self._on_enter: dict[str, Callable] = {}
        self._on_exit: dict[str, Callable] = {}

    def transition(self, new_state: str) -> bool:
        allowed = self._transitions.get(self._state, [])
        if new_state not in allowed:
            return False
        if self._state in self._on_exit:
            self._on_exit[self._state](self._state)
        self._state = new_state
        if new_state in self._on_enter:
            self._on_enter[new_state](new_state)
        return True

    def on_enter(self, state: str, fn: Callable) -> None:
        self._on_enter[state] = fn

    def on_exit(self, state: str, fn: Callable) -> None:
        self._on_exit[state] = fn

    def can(self, state: str) -> bool:
        return state in self._transitions.get(self._state, [])

    @property
    def current(self) -> str:
        return self._state

    def __repr__(self) -> str:
        return f"StateMachine(state={self._state!r})"


if __name__ == "__main__":
    print("--- Store ---")
    store = Store({"user": None, "theme": "light", "count": 0})
    store.subscribe(lambda s: print(f"  state changed: {s}"))

    store.set("user", "Grzegorz")
    store.update({"theme": "dark", "count": 1})
    print("undo:", store.undo())
    print("state:", store.state)

    print("\n--- StateMachine ---")
    sm = StateMachine(
        initial="idle",
        transitions={
            "idle": ["running"],
            "running": ["paused", "stopped"],
            "paused": ["running", "stopped"],
            "stopped": [],
        },
    )
    sm.on_enter("running", lambda s: print(f"  entered: {s}"))
    sm.on_exit("running", lambda s: print(f"  exited: {s}"))

    print("current:", sm.current)
    print("transition to running:", sm.transition("running"))
    print("transition to idle:", sm.transition("idle"))
    print("transition to paused:", sm.transition("paused"))
    print("current:", sm.current)
    print(sm)
