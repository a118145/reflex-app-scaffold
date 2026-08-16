---
name: reflex-app-scaffold
description: Scaffold a new Reflex (reflex.dev) web application with a config-driven navigation, base page template, dialogs/toasts, optional SQLModel+alembic CRUD, structlog, and mypy/ruff/pytest wiring. Use when the user wants to start a new Reflex app, scaffold a Reflex project, create a Reflex boilerplate, or set up the folder structure for a Reflex web app. Not for adding a page to an existing app.
---

# Reflex app scaffold

Generates a working, no-auth Reflex app with a fixed folder contract.
Authentication is deliberately out of scope.

**Read `references/reflex_098_gotchas.md` before writing any Reflex code.** It
records API facts verified against the installed source; a lot of Reflex
material online is stale and will lead you to write deprecated code.

## Step 1 — Interview

Five questions in two calls: the shape of the app, then the menu. They are
split because `AskUserQuestion` takes at most four, and because the menu
default depends on the layout answered in the first call. Do not scaffold
before both phases are done.

### Phase A — one `AskUserQuestion` call, four questions

1. **App name** — Python package name, `snake_case` (e.g. `motor_toolbox`).
   Also derive `{{app_title}}`, the display name shown in the nav chrome
   (e.g. "Motor Toolbox").
2. **Layout** — `both` (top bar = sections, sidebar = that section's
   sub-pages), `top` (top bar only, one level), or `side` (sidebar only, flat).
   Sketch each one as an ASCII `preview` — the difference is spatial and a
   picture settles it faster than a sentence.
3. **Database** — SQLModel + SQLite + alembic with a working CRUD demo page,
   or no database.
4. **Top bar alignment** — `left` (default) or `center`, filling
   `{{nav_alignment}}` in `ui/nav.py`. Ask it here regardless, and say it only
   applies to `top` and `both`; for `side` there is no top bar, so discard the
   answer rather than asking a fifth question later.

Also ask for an accent colour only if the user seems to care; otherwise use
`blue`. Valid values are the 26 Radix accents.

### Phase B — the menu structure

**One `AskUserQuestion` call, one question.** Ask for the nav tree and offer a
default concrete enough to accept in one keystroke — `Home`, `About`, plus a
CRUD section when database == yes; for `both`, sections with their sub-pages
(`Home [Welcome, Getting started]`). Tailor the default to the layout chosen
in Phase A: a flat list for `top` and `side`, two levels for `both`.

A section may legitimately have no sub-pages — the sidebar then renders its
heading above an empty submenu. That is a valid outcome, not a gap to fill
with an invented page.

Restate the tree before scaffolding so a misunderstanding costs one correction
rather than a regeneration.

**Do not walk the tree section by section.** That was built and deliberately
reverted. Asking per section only looks more rigorous: to be genuinely
consistent it would also have to ask, for every page, whether it needs a model
and a database table — and that interrogation costs far more than the edit it
saves. The nav tree is a handful of lines across `nav_config.py`, `routes.py`
and `pages/`; users adjust it afterwards by hand or with a coding agent. Ask
once, offer a default, move on.

## Step 2 — Project setup

Run in the target directory (create it if the user named a new one):

```bash
uv init --bare                      # skip if pyproject.toml already exists
uv add reflex structlog             # add "reflex[db]" instead if database == yes
uv add --dev mypy ruff pytest
uv run reflex init --template blank
rm -f main.py                       # uv init leaves a stub
```

`reflex init` creates `rxconfig.py`, `assets/`, `{{app_name}}/{{app_name}}.py`,
`AGENTS.md` and `CLAUDE.md`.

`AGENTS.md` tells you to install the `reflex-dev/agent-skills` plugin
marketplace. **Do not run that install** unless the user asks — you already
have verified API facts in `references/`.

## Step 3 — Write the tree

Copy from `templates/`, substituting `{{app_name}}` and `{{app_title}}`.
`.tmpl` files carry placeholders; plain `.py` files are copied verbatim, with
two exceptions in `templates/layout_*/ui/`:

| Placeholder | File | Value |
|---|---|---|
| `{{app_title}}` | `nav.py` (top, both), `side.py` (both, side) | the display name |
| `{{nav_alignment}}` | `nav.py` (top, both only) | `"left"` or `"center"` |

Grep the copied tree for `{{` before moving on — a placeholder that survives
into the generated app is a syntax-valid string that silently does the wrong
thing (`NAV_ALIGNMENT = "{{nav_alignment}}"` just falls through to the `left`
branch).

```
templates/common/          -> always
  rxconfig.py.tmpl              -> rxconfig.py
  app_module.py.tmpl            -> {{app_name}}/{{app_name}}.py
  navigation/{state,__init__}.py
  ui/resize_gate.py
  components/{__init__,toast,confirm_dialog,cards}.py
  utils/{__init__,casting,formatting,validation,logging}.py
  pages/not_found.py
  tests/{test_navigation,test_routes}.py.tmpl
  pyproject_additions.toml      -> append to pyproject.toml
  gitignore_additions           -> append to .gitignore

templates/layout_{both,top,side}/ui/   -> pick ONE, copy into {{app_name}}/ui/
templates/nav_config/nav_config.py.tmpl -> {{app_name}}/navigation/nav_config.py

templates/db/              -> only when database == yes
  models/{__init__,item,item_form}.py
  states/{items_state,item_detail_state}.py
  components/{item_dialog,data_table}.py
  pages/{items,item_detail}.py
  tests/{test_casting,test_persistence}.py.tmpl
```

