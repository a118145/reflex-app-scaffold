"""Detail page state — dynamic route args + cross-state access.

Declaring ``@rx.page(route="/data/[item_id]")`` makes Reflex install a
dynamic var named ``item_id`` (always a ``str``) on every state class. It must
NOT be declared as a field here, or Reflex raises
``DynamicRouteArgShadowsStateVarError`` — hence the ``TYPE_CHECKING`` block,
which tells mypy the attribute exists without creating a real field.
"""

from typing import TYPE_CHECKING

import reflex as rx

from ..models import Item
from ..utils.logging import get_logger
from .items_state import ItemsState

log = get_logger(__name__).bind(state="ItemDetailState")


class ItemDetailState(rx.State):
    if TYPE_CHECKING:
        item_id: str  # injected by the dynamic route — never assign it

    item: Item | None = None
    not_found: bool = False
    sibling_count: int = 0

    @rx.var
    def title(self) -> str:
        return self.item.name if self.item is not None else "Item not found"

    @rx.event
    async def load(self):
        """Page ``on_load``.

        Reads the dynamic route arg, then pulls an unrelated number off
        ItemsState — the flat-state way to share, no inheritance involved.
        """
        raw_id = self.item_id
        self.item = None
        self.not_found = False

        try:
            item_id = int(raw_id)
        except (TypeError, ValueError):
            self.not_found = True
            log.info("item_detail.bad_id", raw_id=raw_id)
            return

        with rx.session() as session:
            self.item = session.get(Item, item_id)

        self.not_found = self.item is None

        items_state = await self.get_state(ItemsState)
        self.sibling_count = items_state.item_count

        log.info("item_detail.load", item_id=item_id, found=not self.not_found)
