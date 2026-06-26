"""Mos ID ephemeral OAuth — token in Redis TTL 15min (v1 scaffold)."""

import json
import uuid
from datetime import timedelta

import redis

from app.config import settings


class MosIdEphemeralSession:
    TTL_SECONDS = 900

    def __init__(self):
        self._redis = redis.from_url(settings.redis_url, decode_responses=True)

    def start_submit_flow(self, user_id: int, issue_id: int) -> str:
        session_id = str(uuid.uuid4())
        payload = {"user_id": user_id, "issue_id": issue_id}
        self._redis.setex(f"mosid:session:{session_id}", self.TTL_SECONDS, json.dumps(payload))
        if settings.mos_id_enabled and settings.mos_id_client_id:
            return (
                f"https://login.mos.ru/oauth/authorize"
                f"?client_id={settings.mos_id_client_id}"
                f"&redirect_uri={settings.mos_id_redirect_uri}"
                f"&state={session_id}"
            )
        return f"/mock-mos-id?session={session_id}"

    def discard(self, session_id: str) -> None:
        self._redis.delete(f"mosid:session:{session_id}")
