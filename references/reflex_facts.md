# Reflex 0.11.0 — verified API facts

Read from the installed package source and checked in generated apps (all
six layout × database combinations: compile, tests, `reflex run`; a browser
walk through the CRUD loop; the same apps with reflex-auth-boilerplate
applied), not from documentation. Much of the Reflex
material online (and in older project notes) predates these. Do not "fix"
generated code to match older docs.

The scaffold pins `reflex==0.11.0`. Re-verify before moving to another
release — check `.venv/lib/python3.*/site-packages/reflex-*.dist-info/METADATA`.
The companion skill `reflex-auth-boilerplate` pins the same release; its
`references/reflex_auth_facts.md` covers the event, router and HTTP internals
the auth code depends on.

## What changed since 0.9.8 (the previous verified release)

| Change | Consequence for generated apps |
|---|---|
| `reflex[db]` depends on `greenlet` (since 0.10). | `uv add "reflex[db]==0.11.0"` is enough; no separate `greenlet`. |
| A plain `reflex` install no longer brings `pydantic` (0.11: only the `db` and `pydantic` extras do). | `pydantic` is a direct dependency of every generated app (`utils/casting.py`, `utils/validation.py`); without it a database-less app fails with `ModuleNotFoundError`. |
| `reflex.page.DECORATED_PAGES` is deprecated (since 0.9.9). | `tests/test_routes.py` reads `RegistrationContext.ensure_context().decorated_pages` (`reflex_base.registry`). |
| Reflex logs through stdlib `logging` (logger `reflex`). Under the CLI it attaches its own handler and sets `propagate=False`; outside the CLI (pytest, scripts) records propagate to the root logger. | The app's `logging.basicConfig` does not double Reflex's output. A deprecation hit only in tests is a log record, not a failure — the gate catches compile-time deprecations (`check.sh --full`). |
| `deploy_url` defaults to `None` (was `http://localhost:3000`); `config.frontend_url` is `deploy_url` or `http://localhost:<frontend_port>`. | Do not hard-code either in `rxconfig.py`. Production sets `REFLEX_DEPLOY_URL` and `REFLEX_API_URL`. |
| CORS / socket origin: `*` in dev; in prod the backend's own origin plus `deploy_url`'s, unless `cors_allowed_origins` is set. | Nothing to do for a no-auth app; the auth skill sets it explicitly. |
| `rx.event(fn)` returns a frozen `EventHandler`. Decorators *above* `@rx.event`, `@rx.event` on a static/class method or on a function without a state parameter are deprecated (0.11). | Put other decorators **below** `@rx.event`. Attributes go on the function (`handler.fn`), never on the handler. |
| A handler can be awaited: `await OtherState.handler(...)` runs it inline on the locked state tree. A non-event return value is a *result* for the awaiting caller; triggered from the browser it is dropped with a dev warning. | Handlers return `None`, an event or a list of events. Use `await self.get_state(X)` to read another state. |
| `state_auto_setters` still defaults to `False`; setting it explicitly is deprecated (0.11). | Leave it out of `rx.Config`. |
| Router headers sent to the browser omit `cookie` (since 0.10); `State.router.headers.cookie` on the frontend is an empty string (deprecated). | Still: never put a secret in a header the browser sends. See "Router data" below. |
| `rx.input(auto_complete=...)` takes the HTML string (`"email"`), not a bool (since 0.10). | — |
| Submitting a form control by its `id` (no `name`) is deprecated. | Every input in a form carries `name=`. |
| `reflex db init` writes its own `alembic/env.py`; an `env.py` from an older release "cannot load the app". | Only for apps upgraded in place: run `reflex db init` once, existing revisions are kept. |
| Bun ≥ 1.4.4 is required (1.4 writes `bun.lock` v2, which 1.3 cannot read); the npm fallback needs Node ≥ 22.22.0. | Older bun on PATH → Reflex installs its own (network). |
| `rx.App(admin_dash=...)` is removed. | Not used. |

## Package layout

0.9+ is split into namespace distributions. `reflex/` is largely a re-export
shell. Real definitions live in `reflex_base/` (config, events, vars,
registry, logging), `reflex_components_radix/`, `reflex_components_core/`,
`reflex_components_sonner/` (toast), `reflex_components_lucide/` (icons).
Read `reflex_base/` when checking an API.

