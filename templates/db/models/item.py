"""Table model.

``rx.Model`` is deprecated (removal in Reflex 1.0) — subclass ``SQLModel``
directly and register the class so ``reflex db makemigrations`` can see it.

``ModelRegistry.register`` works as a decorator or a plain call.
"""

from datetime import datetime
from decimal import Decimal

from reflex.model import ModelRegistry
from sqlmodel import Field, SQLModel


@ModelRegistry.register
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    quantity: int = Field(default=0)
    price: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    note: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
