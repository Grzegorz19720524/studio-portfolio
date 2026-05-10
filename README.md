# Studio Portfolio

Strona portfolio studia cyfrowego — nowoczesny, responsywny frontend w HTML/CSS z animacjami i sekcjami: hero, usługi, portfolio, kontakt.

## Podgląd

![Studio Portfolio](https://raw.githubusercontent.com/Grzegorz19720524/studio-portfolio/main/strona1/preview.png)

## Struktura projektu

```
├── strona1/
│   ├── index.html      # Główny plik HTML
│   └── style.css       # Style CSS z custom properties
├── src/
│   └── Main.java       # Szablon Java 21 (placeholder)
└── README.md
```

## Frontend (`strona1/`)

Statyczna strona w czystym HTML + CSS, bez frameworków i kroku budowania.

### Sekcje

- **Hero** — animowane blobs, pierścienie, karty float
- **Usługi** — 4 karty z ikonami (strony, aplikacje, branding, marketing)
- **Portfolio** — siatka 3×2 z efektem hover overlay
- **Kontakt** — formularz z walidacją HTML5

### Uruchomienie

```bash
cd strona1
python -m http.server 8080
# Otwórz http://localhost:8080
```

### Technologie

- HTML5, CSS3 (custom properties, Grid, Flexbox, animacje)
- Google Fonts (Inter)
- Bez JavaScript, bez zależności npm

### Paleta kolorów

| Zmienna | Wartość | Opis |
|---------|---------|------|
| `--primary` | `#00f0ff` | Cyan |
| `--accent` | `#ff00e5` | Magenta |
| `--dark` | `#07070f` | Tło główne |

### Breakpointy

| Szerokość | Zachowanie |
|-----------|-----------|
| `≤ 900px` | Siatki 2-kolumnowe, ukryty navbar |
| `≤ 600px` | Siatki 1-kolumnowe, formularz pionowo |

## Automatyzacja (N8N + GitHub MCP)

Projekt zawiera workflow N8N (`docker-compose.yml` w `~/n8n/`) łączący się z GitHub przez protokół MCP.

### Uruchomienie N8N

```bash
cd ~/n8n
docker compose up -d
# Panel: http://localhost:5678
```

### Workflow

Workflow **"GitHub MCP - polaczenie testowe"** uruchamia się co godzinę i pobiera:

- Dane konta GitHub (`get_me`)
- Listę repozytoriów (`search_repositories`)
- Otwarte issues (`search_issues`)
- Otwarte pull requesty (`search_pull_requests`)

## Licencja

MIT