`reflex.base` does not exist as an importable module.

## Removed / renamed

| Gone | Use instead |
|---|---|
| `rx.Base` | dataclasses, `TypedDict`, `rx.PropsBase` (props only), `rx.serializer` |
| `rx.cached_var` | `@rx.var` — caching is the default (`cache=True`); opt out with `@rx.var(cache=False)` |
| `State.set_x` auto-setters | Write `@rx.event def set_x(self, v)`, or call `State.setvar("x", v)` |
| `rx.App(admin_dash=...)` | — |

## Deprecated (still work, will warn; removal 1.0)

| Deprecated | Replacement |
|---|---|
| `rx.App(theme=...)` | `rx.plugins.RadixThemesPlugin(theme=rx.theme(...))` in `rxconfig.py` |
| `rx.Model` | `sqlmodel.SQLModel` + `reflex.model.ModelRegistry.register` |
| `router.page.*` | `router.url.path`, `router.url.query_parameters`, `router.route_id` |
| `reflex.page.DECORATED_PAGES` | `reflex_base.registry.RegistrationContext.ensure_context().decorated_pages` |
| `ArrayVar.foreach` | `ArrayVar.map` (the `rx.foreach` component is fine) |
| `get_config(reload=True)` | `reload_config()` |
| `ComputedVar` `deps=["router"]` | `deps=[State.router]` or one field, e.g. `deps=[State.router.url]` |
| Decorators above `@rx.event`; `@rx.event` on static/class methods or plain functions | Other decorators below `@rx.event`; no decorator where there is no state |
| `reflex.model.alembic_autogenerate` / `get_migration_history` / `format_revision` | `reflex db makemigrations`, `reflex db status` |

Rendering any Radix component without declaring `RadixThemesPlugin` emits an
"implicit Radix Themes enablement" deprecation. Always declare it.

## Database

`reflex[db]` extras are **not** installed by a plain `reflex` install —
`sqlmodel`, `sqlalchemy` and `alembic` are all absent. Run
`uv add "reflex[db]==0.11.0"`; it brings `greenlet` (needed by
`sqlalchemy.ext.asyncio`, which `reflex.model` imports) and `aiosqlite`.

**Datetimes must be timezone-aware.** sqlmodel ≥ 0.0.48 maps `datetime`
fields to `UTCDateTime`: binding a naive value raises `ValueError: Datetime
values must have timezone information` at insert time, and values come back
UTC-aware. Use `datetime.now(UTC)`; attach a zone to parsed form input
before persisting it.

```python
from reflex.model import ModelRegistry
from sqlmodel import Field, SQLModel

@ModelRegistry.register          # decorator or direct call
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
```

Sessions: `rx.session(url=None)` → `sqlmodel.Session`; `rx.asession()` →
`AsyncSession`. The `url` argument is what makes tests against a throwaway
database possible.

CLI: `reflex db init` (needs `config.db_url`; creates `alembic.ini`,
`alembic/` and an initial revision from the registered models, and applies
it), `db makemigrations` (needs the database at head: on a fresh checkout run
`db migrate` first), `db migrate`, `db status`.

**Known benign warning**: `SAWarning: Table '<name>' already exists within the
given MetaData - not copying`. Reflex pre-registers its own deprecated
`rx.Model`, which shares `SQLModel.metadata` with user models, so the registry
merges the same metadata twice. Migrations are generated correctly.

When creating tables against a non-Reflex database, always filter:
`SQLModel.metadata.create_all(engine, tables=[...])` — never bare
`create_all(engine)`, which would create every registered model there.

Autogenerate runs alembic with `compare_type=False` and
`render_as_batch=True`. Batch mode makes SQLite `ALTER`s work; but **column
type changes are not detected** — the revision comes out empty for them.
Write that migration by hand (`op.alter_column(..., type_=...)` inside
`op.batch_alter_table`). Adding a foreign key to an existing table renders
`create_foreign_key(None, …)`, which fails on SQLite: name the constraint by
hand.

## Network and telemetry

