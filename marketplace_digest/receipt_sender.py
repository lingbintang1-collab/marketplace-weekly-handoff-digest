"""Build the marketplace email body and send it through configured SMTP."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from .models import DigestRequest, DigestResult, DigestSection


def build_digest(request: DigestRequest) -> DigestResult:
    sections: list[DigestSection] = []
    for seller in request.sellers:
        lines = [
            f"Asset: {asset.title} ({asset.state}) - {asset.storefront_url}"
            for asset in seller.assets
        ]
        lines.extend(
            f"Buyer: {update.buyer_name} - {update.note}"
            for update in seller.buyer_updates
        )
        lines.extend(
            f"Handoff: {order.order_number} to {order.destination}"
            for order in seller.orders
            if order.ready_for_handoff
        )
        if lines:
            sections.append(DigestSection(seller_name=seller.seller_name, lines=lines))

    return DigestResult(
        audience_email=request.audience_email,
        subject=f"Marketplace handoff digest - week of {request.week_of.isoformat()}",
        sections=sections,
        included_sellers=len(sections),
    )


def send_digest(result: DigestResult) -> None:
    message = EmailMessage()
    message["From"] = os.environ["DIGEST_FROM_EMAIL"]
    message["To"] = str(result.audience_email)
    message["Subject"] = result.subject
    message.set_content(
        "\n\n".join(
            f"{section.seller_name}\n" + "\n".join(f"- {line}" for line in section.lines)
            for section in result.sections
        )
    )
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)