Then write by hand, from the interview answers:

- **`navigation/routes.py`** — one `UPPER_SNAKE = "/path"` constant per page.
  Nested routes compose: `ITEM_DETAIL_ROUTE = DATA_ROUTE + "/[item_id]"`.

  These four constant **names** are referenced by the templates and must exist
  verbatim (the paths are yours to choose):

  | Constant | Needed by |
  |---|---|
  | `HOME_ROUTE` | `not_found.py` ("back home" link) |
  | `NOT_FOUND_ROUTE` | `not_found.py` (must be `"/404"`) |
  | `DATA_ROUTE` | db only — `items.py`, `data_table.py`, `item_detail.py` |
  | `ITEM_DETAIL_ROUTE` | db only — `item_detail.py`; must end in `/[item_id]` |

  If the user names the CRUD section something other than "Data", keep the
  constant `DATA_ROUTE` and change only its path and its nav label, or rename
  it consistently across the four db template files.
- **`navigation/nav_config.py`** — fill `{{NAV_ITEMS}}` in the template. Omit
  `sub_items` entirely for `top` layouts. Icons are lucide names.
- **`pages/<name>.py`** — one per page. Each is
  `@rx.page(route=routes.X, title="…")` returning `base_page(...)`. Keep them
  short; real content is the user's job.
- **`pages/__init__.py`** — import every page module. This import *is* the
  route registration.
- **`states/__init__.py`**, **`models/__init__.py`** — re-export as needed.
  **`components/__init__.py` must stay free of re-exports** (see below).
- **`AGENTS.md`** — append `references/conventions.md` outside the
  `<!-- reflex managed -->` markers.
- **`README.md`** — run commands, layout table, "adding a page" steps.

Fill the test placeholders: `{{EXPECTED_ROUTES}}` (every `routes.py` constant)
and `{{EXACT_ROUTE_CASES}}` (a list of `(path, expected_route)` pairs).

## Step 4 — Database (only when database == yes)

```bash
uv run reflex db init          # creates alembic/ + the initial revision
```

`rxconfig.py.tmpl` has two database placeholders. Both must be filled, even
when there is no database — leaving `import os` behind is a lint error.

| Placeholder | database == yes | database == no |
|---|---|---|
| `{{DB_IMPORT}}` | `import os\n\n` | `""` |
| `{{DB_URL_LINE}}` | `    db_url=os.environ.get("REFLEX_DB_URL", "sqlite:///reflex.db"),\n` | `""` |

Without a database also drop `models/`, `states/items_state.py`,
`states/item_detail_state.py`, `components/{item_dialog,data_table}.py`, the
CRUD and detail pages, and the db tests.

## Step 5 — Verify

**Check ruff's scope before running `ruff format .`.** A formatter that walks
into `.venv` reformats every installed dependency and still exits 0, so no
other gate can catch it:

```bash
uv run ruff check --show-files . | grep -Ev "^$PWD/(<app_name>|tests)/|^$PWD/(rxconfig|pyproject)" \
  && echo "❌ ruff scope leaks outside the project" || echo "✅ scope clean"
```

Anything listed outside the app package, `tests/`, `rxconfig.py` and
`pyproject.toml` means `[tool.ruff]` is using `exclude` instead of
`extend-exclude` — fix that before formatting.

Then format (hand-written `routes.py` / `nav_config.py` / test parameters
will not be formatter-clean), and all four must pass:

```bash
uv run ruff format .
uv run reflex compile 2>&1 | grep -i deprecat   # must print nothing
uv run pytest -q
uv run mypy .
uv run ruff check . && uv run ruff format --check .
```

A deprecation warning means a fact in `references/reflex_098_gotchas.md` was
missed. Fix it rather than suppressing the warning.

Exit codes are not enough on their own: `ruff format` reports success no
matter how many files it touched, so check *what* a tool acted on, not only
whether it succeeded.

Then start the app (`uv run reflex run`) and confirm each route returns 200:

```bash
for p in / /your /routes; do curl -s -o /dev/null -w "%{http_code} $p\n" "http://localhost:3000$p"; done
```

## Invariants — do not "improve" these

These are the reasons the template exists. Breaking one reintroduces a bug it
was built to remove.

1. **Nav highlighting is derived from the router, never stored.** `NavState`
   has only computed vars. Nav links are plain `href=`. Adding an `on_click`
   to "keep state in sync" recreates the desync on deep links, refresh and
   browser back/forward.
2. **`resolve_active_route` matching is segment-aware.** `"/"` matches only
   exactly, and a route matches a child only via `route + "/"`. A plain
   `startswith` makes `"/"` win everywhere and makes `/data-export` match
   `/data`.
3. **States are flat.** No shared base state; use `await self.get_state(X)`.
4. **`components/__init__.py` has no re-exports, and `ui/` never imports from
   `pages/`.** Components import states, states import the toast helpers from
   components — eager re-exports make that circular. This is why the resize
   gate lives in `ui/`, not `pages/`.
5. **No second toaster.** `rx.App` already provides one.
6. **mypy relaxations stay scoped** to `components.*` and `pages.*` in
   `pyproject.toml`. Never global, never scattered `# type: ignore`.
