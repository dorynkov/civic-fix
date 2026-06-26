from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Issue, IssueMode, IssueStatus, Petition, PublicStatus, Signature, User
from app.schemas import IssueCreate, IssueOut, MergeRequest
from app.services.issues import (
    add_status_event,
    can_convert,
    create_petition_for_issue,
    ensure_tracking,
    issue_to_dict,
)

router = APIRouter(prefix="/issues", tags=["issues"])


@router.get("")
def list_issues(city: str = "moscow", db: Session = Depends(get_db)):
    issues = (
        db.query(Issue)
        .options(joinedload(Issue.petition).joinedload(Petition.signatures), joinedload(Issue.tracking))
        .filter(Issue.city_id == city, Issue.status != IssueStatus.merged)
        .order_by(Issue.created_at.desc())
        .all()
    )
    return [issue_to_dict(i, db) for i in issues]


@router.post("", response_model=IssueOut)
def create_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    mode = IssueMode.collective if payload.mode == "collective" else IssueMode.personal
    issue = Issue(
        city_id=settings.city_default,
        mode=mode,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address_text=payload.address_text,
        status=IssueStatus.open if mode == IssueMode.personal else IssueStatus.petition_active,
        reporter_id=user.id,
        organizer_id=user.id if mode == IssueMode.collective else None,
    )
    db.add(issue)
    db.flush()
    ensure_tracking(db, issue)
    if mode == IssueMode.collective:
        create_petition_for_issue(db, issue, payload.signature_goal)
    add_status_event(db, issue.id, PublicStatus.registered.value, "Issue created")
    db.commit()
    db.refresh(issue)
    return issue_to_dict(issue, db)


@router.get("/{issue_id}")
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.petition).joinedload(Petition.signatures), joinedload(Issue.tracking))
        .filter(Issue.id == issue_id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue_to_dict(issue, db)


@router.post("/{issue_id}/upgrade-to-collective")
def upgrade_to_collective(
    issue_id: int,
    signature_goal: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.reporter_id != user.id:
        raise HTTPException(status_code=403, detail="Only reporter can upgrade")
    if not can_convert(issue):
        raise HTTPException(status_code=409, detail="Issue locked for conversion")
    if issue.mode == IssueMode.collective:
        raise HTTPException(status_code=400, detail="Already collective")
    create_petition_for_issue(db, issue, signature_goal)
    db.commit()
    db.refresh(issue)
    return issue_to_dict(issue, db)


@router.post("/{issue_id}/photos")
async def upload_photo(
    issue_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.reporter_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    import os
    from pathlib import Path

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    dest = upload_dir / f"issue_{issue_id}{ext}"
    content = await file.read()
    dest.write_bytes(content)
    issue.photo_path = str(dest)
    db.commit()
    return {"photo_path": issue.photo_path}


@router.post("/merge")
def merge_issues(
    payload: MergeRequest,
    target_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target = db.get(Issue, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    if not can_convert(target):
        raise HTTPException(status_code=409, detail="Target locked")
    if target.mode != IssueMode.collective and target.petition is None:
        create_petition_for_issue(db, target, 10)

    for sid in payload.source_ids:
        if sid == target_id:
            continue
        source = db.get(Issue, sid)
        if not source or source.mode != IssueMode.personal:
            continue
        if not can_convert(source):
            continue
        source.status = IssueStatus.merged
        source.merged_into_id = target_id
        if source.description:
            target.description += f"\n\n[Merged #{source.id}]: {source.description}"
    db.commit()
    db.refresh(target)
    return issue_to_dict(target, db)


@router.get("/nearby")
def nearby(lat: float, lon: float, radius_m: float = 500, db: Session = Depends(get_db)):
    # P0: simple bbox ~500m
    delta = radius_m / 111_000
    issues = (
        db.query(Issue)
        .filter(
            Issue.latitude.between(lat - delta, lat + delta),
            Issue.longitude.between(lon - delta, lon + delta),
            Issue.status != IssueStatus.merged,
        )
        .limit(20)
        .all()
    )
    return [issue_to_dict(i, db) for i in issues]
