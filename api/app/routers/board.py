from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Issue, IssueStatus, Petition, PublicStatus, Signature, StatusEvent, TrackingRecord, User
from app.schemas import StatusReport, TrackingLink
from app.services.issues import add_status_event, ensure_tracking, issue_to_dict, mask_case_number

router = APIRouter(tags=["tracking"])


@router.get("/board")
def board(city: str = "moscow", status: str | None = None, db: Session = Depends(get_db)):
    q = (
        db.query(Issue)
        .options(joinedload(Issue.petition).joinedload(Petition.signatures), joinedload(Issue.tracking))
        .filter(Issue.city_id == city, Issue.status != IssueStatus.merged)
    )
    issues = q.order_by(Issue.created_at.desc()).all()
    items = []
    for issue in issues:
        data = issue_to_dict(issue, db)
        if status and data.get("public_status") != status:
            continue
        items.append(data)
    return {"city": city, "items": items}


@router.post("/tracking/link")
def link_tracking(
    payload: TrackingLink,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, payload.issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.reporter_id != user.id and issue.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    record = ensure_tracking(db, issue)
    record.external_case_number = payload.external_case_number
    record.public_status = PublicStatus.linked
    record.sync_source = "user_link"
    record.last_synced_at = datetime.utcnow()
    issue.status = IssueStatus.awaiting_response
    add_status_event(
        db,
        issue.id,
        PublicStatus.linked.value,
        f"Case {mask_case_number(payload.external_case_number)}",
        "user_link",
    )
    db.commit()
    return {"issue_id": issue.id, "public_status": record.public_status.value}


@router.get("/tracking/{issue_id}")
def get_tracking(issue_id: int, db: Session = Depends(get_db)):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.tracking), joinedload(Issue.petition).joinedload(Petition.signatures))
        .filter(Issue.id == issue_id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    events = (
        db.query(StatusEvent)
        .filter(StatusEvent.issue_id == issue_id)
        .order_by(StatusEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "issue": issue_to_dict(issue, db),
        "timeline": [
            {
                "public_status": e.public_status,
                "note": e.note,
                "source": e.source,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }


@router.post("/tracking/{issue_id}/status-report")
def status_report(
    issue_id: int,
    payload: StatusReport,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    record = ensure_tracking(db, issue)
    try:
        record.public_status = PublicStatus(payload.public_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid status") from exc
    record.sync_source = "user_report"
    record.last_synced_at = datetime.utcnow()
    add_status_event(db, issue.id, payload.public_status, payload.note, "user_report")
    db.commit()
    return {"public_status": record.public_status.value}


@router.post("/issues/{issue_id}/mock-submit")
def mock_submit(
    issue_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.organizer_id != user.id and issue.reporter_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if issue.mode.value == "collective" and issue.petition:
        if len(issue.petition.signatures) < issue.petition.signature_goal:
            raise HTTPException(status_code=400, detail="Signature threshold not met")
    issue.status = IssueStatus.submission_pending
    issue.submission_locked_at = datetime.utcnow()
    record = ensure_tracking(db, issue)
    record.public_status = PublicStatus.in_moderation
    add_status_event(db, issue.id, PublicStatus.in_moderation.value, "Mock submit — open gorod.mos.ru", "mock")
    db.commit()
    return {
        "redirect_url": "https://gorod.mos.ru/",
        "message": "P0: open Nash Gorod and submit with your Mos ID, then link case number",
    }
