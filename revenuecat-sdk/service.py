import json
from datetime import datetime
from http.cookiejar import CookiePolicy
from typing import Any, Dict, List, Union

import requests

from .enums import AttributionSource, Platform, PaymentMode, PromotionDuration
from .utils import encode, datetime_to_ms
from .errors import RevenutCatError, Unavailable


JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class BlockAll(CookiePolicy):
    def set_ok(self, cookie, request):
        return False


class ProductService:
    base_api_url = "https://api.revenuecat.com/v1"

    def __init__(self, public_key, secret_key):
        self.session = self.create_session()
        self.public_key = public_key
        self.secret_key = secret_key

    def create_session(self):
        session = requests.Session()
        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.public_key}",
            }
        )
        session.cookies.policy = BlockAll()

        return session

    def make_request(
        self, method, path, payload=None, platform=None, timeout=5
    ) -> JSONType:
        url = self.base_api_url + path
        data = json.dumps(payload) if payload is not None else None
        headers = None

        if platform is not None:
            headers = {"X-Platform": platform}

        try:
            response = self.session.request(
                method=method, url=url, headers=headers, data=data, timeout=timeout
            )
            response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as e:
            raise Unavailable() from e
        except Exception as e:
            raise RevenutCatError() from e

        return response.json()

    def get_subscriber_info(self, app_user_id: str):
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}"

        response = self.make_request("GET", path)

        return response

    def is_user_subscribed(self, app_user_id: str) -> bool:
        info = self.get_subscriber_info(app_user_id)
        subscriptions = info["subscriber"]["subscriptions"]
        is_subscribed = False

        if subscriptions != {}:
            expires_date = datetime.fromtimestamp(
                subscriptions["expires_date"] / 1000.0
            )
            if expires_date >= datetime.now():
                is_subscribed = True

        return is_subscribed

    def update_subscriber_attrs(self, app_user_id: str, attrs: dict):
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/attributes"
        payload = {"attributes": attrs}

        response = self.make_request("POST", path, payload)

        return response

    def delete_subscriber(self, app_user_id: str):
        # secret
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}"

        response = self.make_request("DELETE", path)

        return response

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
        attributes: dict = None,
    ):
        # public needed
        encoded_uid = encode(app_user_id)
        path = "/receipts"

        payload = {
            "app_user_id": encoded_uid,
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

        response = self.make_request("POST", path, payload=payload, platform=platform)

        return response

    def grant_promotional_entitlement(
        self,
        app_user_id: str,
        entitlement_identifier: str,
        duration: PromotionDuration,
        start_time: datetime,
    ):
        # secret
        encoded_uid = encode(app_user_id)
        path = f"""
        /subscribers/{encoded_uid}/entitlements/{entitlement_identifier}/promotional
        """
        start_time_ms = datetime_to_ms(start_time)
        payload = {"duration": duration, "start_time_ms": start_time_ms}

        response = self.make_request("POST", path, payload=payload)

        return response

    def revoke_promotinal_entitlements(
        self, app_user_id: str, entitlement_identifier: str
    ):
        # secret key, response: subscriber
        encoded_uid = encode(app_user_id)
        path = f"""
        subscribers/{encoded_uid}/entitlements/{entitlement_identifier}/revoke_promotionals
        """

        response = self.make_request("POST", path)

        return response

    def revoke_google_subscription(self, app_user_id: str, product_identifier: str):
        # secret key, response: subscriber
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/subscriptions/{product_identifier}/revoke"

        response = self.make_request("POST", path)

        return response

    def defer_google_subscription(
        self, app_user_id: str, product_identifier: str, expiry_time: datetime
    ):
        # secret key, response: subscriber
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/subscriptions/{product_identifier}/defer"
        expiry_time_ms = datetime_to_ms(expiry_time)
        payload = {"expiry_time_ms": expiry_time_ms}

        response = self.make_request("POST", path, payload)

        return response

    def refund_google_subscription(self, app_user_id: str, product_identifier: str):
        # store_transaction_identifier, secret key, response: subscriber
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/subscriptions/{product_identifier}/refund"

        response = self.make_request("POST", path)

        return response

    def add_user_attribution(
        self,
        app_user_id: str,
        network: AttributionSource,
        rc_idfa: str = None,
        rc_gps_adid: str = None,
    ):
        encoded_uid = encode(app_user_id)
        path = f"subscribers/{encoded_uid}/attribution"

        response = self.make_request("POST", path)

        return response

    def get_offerings(self, app_user_id: str, platform: Platform):
        # public only
        encoded_uid = encode(app_user_id)
        path = f"subscribers/{encoded_uid}/offerings"

        response = self.make_request("GET", path, platform=platform)

        return response

    def override_current_offering(self, app_user_id: str, offering_uuid: str):
        # secret key
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/offerings/{offering_uuid}/override"

        response = self.make_request("POST", path)

        return response

    def delete_current_offering_override(self, app_user_id: str):
        # secret key
        encoded_uid = encode(app_user_id)
        path = f"/subscribers/{encoded_uid}/offerings/override"

        response = self.make_request("DELETE", path)

        return response
