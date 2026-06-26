# Civic Fix — Agents

Product repo for collective civic complaints. Hub: `dev-hub-personal` change `ops-023-civic-fix`.

## Stack

- API: FastAPI, SQLAlchemy, PostgreSQL (SQLite local)
- Web: Next.js 15, MapLibre, Tailwind
- Ports: web 20640, api 20642 (see hub `ports.personal.yaml`)

## Run

`docker compose up --build` or see README.

## Personal infra

VPS deploy via admin-tools (future). See hub `docs/methodology/personal-infra.md`.

## Personal infra (AdminTools)

Sibling repo (**not** kit): VPS, secrets, deploy — [personal-infra](https://github.com/dorynkov/dev-hub-personal/blob/main/docs/methodology/personal-infra.md).

- Path: `E:/Проекты/personal/admin-tools` · override: `ADMINTOOLS_ROOT`
- Catalog: [admin-tools/AGENTS.md](https://github.com/dorynkov/admin-tools/blob/main/AGENTS.md)
