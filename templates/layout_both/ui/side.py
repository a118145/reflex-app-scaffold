"""Sidebar — the submenu.

Shows the ``sub_items`` of whichever section is active in the top bar. The
section list is a Python loop (compile time) and the visibility test is an
``rx.cond`` on ``NavState.active_section`` (runtime), because ``NAV_ITEMS`` is
static config while the active index is state.

Links are plain ``href``. No ``on_click`` — highlighting is derived from the
router, see ``navigation/state.py``.
"""

import reflex as rx

from ..navigation.nav_config import NAV_ITEMS
from ..navigation.state import NavState

SIDEBAR_WIDTH = "16em"


def sidebar_item(label: str, icon: str, route: str) -> rx.Component:
    active = NavState.active_route == route
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=17),
            rx.text(label, size="3"),
            width="100%",
            padding_x="0.6rem",
            padding_y="0.55rem",
            align="center",
            spacing="3",
            background=rx.cond(active, rx.color("accent", 5), "transparent"),
            color=rx.cond(active, rx.color("accent", 11), rx.color("gray", 12)),
            border_radius="0.5em",
            style={
                "_hover": {
                    "background": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
            },
        ),
        href=route,
        underline="none",
        weight="medium",
        width="100%",
    )


def sidebar() -> rx.Component:
    sections = [
        rx.cond(
            NavState.active_section == index,
            rx.vstack(
                *[
                    sidebar_item(sub["label"], sub["icon"], sub["route"])
                    for sub in item.get("sub_items", [])
                ],
                spacing="1",
                width="100%",
            ),
            rx.fragment(),
        )
        for index, item in enumerate(NAV_ITEMS)
    ]

    return rx.vstack(
        rx.hstack(
            rx.icon("box", size=22, color=rx.color("accent", 10)),
            rx.heading("{{app_title}}", size="4"),
            align="center",
            spacing="2",
            padding_x="0.6rem",
            padding_bottom="0.5em",
            width="100%",
        ),
        rx.text(
            NavState.active_section_label.upper(),
            size="1",
            weight="bold",
            color_scheme="gray",
            padding_x="0.6rem",
        ),
        *sections,
        spacing="3",
        position="fixed",
        left="0px",
        top="0px",
        padding_x="1em",
        padding_y="1.5em",
        background=rx.color("accent", 3),
        align="start",
        height="100vh",
        width=SIDEBAR_WIDTH,
        z_index="10",
    )
