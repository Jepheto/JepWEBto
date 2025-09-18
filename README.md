# mysite (Flask + PostgreSQL)

## Run (dev / prod-like)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env의 DATABASE_URL을 Postgres로 설정 (예: RDS/Neon/Supabase 등)
mkdir -p uploads instance
