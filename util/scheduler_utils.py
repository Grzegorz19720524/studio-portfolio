import threading
import time
from typing import Callable
from datetime import datetime


class Task:
    def __init__(self, name: str, func: Callable, interval: float, repeat: bool = True):
        self.name = name
        self.func = func
        self.interval = interval
        self.repeat = repeat
        self.last_run: datetime | None = None
        self.run_count = 0
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def __repr__(self) -> str:
        return f"Task(name={self.name!r}, interval={self.interval}s, runs={self.run_count})"


class Scheduler:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._threads: dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def schedule(self, name: str, func: Callable, interval: float, repeat: bool = True) -> Task:
        task = Task(name, func, interval, repeat)
        with self._lock:
            self._tasks[name] = task
        thread = threading.Thread(target=self._run, args=(task,), daemon=True)
        self._threads[name] = thread
        thread.start()
        return task

    def _run(self, task: Task) -> None:
        while not task.is_cancelled():
            time.sleep(task.interval)
            if task.is_cancelled():
                break
            task.func()
            task.last_run = datetime.now()
            task.run_count += 1
            if not task.repeat:
                break

    def cancel(self, name: str) -> bool:
        with self._lock:
            task = self._tasks.get(name)
        if task:
            task.cancel()
            return True
        return False

    def cancel_all(self) -> None:
        with self._lock:
            for task in self._tasks.values():
                task.cancel()

    def status(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "name": t.name,
                    "interval": t.interval,
                    "runs": t.run_count,
                    "last_run": t.last_run.strftime("%H:%M:%S") if t.last_run else None,
                    "cancelled": t.is_cancelled(),
                }
                for t in self._tasks.values()
            ]

    def __repr__(self) -> str:
        return f"Scheduler(tasks={list(self._tasks.keys())})"


if __name__ == "__main__":
    scheduler = Scheduler()
    log = []

    def tick():
        log.append(f"tick at {datetime.now().strftime('%H:%M:%S')}")

    def once():
        log.append("one-time task ran")

    scheduler.schedule("ticker", tick, interval=0.3, repeat=True)
    scheduler.schedule("once", once, interval=0.1, repeat=False)

    time.sleep(1.1)
    scheduler.cancel_all()

    for entry in log:
        print(entry)

    print()
    for s in scheduler.status():
        print(s)
