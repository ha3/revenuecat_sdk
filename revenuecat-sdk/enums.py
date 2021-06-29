from enum import Enum


class AttributionSource(Enum):
    APPLE_SEARCH_ADS = 0
    ADJUST = 1
    APPSFLYER = 2
    BRANCH = 3
    TENJIN = 4
    FACEBOOK = 5


class PaymentMode(Enum):
    PAY_AS_YOU_GO = "0"
    PAY_UP_FRONT = "1"
    FREE_TRIAL = "2"


class PeriodType(Enum):
    NORMAL = "normal"
    TRIAL = "trial"
    INTRO = "intro"


class Platform(Enum):
    IOS = "ios"
    ANDROID = "android"
    MAC_OS = "macos"
    UI_KIT_FOR_MAC = "uikitformac"


class PromotionDuration(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TWO_MONTH = "two_month"
    THREE_MONTH = "three_month"
    SIX_MONTH = "six_month"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class Store(Enum):
    APP_STORE = "app_store"
    MAC_APP_STORE = "mac_app_store"
    PLAY_STORE = "play_store"
    STRIPE = "stripe"
    PROMOTIONAL = "promotional"


class OwnershipType(Enum):
    PURCHASED = "PURCHASED"
    FAMILY_SHARED = "FAMILY_SHARED"
