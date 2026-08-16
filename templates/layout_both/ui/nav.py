"""Top bar — the section switcher.

Sits to the right of the sidebar (``left=16em``), matching the toolbox
geometry. Each entry links to its section's first sub-page.
"""

import reflex as rx

from ..navigation.nav_config import NAV_ITEMS, NavItem
from ..navigation.state import NavState
from .side import SIDEBAR_WIDTH

NAVBAR_HEIGHT = "4em"


def _section_target(item: NavItem) -> str:
    """Where a section link goes: its first sub-page, else the section route."""
    sub_items = item.get("sub_items", [])
    return sub_items[0]["route"] if sub_items else item["route"]


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
        href=_section_target(item),
        underline="none",
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                *[navbar_item(item, i) for i, item in enumerate(NAV_ITEMS)],
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.color_mode.button(),
            align="center",
            width="100%",
        ),
        background=rx.color("accent", 3),
        padding_x="1em",
        height=NAVBAR_HEIGHT,
        display="flex",
        align_items="center",
        position="fixed",
        top="0px",
        left=SIDEBAR_WIDTH,
        right="0px",
        z_index="5",
    )
