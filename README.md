# reflex-app-scaffold

A [Claude Code](https://claude.com/claude-code) skill that scaffolds a
[Reflex](https://reflex.dev) web application from a short interview: app name,
layout, database, and the nav tree.

No authentication — that is deliberately out of scope.

## What it generates

- **Config-driven navigation** in three layout variants (top bar, sidebar, or
  both) driven by a single `NAV_ITEMS` list.
- **Router-derived highlighting** — the active nav entry is computed from
  `router.url.path`, never tracked on click, so deep links, refresh and browser
  back/forward all highlight correctly.
- A `base_page` template, dialogs (create/edit + destructive confirm), toast
  helpers, and cards.
- Optional **SQLModel + SQLite + Alembic** with a working CRUD page, including
  form-string → model-type casting with per-field validation errors.
- structlog, mypy, ruff and pytest already wired up.

## Install

```bash
git clone https://github.com/<you>/reflex-app-scaffold \
  ~/.claude/skills/reflex-app-scaffold
```

Skills load on the next Claude Code session. Then ask for a new Reflex app.

## Verified against

Reflex 0.9.8. `references/reflex_098_gotchas.md` records the API surface read
from the installed package source rather than from documentation — several
widely-copied Reflex idioms (`rx.Base`, `rx.cached_var`, auto-setters,
`rx.Model`, `App(theme=...)`, `router.page`) are removed or deprecated in this
version.

All six combinations (3 layouts × database on/off) are round-trip tested: each
generated app compiles with zero deprecation warnings and passes its own
tests, mypy and ruff.

## Layout

```
SKILL.md                  the instructions Claude follows
references/               API facts + the conventions block written into each app
templates/common/         layout- and database-independent files
templates/layout_{both,top,side}/   the ui/ chrome per variant
templates/db/             models, CRUD state, dialogs, tests
templates/nav_config/     nav config skeleton
```
