from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.auth_providers.mos_id import MosIdEphemeralSession
from app.connectors.nash_gorod import NashGorodConnector
from app.connectors.mos_reception import MosReceptionConnector
from app.database import get_db
from app.models import Issue, Petition, Signature, User
from app.workers.mass_relay import enqueue_mass_relay

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/{issue_id}/assisted")
async def assisted_submit(
    issue_id: int,
    channel: str = "nash_gorod",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Not found")
    mos = MosIdEphemeralSession()
    redirect = mos.start_submit_flow(user.id, issue_id)
    if channel == "nash_gorod":
        connector = NashGorodConnector()
    else:
        connector = MosReceptionConnector()
    draft = await connector.prepare_draft(issue_id)
    portal = await connector.build_redirect(draft)
    return {"mos_id_redirect": redirect, "portal_url": portal, "draft": draft}


@router.post("/{issue_id}/mass-relay/trigger")
async def trigger_mass_relay(
    issue_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.petition).joinedload(Petition.signatures))
        .filter(Issue.id == issue_id)
        .first()
    )
    if not issue or not issue.petition:
        raise HTTPException(status_code=404, detail="No petition")
    signer_ids = [s.user_id for s in issue.petition.signatures]
    count = await enqueue_mass_relay(None, issue.petition.id, signer_ids)
    return {"queued": count}


@router.get("/{issue_id}/collective-pdf")
def collective_pdf(issue_id: int, db: Session = Depends(get_db)):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.petition).joinedload(Petition.signatures).joinedload(Signature.user))
        .filter(Issue.id == issue_id)
        .first()
    )
    if not issue or not issue.petition:
        raise HTTPException(status_code=404, detail="No petition")
    connector = MosReceptionConnector()
    names = [s.user.display_name for s in issue.petition.signatures]
    pdf = connector.build_signatures_pdf(issue.petition.title, names)
    from fastapi.responses import Response

    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=signatures.pdf"})
