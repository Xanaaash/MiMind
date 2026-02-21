from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DomesticBillingConfig:
    alipay_gateway_url: str
    alipay_notify_secret: str
    wechat_gateway_url: str
    wechat_notify_secret: str

    @property
    def enabled(self) -> bool:
        return bool(self.alipay_notify_secret or self.wechat_notify_secret)


def load_domestic_billing_config() -> DomesticBillingConfig:
    return DomesticBillingConfig(
        alipay_gateway_url=os.getenv("ALIPAY_GATEWAY_URL", "https://openapi.alipay.com/gateway.do").strip(),
        alipay_notify_secret=os.getenv("ALIPAY_NOTIFY_SECRET", "").strip(),
        wechat_gateway_url=os.getenv(
            "WECHAT_PAY_GATEWAY_URL",
            "https://api.mch.weixin.qq.com/v3/pay/transactions/native",
        ).strip(),
        wechat_notify_secret=os.getenv("WECHAT_PAY_NOTIFY_SECRET", "").strip(),
    )
