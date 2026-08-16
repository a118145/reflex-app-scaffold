"""Form model — non-table.

**When to add one of these:** only when a model is populated from a form.
A table model alone is usually enough; add a form model when the two shapes
genuinely differ — here the form must not accept ``id`` or ``created_at``
(server-owned), and it carries validation rules that belong to user input
rather than to the stored row.

``cast_form_data`` targets this class, so the constraints below are what the
user actually gets told about.
"""

from decimal import Decimal

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class ItemForm(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    note: str | None = None

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name must not be blank.")
        return stripped
