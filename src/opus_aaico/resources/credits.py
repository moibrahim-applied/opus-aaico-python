"""Credits resource — credit usage history (v2)."""

from __future__ import annotations

from typing import Any

from opus_aaico._exceptions import NotSupportedError
from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.credits import CreditBalance, CreditHistoryEntry


_GONE_MSG = (
    "{method}() is no longer available. The /credits/balance and /credits/usage "
    "endpoints were removed in OPUS v2. Use credits.history() instead — it returns "
    "every credit transaction with a running balance_after field. The latest entry's "
    "balance_after is your current balance."
)


def _parse_history(raw: Any) -> list[CreditHistoryEntry]:
    if not isinstance(raw, list):
        return []
    out: list[CreditHistoryEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        # API returns numbers as strings sometimes — coerce
        cleaned = dict(item)
        for k in ("balance_after", "credits_used"):
            v = cleaned.get(k)
            if isinstance(v, str):
                try:
                    cleaned[k] = float(v)
                except ValueError:
                    cleaned[k] = None
        out.append(CreditHistoryEntry(**cleaned))
    return out


class SyncCredits(SyncResource):
    """Synchronous credits resource (v2)."""

    def history(
        self, offset: int = 0, max_results: int = 100
    ) -> list[CreditHistoryEntry]:
        """Return credit transaction history with running balance.

        Replaces the removed get_balance() and get_usage() methods. The newest
        entry's ``balance_after`` is your current balance.
        """
        data = self._client.request(
            "GET",
            "/credits/history",
            params={"offset": offset, "max_results": max_results},
        )
        return _parse_history(data)

    def current_balance(self) -> float | None:
        """Convenience: return the latest balance_after from history."""
        entries = self.history(max_results=1)
        return entries[0].balance_after if entries else None

    # ---- removed in v2 ---------------------------------------------------

    def get_balance(self) -> CreditBalance:
        raise NotSupportedError(_GONE_MSG.format(method="get_balance"))

    def create_balance(self, *args: Any, **kwargs: Any) -> CreditBalance:
        raise NotSupportedError(_GONE_MSG.format(method="create_balance"))

    def get_usage(self) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="get_usage"))

    def get_workflow_usage(self, workflow_id: str) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="get_workflow_usage"))

    def record_usage(self, *args: Any, **kwargs: Any) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="record_usage"))


class AsyncCredits(AsyncResource):
    """Asynchronous credits resource (v2)."""

    async def history(
        self, offset: int = 0, max_results: int = 100
    ) -> list[CreditHistoryEntry]:
        data = await self._client.request(
            "GET",
            "/credits/history",
            params={"offset": offset, "max_results": max_results},
        )
        return _parse_history(data)

    async def current_balance(self) -> float | None:
        entries = await self.history(max_results=1)
        return entries[0].balance_after if entries else None

    # ---- removed in v2 ---------------------------------------------------

    async def get_balance(self) -> CreditBalance:
        raise NotSupportedError(_GONE_MSG.format(method="get_balance"))

    async def create_balance(self, *args: Any, **kwargs: Any) -> CreditBalance:
        raise NotSupportedError(_GONE_MSG.format(method="create_balance"))

    async def get_usage(self) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="get_usage"))

    async def get_workflow_usage(self, workflow_id: str) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="get_workflow_usage"))

    async def record_usage(self, *args: Any, **kwargs: Any) -> Any:
        raise NotSupportedError(_GONE_MSG.format(method="record_usage"))
