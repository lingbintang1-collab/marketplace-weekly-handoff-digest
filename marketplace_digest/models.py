"""Typed marketplace inputs and digest output."""

from datetime import date

from pydantic import BaseModel, EmailStr, Field


class SellerAsset(BaseModel):
    title: str
    storefront_url: str
    state: str


class BuyerUpdate(BaseModel):
    buyer_name: str
    note: str


class OrderHandoff(BaseModel):
    order_number: str
    destination: str
    ready_for_handoff: bool


class SellerWeek(BaseModel):
    seller_name: str
    assets: list[SellerAsset] = Field(default_factory=list)
    buyer_updates: list[BuyerUpdate] = Field(default_factory=list)
    orders: list[OrderHandoff] = Field(default_factory=list)


class DigestRequest(BaseModel):
    audience_email: EmailStr
    week_of: date
    sellers: list[SellerWeek]


class DigestSection(BaseModel):
    seller_name: str
    lines: list[str]


class DigestResult(BaseModel):
    audience_email: EmailStr
    subject: str
    sections: list[DigestSection]
    included_sellers: int


class ScheduleRequest(BaseModel):
    public_base_url: str
    cron_expr: str = "0 9 * * 1"


class ScheduleResult(BaseModel):
    job_id: str
