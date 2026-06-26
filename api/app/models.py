import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IssueMode(str, enum.Enum):
    personal = "personal"
    collective = "collective"


class IssueStatus(str, enum.Enum):
    draft = "draft"
    pending_moderation = "pending_moderation"
    open = "open"
    petition_active = "petition_active"
    petition_threshold_met = "petition_threshold_met"
    submission_pending = "submission_pending"
    submitted = "submitted"
    awaiting_response = "awaiting_response"
    in_progress = "in_progress"
    claimed_fixed = "claimed_fixed"
    verifying = "verifying"
    closed_verified = "closed_verified"
    reopened = "reopened"
    merged = "merged"
    cancelled = "cancelled"


class PublicStatus(str, enum.Enum):
    registered = "registered"
    linked = "linked"
    in_moderation = "in_moderation"
    in_progress = "in_progress"
    claimed_fixed = "claimed_fixed"
    verifying = "verifying"
    closed = "closed"
    rejected = "rejected"
    reopened = "reopened"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issues: Mapped[list["Issue"]] = relationship(
        back_populates="reporter", foreign_keys="Issue.reporter_id"
    )


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[str] = mapped_column(String(64), default="moscow", index=True)
    mode: Mapped[IssueMode] = mapped_column(Enum(IssueMode), default=IssueMode.personal)
    category: Mapped[str] = mapped_column(String(64), default="pothole_street")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address_text: Mapped[str] = mapped_column(String(512), default="")
    photo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[IssueStatus] = mapped_column(Enum(IssueStatus), default=IssueStatus.open)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organizer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    merged_into_id: Mapped[int | None] = mapped_column(ForeignKey("issues.id"), nullable=True)
    submission_locked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reporter: Mapped["User"] = relationship(
        back_populates="issues", foreign_keys=[reporter_id]
    )
    petition: Mapped["Petition | None"] = relationship(back_populates="issue", uselist=False)
    tracking: Mapped["TrackingRecord | None"] = relationship(back_populates="issue", uselist=False)


class Petition(Base):
    __tablename__ = "petitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, default="")
    signature_goal: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[str] = mapped_column(String(32), default="collecting")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue: Mapped["Issue"] = relationship(back_populates="petition")
    signatures: Mapped[list["Signature"]] = relationship(back_populates="petition")


class Signature(Base):
    __tablename__ = "signatures"
    __table_args__ = (UniqueConstraint("petition_id", "user_id", name="uq_petition_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    petition_id: Mapped[int] = mapped_column(ForeignKey("petitions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    signed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    petition: Mapped["Petition"] = relationship(back_populates="signatures")
    user: Mapped["User"] = relationship()


class TrackingRecord(Base):
    __tablename__ = "tracking_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), unique=True)
    authority_channel: Mapped[str] = mapped_column(String(64), default="moscow_nash_gorod")
    external_case_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    public_status: Mapped[PublicStatus] = mapped_column(Enum(PublicStatus), default=PublicStatus.registered)
    sync_source: Mapped[str] = mapped_column(String(32), default="user_link")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue: Mapped["Issue"] = relationship(back_populates="tracking")


class StatusEvent(Base):
    __tablename__ = "status_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), index=True)
    public_status: Mapped[str] = mapped_column(String(32))
    note: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(32), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"))
    verifier_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    verdict: Mapped[str] = mapped_column(String(32))
    note: Mapped[str] = mapped_column(Text, default="")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
