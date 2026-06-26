"""ESIA / other regions (v2 stub)."""

from app.connectors.base import SubmissionConnector


class EsiaConnector(SubmissionConnector):
    async def prepare_draft(self, issue_id: int) -> dict:
        raise NotImplementedError("ESIA connector — v2")

    async def build_redirect(self, draft: dict) -> str:
        raise NotImplementedError("ESIA connector — v2")
