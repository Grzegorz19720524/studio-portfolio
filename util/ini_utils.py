import configparser
import io


def _new() -> configparser.ConfigParser:
    return configparser.ConfigParser(interpolation=None)


def read_ini(path: str, encoding: str = "utf-8") -> configparser.ConfigParser:
    config = _new()
    config.read(path, encoding=encoding)
    return config


def write_ini(config: configparser.ConfigParser, path: str, encoding: str = "utf-8") -> None:
    with open(path, "w", encoding=encoding) as f:
        config.write(f)


def parse_string(text: str) -> configparser.ConfigParser:
    config = _new()
    config.read_string(text)
    return config


def to_string(config: configparser.ConfigParser) -> str:
    buf = io.StringIO()
    config.write(buf)
    return buf.getvalue()


def get(config: configparser.ConfigParser, section: str, key: str,
        default: str | None = None) -> str | None:
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default


def get_int(config: configparser.ConfigParser, section: str, key: str,
            default: int = 0) -> int:
    try:
        return config.getint(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return default


def get_float(config: configparser.ConfigParser, section: str, key: str,
              default: float = 0.0) -> float:
    try:
        return config.getfloat(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return default


def get_bool(config: configparser.ConfigParser, section: str, key: str,
             default: bool = False) -> bool:
    try:
        return config.getboolean(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return default


def set_value(config: configparser.ConfigParser, section: str, key: str, value: str) -> None:
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, str(value))


def has_section(config: configparser.ConfigParser, section: str) -> bool:
    return config.has_section(section)


def has_key(config: configparser.ConfigParser, section: str, key: str) -> bool:
    return config.has_option(section, key)


def sections(config: configparser.ConfigParser) -> list[str]:
    return config.sections()


def keys(config: configparser.ConfigParser, section: str) -> list[str]:
    if not config.has_section(section):
        return []
    return [k for k in config.options(section) if k not in config.defaults()]


def items(config: configparser.ConfigParser, section: str) -> dict[str, str]:
    if not config.has_section(section):
        return {}
    return dict(config.items(section))


def to_dict(config: configparser.ConfigParser) -> dict[str, dict[str, str]]:
    return {section: dict(config.items(section)) for section in config.sections()}


def from_dict(data: dict[str, dict[str, str]]) -> configparser.ConfigParser:
    config = _new()
    for section, values in data.items():
        config.add_section(section)
        for key, value in values.items():
            config.set(section, key, str(value))
    return config


def remove_section(config: configparser.ConfigParser, section: str) -> bool:
    return config.remove_section(section)


def remove_key(config: configparser.ConfigParser, section: str, key: str) -> bool:
    return config.remove_option(section, key)


def merge(base: configparser.ConfigParser,
          override: configparser.ConfigParser) -> configparser.ConfigParser:
    result = _new()
    for section in base.sections():
        result.add_section(section)
        for key, value in base.items(section):
            result.set(section, key, value)
    for section in override.sections():
        if not result.has_section(section):
            result.add_section(section)
        for key, value in override.items(section):
            result.set(section, key, value)
    return result


if __name__ == "__main__":
    ini_text = """
[database]
host = localhost
port = 5432
name = mydb
debug = true

[server]
host = 0.0.0.0
port = 8080
workers = 4
timeout = 30.5

[logging]
level = INFO
file = app.log
"""

    config = parse_string(ini_text)

    print("sections:          ", sections(config))
    print("keys(database):    ", keys(config, "database"))

    print("\nget(database,host):", get(config, "database", "host"))
    print("get_int(server,port):", get_int(config, "server", "port"))
    print("get_float(server,timeout):", get_float(config, "server", "timeout"))
    print("get_bool(database,debug):", get_bool(config, "database", "debug"))
    print("get(missing,key,'N/A'):", get(config, "missing", "key", "N/A"))

    print("\nitems(logging):    ", items(config, "logging"))

    print("\nhas_section(server):", has_section(config, "server"))
    print("has_section(cache): ", has_section(config, "cache"))
    print("has_key(database,name):", has_key(config, "database", "name"))

    set_value(config, "cache", "ttl", "300")
    set_value(config, "cache", "max_size", "1000")
    print("\nafter set_value, sections:", sections(config))

    remove_key(config, "logging", "file")
    print("after remove_key(logging,file):", keys(config, "logging"))

    print("\nto_dict:")
    import pprint
    pprint.pprint(to_dict(config))

    print("\nfrom_dict + to_string:")
    cfg2 = from_dict({"app": {"name": "MyApp", "version": "1.0"}, "env": {"mode": "prod"}})
    print(to_string(cfg2))

    print("merge demo:")
    override = parse_string("[server]\nport = 9090\n[cache]\nttl = 600\n")
    merged = merge(config, override)
    print("  server.port:", get(merged, "server", "port"))
    print("  cache.ttl:  ", get(merged, "cache", "ttl"))
