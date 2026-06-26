from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Issue, IssueStatus, User

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.patch("/issues/{issue_id}/approve")
def approve_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Not found")
    issue.status = IssueStatus.open
    db.commit()
    return {"status": issue.status.value}


@router.patch("/issues/{issue_id}/reject")
def reject_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Not found")
    issue.status = IssueStatus.cancelled
    db.commit()
    return {"status": issue.status.value}
