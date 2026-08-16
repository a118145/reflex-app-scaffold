"""Item detail — dynamic route.

The route pattern ``/data/[item_id]`` makes Reflex inject ``item_id`` into
every state. Note this page has no nav entry: the menu still highlights its
parent because ``NavState.active_route`` resolves ``/data/5`` to ``/data`` by
longest-prefix match.
"""

import reflex as rx

from ..navigation import routes
from ..navigation.nav_config import label_for_route
from ..states.item_detail_state import ItemDetailState
from ..ui.base import base_page

# Read from the nav config rather than written out, so the back link names
# whatever the menu actually calls this section. A plain Python constant, so
# it is resolved at compile time.
_PARENT_LABEL = label_for_route(routes.DATA_ROUTE)


def _row(label: str, value: rx.Var | str) -> rx.Component:
    return rx.data_list.item(
        rx.data_list.label(label),
        rx.data_list.value(value),
    )


def _found() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading(ItemDetailState.title, size="7"),
            rx.badge(
                "1 of " + ItemDetailState.sibling_count.to_string(),
                color_scheme="gray",
            ),
            align="center",
            spacing="3",
        ),
        rx.card(
            rx.data_list.root(
                _row("ID", ItemDetailState.item.id.to_string()),
                _row("Name", ItemDetailState.item.name),
                _row("Quantity", ItemDetailState.item.quantity.to_string()),
                _row("Price", ItemDetailState.item.price.to_string()),
                _row(
                    "Note",
                    rx.cond(ItemDetailState.item.note, ItemDetailState.item.note, "—"),
                ),
                _row("Created", ItemDetailState.item.created_at.to_string()),
            ),
            width="100%",
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def _missing() -> rx.Component:
    return rx.callout(
        "No item with that id.",
        icon="search-x",
        color_scheme="red",
    )


@rx.page(route=routes.ITEM_DETAIL_ROUTE, title="Item", on_load=ItemDetailState.load)
def item_detail() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.link(
                rx.hstack(
                    rx.icon("arrow-left", size=15),
                    rx.text(f"Back to {_PARENT_LABEL}", size="2"),
                    align="center",
                    spacing="1",
                ),
                href=routes.DATA_ROUTE,
                underline="none",
                color_scheme="gray",
            ),
            rx.cond(ItemDetailState.not_found, _missing(), _found()),
            spacing="4",
            align="start",
            width="100%",
        )
    )
