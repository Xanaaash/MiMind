HOTLINE_BY_LOCALE = {
    "en-US": {
        "name": "988 Suicide & Crisis Lifeline",
        "phone": "988",
        "text": "Text or call 988",
    },
    "zh-CN": {
        "name": "全国心理援助热线",
        "phone": "12356",
        "text": "可拨打本地心理援助热线",
    },
}

FALLBACK_HOTLINE = {
    "name": "Local Emergency Support",
    "phone": "112",
    "text": "Call your local emergency number immediately if danger is imminent.",
}


class HotlineResolver:
    def resolve(self, locale: str) -> dict:
        return HOTLINE_BY_LOCALE.get(locale, FALLBACK_HOTLINE)

    def local_cache_payload(self) -> dict:
        payload = dict(HOTLINE_BY_LOCALE)
        payload["default"] = FALLBACK_HOTLINE
        return payload
