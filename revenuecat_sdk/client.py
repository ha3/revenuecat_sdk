import json
from datetime import datetime
from http.cookiejar import CookiePolicy
from typing import Any, Dict, List, Union

import requests

from .enums import AttributionSource, PaymentMode, Platform, PromotionDuration
from .errors import RevenueCatError, Unavailable
from .response import Offering, Offerings, Package, Subscriber, SubscriberAttribute
from .utils import encode, to_timestamp

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class BlockAll(CookiePolicy):
    def set_ok(self, cookie, request):
        return False


class Client:
    base_api_url = "https://api.revenuecat.com/v1"

    def __init__(self, public_key: str = None, secret_key: str = None):
        if public_key is None and secret_key is None:
            raise Exception("Either public key or secret key must be set")

        self.session = self.create_session()
        self.public_key = public_key
        self.secret_key = secret_key

    def create_session(self):
        session = requests.Session()
        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        session.cookies.policy = BlockAll()

        return session

    def make_request(
        self, method, path, payload=None, platform=None, key=None, timeout=5
    ) -> JSONType:
        url = self.base_api_url + encode(path)
        data = json.dumps(payload) if payload is not None else None
        headers = {}

        if platform is not None:
            headers.update({"X-Platform": platform})

        if key is not None:
            token = self.public_key if key == "public" else self.secret_key

            if token is None:
                raise Exception(f"This functionality requires {key} key to be set")

            headers.update({"Authorization": f"Bearer {token}"})

        try:
            response = self.session.request(
                method=method, url=url, headers=headers, data=data, timeout=timeout
            )
            response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as e:
            raise Unavailable() from e
        except Exception as e:
            raise RevenueCatError() from e

        return response.json()

    @staticmethod
    def generate_subscriber_response(data: JSONType) -> Subscriber:
        return Subscriber(**data)

    @staticmethod
    def generate_offerings_response(data: JSONType) -> Offerings:
        offerings = []

        for o in data["offerings"]:
            packages = []

            for p in data["offerings"]["packages"]:
                packages.append(Package(**p))

            offerings.append(Offering(**o, packages=packages))

        return Offerings(
            current_offering_id=data["current_offering_id"], offerings=offerings
        )

    def get_subscriber_info(self, app_user_id: str) -> Subscriber:
        path = f"/subscribers/{app_user_id}"
        key = "secret" if self.secret_key else "public"

        data = self.make_request("GET", path, key=key)

        return self.generate_subscriber_response(data["subscriber"])

    def is_user_subscribed(self, app_user_id: str) -> bool:
        info = self.get_subscriber_info(app_user_id)
        is_subscribed = False

        if info.subscriptions:
            expires_date = datetime.strptime(
                next(iter(info.subscriptions)).expires_date, "%Y-%m-%dT%H:%M:%SZ"
            )
            if expires_date >= datetime.now():
                is_subscribed = True

        return is_subscribed

    def update_subscriber_attrs(
        self, app_user_id: str, attrs: Dict[str, SubscriberAttribute]
    ) -> None:
        path = f"/subscribers/{app_user_id}/attributes"
        payload = {"attributes": attrs}

        self.make_request("POST", path, payload, key="public")  # check key

        return None

    def delete_subscriber(self, app_user_id: str) -> str:
        path = f"/subscribers/{app_user_id}"

        data = self.make_request("DELETE", path, key="secret")

        return data["app_user_id"]

    def create_purchase(
        self,
        app_user_id: str,
        platform: Platform,
        fetch_token: str,
        product_id: str = None,
        price: float = None,
        currency: str = None,
        payment_mode: PaymentMode = None,
        introductory_price: float = None,
        is_restore: bool = False,
        presented_offering_identifier: str = None,
        attributes: Dict[str, SubscriberAttribute] = None,
    ) -> Subscriber:
        path = "/receipts"
        payload = {
            "app_user_id": app_user_id,
            "fetch_token": fetch_token,
            "product_id": product_id,
            "price": price,
            "currency": currency,
            "payment_mode": payment_mode,
            "introductory_price": introductory_price,
            "is_restore": str(is_restore).lower(),
            "presented_offering_identifier": presented_offering_identifier,
            "attributes": attributes,
        }

        data = self.make_request(
            "POST", path, payload=payload, platform=platform, key="public"
        )

        return self.generate_subscriber_response(data)

    def grant_promotional_entitlement(
        self,
        app_user_id: str,
        entitlement_identifier: str,
        duration: PromotionDuration,
        start_time: datetime,
    ) -> Subscriber:
        path = f"""
        /subscribers/{app_user_id}/entitlements/{entitlement_identifier}/promotional
        """
        start_time_ms = to_timestamp(start_time)
        payload = {"duration": duration, "start_time_ms": start_time_ms}

        data = self.make_request("POST", path, payload=payload, key="secret")

        return self.generate_subscriber_response(data)

    def revoke_promotinal_entitlements(
        self, app_user_id: str, entitlement_identifier: str
    ) -> Subscriber:
        path = f"""
        /subscribers/{app_user_id}/entitlements/{entitlement_identifier}/revoke_promotionals
        """

        data = self.make_request("POST", path, key="secret")

        return self.generate_subscriber_response(data)

    def revoke_google_subscription(
        self, app_user_id: str, product_identifier: str
    ) -> Subscriber:
        path = f"/subscribers/{app_user_id}/subscriptions/{product_identifier}/revoke"

        data = self.make_request("POST", path, key="secret")

        return self.generate_subscriber_response(data)

    def defer_google_subscription(
        self, app_user_id: str, product_identifier: str, expiry_time: datetime
    ) -> Subscriber:
        path = f"/subscribers/{app_user_id}/subscriptions/{product_identifier}/defer"
        expiry_time_ms = to_timestamp(expiry_time)
        payload = {"expiry_time_ms": expiry_time_ms}

        data = self.make_request("POST", path, payload, key="secret")

        return self.generate_subscriber_response(data)

    def refund_google_subscription(
        self, app_user_id: str, product_identifier: str
    ) -> Subscriber:
        # store_transaction_identifier
        path = f"/subscribers/{app_user_id}/subscriptions/{product_identifier}/refund"

        data = self.make_request("POST", path, key="secret")

        return self.generate_subscriber_response(data)

    def add_user_attribution(
        self,
        app_user_id: str,
        network: AttributionSource,
        rc_idfa: str = None,
        rc_gps_adid: str = None,
    ) -> None:
        path = f"subscribers/{app_user_id}/attribution"

        self.make_request("POST", path, key="public")  # check key

        return None

    def get_offerings(self, app_user_id: str, platform: Platform) -> Offerings:
        path = f"subscribers/{app_user_id}/offerings"

        data = self.make_request("GET", path, platform=platform, key="public")

        return self.get_offerings_response(data)

    def override_current_offering(
        self, app_user_id: str, offering_uuid: str
    ) -> Subscriber:
        path = f"/subscribers/{app_user_id}/offerings/{offering_uuid}/override"

        data = self.make_request("POST", path, key="secret")

        return self.generate_subscriber_response(data)

    def delete_current_offering_override(self, app_user_id: str) -> Subscriber:
        path = f"/subscribers/{app_user_id}/offerings/override"

        data = self.make_request("DELETE", path, key="secret")

        return self.generate_subscriber_response(data)
