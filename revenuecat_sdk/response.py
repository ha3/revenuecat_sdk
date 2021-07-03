from typing import Dict, List, NamedTuple, Optional

from .enums import OwnershipType, PeriodType, Store


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


class SubscriberAttribute(NamedTuple):
    value: str
    updated_at_ms: int


class Subscriber(NamedTuple):
    original_app_user_id: str
    original_application_version: Optional[str]
    first_seen: str
    last_seen: str
    management_url: Optional[str]
    original_purchase_date: Optional[str]
    other_purchases: dict
    entitlements: Dict[str, Entitlement]
    subscriptions: Dict[str, Subscription]
    non_subscriptions: Dict[str, NonSubscription]
    subscriber_attributes: Optional[Dict[str, SubscriberAttribute]] = None


class Package(NamedTuple):
    identifier: str
    platform_product_identifier: str


class Offering(NamedTuple):
    description: str
    identifier: str
    packages: List[Package]


class Offerings(NamedTuple):
    current_offering_id: str
    offerings: List[Offering]
