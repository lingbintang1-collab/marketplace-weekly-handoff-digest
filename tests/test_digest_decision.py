from datetime import date

from marketplace_digest.models import DigestRequest, OrderHandoff, SellerWeek
from marketplace_digest.receipt_sender import build_digest


def test_digest_includes_only_sellers_with_visible_weekly_work() -> None:
    request = DigestRequest(
        audience_email="marketplace@example.com",
        week_of=date(2026, 8, 24),
        sellers=[
            SellerWeek(seller_name="Quiet Shop"),
            SellerWeek(
                seller_name="Ready Shop",
                orders=[
                    OrderHandoff(order_number="ORD-7", destination="Carrier desk", ready_for_handoff=True),
                    OrderHandoff(order_number="ORD-8", destination="Packing bench", ready_for_handoff=False),
                ],
            ),
        ],
    )

    result = build_digest(request)

    assert result.included_sellers == 1
    assert result.sections[0].seller_name == "Ready Shop"
    assert result.sections[0].lines == ["Handoff: ORD-7 to Carrier desk"]
