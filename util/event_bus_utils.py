import time
import threading
import fnmatch
from typing import Any, Callable


class Event:
    def __init__(self, name: str, data: Any = None, source: Any = None) -> None:
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = time.time()
        self._stopped = False

    def stop_propagation(self) -> None:
        self._stopped = True

    @property
    def is_stopped(self) -> bool:
        return self._stopped

    def __repr__(self) -> str:
        return f"Event({self.name!r}, data={self.data!r})"


class _Subscription:
    def __init__(
        self,
        handler: Callable,
        priority: int = 0,
        once: bool = False,
    ) -> None:
        self.handler = handler
        self.priority = priority
        self.once = once

    def __call__(self, event: Event) -> None:
        self.handler(event)


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[_Subscription]] = {}
        self._middleware: list[Callable] = []
        self._lock = threading.Lock()

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[Event], None],
        *,
        priority: int = 0,
        once: bool = False,
    ) -> Callable:
        sub = _Subscription(handler, priority, once)
        with self._lock:
            self._subs.setdefault(event_name, []).append(sub)
            self._subs[event_name].sort(key=lambda s: -s.priority)
        return handler

    def unsubscribe(self, event_name: str, handler: Callable) -> bool:
        with self._lock:
            subs = self._subs.get(event_name, [])
            before = len(subs)
            self._subs[event_name] = [s for s in subs if s.handler is not handler]
            return len(self._subs[event_name]) < before

    def once(self, event_name: str, handler: Callable[[Event], None], *, priority: int = 0) -> Callable:
        return self.subscribe(event_name, handler, priority=priority, once=True)

    def publish(self, event_name: str, data: Any = None, source: Any = None) -> Event:
        event = Event(event_name, data, source)
        for mw in self._middleware:
            result = mw(event)
            if result is False:
                return event

        to_remove: list[tuple[str, Callable]] = []

        with self._lock:
            matching: list[_Subscription] = []
            for pattern, subs in self._subs.items():
                if pattern == event_name or pattern == "*" or fnmatch.fnmatch(event_name, pattern):
                    matching.extend(subs)
            matching.sort(key=lambda s: -s.priority)
            once_subs = [(event_name if s in self._subs.get(event_name, []) else p, s.handler)
                         for p, subs in self._subs.items()
                         for s in subs if s.once and s in matching]

        for sub in matching:
            if event.is_stopped:
                break
            sub(event)
            if sub.once:
                key = next(
                    (p for p, subs in self._subs.items() if sub in subs), None
                )
                if key:
                    to_remove.append((key, sub.handler))

        for key, handler in to_remove:
            self.unsubscribe(key, handler)

        return event

    def emit(self, event_name: str, data: Any = None, source: Any = None) -> Event:
        return self.publish(event_name, data, source)

    def publish_async(self, event_name: str, data: Any = None, source: Any = None) -> threading.Thread:
        t = threading.Thread(target=self.publish, args=(event_name, data, source), daemon=True)
        t.start()
        return t

    def use(self, middleware: Callable[[Event], Any]) -> None:
        self._middleware.append(middleware)

    def on(self, event_name: str, *, priority: int = 0, once: bool = False) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self.subscribe(event_name, fn, priority=priority, once=once)
            return fn
        return decorator

    def clear(self, event_name: str | None = None) -> None:
        with self._lock:
            if event_name is None:
                self._subs.clear()
            else:
                self._subs.pop(event_name, None)

    def listeners(self, event_name: str) -> list[Callable]:
        with self._lock:
            return [s.handler for s in self._subs.get(event_name, [])]

    def listener_count(self, event_name: str) -> int:
        with self._lock:
            return len(self._subs.get(event_name, []))

    def event_names(self) -> list[str]:
        with self._lock:
            return list(self._subs.keys())

    def wait_for(self, event_name: str, timeout: float | None = None) -> Event | None:
        """Block until the named event fires, then return it."""
        result: list[Event] = []
        ready = threading.Event()

        def _handler(event: Event) -> None:
            result.append(event)
            ready.set()

        self.once(event_name, _handler)
        fired = ready.wait(timeout)
        if not fired:
            self.unsubscribe(event_name, _handler)
            return None
        return result[0] if result else None

    def __repr__(self) -> str:
        with self._lock:
            total = sum(len(v) for v in self._subs.values())
            return f"EventBus(events={list(self._subs.keys())}, total_handlers={total})"


_default_bus = EventBus()


def subscribe(
    event_name: str,
    handler: Callable[[Event], None],
    *,
    priority: int = 0,
    once: bool = False,
) -> Callable:
    return _default_bus.subscribe(event_name, handler, priority=priority, once=once)


def unsubscribe(event_name: str, handler: Callable) -> bool:
    return _default_bus.unsubscribe(event_name, handler)


def once(event_name: str, handler: Callable[[Event], None], *, priority: int = 0) -> Callable:
    return _default_bus.once(event_name, handler, priority=priority)


