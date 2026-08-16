"""Items CRUD state.

Flat state: subclasses ``rx.State`` directly. Other states reach it with
``await self.get_state(ItemsState)`` rather than through inheritance.

Note there are no implicit setters — Reflex 0.9.x ships with
``state_auto_setters=False``, so ``ItemsState.set_dialog_open`` only exists
because it is written out below.
"""

from typing import Any

import reflex as rx
from sqlmodel import col, select

from ..components.toast import notify_error, notify_success
from ..models import Item, ItemForm
from ..utils.logging import get_logger
from ..utils.validation import parse_form

log = get_logger(__name__).bind(state="ItemsState")


class ItemsState(rx.State):
    items: list[Item] = []

    dialog_open: bool = False
    confirm_open: bool = False

    editing_id: int | None = None
    pending_delete_id: int | None = None

    form_errors: dict[str, str] = {}

    # Prefill values for the dialog's inputs. Uncontrolled inputs read these
    # as `default_value`; `form_key` is bumped on every open so React remounts
    # the form and actually picks the new defaults up.
    form_key: int = 0
    form_name: str = ""
    form_quantity: str = "0"
    form_price: str = "0.00"
    form_note: str = ""

    @rx.var
    def has_items(self) -> bool:
        return len(self.items) > 0

    @rx.var
    def item_count(self) -> int:
        return len(self.items)

    @rx.var
    def total_quantity(self) -> int:
        """Derived in state, not in the component — components render, they
        do not compute."""
        return sum(item.quantity for item in self.items)

    @rx.var
    def dialog_title(self) -> str:
        return "Edit item" if self.editing_id is not None else "New item"

    @rx.var
    def submit_label(self) -> str:
        return "Save changes" if self.editing_id is not None else "Create"

    @rx.event
    def load(self):
        """Page ``on_load`` — refresh the list from the database."""
        with rx.session() as session:
            self.items = list(session.exec(select(Item).order_by(col(Item.id))).all())
        log.info("items.load", count=len(self.items))

    @rx.event
    def open_create(self):
        self.editing_id = None
        self.form_errors = {}
        self.form_name = ""
        self.form_quantity = "0"
        self.form_price = "0.00"
        self.form_note = ""
        self.form_key += 1
        self.dialog_open = True

    @rx.event
    def open_edit(self, item_id: int):
        with rx.session() as session:
            item = session.get(Item, item_id)
        if item is None:
            log.warning("items.edit.missing", item_id=item_id)
            return notify_error("That item no longer exists.")

        self.editing_id = item_id
        self.form_errors = {}
        self.form_name = item.name
        self.form_quantity = str(item.quantity)
        self.form_price = str(item.price)
        self.form_note = item.note or ""
        self.form_key += 1
        self.dialog_open = True
        return None

    @rx.event
    def set_dialog_open(self, value: bool):
        """Bound to ``rx.dialog.root(on_open_change=...)`` so Escape and
        click-outside also clear the form errors."""
        self.dialog_open = value
        if not value:
            self.form_errors = {}

    @rx.event
    def submit_form(self, form_data: dict[str, Any]):
        """Cast, validate, persist.

        On failure the handler returns early, which leaves ``dialog_open``
        True — the user keeps their input and sees per-field messages.
        """
        parsed, errors = parse_form(form_data, ItemForm)
        if errors or parsed is None:
            self.form_errors = errors
            # Keep what the user typed so the remount does not wipe it.
            self.form_name = str(form_data.get("name", ""))
            self.form_quantity = str(form_data.get("quantity", ""))
            self.form_price = str(form_data.get("price", ""))
            self.form_note = str(form_data.get("note", ""))
            log.info("items.submit.invalid", fields=sorted(errors))
            return None

        self.form_errors = {}
        with rx.session() as session:
            if self.editing_id is None:
                item = Item(**parsed.model_dump())
                session.add(item)
                session.commit()
                session.refresh(item)
                log.info("items.create", item_id=item.id, name=item.name)
                message = f"Created “{item.name}”."
            else:
                existing = session.get(Item, self.editing_id)
                if existing is None:
                    self.dialog_open = False
                    log.warning("items.update.missing", item_id=self.editing_id)
                    return notify_error("That item no longer exists.")
                for field, value in parsed.model_dump().items():
                    setattr(existing, field, value)
                session.add(existing)
                session.commit()
                log.info("items.update", item_id=self.editing_id, name=existing.name)
                message = f"Updated “{existing.name}”."

        self.dialog_open = False
        self.editing_id = None
        return [ItemsState.load, notify_success(message)]

    @rx.event
    def ask_delete(self, item_id: int):
        self.pending_delete_id = item_id
        self.confirm_open = True

    @rx.event
    def set_confirm_open(self, value: bool):
        self.confirm_open = value
        if not value:
            self.pending_delete_id = None

    @rx.event
    def confirm_delete(self):
        item_id = self.pending_delete_id
        self.confirm_open = False
        self.pending_delete_id = None
        if item_id is None:
            return None

        with rx.session() as session:
            item = session.get(Item, item_id)
            if item is None:
                log.warning("items.delete.missing", item_id=item_id)
                return notify_error("That item no longer exists.")
            name = item.name
            session.delete(item)
            session.commit()

        log.info("items.delete", item_id=item_id, name=name)
        return [ItemsState.load, notify_success(f"Deleted “{name}”.")]
