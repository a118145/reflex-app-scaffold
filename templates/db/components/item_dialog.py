"""Create/edit dialog for Item.

One dialog serves both operations — ``ItemsState.editing_id`` decides which.
That keeps the field list, the casting and the validation display in a single
place instead of two nearly-identical forms drifting apart.

The form is *uncontrolled*: inputs carry ``default_value`` and the values
arrive as a dict in ``on_submit``, which is what ``cast_form_data`` is built
for. ``key=`` forces a remount whenever the dialog reopens so those defaults
are actually re-read.
"""

import reflex as rx

from ..states.items_state import ItemsState


def _field(
    label: str,
    name: str,
    # A state var is a Var at runtime but is annotated as its Python type, so
    # both spellings have to be accepted here.
    default_value: str | rx.Var[str],
    *,
    placeholder: str = "",
    input_type: str = "text",
    step: str | None = None,
) -> rx.Component:
    """One labelled input plus its error slot."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.input(
            name=name,
            default_value=default_value,
            placeholder=placeholder,
            type=input_type,
            step=step,
            width="100%",
        ),
        rx.cond(
            ItemsState.form_errors.contains(name),
            rx.text(
                ItemsState.form_errors[name],
                size="1",
                color=rx.color("red", 11),
            ),
        ),
        spacing="1",
        width="100%",
        align="start",
    )


def item_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(ItemsState.dialog_title),
            rx.dialog.description(
                "Values are submitted as strings and cast to the model's types before validation.",
                size="2",
                color_scheme="gray",
                margin_bottom="1em",
            ),
            rx.form(
                rx.vstack(
                    _field("Name", "name", ItemsState.form_name, placeholder="Widget"),
                    _field(
                        "Quantity",
                        "quantity",
                        ItemsState.form_quantity,
                        input_type="number",
                    ),
                    _field(
                        "Price",
                        "price",
                        ItemsState.form_price,
                        input_type="number",
                        step="0.01",
                    ),
                    _field(
                        "Note",
                        "note",
                        ItemsState.form_note,
                        placeholder="Optional",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                type="button",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        # Deliberately NOT wrapped in rx.dialog.close — the
                        # dialog must stay open when validation fails.
                        rx.button(ItemsState.submit_label, type="submit"),
                        spacing="3",
                        justify="end",
                        width="100%",
                        margin_top="0.5em",
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=ItemsState.submit_form,
                reset_on_submit=False,
            ),
            max_width="30em",
            # Remount on every open so default_value picks up the new prefill.
            key=ItemsState.form_key.to_string(),
        ),
        open=ItemsState.dialog_open,
        on_open_change=ItemsState.set_dialog_open,
    )
