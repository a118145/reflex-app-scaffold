"""Data > Items — the full CRUD loop.

Table, create/edit dialog, delete confirmation, toasts and persistence, all
wired to the SQLModel table.
"""

import reflex as rx

from ..components.cards import stat_card
from ..components.confirm_dialog import confirm_dialog
from ..components.data_table import items_table
from ..components.item_dialog import item_dialog
from ..navigation import routes
from ..states.items_state import ItemsState
from ..ui.base import base_page


@rx.page(route=routes.DATA_ROUTE, title="Items", on_load=ItemsState.load)
def items() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Items", size="7"),
                    rx.text(
                        rx.cond(
                            ItemsState.has_items,
                            ItemsState.item_count.to_string() + " item(s) stored.",
                            "Nothing stored yet.",
                        ),
                        size="2",
                        color_scheme="gray",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("plus", size=16),
                    "New item",
                    on_click=ItemsState.open_create,
                ),
                width="100%",
                align="center",
            ),
            rx.grid(
                stat_card("Items", ItemsState.item_count.to_string(), "package"),
                stat_card("Total quantity", ItemsState.total_quantity.to_string(), "sigma"),
                columns="2",
                spacing="3",
                width="100%",
            ),
            items_table(),
            item_dialog(),
            confirm_dialog(
                open=ItemsState.confirm_open,
                on_open_change=ItemsState.set_confirm_open,
                on_confirm=ItemsState.confirm_delete,
                title="Delete this item?",
                description="The row is removed from the database immediately.",
            ),
            spacing="4",
            width="100%",
            align="start",
        )
    )
