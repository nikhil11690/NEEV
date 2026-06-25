# NEEV Backend — API Reference

Track owner: Nikhil  
Files: `auth.py` · `credential.py` · `verify.py` · `trust.py` · `passport.py` · `community.py` · `database.py` · `hasher.py`  
Base URL (local dev): `http://127.0.0.1:8000`  
Base URL (production): `https://neev-1.onrender.com`

> All routes are registered in `main.py` under a single FastAPI app. The old two-port setup (`8000` + `8001`) no longer exists.

---

## Table of Contents

1. [Auth](#1-auth)
2. [Credential](#2-credential)
3. [Verify](#3-verify)
4. [Trust & Reviews](#4-trust--reviews)
5. [Passport PDF](#5-passport-pdf)
6. [Community Endorsements](#6-community-endorsements)
7. [Database Schema](#7-database-schema)
8. [Hashing — Security Model](#8-hashing--security-model)
9. [Typical Flows](#9-typical-flows)

---

## 1. Auth

**File:** `auth.py`  
Handles signup, login, logout, and token introspection. Tokens are stored in-memory (`active_tokens` dict) — suitable for demo; replace with Redis in production.

---

### POST `/signup`

Registers a new worker or employer account.

#### Request Body
```json
{
  "name": "Raju Kumar",
  "email": "raju@example.com",
  "password": "mypassword",
  "role": "worker"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | Yes | Full name |
| `email` | string | Yes | Must be unique |
| `password` | string | Yes | Stored as SHA256 hash |
| `role` | string | Yes | `"worker"` or `"employer"` only |

#### Response — 200 OK
```json
{
  "success": true,
  "token": "a3f9c2...",
  "user": {
    "id": 1,
    "name": "Raju Kumar",
    "email": "raju@example.com",
    "role": "worker"
  },
  "message": "Account created successfully"
}
```

#### Response — 400
```json
{ "detail": "Email already registered" }
{ "detail": "Role must be 'worker' or 'employer'" }
```

---

### POST `/login`

Authenticates an existing user and returns a session token.

#### Request Body
```json
{
  "email": "raju@example.com",
  "password": "mypassword"
}
```

#### Response — 200 OK
```json
{
  "success": true,
  "token": "b7e1d4...",
  "user": {
    "id": 1,
    "name": "Raju Kumar",
    "email": "raju@example.com",
    "role": "worker"
  }
}
```

#### Response — 401
```json
{ "detail": "Email not found" }
{ "detail": "Wrong password" }
```

---

### POST `/logout`

Invalidates a session token.

#### Query Parameter
| Param | Type | Notes |
|---|---|---|
| `token` | string | Token to invalidate |

#### Response — 200 OK
```json
{ "success": true, "message": "Logged out" }
```

---

### GET `/me`

Returns the user info attached to a token.

#### Query Parameter
| Param | Type | Notes |
|---|---|---|
| `token` | string | Active session token |

#### Response — 200 OK
```json
{
  "user_id": 1,
  "name": "Raju Kumar",
  "email": "raju@example.com",
  "role": "worker"
}
```

#### Response — 401
```json
{ "detail": "Invalid or expired token" }
```

---

## 2. Credential

**File:** `credential.py`  
Handles credential creation, skill updates, and interview completion. Core design principle: **the QR encodes only the `worker_id` UUID — never the skill data**. Skills are stored in the DB and fetched live at verify time, so they can be updated without ever changing the QR.

---

### POST `/generate-credential`

Creates a new worker record and generates a permanent QR. Idempotent — calling again with the same name returns the existing QR, never regenerates it.

#### Request Body
```json
{
  "name": "Raju Kumar",
  "skills": ["plastering", "painting"],
  "nsqf_levels": [4, 3],
  "experience_years": 5,
  "ai_validation_score": 0.0
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | Yes | Must be unique across workers |
| `skills` | list[string] | Yes | Skill names from `/process` or `/extract-skills` |
| `nsqf_levels` | list[int] | Yes | Matching NSQF level per skill |
| `experience_years` | int | No | Defaults to `0` |
| `ai_validation_score` | float | No | Defaults to `0.0`. Pass the score from `/validate-answer` if interview already done. |

#### Response — 200 OK (new worker)
```json
{
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "interview_completed": false,
  "message": "new_worker"
}
```

#### Response — 200 OK (existing worker)
```json
{
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "interview_completed": true,
  "message": "existing_worker"
}
```

| Field | Type | Notes |
|---|---|---|
| `worker_id` | string | Permanent UUID. Frontend must store this in `sessionStorage`. |
| `qr_code_base64` | string | Base64 PNG. Render as `<img src="data:image/png;base64,{value}">`. Never changes. |
| `interview_completed` | boolean | `false` → frontend should gate the passport and redirect to interview. |
| `message` | string | `"new_worker"` or `"existing_worker"` |

#### What the QR encodes
The QR contains **only** the `worker_id` UUID string — nothing else:
```
f47ac10b-58cc-4372-a567-0e02b2c3d479
```
All profile data (skills, NSQF levels, trust score) is fetched from the DB at verify time using this ID.

---

### POST `/update-skills`

Updates a worker's skills in the DB. The QR code is **not affected** — same QR, new skills, instantly reflected on the next verify scan.

#### Request Body
```json
{
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "new_skills": ["plastering", "painting", "driving"],
  "new_nsqf_levels": [4, 3, 3]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `worker_id` | string | Yes | Permanent UUID from `/generate-credential` |
| `new_skills` | list[string] | Yes | Full updated skill list (not just new ones) |
| `new_nsqf_levels` | list[int] | Yes | Matching NSQF level per skill |

#### Response — 200 OK
```json
{
  "success": true,
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "updated_skills": ["plastering", "painting", "driving"],
  "qr_unchanged": true,
  "message": "Skills updated. QR code remains the same."
}
```

#### Response — 404
```json
{ "detail": "Worker not found" }
```

---

### POST `/complete-interview`

Marks a worker's interview as complete and saves the AI confidence score. Called by the frontend after `/validate-answer` returns a score.

#### Query Parameters
| Param | Type | Required | Notes |
|---|---|---|---|
| `worker_id` | string | Yes | Permanent UUID |
| `ai_score` | float | Yes | Confidence score (0–100) from `/validate-answer` |

#### Example curl
```bash
curl -X POST "http://127.0.0.1:8000/complete-interview?worker_id=f47ac10b...&ai_score=82.5"
```

#### Response — 200 OK
```json
{
  "success": true,
  "interview_completed": true,
  "ai_score": 82.5
}
```

#### Response — 404
```json
{ "detail": "Worker not found" }
```

---

## 3. Verify

**File:** `verify.py`  
The employer-facing verification layer. Accepts a `worker_id` scanned from a QR, fetches the full worker profile live from DB, recalculates trust score, runs fraud detection, and returns everything in a single response.

---

### POST `/verify`

Verifies a worker's credential by `worker_id`. Every call logs a verification record to the `verifications` table.

#### Request Body
```json
{
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

#### Response — 200 OK (valid)
```json
{
  "valid": true,
  "worker_data": {
    "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Raju Kumar",
    "skills": ["plastering", "painting"],
    "nsqf_levels": [4, 3],
    "experience_years": 5,
    "interview_completed": true,
    "ai_validation_score": 82.5,
    "member_since": "Jun 2026"
  },
  "trust_score": 76.43,
  "employer_reviews": [
    {
      "rating": 4,
      "feedback": "Very reliable worker",
      "skill_level": "intermediate",
      "date": "Jun 2026"
    }
  ],
  "employer_mcqs": [
    {
      "employer": "Sharma Constructions",
      "satisfaction": 4,
      "skill_accuracy": 5,
      "would_rehire": true,
      "unexpected_handling": "Bohot achhe se handle kiya",
      "date": "Jun 2026"
    }
  ],
  "employer_reviews_count": 2,
  "community_endorsements": [
    {
      "endorser": "Suresh Contractor",
      "role": "contractor",
      "duration": "2 years",
      "comment": "Very reliable on site",
      "date": "Jun 2026"
    }
  ],
  "fraud_risk": "low",
  "fraud_flags": [],
  "verified_at": "2026-06-28 10:45 UTC"
}
```

#### Response — 200 OK (invalid / not found)
```json
{
  "valid": false,
  "reason": "Worker not found",
  "worker_data": null
}
```

> Note: `/verify` always returns HTTP 200. The `valid` boolean carries the actual result. It does not return 404 for missing workers — callers must check `valid`.

#### Fraud Detection Logic

Cross-checks `experience_years` against employer reviews and MCQ scores:

| Source | Flag condition |
|---|---|
| Text review | `skill_level == "beginner"` AND `experience_years >= 5` |
| Text review | `rating <= 2` AND `experience_years >= 7` |
| MCQ review | `q1_satisfaction <= 2` AND `experience_years >= 5` |
| MCQ review | `q4_skill_accuracy <= 2` (any experience) |

`fraud_risk` classification:
- `"low"` — 0 flags
- `"medium"` — 1–2 flags
- `"high"` — 3+ flags

#### Trust Score at Verify Time

Trust is **always recalculated live** using `_recency_weighted_trust()` from `employer_mcq.py`:

```
weight per MCQ  = 1 / (days_since_submission + 1)
mcq_score       = ((q1/5 * 100) + (q4/5 * 100)) / 2 + (10 if rehire else 0), capped at 100
employer_score  = weighted_average(all mcq_scores)
trust_score     = (ai_validation_score × 0.30) + (employer_score × 0.70)
```

If no MCQ reviews exist: `trust_score = ai_validation_score`.

---

### GET `/worker/{worker_id}`

Public profile fetch by `worker_id`. Used by the frontend after interview to reload the passport without re-scanning.

#### Path Parameter
| Param | Type | Notes |
|---|---|---|
| `worker_id` | string | Permanent UUID |

#### Response — 200 OK
```json
{
  "worker_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "name": "Raju Kumar",
  "skills": ["plastering", "painting"],
  "nsqf_levels": [4, 3],
  "experience_years": 5,
  "trust_score": 76.43,
  "ai_validation_score": 82.5,
  "interview_completed": true,
  "qr_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "member_since": "Jun 2026"
}
```

#### Response — 404
```json
{ "detail": "Worker not found" }
```

---

## 4. Trust & Reviews

**File:** `trust.py`  
Free-text employer reviews and standalone trust/fraud utilities. The primary review system is the structured MCQ (`employer_mcq.py` in Track A) — these endpoints supplement it.

---

### POST `/add-review`

Submits a free-text employer review for a worker.

#### Request Body
```json
{
  "worker_name": "Raju Kumar",
  "rating": 4,
  "feedback": "Very reliable, good plastering work",
  "skill_level": "intermediate",
  "claimed_experience_years": 5
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `worker_name` | string | Yes | Must match name in `workers` table |
| `rating` | int | Yes | 1–5 |
| `feedback` | string | Yes | Free text |
| `skill_level` | string | Yes | `"beginner"` / `"intermediate"` / `"expert"` |
| `claimed_experience_years` | int | Yes | Used in fraud check cross-reference |

#### Response — 200 OK
```json
{ "message": "Review added", "worker": "Raju Kumar" }
```

---

### POST `/trust-score`

Calculates a blended trust score from AI score, employer reviews, identity score, and profile completeness.

> Note: This is a utility endpoint. The live trust score shown on `/verify` uses the MCQ-based recency-weighted formula in `employer_mcq.py` instead.

#### Request Body
```json
{
  "worker_name": "Raju Kumar",
  "ai_validation_score": 82.5,
  "identity_score": 75.0,
  "profile_completeness": 90.0
}
```

#### Response — 200 OK
```json
{
  "worker_name": "Raju Kumar",
  "trust_score": 74.25,
  "employer_reviews_count": 2,
  "employer_score": 80.0
}
```

Trust formula (text-review based):
```
trust = (ai_score × 0.30) + (employer_score × 0.40) + (identity_score × 0.20) + (profile_completeness × 0.10)
```

---

### POST `/fraud-check`

Standalone fraud check based on free-text reviews.

#### Request Body
```json
{
  "worker_name": "Raju Kumar",
  "claimed_experience_years": 8
}
```

#### Response — 200 OK
```json
{
  "fraud_risk": "low",
  "reason": "No inconsistencies found"
}
```

```json
{
  "fraud_risk": "high",
  "flags": [
    "Claims 8 years but rated beginner by employer",
    "Low rating (2/5) despite high experience claim"
  ]
}
```

---

### GET `/stats`

Platform-wide statistics. Shown on `stats.html` and the landing page.

#### Response — 200 OK
```json
{
  "total_reviews": 12,
  "total_verifications": 34,
  "fraud_cases_detected": 2,
  "average_employer_rating": 3.75,
  "platform": "NEEV Skill Passport",
  "status": "live"
}
```

---

## 5. Passport PDF

**File:** `passport.py`  
Generates a downloadable A4 PDF passport using ReportLab.

---

### POST `/generate-passport`

Returns a streaming PDF response — browser downloads it directly.

#### Request Body
```json
{
  "worker_name": "Raju Kumar",
  "skills": ["plastering", "painting"],
  "nsqf_levels": [4, 3],
  "experience_years": 5,
  "ai_validation_score": 82.5
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `worker_name` | string | Yes | Used to fetch reviews from DB |
| `skills` | list[string] | Yes | |
| `nsqf_levels` | list[int] | Yes | |
| `experience_years` | int | Yes | |
| `ai_validation_score` | float | No | Defaults to `70.0` |

#### Response — 200 OK
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename={worker_name}_passport.pdf`
- Body: streaming PDF

#### PDF Contents
- Header: NEEV Skill Passport + "National Electronic Evidence of Vocation"
- Worker info table: name, experience, trust score, review count, verification status
- Skills table: skill name · NSQF level · "✅ Verified" per row
- Employer reviews table (if any): rating · skill level · feedback
- Footer: first 32 chars of QR hash + verification URL

#### Trust Score in PDF
If text reviews exist:
```
trust = (ai_score × 0.30) + (employer_avg × 0.40) + (75.0 × 0.20) + (60.0 × 0.10)
```
If no reviews: `trust = ai_validation_score`

> Note: The PDF uses a separate QR (embedding `{data, hash}` JSON) for visual authenticity. The primary QR in `credential.py` encodes only the `worker_id`.

---

## 6. Community Endorsements

**File:** `community.py`  
Peer vouches from contractors, supervisors, co-workers, and clients.

---

### POST `/community-verify`

Submits a community endorsement for a worker.

#### Request Body
```json
{
  "worker_name": "Raju Kumar",
  "endorser_name": "Suresh Contractor",
  "endorser_role": "contractor",
  "relationship_duration": "2 years",
  "comment": "Raju ne mere 3 sites pe wiring ka kaam kiya, bahut reliable hai"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `worker_name` | string | Yes | Case-insensitive match on lookup |
| `endorser_name` | string | Yes | |
| `endorser_role` | string | Yes | `contractor` / `supervisor` / `co-worker` / `client` |
| `relationship_duration` | string | Yes | Free text, e.g. `"2 years"` |
| `comment` | string | Yes | |

#### Response — 200 OK
```json
{
  "message": "Endorsement added",
  "worker": "Raju Kumar",
  "endorsed_by": "Suresh Contractor"
}
```

---

### GET `/endorsements/{worker_name}`

Fetches all endorsements for a worker. Case-insensitive match.

#### Response — 200 OK
```json
{
  "worker_name": "Raju Kumar",
  "endorsement_count": 2,
  "endorsements": [
    {
      "endorser_name": "Suresh Contractor",
      "endorser_role": "contractor",
      "relationship_duration": "2 years",
      "comment": "Bahut reliable hai"
    }
  ]
}
```

---

## 7. Database Schema

**File:** `database.py`  
SQLite (`neev.db`) via SQLAlchemy ORM. All tables are auto-created on startup via `Base.metadata.create_all(engine)`. Schema migrations are handled by `migrate.py`.

---

### `workers`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `worker_id` | String UNIQUE | UUID — goes in QR, never changes |
| `name` | String UNIQUE | Indexed |
| `skills` | String | JSON-encoded list, e.g. `'["plastering", "painting"]'` |
| `nsqf_levels` | String | JSON-encoded list, e.g. `'[4, 3]'` |
| `experience_years` | Integer | Default `0` |
| `trust_score` | Float | Default `0.0`. Updated by `/employer-mcq`. |
| `ai_validation_score` | Float | Default `0.0`. Set by `/complete-interview`. |
| `qr_base64` | Text | Stored once on creation, never regenerated |
| `interview_completed` | Boolean | Default `False`. Gate for passport display. |
| `created_at` | DateTime | UTC |
| `updated_at` | DateTime | UTC, auto-updates on row change |

---

### `employer_mcqs`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `worker_name` | String | Indexed |
| `employer_name` | String | |
| `q1_satisfaction` | Integer | 1–5: overall satisfaction |
| `q2_unexpected` | String | Free text: how unexpected situations were handled |
| `q3_would_rehire` | Boolean | |
| `q4_skill_accuracy` | Integer | 1–5: did skills match what was claimed |
| `created_at` | DateTime | Used for recency weighting |

---

### `verifications`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `worker_name` | String | Indexed |
| `worker_id` | String | Indexed — stable reference even if name changes |
| `verified_at` | DateTime | Logged on every `/verify` call |

---

### `endorsements`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `worker_name` | String | Indexed |
| `endorser_name` | String | |
| `endorser_role` | String | |
| `relationship_duration` | String | |
| `comment` | String | |
| `created_at` | DateTime | |

---

### `reviews`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `worker_name` | String | Indexed |
| `rating` | Integer | 1–5 |
| `feedback` | String | |
| `skill_level` | String | `beginner` / `intermediate` / `expert` |
| `claimed_experience_years` | Integer | Used in fraud detection |
| `created_at` | DateTime | |

---

### `auth_users`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `name` | String | |
| `email` | String UNIQUE | Indexed |
| `password_hash` | String | SHA256 of plaintext password |
| `role` | String | `"worker"` or `"employer"` |
| `created_at` | DateTime | |

---

## 8. Hashing — Security Model

**File:** `hasher.py`

```python
def hash_dict(data):
    canonical_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical_str.encode()).hexdigest()
```

- `sort_keys=True` ensures field order never affects the hash
- Used by `passport.py` to embed a tamper-detection hash in the PDF QR
- The primary QR (from `credential.py`) does **not** use this hash — it encodes only the `worker_id` UUID directly
- Passwords in `auth.py` also use `hashlib.sha256` (separate, on the raw string)

---

## 9. Typical Flows

### Worker onboarding (full)
```
POST /signup                     →  token + user
POST /process  (Track A)         →  transcript + skills + QR draft
POST /generate-credential        →  worker_id + QR (permanent)
POST /generate-question          →  interview question
POST /validate-answer            →  confidence_score
POST /complete-interview         →  interview_completed = true
GET  /worker/{worker_id}         →  full profile for passport display
```

### Employer verifying a worker
```
jsQR (client-side)               →  extracts worker_id from QR image
POST /verify                     →  full profile + trust score + fraud check
POST /employer-mcq  (Track A)    →  submit review, trust score updated immediately
POST /community-verify           →  optional endorsement
```

### Worker updating skills later
```
POST /update-skills              →  new skills in DB, QR unchanged
POST /generate-question          →  new interview question for new skill
POST /validate-answer            →  new confidence score
POST /complete-interview         →  ai_score updated
```

---

## Environment Variables Required

```
GROQ_API_KEY=your_groq_key_here
```

Add to `Backend/.env`. Never push to GitHub.