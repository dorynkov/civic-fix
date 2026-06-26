"""Moscow Nash Gorod — assisted submit (v1)."""

from app.connectors.base import SubmissionConnector


class NashGorodConnector(SubmissionConnector):
    PORTAL_URL = "https://gorod.mos.ru/"

    async def prepare_draft(self, issue_id: int) -> dict:
        return {"issue_id": issue_id, "portal": self.PORTAL_URL, "theme_hint": "pothole_street"}

    async def build_redirect(self, draft: dict) -> str:
        return self.PORTAL_URL
