#!/usr/bin/env python3
"""P0 happy path smoke test — run from repo root with API deps installed."""

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(ROOT, "api")
SMOKE_DB = os.path.join(API_DIR, "data", "civic_fix_smoke.db")

os.environ["DATABASE_URL"] = f"sqlite:///{SMOKE_DB.replace(os.sep, '/')}"
os.environ.setdefault("JWT_SECRET", "dev-secret-change-in-production-min-32-chars")
os.environ.setdefault("UPLOAD_DIR", os.path.join(API_DIR, "data", "uploads"))

sys.path.insert(0, API_DIR)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def main() -> None:
    os.makedirs(os.path.dirname(SMOKE_DB), exist_ok=True)
    if os.path.isfile(SMOKE_DB):
        try:
            os.remove(SMOKE_DB)
        except PermissionError:
            fd, alt = tempfile.mkstemp(suffix=".db", dir=os.path.dirname(SMOKE_DB))
            os.close(fd)
            os.environ["DATABASE_URL"] = f"sqlite:///{alt.replace(os.sep, '/')}"
            import importlib
            import app.main as main_mod
            importlib.reload(main_mod)
            global app
            app = main_mod.app

    client = TestClient(app)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@example.com", "password": "demo1234"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    board = client.get("/api/v1/board")
    assert board.status_code == 200
    assert len(board.json()["items"]) >= 3

    created = client.post(
        "/api/v1/issues",
        json={
            "title": "Smoke test pothole",
            "description": "Automated P0 check",
            "latitude": 55.751,
            "longitude": 37.618,
            "mode": "personal",
        },
        headers=headers,
    )
    assert created.status_code == 200, created.text
    issue_id = created.json()["id"]

    upgrade = client.post(
        f"/api/v1/issues/{issue_id}/upgrade-to-collective?signature_goal=1",
        headers=headers,
    )
    assert upgrade.status_code == 200, upgrade.text

    petition = client.get(f"/api/v1/petitions/by-issue/{issue_id}")
    assert petition.status_code == 200
    petition_id = petition.json()["id"]

    sign = client.post(f"/api/v1/petitions/{petition_id}/sign", headers=headers)
    assert sign.status_code == 200, sign.text

    mock = client.post(f"/api/v1/issues/{issue_id}/mock-submit", headers=headers)
    assert mock.status_code == 200, mock.text
    assert "gorod.mos.ru" in mock.json()["redirect_url"]

    link = client.post(
        "/api/v1/tracking/link",
        json={"issue_id": issue_id, "external_case_number": "NG-12345"},
        headers=headers,
    )
    assert link.status_code == 200, link.text

    board_after = client.get("/api/v1/board")
    item = next(x for x in board_after.json()["items"] if x["id"] == issue_id)
    assert item["public_status"] == "linked"
    assert item["external_case_number_masked"] == "NG-***45"

    print("OK: P0 happy path passed")


if __name__ == "__main__":
    main()
