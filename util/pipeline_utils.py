from typing import Any, Callable


class Pipeline:
    def __init__(self, *steps: Callable):
        self._steps: list[Callable] = list(steps)

    def pipe(self, *steps: Callable) -> "Pipeline":
        return Pipeline(*self._steps, *steps)

    def run(self, value: Any) -> Any:
        for step in self._steps:
            value = step(value)
        return value

    def __call__(self, value: Any) -> Any:
        return self.run(value)

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        names = [fn.__name__ for fn in self._steps]
        return f"Pipeline({' -> '.join(names)})"


class AsyncPipeline:
    def __init__(self, *steps: Callable):
        self._steps: list[Callable] = list(steps)

    def pipe(self, *steps: Callable) -> "AsyncPipeline":
        return AsyncPipeline(*self._steps, *steps)

    async def run(self, value: Any) -> Any:
        import inspect
        for step in self._steps:
            if inspect.iscoroutinefunction(step):
                value = await step(value)
            else:
                value = step(value)
        return value

    def __repr__(self) -> str:
        names = [fn.__name__ for fn in self._steps]
        return f"AsyncPipeline({' -> '.join(names)})"


def compose(*fns: Callable) -> Callable:
    def composed(value: Any) -> Any:
        for fn in fns:
            value = fn(value)
        return value
    return composed


def branch(condition: Callable, if_true: Callable, if_false: Callable) -> Callable:
    def step(value: Any) -> Any:
        return if_true(value) if condition(value) else if_false(value)
    return step


if __name__ == "__main__":
    import re

    def strip(s: str) -> str:
        return s.strip()

    def lowercase(s: str) -> str:
        return s.lower()

    def remove_punctuation(s: str) -> str:
        return re.sub(r"[^\w\s]", "", s)

    def tokenize(s: str) -> list[str]:
        return s.split()

    def remove_short(words: list[str]) -> list[str]:
        return [w for w in words if len(w) > 2]

    pipeline = Pipeline(strip, lowercase, remove_punctuation, tokenize, remove_short)
    print(pipeline)

    text = "  Hello, World! This is a test of the Pipeline.  "
    result = pipeline.run(text)
    print("input: ", repr(text))
    print("output:", result)

    double = compose(lambda x: x * 2, lambda x: x + 10)
    print("\ncompose:", double(5))

    is_even = branch(lambda x: x % 2 == 0, lambda x: f"{x} is even", lambda x: f"{x} is odd")
    print("branch:", is_even(4))
    print("branch:", is_even(7))