| What | Default | Off |
|---|---|---|
| Usage telemetry to PostHog (`app.posthog.com`) on init/run/compile | on | `telemetry_enabled=False` in `rx.Config`, or `REFLEX_TELEMETRY_ENABLED=false` |
| "Newer version available" check against PyPI | on | `REFLEX_CHECK_LATEST_VERSION=false` |
| `reflex init` downloads AGENTS.md (`raw.githubusercontent.com/reflex-dev/agent-skills/…`) and writes a marker-wrapped section into `AGENTS.md`, plus a `CLAUDE.md` bridge | on | `reflex init --no-agents` (only `init` does this; `run`/`compile` never touch the files) |
| No bun ≥ 1.4.4 in `~/.reflex` or on PATH → install script from `raw.githubusercontent.com` is downloaded and run | — | bun ≥ 1.4.4 on PATH, or `REFLEX_USE_NPM=1` with Node ≥ 22.22.0 |

Any `rx.Config` field can be overridden with `REFLEX_<FIELD>` (e.g.
`REFLEX_DB_URL`, `REFLEX_FRONTEND_PORT`, `REFLEX_DEPLOY_URL`).

`reflex init --name <app_name>` sets the package name; without it the name is
derived from the directory.

`reflex compile` (also `--dry`) re-initialises when `.web/` is missing or was
built by another Reflex version — that includes the frontend package install.
In a fresh checkout or git worktree the first compile is therefore slow and
needs the npm registry.

## Logging

Reflex's own output goes through `logging.getLogger("reflex")` (packages
`reflex_base`, `reflex_components_*` … are re-parented under it). Under the
CLI (`reflex run/compile`, and the backend workers it spawns) Reflex attaches
its console handler and stops propagation, so an app-side
`logging.basicConfig` neither doubles nor swallows Reflex's lines.
Deprecations are `WARNING` records on `reflex.deprecation` — that is what
`check.sh --full` greps for in the compile output. Outside the CLI (pytest)
they reach the root logger and pass silently.

## State

- MRO: `rx.State → reflex.state.BaseState → EvenMoreBasicBaseState`.
  `rx.BaseState` cannot be subclassed directly.
- Mutable defaults (`items: list[Item] = []`) are **safe**: Reflex copies
  field defaults per instance (verified — two instances get separate lists).
  Ruff's RUF012 is a false positive here; `rx.field(default_factory=...)` also
  works but returns `Field[T] | T`, which mypy will not narrow.
- `@rx.event(background=True)` requires an `async def`; use `async with self:`
  to mutate state inside it.
- Cross-state access: `await self.get_state(OtherState)`. Calling another
  state's handler: `await OtherState.handler(...)` (0.11).
- Private (`_underscore`) vars are never serialised to the client.
- `State(**{"_reflex_internal_init": True})` builds a root state in tests;
  a substate needs `parent_state=root`.

## Routing

- `@rx.page(...)` has `script_tags=` but no `context=`; `app.add_page(...)` is
  the reverse. Decorated pages register only when their module is imported;
  they are recorded on `RegistrationContext.ensure_context().decorated_pages`
  as `(render_fn, kwargs)`.
- 404: register a page at route `"/404"`. There is no `add_custom_404_page`.
- Dynamic args: `@rx.page(route="/data/[item_id]")` injects `item_id` (a
  `str`) into **every** state class. Declaring it as a field raises
  `DynamicRouteArgShadowsStateVarError` — use a `TYPE_CHECKING` annotation if
  a type checker needs to know it exists.
- The first load of a page (and every socket reconnect) sends
  `State.hydrate_and_load`, which queues `on_load_internal` only if the page
  has `on_load` handlers; a client-side navigation always sends
  `on_load_internal`. Anything that must run on *every* page open cannot hang
  off `on_load` alone.

## Components

- `rx.App` already defaults `toaster` to `rx.toast.provider()`. **Do not mount
  a second toaster** — it produces duplicate toasts.
- Toast API: `rx.toast(msg)`, `rx.toast.success/error/warning/info/loading`,
  `rx.toast.dismiss(id)`. Props include `position`, `duration`,
  `close_button`, `action`.
- Available namespaces: `dialog`, `alert_dialog`, `drawer`, `popover`,
  `hover_card`, `menu`/`dropdown_menu`, `context_menu`, `tabs`, `table`,
  `select`, `accordion`, `data_list`, `callout`, `form`, `color_mode`.
