from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SubmissionResult:
    success: bool
    external_case_number: str | None = None
    redirect_url: str | None = None
    message: str = ""


class SubmissionConnector(ABC):
    @abstractmethod
    async def prepare_draft(self, issue_id: int) -> dict:
        ...

    @abstractmethod
    async def build_redirect(self, draft: dict) -> str:
        ...
