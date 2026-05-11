from typing import Callable, Any


class Observable:
    def __init__(self):
        self._observers: list[Callable] = []

    def subscribe(self, observer: Callable) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Callable) -> bool:
        if observer in self._observers:
            self._observers.remove(observer)
            return True
        return False

    def notify(self, *args: Any, **kwargs: Any) -> None:
        for observer in list(self._observers):
            observer(*args, **kwargs)

    def observer_count(self) -> int:
        return len(self._observers)

    def __repr__(self) -> str:
        return f"Observable(observers={self.observer_count()})"


class ObservableValue:
    def __init__(self, value: Any = None):
        self._value = value
        self._observers: list[Callable] = []

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        old_value = self._value
        self._value = new_value
        if old_value != new_value:
            for observer in list(self._observers):
                observer(new_value, old_value)

    def subscribe(self, observer: Callable) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Callable) -> bool:
        if observer in self._observers:
            self._observers.remove(observer)
            return True
        return False

    def __repr__(self) -> str:
        return f"ObservableValue(value={self._value!r}, observers={len(self._observers)})"


if __name__ == "__main__":
    print("--- Observable ---")
    source = Observable()

    def logger(msg: str):
        print(f"  [logger] {msg}")

    def auditor(msg: str):
        print(f"  [auditor] received: {msg!r}")

    source.subscribe(logger)
    source.subscribe(auditor)
    print(source)

    source.notify("user logged in")
    source.unsubscribe(auditor)
    print("\nafter unsubscribe:")
    source.notify("user logged out")

    print("\n--- ObservableValue ---")
    counter = ObservableValue(0)

    def on_change(new: int, old: int):
        print(f"  changed: {old} -> {new}")

    counter.subscribe(on_change)
    counter.value = 1
    counter.value = 2
    counter.value = 2
    counter.value = 5
    print(counter)
