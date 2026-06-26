"""Moscow electronic reception — DualTrack PDF (v1.1)."""

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.connectors.base import SubmissionConnector


class MosReceptionConnector(SubmissionConnector):
    PORTAL_URL = "https://www.mos.ru/feedback/reception/"

    def build_signatures_pdf(self, petition_title: str, signers: list[str]) -> bytes:
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.drawString(50, 800, f"Collective appeal: {petition_title[:80]}")
        y = 770
        for i, name in enumerate(signers, 1):
            c.drawString(50, y, f"{i}. {name}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
        c.save()
        return buf.getvalue()

    async def prepare_draft(self, issue_id: int) -> dict:
        return {"issue_id": issue_id, "portal": self.PORTAL_URL}

    async def build_redirect(self, draft: dict) -> str:
        return self.PORTAL_URL