- Dict Vars support `.get(key, default)`, `.contains(key)`, `.keys()`.
  Non-string Vars need `.to_string()` before use as text.
- **`rx.icon_button(size=...)` overwrites its child icon's size.**
  `IconButton.create` maps the Radix button size onto the Lucide icon through
  a fixed table — `{"1": 12, "2": 24, "3": 36, "4": 48}` — so
  `rx.icon_button(rx.icon("pencil", size=18), size="2")` renders an icon at
  **24**, not 18, with no warning. Size the icon and omit the button's `size`
  when you want a value between the steps. `IconButton.add_style` also adds a
  fixed `padding: 6px`, which is part of the hover box.
- `list[SQLModelClass]` works as a state var; attribute access compiles to a
  dict lookup on the frontend. `Decimal` serialises to a JSON float and
  `datetime` to a string.

## Verifying styling

`Component.render()` does **not** run `add_style`, so inspecting it will show
a component as unstyled even when the style is applied correctly. `rx.center`
is the trap case: `rx.center(x).render()["props"]` is `[]`, which looks like a
no-op wrapper, while the compiled output carries
`display/alignItems/justifyContent: center` from `Center.add_style`.

Check styling against the compiled frontend, not against `.render()`. A
page's own markup is in `.web/app/routes/` (`_index.jsx` for `/`,
`[about]._index.jsx`, `[data].$[item_id]._index.jsx`, …); components that
read state are memoised into `.web/app_components/<app_name>/pages/<page>.jsx`.

```bash
grep -o 'justifyContent[^,]\{0,30\}' '.web/app/routes/[404]._index.jsx'
```

Those files are minified onto very long lines — use Python or `grep -o` with a
bounded pattern. An unanchored `grep -E` with `[^)]{0,120}`-style quantifiers
will backtrack catastrophically and hang.

## Lockfiles

`reflex.lock/` (created on the first compile) holds `bun.lock` and
`package.json`: the frozen lockfile Reflex installs the frontend packages
from. **Commit it, never gitignore it.** It is to the frontend what `uv.lock`
is to Python. Without it every fresh checkout and every CI or Docker build
resolves new JS package versions; a mismatch fails with "lockfile had
changes, but lockfile is frozen". A `bun.lock` written by bun 1.4 cannot be
read by bun 1.3.

## Type checking

mypy cannot see through the Var system: at class level `State.items` is a
`Var` while annotated `list[Item]`, so every `.to_string()`, `.contains()` and
`Handler(arg)` call reads as an error. Disable `attr-defined`, `union-attr`,
`arg-type`, `operator` and `untyped-decorator` for the `components` and
`pages` modules only — never globally, and never with scattered
`# type: ignore` comments.

For SQLModel `order_by`, use `sqlmodel.col(Model.field)` — the bare attribute
is typed as its Python type, not a column.

## Router data

`State.router` is a descriptor over per-field state vars; its headers are
serialised to the browser. Since 0.10 `cookie` is omitted there, and
`raw_headers` drops `cookie`, `authorization`, `proxy-authorization` and
common proxy token headers. On the backend `self.router.headers.cookie`
still holds the full cookie string, and every other handshake header still
reaches the browser — never put a secret in one. (The reflex-auth-boilerplate
skill strips its session cookie from the router data in an event middleware.)

`router.session.client_ip` ignores `X-Forwarded-For` unless
`rx.Config(trusted_proxy_hops=N)` is set (default 0).

## Forms

- `rx.form` **and** `rx.el.form` always attach an `onSubmit` that calls
  `preventDefault`: neither can do a native POST to a URL. A bare
  `rx.Component` with `tag = "form"` and `_is_tag_in_global_scope = True`
  can. Without that flag the tag compiles to a JS identifier — dev mode
  tolerates it, the production build fails with
  `ReferenceError: form is not defined`.
- Form data contains controls with a `name`; submitting one by `id` only is
  deprecated.
- `rx.input(auto_complete="email")` — the HTML string.

## Production build

`reflex run --env prod` serves the static frontend, which redirects `/data`
to `/data/` (307). Compare paths without a trailing slash.
`--single-port` requires `--env prod`; set `REFLEX_DEPLOY_URL` and
`REFLEX_API_URL` to the same public URL. Without `uvicorn`/`gunicorn`
installed the backend runs on Granian, which writes no access log.
