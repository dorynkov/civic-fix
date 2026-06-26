from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=2, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str

    model_config = {"from_attributes": True}


class IssueCreate(BaseModel):
    mode: str = "personal"
    category: str = "pothole_street"
    title: str = Field(min_length=3, max_length=255)
    description: str = ""
    latitude: float
    longitude: float
    address_text: str = ""
    signature_goal: int = 10


class IssueOut(BaseModel):
    id: int
    city_id: str
    mode: str
    category: str
    title: str
    description: str
    latitude: float
    longitude: float
    address_text: str
    photo_path: str | None
    status: str
    reporter_id: int
    organizer_id: int | None
    submission_locked_at: datetime | None
    signature_count: int = 0
    signature_goal: int | None = None
    public_status: str | None = None
    external_case_number_masked: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PetitionOut(BaseModel):
    id: int
    issue_id: int
    title: str
    body: str
    signature_goal: int
    signature_count: int
    status: str

    model_config = {"from_attributes": True}


class TrackingLink(BaseModel):
    issue_id: int
    external_case_number: str = Field(min_length=3, max_length=128)


class StatusReport(BaseModel):
    public_status: str
    note: str = ""


class MergeRequest(BaseModel):
    source_ids: list[int] = Field(min_length=1)


class VerificationCreate(BaseModel):
    verdict: str
    note: str = ""
    latitude: float | None = None
    longitude: float | None = None
