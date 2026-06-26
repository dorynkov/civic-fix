from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import VerificationCreate
from app.auth import get_current_user
from app.database import get_db
from app.models import Issue, IssueStatus, PublicStatus, User, Verification
from app.services.issues import add_status_event, ensure_tracking

router = APIRouter(prefix="/verifications", tags=["verifications"])


@router.post("")
def create_verification(
    issue_id: int,
    payload: VerificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.add(
        Verification(
            issue_id=issue_id,
            verifier_id=user.id,
            verdict=payload.verdict,
            note=payload.note,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    )
    record = ensure_tracking(db, issue)
    if payload.verdict == "confirmed_fixed":
        record.public_status = PublicStatus.closed
        issue.status = IssueStatus.closed_verified
    elif payload.verdict == "not_fixed":
        record.public_status = PublicStatus.reopened
        issue.status = IssueStatus.reopened
        issue.submission_locked_at = None
    add_status_event(db, issue.id, record.public_status.value, payload.note, "verifier")
    db.commit()
    return {"verdict": payload.verdict, "public_status": record.public_status.value}
