# Conventions block for generated apps

Write this as the generated `AGENTS.md` (everything below the `---`), and
write `CLAUDE.md` containing exactly `@AGENTS.md` so Claude Code sessions read
it too. `reflex init --no-agents` creates neither file, which is deliberate:
the stock AGENTS.md is downloaded from GitHub at init time and points agents at
an external plugin marketplace.

Replace `{{app_name}}` and prune what the app does not have: drop
folder-contract rows for missing folders (a database-less app has no
`models/`), and drop the **Database** rules when there is no database.
Documenting something that is not there sends the next reader looking for it.

---

# Project conventions

Everything below is project-specific and takes precedence over generic Reflex
advice. Read it before editing.

## Folder contract

| Path | Holds |
|---|---|
| `navigation/routes.py` | Route constants. **The only place a URL string is written.** |
| `navigation/nav_config.py` | `NAV_ITEMS` + `resolve_active_route`. Drives the nav chrome. |
| `navigation/state.py` | `NavState`. The one state outside `states/`. |
| `ui/` | `base_page` template, nav chrome, mobile resize gate. |
| `components/` | Dialogs, toasts, cards, tables. Reused by pages. |
| `models/` | SQLModel tables; form models only where a form feeds them. |
| `pages/` | One module per page. Composes components. |
| `states/` | All other states. |
| `utils/` | Casting, formatting, validation, logging. |
| `scripts/check.sh` | The gate. `--full` adds `reflex compile`. |
| `scripts/smoke.sh` | Starts the app, checks every route, stops it. |
| `docs/reflex-facts.md` | Verified Reflex 0.9.8 API facts. |

## Rules

1. **Navigation highlighting is derived, never stored.** `NavState` has only
   computed vars reading `self.router.url.path`. Nav links are plain `href=`.
   Never add an `on_click` to "keep nav state in sync" — click-tracking
   desyncs on deep links, F5 and browser back/forward. `tests/test_navigation.py`
   guards this.

2. **States are flat.** Subclass `rx.State` directly. Share via
   `await self.get_state(Other)`, not inheritance.

3. **A new page touches four files**: `routes.py`, `nav_config.py`,
   `pages/your_page.py`, `pages/__init__.py`. Missing the last one means the
   `@rx.page` decorator never runs and the route silently 404s.

4. **`components/__init__.py` stays empty of re-exports.** Components import
   from `states/`; states import toast helpers from `components/`. Eager
   re-exports make that circular. Likewise, `ui/` must never import from
   `pages/` — that is why the resize gate lives in `ui/`.

5. **Log events, not sentences**: `log.info("item.create", item_id=7)`.

6. **Form data is cast before validation** via `utils/validation.parse_form`,
   which returns `(instance | None, errors)`. On errors, return early from the
   handler so the dialog stays open with the user's input intact.

7. **Never mount a second toaster.** `rx.App` provides one.

8. **Read `docs/reflex-facts.md` before writing Reflex code.** It records the
   API as it is in the installed version; much Reflex material online (and in
   model memory) is stale.

9. **The gate is `scripts/check.sh`.** Run it before every commit; green means
   exit 0. `scripts/check.sh --full` adds `reflex compile` with zero
   deprecation warnings. Do not start `reflex run` unless asked —
   `scripts/smoke.sh` is the runtime check, and it binds ports 3000/8000.

10. **No phoning home.** `telemetry_enabled=False` stays in `rxconfig.py`. No
    analytics, trackers, CDN assets or calls to external services unless the
    project explicitly asks for them.

## Database

- Schema changes only through migrations:
  `uv run reflex db makemigrations --message "<what>"`, then
  `uv run reflex db migrate`. Never edit or regenerate an existing revision;
  keep a single head.
- Autogenerate ignores column **type** changes (`compare_type=False`). A type
  change needs a hand-written migration (`op.alter_column(..., type_=...)`
  inside `with op.batch_alter_table(...)` for SQLite).
- Models stay portable between SQLite and Postgres: standard SQLModel/
  SQLAlchemy types only, no dialect-specific types (JSONB, ARRAY), no raw SQL.
  The database is chosen only by `REFLEX_DB_URL`.

## Type checking

`mypy .` is strict everywhere except `components/` and `pages/`, where several
error codes are disabled in `pyproject.toml` because mypy cannot see through
Reflex's Var system. Do not add `# type: ignore` comments there, and do not
rewrite Var expressions to satisfy a type checker that cannot read them.
