from typing import NamedTuple

from .enums import PeriodType, Store, OwnershipType


class Entitlement(NamedTuple):
    expires_date: str
    purchase_date: str
    product_identifier: str


class Subscription(NamedTuple):
    expires_date: str
    purchase_date: str
    original_purchase_date: str
    ownership_type: OwnershipType
    period_type: PeriodType
    store: Store
    is_sandbox: bool
    unsubscribe_detected_at: str
    billing_issues_detected_at: str


class NonSubscription(NamedTuple):
    id: str
    purchase_date: str
    store: Store
    is_sandbox: bool


class Subscriber(NamedTuple):
    original_app_user_id: str
    original_application_version: str | None
    first_seen: str
    last_seen: str
    entitlements: dict  # #
    subscriptions: dict  # #
    non_subscriptions: dict  # #
    subscriber_attributes: dict  # #
