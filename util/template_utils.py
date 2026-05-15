import re
import html
from pathlib import Path
from typing import Any, Callable


_FILTERS: dict[str, Callable] = {
    "upper":   str.upper,
    "lower":   str.lower,
    "title":   str.title,
    "strip":   str.strip,
    "length":  len,
    "reverse": lambda s: s[::-1],
    "escape":  html.escape,
    "int":     int,
    "float":   float,
    "bool":    bool,
    "default": lambda v, d="": v if v else d,
}

_TOKEN_RE = re.compile(r"(\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\})", re.DOTALL)


def register_filter(name: str, fn: Callable) -> None:
    _FILTERS[name] = fn


def escape_html(text: str) -> str:
    return html.escape(str(text))


def _resolve(expr: str, context: dict) -> Any:
    expr = expr.strip()
    parts = [p.strip() for p in expr.split("|")]
    name = parts[0]
    try:
        value = eval(name, {"__builtins__": {}}, context)
    except Exception:
        value = context.get(name, "")
    for filt in parts[1:]:
        if ":" in filt:
            fname, _, farg = filt.partition(":")
            fn = _FILTERS.get(fname.strip())
            if fn:
                value = fn(value, farg.strip().strip("'\""))
        else:
            fn = _FILTERS.get(filt)
            if fn:
                value = fn(value)
    return value


def _tokenize(template: str) -> list[tuple[str, str]]:
    tokens = []
    for part in _TOKEN_RE.split(template):
        if part.startswith("{{") and part.endswith("}}"):
            tokens.append(("var", part[2:-2].strip()))
        elif part.startswith("{%") and part.endswith("%}"):
            tokens.append(("tag", part[2:-2].strip()))
        elif part.startswith("{#") and part.endswith("#}"):
            pass
        else:
            tokens.append(("text", part))
    return tokens


def _render_tokens(tokens: list, context: dict, pos: int = 0) -> tuple[str, int]:
    result = []
    while pos < len(tokens):
        kind, value = tokens[pos]
        if kind == "text":
            result.append(value)
            pos += 1
        elif kind == "var":
            result.append(str(_resolve(value, context)))
            pos += 1
        elif kind == "tag":
            parts = value.split(None, 1)
            keyword = parts[0]
            if keyword in ("endif", "endfor", "else", "elif"):
                return "".join(result), pos
            elif keyword == "if":
                cond_expr = parts[1] if len(parts) > 1 else ""
                pos += 1
                body, pos = _render_tokens(tokens, context, pos)
                _, _ = tokens[pos][0], tokens[pos][1].split(None, 1)
                if _resolve(cond_expr, context):
                    result.append(body)
                    while pos < len(tokens) and tokens[pos][1].split()[0] not in ("endif",):
                        _, pos = _render_tokens(tokens, context, pos + 1)
                        if pos < len(tokens) and tokens[pos][1].split()[0] == "endif":
                            break
                else:
                    while pos < len(tokens):
                        tag_parts = tokens[pos][1].split(None, 1)
                        kw = tag_parts[0]
                        if kw == "elif":
                            cond_expr = tag_parts[1] if len(tag_parts) > 1 else ""
                            pos += 1
                            body, pos = _render_tokens(tokens, context, pos)
                            if _resolve(cond_expr, context):
                                result.append(body)
                                while pos < len(tokens) and tokens[pos][1].split()[0] != "endif":
                                    _, pos = _render_tokens(tokens, context, pos + 1)
                                break
                        elif kw == "else":
                            pos += 1
                            body, pos = _render_tokens(tokens, context, pos)
                            result.append(body)
                            break
                        elif kw == "endif":
                            break
                        else:
                            pos += 1
                pos += 1
            elif keyword == "for":
                m = re.match(r"(\w+)\s+in\s+(.+)", parts[1] if len(parts) > 1 else "")
                if not m:
                    pos += 1
                    continue
                var_name, iter_expr = m.group(1), m.group(2)
                pos += 1
                body_tokens_start = pos
                _, body_end = _render_tokens(tokens, context, pos)
                body_tokens = tokens[body_tokens_start:body_end]
                iterable = _resolve(iter_expr, context)
                if hasattr(iterable, "__iter__"):
                    for i, item in enumerate(iterable):
                        loop_ctx = {**context, var_name: item,
                                    "loop": {"index": i + 1, "index0": i,
                                             "first": i == 0,
                                             "last": i == len(list(type(iterable)(iterable))) - 1}}
                        chunk, _ = _render_tokens(body_tokens, loop_ctx)
                        result.append(chunk)
                pos = body_end + 1
            else:
                pos += 1
        else:
            pos += 1
    return "".join(result), pos


def render(template: str, context: dict | None = None) -> str:
    tokens = _tokenize(template)
    output, _ = _render_tokens(tokens, context or {})
    return output


def render_safe(template: str, context: dict | None = None) -> str:
    ctx = context or {}
    result = re.sub(r"\{\{(.+?)\}\}", lambda m: str(_resolve(m.group(1), ctx)), template)
    result = re.sub(r"\{#.*?#\}", "", result, flags=re.DOTALL)
    return result


def render_file(path: str, context: dict | None = None, encoding: str = "utf-8") -> str:
    return render(Path(path).read_text(encoding=encoding), context)


class Template:
    def __init__(self, source: str):
        self.source = source
        self._tokens = _tokenize(source)

    def render(self, context: dict | None = None) -> str:
        output, _ = _render_tokens(self._tokens, context or {})
        return output

    @classmethod
    def from_file(cls, path: str, encoding: str = "utf-8") -> "Template":
        return cls(Path(path).read_text(encoding=encoding))


if __name__ == "__main__":
    print("--- basic variable substitution ---")
    t = "Hello, {{ name }}! You have {{ count }} messages."
    print(render(t, {"name": "Alice", "count": 5}))

    print("\n--- filters ---")
    t2 = "{{ name | upper }} | {{ title | title }} | {{ tag | escape }}"
    print(render(t2, {"name": "hello", "title": "the quick fox", "tag": "<b>bold</b>"}))

    print("\n--- if / elif / else ---")
    t3 = """\
{% if score >= 90 %}Grade: A
{% elif score >= 75 %}Grade: B
{% elif score >= 60 %}Grade: C
{% else %}Grade: F
{% endif %}"""
    for score in [95, 80, 65, 45]:
        print(f"score={score}: {render(t3, {'score': score}).strip()}")

    print("\n--- for loop ---")
    t4 = """\
{% for item in items %}- {{ item }}
{% endfor %}"""
    print(render(t4, {"items": ["apple", "banana", "cherry"]}), end="")

    print("\n--- nested context ---")
    t5 = "{{ user }} | items: {{ count }} | {{ label | lower }}"
    print(render(t5, {"user": "Bob", "count": 3, "label": "ACTIVE"}))

    print("\n--- comments ignored ---")
    t6 = "Hello {# this is a comment #}{{ name }}!"
    print(render(t6, {"name": "World"}))

    print("\n--- Template class ---")
    tmpl = Template("Dear {{ name }},\n\nYour score is {{ score | int }}.\n\nRegards")
    print(tmpl.render({"name": "Carol", "score": "98"}))

    print("\n--- render_safe (missing keys left blank) ---")
    t7 = "{{ present }} and {{ missing }}"
    print(render_safe(t7, {"present": "hello"}))

    print("\n--- register_filter ---")
    register_filter("shout", lambda s: s.upper() + "!!!")
    print(render("{{ msg | shout }}", {"msg": "hello world"}))