def publish(event_name: str, data: Any = None, source: Any = None) -> Event:
    return _default_bus.publish(event_name, data, source)


def emit(event_name: str, data: Any = None, source: Any = None) -> Event:
    return _default_bus.emit(event_name, data, source)


def publish_async(event_name: str, data: Any = None, source: Any = None) -> threading.Thread:
    return _default_bus.publish_async(event_name, data, source)


def on(event_name: str, *, priority: int = 0, once: bool = False) -> Callable:
    return _default_bus.on(event_name, priority=priority, once=once)


def use(middleware: Callable[[Event], Any]) -> None:
    _default_bus.use(middleware)


def clear(event_name: str | None = None) -> None:
    _default_bus.clear(event_name)


def listeners(event_name: str) -> list[Callable]:
    return _default_bus.listeners(event_name)


def listener_count(event_name: str) -> int:
    return _default_bus.listener_count(event_name)


def wait_for(event_name: str, timeout: float | None = None) -> Event | None:
    return _default_bus.wait_for(event_name, timeout)


if __name__ == "__main__":
    print("--- basic subscribe / publish ---")
    bus = EventBus()
    log = []

    bus.subscribe("user.login", lambda e: log.append(f"login: {e.data}"))
    bus.subscribe("user.logout", lambda e: log.append(f"logout: {e.data}"))

    bus.publish("user.login", {"user": "alice"})
    bus.publish("user.logout", {"user": "alice"})
    print("log:", log)

    print("\n--- priority ---")
    order = []
    bus2 = EventBus()
    bus2.subscribe("task", lambda e: order.append("low"),   priority=1)
    bus2.subscribe("task", lambda e: order.append("high"),  priority=10)
    bus2.subscribe("task", lambda e: order.append("mid"),   priority=5)
    bus2.publish("task")
    print("order (high to low):", order)

    print("\n--- once ---")
    fired = []
    bus3 = EventBus()
    bus3.once("ping", lambda e: fired.append("pong"))
    bus3.publish("ping")
    bus3.publish("ping")
    print("fired count (expect 1):", len(fired))

    print("\n--- stop_propagation ---")
    reached = []
    bus4 = EventBus()
    def stopper(e):
        reached.append("first")
        e.stop_propagation()
    bus4.subscribe("evt", stopper, priority=10)
    bus4.subscribe("evt", lambda e: reached.append("second"), priority=5)
    bus4.publish("evt")
    print("reached (expect only 'first'):", reached)

    print("\n--- wildcard pattern ---")
    caught = []
    bus5 = EventBus()
    bus5.subscribe("user.*", lambda e: caught.append(e.name))
    bus5.publish("user.created")
    bus5.publish("user.deleted")
    bus5.publish("order.placed")
    print("caught:", caught)

    print("\n--- catch-all (*) ---")
    all_events = []
    bus6 = EventBus()
    bus6.subscribe("*", lambda e: all_events.append(e.name))
    bus6.publish("a")
    bus6.publish("b")
    bus6.publish("c")
    print("all caught:", all_events)

    print("\n--- @on decorator ---")
    results = []
    bus7 = EventBus()

    @bus7.on("order.placed", priority=10)
    def handle_order(e):
        results.append(f"order: {e.data}")

    @bus7.on("order.placed")
    def notify(e):
        results.append("notified")

    bus7.publish("order.placed", "ORD-001")
    print("results:", results)

    print("\n--- middleware ---")
    bus8 = EventBus()
    seen = []

    def logger_mw(event):
        seen.append(f"[mw] {event.name}")

    def blocker_mw(event):
        if event.name == "blocked":
            return False

    bus8.use(logger_mw)
    bus8.use(blocker_mw)
    bus8.subscribe("allowed", lambda e: seen.append("handler"))
    bus8.subscribe("blocked", lambda e: seen.append("should not run"))
    bus8.publish("allowed")
    bus8.publish("blocked")
    print("seen:", seen)

    print("\n--- publish_async ---")
    async_log = []
    bus9 = EventBus()
    bus9.subscribe("bg", lambda e: async_log.append(e.data))
    t = bus9.publish_async("bg", "background")
    t.join()
    print("async result:", async_log)

    print("\n--- wait_for ---")
    bus10 = EventBus()
    def trigger():
        time.sleep(0.05)
        bus10.publish("ready", 42)
    threading.Thread(target=trigger, daemon=True).start()
    event = bus10.wait_for("ready", timeout=1.0)
    print("waited for event:", event)

    print("\n--- listener_count / unsubscribe ---")
    bus11 = EventBus()
    h1 = lambda e: None
    h2 = lambda e: None
    bus11.subscribe("x", h1)
    bus11.subscribe("x", h2)
    print("count before:", bus11.listener_count("x"))
    bus11.unsubscribe("x", h1)
    print("count after unsubscribe:", bus11.listener_count("x"))
    bus11.clear("x")
    print("count after clear:", bus11.listener_count("x"))
