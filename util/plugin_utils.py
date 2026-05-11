from typing import Callable, Any, Type


class Plugin:
    name: str = ""
    version: str = "1.0.0"
    description: str = ""

    def setup(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"Plugin(name={self.name!r}, version={self.version})"


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self._hooks: dict[str, list[Callable]] = {}

    def register(self, plugin: Plugin) -> None:
        if not plugin.name:
            raise ValueError("Plugin must have a name")
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin {plugin.name!r} already registered")
        self._plugins[plugin.name] = plugin
        plugin.setup()

    def unregister(self, name: str) -> bool:
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.teardown()
            return True
        return False

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def all(self) -> list[Plugin]:
        return list(self._plugins.values())

    def hook(self, event: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._hooks.setdefault(event, []).append(fn)
            return fn
        return decorator

    def trigger(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        return [fn(*args, **kwargs) for fn in self._hooks.get(event, [])]

    def is_registered(self, name: str) -> bool:
        return name in self._plugins

    def __len__(self) -> int:
        return len(self._plugins)

    def __repr__(self) -> str:
        return f"PluginRegistry(plugins={list(self._plugins.keys())})"


if __name__ == "__main__":
    registry = PluginRegistry()

    class LoggerPlugin(Plugin):
        name = "logger"
        version = "1.2.0"
        description = "Logs all events"

        def setup(self):
            print(f"  [{self.name}] setup complete")

        def teardown(self):
            print(f"  [{self.name}] teardown complete")

    class AuthPlugin(Plugin):
        name = "auth"
        version = "2.0.1"
        description = "Handles authentication"

        def setup(self):
            print(f"  [{self.name}] setup complete")

    registry.register(LoggerPlugin())
    registry.register(AuthPlugin())
    print(registry)

    @registry.hook("on_request")
    def log_request(url: str):
        return f"[logger] request: {url}"

    @registry.hook("on_request")
    def auth_check(url: str):
        return f"[auth] checking: {url}"

    print("\ntrigger on_request:")
    results = registry.trigger("on_request", "https://example.com/api")
    for r in results:
        print(" ", r)

    print("\nunregister logger:")
    registry.unregister("logger")
    print(registry)
    print("is_registered('logger'):", registry.is_registered("logger"))
