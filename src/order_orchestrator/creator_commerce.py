from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass(frozen=True)
class CreatorAttribution:
    order_id: str
    creator_id: Optional[str]
    storefront_id: Optional[str]
    source: str

    @property
    def attributed(self) -> bool:
        return bool(self.creator_id and self.storefront_id)


@dataclass(frozen=True)
class CommissionPolicy:
    rate: Decimal

    def commission(self, eligible_subtotal: Decimal) -> Decimal:
        if eligible_subtotal < 0:
            raise ValueError("eligible_subtotal must be non-negative")
        if not Decimal("0") <= self.rate <= Decimal("1"):
            raise ValueError("commission rate must be between 0 and 1")
        return (eligible_subtotal * self.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
