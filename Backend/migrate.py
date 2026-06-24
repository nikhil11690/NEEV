"""
Run this ONCE on the server after deploying the new database.py.
It safely adds new columns to the existing neev.db without dropping any data.

Usage:
    cd Backend
    python migrate.py
"""

import sqlite3
import uuid

conn = sqlite3.connect("neev.db")
cur = conn.cursor()

# Add new columns to workers table (ALTER TABLE is safe — won't fail if column exists)
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
        print(f"OK: {sql}")
    except sqlite3.OperationalError as e:
        print(f"SKIP (already exists): {e}")

# Generate worker_id UUIDs for existing workers that don't have one
cur.execute("SELECT id, worker_id FROM workers")
rows = cur.fetchall()
for row_id, existing_wid in rows:
    if not existing_wid:
        new_id = str(uuid.uuid4())
        cur.execute("UPDATE workers SET worker_id = ? WHERE id = ?", (new_id, row_id))
        print(f"Assigned worker_id {new_id} to worker row {row_id}")

# Create EmployerMCQ table if not exists
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
print("OK: employer_mcqs table ready")

# Add worker_id column to verifications if missing
try:
    cur.execute("ALTER TABLE verifications ADD COLUMN worker_id TEXT")
    print("OK: verifications.worker_id added")
except sqlite3.OperationalError as e:
    print(f"SKIP: {e}")

conn.commit()
conn.close()
print("\nMigration complete.")
