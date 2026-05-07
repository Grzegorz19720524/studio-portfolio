# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hybrid project containing two independent parts:
- **Frontend** (`strona1/`): Polish-language studio/agency portfolio site — static HTML + CSS, no build step
- **Backend** (`src/Main.java`): Minimal Java 21 template using preview features (`main()` without enclosing class, `IO.println()` custom module)

The frontend is the primary focus. The Java side is a placeholder stub.

## Running the Frontend

```bash
cd strona1
python -m http.server 8080
```

Then open `http://localhost:8080`.

## CSS Architecture

All theme values are CSS custom properties in `:root` (`style.css` lines 4–16). Changing them affects the entire site:

- `--primary: #00f0ff` (cyan), `--accent: #ff00e5` (magenta)
- `--dark` / `--dark-2` / `--dark-3` — layered dark backgrounds
- `--text` / `--text-muted` — text contrast hierarchy

**Naming convention**: BEM-like with dashes and double-dash modifiers (`.feature-card`, `.feature-card--highlight`, `.btn-primary`, `.btn-ghost`).

**Responsive breakpoints**:
- `≤900px`: 2-column grids collapse, navbar links hidden
- `≤600px`: all grids go single column, form rows stack

## HTML Structure

Anchor-linked sections for smooth-scroll navigation: `#hero` → `#features` → `#portfolio` → `#contact`. Each section uses an `id` that matches navbar `<a href="#">` targets.

Portfolio grid (`strona1/index.html` lines 115–151): 3-column × 2-row CSS grid; `.item-large` spans 2 columns. Item background gradients are set inline (`style="background: linear-gradient(...)"`).

## Animation Patterns

- Blobs: `blobMove` 8s alternate, 3 elements with staggered `animation-delay`
- Hero rings: `ringPulse` scale animation on concentric circles
- Floating cards: `cardFloat` Y-axis translateY, alternate direction
- Hover: consistently `transform: translateY(-2px)` + shadow/border enhancement

## Known Limitations

- Contact form has no backend — submit is non-functional
- `IO.println()` in `Main.java` is a custom IntelliJ module, not standard Java
- Google Fonts (Inter) requires internet access

## Language

All content is in **Polish** (`lang="pl"`). Maintain Polish when adding or editing copy.
