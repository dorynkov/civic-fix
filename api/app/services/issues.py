from datetime import datetime

from app.models import Issue, IssueMode, IssueStatus, Petition, PublicStatus, StatusEvent, TrackingRecord


def mask_case_number(case: str | None) -> str | None:
    if not case or len(case) < 4:
        return case
    return f"{case[:3]}***{case[-2:]}"


def ensure_tracking(db, issue: Issue) -> TrackingRecord:
    if issue.tracking:
        return issue.tracking
    record = TrackingRecord(issue_id=issue.id, public_status=PublicStatus.registered)
    db.add(record)
    db.flush()
    return record


def add_status_event(db, issue_id: int, public_status: str, note: str = "", source: str = "system"):
    db.add(
        StatusEvent(
            issue_id=issue_id,
            public_status=public_status,
            note=note,
            source=source,
        )
    )


def issue_to_dict(issue: Issue, db) -> dict:
    sig_count = 0
    sig_goal = None
    if issue.petition:
        sig_count = len(issue.petition.signatures)
        sig_goal = issue.petition.signature_goal
    public_status = None
    case_masked = None
    if issue.tracking:
        public_status = issue.tracking.public_status.value
        case_masked = mask_case_number(issue.tracking.external_case_number)
    return {
        "id": issue.id,
        "city_id": issue.city_id,
        "mode": issue.mode.value,
        "category": issue.category,
        "title": issue.title,
        "description": issue.description,
        "latitude": issue.latitude,
        "longitude": issue.longitude,
        "address_text": issue.address_text,
        "photo_path": issue.photo_path,
        "status": issue.status.value,
        "reporter_id": issue.reporter_id,
        "organizer_id": issue.organizer_id,
        "submission_locked_at": issue.submission_locked_at,
        "signature_count": sig_count,
        "signature_goal": sig_goal,
        "public_status": public_status,
        "external_case_number_masked": case_masked,
        "created_at": issue.created_at,
    }


def can_convert(issue: Issue) -> bool:
    return issue.submission_locked_at is None and issue.status not in {
        IssueStatus.submitted,
        IssueStatus.merged,
        IssueStatus.cancelled,
    }


def create_petition_for_issue(db, issue: Issue, goal: int = 10) -> Petition:
    petition = Petition(
        issue_id=issue.id,
        title=issue.title,
        body=issue.description,
        signature_goal=goal,
        status="collecting",
    )
    issue.mode = IssueMode.collective
    issue.status = IssueStatus.petition_active
    issue.organizer_id = issue.organizer_id or issue.reporter_id
    db.add(petition)
    ensure_tracking(db, issue)
    add_status_event(db, issue.id, PublicStatus.registered.value, "Collective petition opened")
    return petition
