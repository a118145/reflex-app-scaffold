"""Item table with an empty state.

Kept item-specific on purpose: a fully generic table over arbitrary models
needs column descriptors and per-cell renderers, which is more machinery than
a boilerplate should impose. Copy this file and change the columns.
"""

import reflex as rx

from ..models import Item
from ..navigation import routes
from ..states.items_state import ItemsState


def _row(item: Item) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(
            rx.link(item.name, href=f"{routes.DATA_ROUTE}/" + item.id.to_string()),
        ),
        rx.table.cell(item.quantity.to_string()),
        rx.table.cell(item.price.to_string()),
        rx.table.cell(
            rx.cond(item.note, item.note, rx.text("—", color_scheme="gray")),
        ),
        rx.table.cell(
            # Row actions. `variant="ghost"` draws no border, so the only
            # visible bounds are the hover backgrounds — at the default gap
            # those two squares touch and read as a single control. A
            # destructive action sitting next to an edit needs clearly
            # separated hit targets, hence the explicit gap.
            #
            # Do NOT add `size=` to these buttons: `IconButton.create`
            # overwrites its child icon's size from a fixed table
            # ({"1": 12, "2": 24, "3": 36, "4": 48}), so the `size=18` below
            # would be silently discarded and the icons would jump to 12 or
            # 24px. Size the icon, not the button.
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=18),
                    variant="ghost",
                    title="Edit",
                    on_click=ItemsState.open_edit(item.id),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=18),
                    variant="ghost",
                    color_scheme="red",
                    title="Delete",
                    on_click=ItemsState.ask_delete(item.id),
                ),
                spacing="3",
                justify="end",
            ),
            text_align="right",
        ),
        align="center",
    )


def _empty_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("package-open", size=32, color=rx.color("gray", 8)),
            rx.text("No items yet.", weight="medium"),
            rx.text(
                "Create the first one to see the full CRUD loop.",
                size="2",
                color_scheme="gray",
            ),
            rx.button(
                rx.icon("plus", size=16),
                "New item",
                on_click=ItemsState.open_create,
                margin_top="0.5em",
            ),
            spacing="2",
            align="center",
        ),
        padding_y="3em",
    )


def items_table() -> rx.Component:
    return rx.cond(
        ItemsState.has_items,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Quantity"),
                    rx.table.column_header_cell("Price"),
                    rx.table.column_header_cell("Note"),
                    rx.table.column_header_cell("", text_align="right"),
                ),
            ),
            rx.table.body(rx.foreach(ItemsState.items, _row)),
            variant="surface",
            width="100%",
        ),
        _empty_state(),
    )
