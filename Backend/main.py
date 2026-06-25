import sqlite3
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# ── Auto-migration (runs on every startup, safe to re-run) ───────────────────
def run_migrations():
    conn = sqlite3.connect("neev.db")
    cur = conn.cursor()

    migrations = [
        "ALTER TABLE workers ADD COLUMN worker_id TEXT",
        "ALTER TABLE workers ADD COLUMN nsqf_levels TEXT",
        "ALTER TABLE workers ADD COLUMN qr_base64 TEXT",
        "ALTER TABLE workers ADD COLUMN interview_completed INTEGER DEFAULT 0",
        "ALTER TABLE workers ADD COLUMN updated_at TEXT",
    ]
    for sql in migrations:
        try:
            cur.execute(sql)
        except sqlite3.OperationalError:
            pass

    cur.execute("SELECT id, worker_id FROM workers")
    for row_id, wid in cur.fetchall():
        if not wid:
            cur.execute(
                "UPDATE workers SET worker_id = ? WHERE id = ?",
                (str(uuid.uuid4()), row_id)
            )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employer_mcqs (
            id INTEGER PRIMARY KEY,
            worker_name TEXT,
            employer_name TEXT,
            q1_satisfaction INTEGER,
            q2_unexpected TEXT,
            q3_would_rehire INTEGER,
            q4_skill_accuracy INTEGER,
            created_at TEXT
        )
    """)

    try:
        cur.execute("ALTER TABLE verifications ADD COLUMN worker_id TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

run_migrations()


# ── App setup ─────────────────────────────────────────────────────────────────
from Aayush.transcribe import router as transcribe_router
from Aayush.extract_skills import router as skills_router
from Aayush.process import router as process_router
from Aayush.validate import router as validate_router
from Aayush.employer_mcq import router as mcq_router
from Nikhil.credential import router as credential_router
from Nikhil.verify import router as verify_router
from Nikhil.trust import router as trust_router
from Nikhil.passport import router as passport_router
from Nikhil.community import router as community_router
from Nikhil.auth import router as auth_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router)
app.include_router(skills_router)
app.include_router(process_router)
app.include_router(validate_router)
app.include_router(mcq_router)
app.include_router(credential_router)
app.include_router(verify_router)
app.include_router(trust_router)
app.include_router(passport_router)
app.include_router(community_router)
app.include_router(auth_router)

# Routes PEHLE — mount ke BAAD nahi
@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/")
def root():
    return {"status": "working", "project": "NEEV Skill Passport"}

# Static mount SABSE LAST MEIN
app.mount("/static", StaticFiles(directory="../Frontend", html=True), name="frontend")