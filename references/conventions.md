# Conventions block for generated apps

Append this to the generated `AGENTS.md`, **outside** the
`<!-- reflex managed ... -->` markers (`reflex init` rewrites the inside).
`CLAUDE.md` created by `reflex init` is just `@AGENTS.md`, so this reaches
Claude Code sessions too. Replace `{{app_name}}` and drop rows for folders the
app does not have.

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

## Type checking

`mypy .` is strict for `utils/`, `models/`, `navigation/` and `tests/`. In
`components/` and `pages/`, several error codes are disabled in
`pyproject.toml` because mypy cannot see through Reflex's Var system. Do not
add `# type: ignore` comments there, and do not rewrite Var expressions to
satisfy a type checker that cannot read them.
