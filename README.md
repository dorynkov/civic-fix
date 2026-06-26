# Civic Fix

Коллективные обращения по городским проблемам (Москва-first). P0 прототип.

## Быстрый старт

```bash
docker compose up --build
```

- Web: http://localhost:20640
- API: http://localhost:20642/health
- Demo login: `demo@example.com` / `demo1234`

## Happy path (P0)

1. Войти → `/board`
2. Создать жалобу → `/issues/new`
3. «Сделать коллективным» → подписать → «Клич» (share)
4. «Подать (mock)» → gorod.mos.ru → ввести № заявки → Link
5. Статус на доске

## Локально без Docker

```bash
# API
cd api && pip install -r requirements.txt
DATABASE_URL=sqlite:///./data/civic_fix.db uvicorn app.main:app --reload --port 20642

# Web
cd web && npm install && npm run dev
```

## Smoke test (API)

```bash
cd api && pip install -r requirements.txt
python ../scripts/smoke_happy_path.py
```

- Change: `dev-hub-personal` → `ops-023-civic-fix`
- Guide: `docs/special-projects/civic-fix/GUIDE.md`

## v1 (scaffold in repo)

- `api/app/auth_providers/mos_id.py` — ephemeral Mos ID
- `api/app/connectors/` — Nash Gorod, Mos Reception, ESIA stub
- `api/app/workers/mass_relay.py` — MassRelay queue
- `api/app/bot/main.py` — Telegram stub
