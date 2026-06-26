from app.auth import hash_password
from app.database import SessionLocal
from app.models import Issue, IssueMode, IssueStatus, Petition, PublicStatus, TrackingRecord, User
from app.services.issues import ensure_tracking


def seed_demo():
    db = SessionLocal()
    try:
        if db.query(Issue).count() > 0:
            return
        demo = User(
            email="demo@example.com",
            display_name="Demo User",
            password_hash=hash_password("demo1234"),
        )
        db.add(demo)
        db.flush()

        samples = [
            ("Яма на тротуаре", 55.751, 37.618, "personal", IssueStatus.open),
            ("Выбоина во дворе", 55.755, 37.625, "collective", IssueStatus.petition_active),
            ("Незакрытый люк", 55.748, 37.610, "personal", IssueStatus.open),
        ]
        for title, lat, lon, mode, status in samples:
            issue = Issue(
                city_id="moscow",
                mode=IssueMode(mode),
                category="pothole_street",
                title=title,
                description=f"Demo: {title}",
                latitude=lat,
                longitude=lon,
                address_text="Москва",
                status=status,
                reporter_id=demo.id,
                organizer_id=demo.id if mode == "collective" else None,
            )
            db.add(issue)
            db.flush()
            tr = TrackingRecord(issue_id=issue.id, public_status=PublicStatus.registered)
            db.add(tr)
            if mode == "collective":
                db.add(
                    Petition(
                        issue_id=issue.id,
                        title=title,
                        body=issue.description,
                        signature_goal=10,
                        status="collecting",
                    )
                )
        db.commit()
    finally:
        db.close()
