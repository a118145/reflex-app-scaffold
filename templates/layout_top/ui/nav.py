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

# Where the section links sit in the bar: "left" (next to the wordmark) or
# "center". A plain Python constant, so the branch below is resolved at
# compile time — flip the word and restart, no regeneration needed.
NAV_ALIGNMENT: str = "{{nav_alignment}}"


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


def _wordmark() -> rx.Component:
    return rx.hstack(
        rx.icon("box", size=22, color=rx.color("accent", 10)),
        rx.heading("{{app_title}}", size="4"),
        align="center",
        spacing="2",
    )


def navbar() -> rx.Component:
    links = rx.hstack(
        *[navbar_item(item, i) for i, item in enumerate(NAV_ITEMS)],
        spacing="2",
        align="center",
    )

    if NAV_ALIGNMENT == "center":
        # Wordmark and colour-mode button are pinned to the edges rather than
        # sitting in the flex row: both occupy width, and since they are not
        # equally wide, leaving them in the row would push the links off-centre
        # by the difference. Both anchor against the fixed-position box below.
        # This assumes a desktop viewport — narrow screens hit the resize gate
        # before the wordmark and the links could collide.
        content: rx.Component = rx.fragment(
            rx.box(
                _wordmark(),
                position="absolute",
                left="1.5em",
                top="50%",
                transform="translateY(-50%)",
            ),
            rx.center(links, width="100%"),
            rx.color_mode.button(
                position="absolute",
                right="1.5em",
                top="50%",
                transform="translateY(-50%)",
            ),
        )
    else:
        content = rx.hstack(
            rx.box(_wordmark(), padding_right="1em"),
            links,
            rx.spacer(),
            rx.color_mode.button(),
            align="center",
            width="100%",
        )

    return rx.box(
        content,
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
