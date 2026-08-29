"""Print the same deterministic digest that the scheduled route delivers."""

from datetime import date

from marketplace_digest.models import BuyerUpdate, DigestRequest, OrderHandoff, SellerAsset, SellerWeek
from marketplace_digest.receipt_sender import build_digest

sample = DigestRequest(
    audience_email="ops@example.com",
    week_of=date(2026, 8, 24),
    sellers=[
        SellerWeek(
            seller_name="North Street Goods",
            assets=[SellerAsset(title="Canvas tote", storefront_url="https://shop.example/items/tote", state="published")],
            buyer_updates=[BuyerUpdate(buyer_name="Mina", note="Gift note confirmed")],
            orders=[OrderHandoff(order_number="ORD-1042", destination="Shanghai carrier desk", ready_for_handoff=True)],
        )
    ],
)

print(build_digest(sample).model_dump_json(indent=2))
