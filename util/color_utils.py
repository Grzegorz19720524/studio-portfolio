import colorsys
import random


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360, 2), round(s * 100, 2), round(l * 100, 2)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return round(h * 360, 2), round(s * 100, 2), round(v * 100, 2)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def luminance(r: int, g: int, b: int) -> float:
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return round(0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b), 6)


def is_light(hex_color: str) -> bool:
    return luminance(*hex_to_rgb(hex_color)) > 0.179


def contrast_color(hex_color: str) -> str:
    return "#000000" if is_light(hex_color) else "#ffffff"


def lighten(hex_color: str, amount: float = 10.0) -> str:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    return rgb_to_hex(*hsl_to_rgb(h, s, min(l + amount, 100)))


def darken(hex_color: str, amount: float = 10.0) -> str:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    return rgb_to_hex(*hsl_to_rgb(h, s, max(l - amount, 0)))


def mix(hex1: str, hex2: str, ratio: float = 0.5) -> str:
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    r = round(r1 * (1 - ratio) + r2 * ratio)
    g = round(g1 * (1 - ratio) + g2 * ratio)
    b = round(b1 * (1 - ratio) + b2 * ratio)
    return rgb_to_hex(r, g, b)


def complementary(hex_color: str) -> str:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    return rgb_to_hex(*hsl_to_rgb((h + 180) % 360, s, l))


def random_color() -> str:
    return rgb_to_hex(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def analogous(hex_color: str, angle: float = 30.0) -> tuple[str, str]:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    return (
        rgb_to_hex(*hsl_to_rgb((h - angle) % 360, s, l)),
        rgb_to_hex(*hsl_to_rgb((h + angle) % 360, s, l)),
    )


def triadic(hex_color: str) -> tuple[str, str]:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    return (
        rgb_to_hex(*hsl_to_rgb((h + 120) % 360, s, l)),
        rgb_to_hex(*hsl_to_rgb((h + 240) % 360, s, l)),
    )


if __name__ == "__main__":
    color = "#3498db"
    r, g, b = hex_to_rgb(color)

    print(f"color:            {color}")
    print(f"hex_to_rgb:       {r}, {g}, {b}")
    print(f"rgb_to_hex:       {rgb_to_hex(r, g, b)}")
    print(f"rgb_to_hsl:       {rgb_to_hsl(r, g, b)}")
    print(f"rgb_to_hsv:       {rgb_to_hsv(r, g, b)}")
    print(f"luminance:        {luminance(r, g, b)}")
    print(f"is_light:         {is_light(color)}")
    print(f"contrast_color:   {contrast_color(color)}")
    print()
    print(f"lighten 15%:      {lighten(color, 15)}")
    print(f"darken 15%:       {darken(color, 15)}")
    print(f"mix with #e74c3c: {mix(color, '#e74c3c')}")
    print(f"complementary:    {complementary(color)}")
    print(f"analogous:        {analogous(color)}")
    print(f"triadic:          {triadic(color)}")
    print(f"random_color:     {random_color()}")
    print()
    print("shorthand hex #fff:")
    print(f"  hex_to_rgb:     {hex_to_rgb('#fff')}")
    print(f"  is_light:       {is_light('#fff')}")
    print(f"  contrast:       {contrast_color('#fff')}")
