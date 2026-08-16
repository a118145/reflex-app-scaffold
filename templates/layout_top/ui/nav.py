"""Top bar — the only navigation surface in this layout.

Renders one entry per ``NAV_ITEMS`` section and ignores ``sub_items``. If a
section grows sub-pages, either switch to the "both" layout or promote the
sub-pages to top-level sections; this bar deliberately stays one level deep.

Links are plain ``href``. No ``on_click`` — highlighting is derived from the
router, see ``navigation/state.py``.
"""

import reflex as rx

from ..navigation.nav_config import NAV_ITEMS, NavItem
from ..navigation.state import NavState

NAVBAR_HEIGHT = "4em"


def navbar_item(item: NavItem, index: int) -> rx.Component:
    active = NavState.active_section == index
    return rx.link(
        rx.hstack(
            rx.icon(item["icon"], size=18),
            rx.text(item["label"], size="3", weight="medium"),
            padding_x="0.75rem",
            padding_y="0.5rem",
            align="center",
            spacing="2",
            background=rx.cond(active, rx.color("accent", 5), "transparent"),
            color=rx.cond(active, rx.color("accent", 11), "inherit"),
            border_radius="0.5em",
            style={
                "_hover": {
                    "background": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
            },
        ),
        href=item["route"],
        underline="none",
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("box", size=22, color=rx.color("accent", 10)),
                rx.heading("{{app_title}}", size="4"),
                align="center",
                spacing="2",
                padding_right="1em",
            ),
            rx.hstack(
                *[navbar_item(item, i) for i, item in enumerate(NAV_ITEMS)],
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.color_mode.button(),
            align="center",
            width="100%",
        ),
        background=rx.color("accent", 3),
        padding_x="1.5em",
        height=NAVBAR_HEIGHT,
        display="flex",
        align_items="center",
        position="fixed",
        top="0px",
        left="0px",
        right="0px",
        z_index="5",
    )
