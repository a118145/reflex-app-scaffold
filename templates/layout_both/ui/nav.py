"""Top bar — the section switcher.

Sits to the right of the sidebar (``left=16em``), matching the toolbox
geometry. Each entry links to its section's first sub-page.
"""

import reflex as rx

from ..navigation.nav_config import NAV_ITEMS, NavItem
from ..navigation.state import NavState
from .side import SIDEBAR_WIDTH

NAVBAR_HEIGHT = "4em"

# Where the section links sit in the bar: "left" (packed against the sidebar)
# or "center". A plain Python constant, so the branch below is resolved at
# compile time — flip the word and restart, no regeneration needed.
NAV_ALIGNMENT: str = "{{nav_alignment}}"


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
    links = rx.hstack(
        *[navbar_item(item, i) for i, item in enumerate(NAV_ITEMS)],
        spacing="3",
        align="center",
    )

    if NAV_ALIGNMENT == "center":
        # The colour-mode button is taken out of the flex row and pinned to the
        # right edge. Left in the row it would occupy real width, pushing the
        # links off-centre by half the button — visibly wrong on a wide screen.
        # It anchors against the fixed-position box below.
        content: rx.Component = rx.fragment(
            rx.center(links, width="100%"),
            rx.color_mode.button(
                position="absolute",
                right="1em",
                top="50%",
                transform="translateY(-50%)",
            ),
        )
    else:
        content = rx.hstack(
            links,
            rx.spacer(),
            rx.color_mode.button(),
            align="center",
            width="100%",
        )

    return rx.box(
        content,
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
