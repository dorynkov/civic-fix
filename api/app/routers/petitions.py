from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Issue, IssueStatus, Petition, Signature, User
from app.schemas import PetitionOut
from app.services.issues import issue_to_dict

router = APIRouter(prefix="/petitions", tags=["petitions"])


def petition_out(p: Petition) -> dict:
    return {
        "id": p.id,
        "issue_id": p.issue_id,
        "title": p.title,
        "body": p.body,
        "signature_goal": p.signature_goal,
        "signature_count": len(p.signatures),
        "status": p.status,
    }


@router.get("/{petition_id}")
def get_petition(petition_id: int, db: Session = Depends(get_db)):
    petition = (
        db.query(Petition)
        .options(joinedload(Petition.signatures))
        .filter(Petition.id == petition_id)
        .first()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")
    return petition_out(petition)


@router.post("/{petition_id}/sign")
def sign_petition(
    petition_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    petition = (
        db.query(Petition)
        .options(joinedload(Petition.signatures), joinedload(Petition.issue))
        .filter(Petition.id == petition_id)
        .first()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")
    if any(s.user_id == user.id for s in petition.signatures):
        raise HTTPException(status_code=400, detail="Already signed")
    db.add(Signature(petition_id=petition.id, user_id=user.id))
    petition.issue.status = IssueStatus.petition_active
    if len(petition.signatures) + 1 >= petition.signature_goal:
        petition.status = "threshold_met"
        petition.issue.status = IssueStatus.petition_threshold_met
    db.commit()
    db.refresh(petition)
    return petition_out(petition)


@router.get("/by-issue/{issue_id}")
def petition_by_issue(issue_id: int, db: Session = Depends(get_db)):
    petition = (
        db.query(Petition)
        .options(joinedload(Petition.signatures))
        .filter(Petition.issue_id == issue_id)
        .first()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="No petition")
    return petition_out(petition)
