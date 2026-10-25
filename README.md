# reflex-app-scaffold

A [Claude Code](https://claude.com/claude-code) skill that scaffolds a
[Reflex](https://reflex.dev) web application from a short interview: app name,
layout, database, and the nav tree.

No authentication — that is deliberately out of scope. Add it afterwards with
the companion skill
[reflex-auth-boilerplate](https://github.com/a118145/reflex-auth-boilerplate).

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
- structlog, mypy, ruff and pytest already wired up, behind two scripts:
  `scripts/check.sh` (lint, format, types, tests; `--full` adds
  `reflex compile` with zero deprecation warnings) and `scripts/smoke.sh`
  (starts the app, expects 200 on every route, stops it).
- `AGENTS.md` / `CLAUDE.md` with the project conventions, and
  `docs/reflex-facts.md` with the verified API facts, so later coding agents
  start from the same ground truth.
- **No phoning home**: `telemetry_enabled=False`, `reflex init --no-agents`
  (no AGENTS.md download), no PyPI version check during the scaffold.

## Non-interactive (crew mode)

With a `Masterplan.md` in the target directory that contains a
`yaml crew-scaffold` block (app name, layout, database, the full nav tree),
the skill skips the interview, validates the block, and generates a stub page
for every route — so parallel work afterwards touches disjoint page files.
Invalid or incomplete block: it stops and lists the problems.

## Install

```bash
git clone https://github.com/a118145/reflex-app-scaffold \
  ~/.claude/skills/reflex-app-scaffold
```

Skills load on the next Claude Code session. Then ask for a new Reflex app.

## Verified against

Reflex 0.9.8, sqlmodel 0.0.48. `references/reflex_098_gotchas.md` records the API surface read
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
