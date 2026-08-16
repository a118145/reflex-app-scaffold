"""Page template.

All navigation chrome lives in ``_page_shell``. ``base_page`` is a thin
wrapper that only decides how the content is arranged, so any future variant
(wide, two-column) stays a one-function change and cannot drift from the nav.

Only ``base_page`` is scaffolded. Add variants when a page actually needs a
different arrangement — not speculatively.
"""

import reflex as rx

from .nav import NAVBAR_HEIGHT, navbar
from .resize_gate import browser_resize_page
from .side import SIDEBAR_WIDTH, sidebar


def _page_shell(content: rx.Component) -> rx.Component:
    return rx.fragment(
        rx.desktop_only(
            sidebar(),
            navbar(),
            rx.box(
                content,
                margin_left=SIDEBAR_WIDTH,
                padding_top=NAVBAR_HEIGHT,
                padding_x="1.5em",
                padding_bottom="2em",
                height="100vh",
                overflow_y="auto",
            ),
        ),
        # Resize gate rather than a responsive reflow: the layout assumes a
        # fixed 16em sidebar, which would eat most of a phone viewport.
        rx.mobile_and_tablet(browser_resize_page()),
    )


def base_page(child: rx.Component) -> rx.Component:
    return _page_shell(rx.container(child, size="4", padding_top="1.5em"))
