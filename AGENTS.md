# AGENTS.md - AI Agent Guide for Studio Portfolio Project

## Project Architecture

This is a **hybrid Java + Frontend web project** containing:
- **Backend**: Minimal Java template in `src/Main.java` (Java 21+ with preview features)
- **Frontend**: Modern portfolio website in `strona1/` (Polish language, dark theme, production-ready)

The project is managed by IntelliJ IDEA (see `untitled.iml`). The frontend is the primary focus—a fully responsive studio/agency portfolio with marketing pages.

## Critical Patterns & Conventions

### CSS Architecture (Primary Codebase)
- **Theme System**: All colors defined as CSS custom properties in `:root` (see `style.css` lines 4-16):
  - Primary colors: `--primary: #00f0ff` (cyan), `--accent: #ff00e5` (magenta)
  - Dark theme: `--dark` through `--dark-3` for layered backgrounds
  - Text: `--text` and `--text-muted` for contrast hierarchy
  
- **Component Naming**: BEM-like convention with dashes and double dashes for variants:
  - Cards: `.feature-card` + `.feature-card--highlight` (see lines 351-368)
  - Buttons: `.btn` + `.btn-primary`, `.btn-ghost`, `.btn-full` (lines 68-97)
  - Icons: `.icon-blue`, `.icon-white`, `.icon-purple`, `.icon-green` for color variants (lines 379-382)

- **Responsive Breakpoints**:
  - Large screens: Standard layout with flex/grid
  - `@media (max-width: 900px)`: 2-column grids collapse, navbar links hide
  - `@media (max-width: 600px)`: All grids become single column (lines 612-635)

### HTML Structure (Semantic Section-Based)
The site uses anchor-linked sections (see `index.html`):
1. **Navbar** (fixed, sticky nav with smooth scroll behavior)
2. **Hero** section with animated blobs, gradient text, and stats
3. **Features** section with 4 service cards (grid layout)
4. **Portfolio** section with 5 project items in custom 3-column grid (using `.item-large` class for 2-column spans; inline gradient backgrounds: lines 116-150)
5. **Contact** section with form (email, phone, address) and left-aligned contact details
6. **Footer** with brand and links

Use `id=""` attributes for navigation targets. All sections can be expanded with new content without breaking layout.

### CSS Animation & Effect Patterns
- **Blob animations** (lines 206-209): `blobMove` 8s with alternate, applied to 3 blobs with staggered delays
- **Ring pulse** (lines 290-293): Scale animation for concentric circles (hero visual)
- **Card float** (lines 332-335): Subtle Y-axis movement for floating cards
- **Hover states**: Consistent use of `transform: translateY(-2px)`, shadow enhancement, and border color changes

### Portfolio Grid Pattern
- **Grid structure** (lines 414-421): 3-column layout with 2 rows; `.item-large` modifier (lines 430-432) spans 2 columns
- **Item styling**: Portfolio items use inline `style="background: linear-gradient(...)"` for background gradients
- **Overlay on hover**: Dark gradient overlay with title/tag/description visible on hover (lines 434-445)

### Form Handling
Contact form in `contact-form` (lines 176-196 in HTML):
- **Layout**: Grid-based (`.form-row` class for 2-column pairs; lines 177-186) that collapses to 1 column on mobile (600px breakpoint)
- **Field types**: Name field (`input type="text"`), Email field (`input type="email"`), Subject (`input type="text"`), Message (`textarea`); all use `.form-group` wrapper for consistent spacing
- **Styling**: Blur background (`rgba(255,255,255,0.04)`), cyan focus glow, consistent border/padding (lines 551-571)
- **Current status**: No backend binding—submit requires API integration

## Developer Workflows

### Frontend Development
1. **Editing CSS**: Modify variables in `:root` to theme-shift the entire site. Test at breakpoints (900px, 600px).
2. **Adding sections**: Copy existing section pattern, ensure `id=""` for nav linking, add to navbar `.nav-links`.
3. **Testing**: Use browser DevTools to toggle breakpoints; smooth scroll is enabled by default on html element.

### Java Backend (Minimal)
- Current `Main.java` uses Java 21 preview feature (no enclosing class for `main()`)
- `IO.println()` is a custom library (not `System.out.println`)—ensure this module is available at runtime
- To extend: add new classes in `src/` and reference them from `Main.java`

## Integration Points & Dependencies

- **Google Fonts**: Inter font fetched from `fonts.googleapis.com` in `<head>` tag—requires internet access
- **No build system detected**: This is a raw Java module + static HTML. For production web deployment, consider:
  - Adding a backend framework (Spring Boot, Quarkus) to serve the static frontend
  - Building a Java HTTP server to route requests
- **Form submission**: Currently no backend endpoint—contact form is non-functional without server-side handler

## Language & Content
All text is in **Polish** (`lang="pl"`). When adding content, maintain Polish language and the studio/agency voice ("Nowa odsłona 2026", "Studio cyfrowe doświadczenia").

---
**Key Files to Reference**:
- `strona1/style.css` — Theme variables and responsive breakpoints (lines 1-50, 612-635)
- `strona1/index.html` — Section structure and semantic markup (lines 74-107 for features, 110-152 for portfolio)
- `src/Main.java` — Java template (preview syntax, custom IO module)

