# NEEV — नींव
### A Voice-First Verifiable Skill Passport for Bharat's Workforce

> **"Where Skills Become Opportunity."**

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Theme](https://img.shields.io/badge/Theme-ROZGAAR%20%7C%20Build%20For%20Good%202026-blue)
![Language](https://img.shields.io/badge/Languages-Hindi%20%2B%20Hinglish-green)

---

## 🔗 Quick Links

| Resource | Link |
|---|---|
| 🎥 Demo Video | `[Coming Soon]` |
| 🌐 Live Prototype | https://neev-1.onrender.com |
| 📊 Presentation | `[Coming Soon]` |

---

## 📌 The Problem

**92% of India's workforce — over 450 million people — operates in the informal economy.**

A daily wage worker, ITI graduate, electrician, plumber, carpenter, or domestic helper may have years of practical experience but possesses none of the following:

- Formal certification
- A written or digital resume
- Verifiable work records
- Any trusted proof of skill

The result: workers cannot prove what they know. Employers cannot trust what they cannot verify. Opportunity is lost on both sides — not due to lack of skill, but lack of infrastructure to recognize it.

---

## 💡 Solution — NEEV

NEEV is a **voice-first digital skill passport** that converts a worker's spoken experience into a cryptographically verifiable digital credential — in their own language, without requiring literacy or a smartphone with high specs.

A worker speaks. NEEV listens, extracts, maps, and certifies.

---

## ⚙️ Core Features

### 🎙️ Voice-First Skill Assessment
- Hindi and Hinglish support via Groq Whisper (whisper-large-v3)
- Conversational interface — no forms, no typing, no resume
- Accessible to users with zero digital literacy

### 🧠 AI-Based Skill Extraction
- Voice → Text via Groq Whisper API
- LLaMA 3.3-70b extracts occupational skills, years of experience, and confidence level from natural speech
- Generates a structured skill profile automatically from conversation

### 📊 NSQF Skill Mapping
- Extracted skills mapped to **National Skills Qualification Framework (NSQF)** levels 1–8
- Covers 40+ occupations across 10 sectors (Construction, Transportation, Hospitality, Apparel, Agriculture, Security, Domestic Work, Logistics, Electronics, Beauty & Wellness)
- Aligned with Skill India Mission and NEP 2020 RPL mandates

### 🤖 AI Skill Interview (Mandatory Gate)
- Worker picks a skill; LLaMA generates a real-world scenario question in Hindi or English
- Worker answers by voice; Whisper transcribes, LLaMA evaluates and returns a confidence score (0–100)
- Credential is only unlocked after the interview is completed — no unverified passports are issued

### 🔐 Verifiable Digital Credential
- QR encodes only the permanent `worker_id` (UUID) — skills can be updated without ever changing the QR
- SHA256 hash ensures tamper-resistance on the credential payload
- Shareable via screenshot, download, or printed QR
- Downloadable PDF passport via ReportLab

### 📈 Trust Score System
- **AI interview score** (30%) + **employer MCQ score** (70%) = final trust score
- Employer MCQ reviews are **recency-weighted** — recent reviews carry more weight than old ones
- Trust score is recalculated live every time a QR is scanned, never stale

### 🏢 Employer Verification Portal
- Employers scan QR via camera or upload a QR image — `jsQR` decodes it client-side
- Full worker profile fetched from DB: skills, NSQF levels, trust score, fraud risk, employer reviews, community endorsements
- Fraud detection flags inconsistencies (e.g. claims 7 years but rated beginner by employers)
- Employers can submit structured 4-question MCQ reviews post-hiring

### 🤝 Community Endorsements
- Contractors, supervisors, co-workers, and clients can vouch for a worker
- Endorsements are surfaced on the employer verification page

---

## 🏗️ System Architecture

```
Worker Voice Input (Hindi / Hinglish)
        ↓
Speech Recognition — Groq Whisper (whisper-large-v3)
        ↓
NLP Pipeline — Skill Extraction + Years + Confidence (LLaMA 3.3-70b via Groq)
        ↓
NSQF Mapping Layer — nsqf_map.json (40+ occupations, 10 sectors)
        ↓
Credential Generation — SHA256 signed payload
        ↓
QR Code Generation — encodes permanent worker_id UUID (base64 PNG)
        ↓
AI Skill Interview Gate — LLaMA question → voice answer → confidence score
        ↓
Skill Passport unlocked — Trust score = AI (30%) + Employer MCQ (70%)
        ↓
Employer Verification Portal — QR scan → live profile + fraud detection
```

---

## 🔄 Complete Workflow

### 1 · Authentication

```
signup.html / login.html
        ↓
POST /signup · POST /login  (auth.py)
        ↓
Token stored in sessionStorage
        ↓
Role-based redirect:
  worker   → Worker/record.html
  employer → Employer/verify.html
```

---

### 2 · Worker: Voice → Passport

```
Worker/record.html
  └── Enter name + record voice in Hindi (MediaRecorder API)
        ↓
POST /process  (process.py — master endpoint)
  ├── Step 1: Groq Whisper (whisper-large-v3)  →  Hindi transcript
  ├── Step 2: LLaMA 3.3-70b  →  skills + years + confidence level
  ├── Step 3: nsqf_map.json lookup  →  NSQF level + sector per skill
  └── Step 4: SHA256 hash + qrcode library  →  QR base64 PNG
        ↓
Worker/confirm.html
  └── Worker reviews extracted skills, removes incorrect ones
        ↓
POST /generate-credential  (credential.py)
  └── New worker: creates DB row, generates permanent UUID, stores QR
  └── Existing worker: returns same stored QR (never regenerated)
        ↓
Worker/credential.html
  └── Interview gate check (interview_completed flag)
        ├── false  →  Shows gate, redirects to interview.html
        └── true   →  Shows passport: QR + skills + trust score
```

---

### 3 · AI Skill Interview

```
Worker/interview.html
  └── Worker types skill name + selects language (Hindi / English)
        ↓
POST /generate-question  (validate.py)
  └── LLaMA generates a practical scenario-based question
        ↓
Worker records voice answer (MediaRecorder → webm)
        ↓
POST /validate-answer  (validate.py)
  ├── Groq Whisper transcribes the answer
  └── LLaMA evaluates: confidence_score (0–100), verified (true/false), level, feedback
        ↓
POST /complete-interview  (credential.py)
  └── ai_validation_score saved to DB, interview_completed = true
        ↓
Redirects back to credential.html → passport now unlocked
```

---

### 4 · Employer: Verify a Worker

```
Employer/verify.html
  └── Scan QR via camera  OR  upload QR image
        ↓
jsQR (client-side) decodes QR → extracts worker_id UUID
        ↓
POST /verify  (verify.py)
  ├── Fetches worker profile fresh from DB
  ├── Fetches employer MCQ reviews + text reviews
  ├── Fetches community endorsements
  ├── Recalculates trust score live (recency-weighted)
  └── Runs fraud detection (cross-checks skill claims vs employer ratings)
        ↓
Displays on verify page:
  ├── valid / invalid credential status
  ├── Worker name + skills + NSQF levels
  ├── Trust score / 100
  ├── Fraud risk: low / medium / high + specific flags
  ├── Employer MCQ reviews + text reviews
  └── Community endorsements
```

---

### 5 · Employer: Submit Review

```
Employer/review.html
  ├── Q1: Overall satisfaction (1–5 stars)
  ├── Q2: Handling of unexpected situations (MCQ)
  ├── Q3: Would you rehire? (Yes/No)
  └── Q4: Skill accuracy vs claims (1–5 stars)
        ↓
POST /employer-mcq  (employer_mcq.py)
  └── Trust score recalculated:
        employer_score = recency_weighted_avg(q1, q4, rehire_bonus)
        trust = (ai_score × 0.30) + (employer_score × 0.70)
        capped at 100, saved to DB immediately
```

---

### 6 · Community Endorsements

```
Employer/endorse.html
  └── Endorser fills: worker name, their name, role, duration, comment
        ↓
POST /community-verify  (community.py)
  └── Saved to endorsements table, surfaced on verify page
```

---

### 7 · Skill Updates + PDF Passport

```
Worker/credential.html  →  Add new skills (comma-separated)
        ↓
POST /update-skills  (credential.py)
  └── DB updated with new skills + NSQF levels
  └── QR code stays the same — permanent, never regenerated

GET /generate-passport  (passport.py)
  └── Generates downloadable PDF with:
        worker info, skills table, trust score, employer reviews, QR hash footer
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | FastAPI, Python |
| Database | SQLite (neev.db) via SQLAlchemy ORM |
| Speech Recognition | Groq Whisper (whisper-large-v3) |
| Skill Extraction | LLaMA 3.3-70b via Groq API |
| AI Interviewer | LLaMA 3.3-70b via Groq API |
| NSQF Mapping | Custom JSON classification (40+ occupations) |
| Credential Security | SHA256 cryptographic hashing |
| QR Generation | Python `qrcode` library |
| QR Scanning | `jsQR` (client-side, no app needed) |
| PDF Generation | ReportLab |
| Deployment | Render.com |

---

## 📁 Project Structure

```
NEEV/
├── Backend/
│   ├── main.py                      # Entry point — all 11 routers registered
│   ├── migrate.py                   # Safe DB migration script
│   ├── requirements.txt
│   ├── render.yaml                  # Render deployment config
│   ├── .env                         # API keys (never pushed to GitHub)
│   │
│   ├── Aayush/                      # Track A — Voice & Skill Extraction
│   │   ├── transcribe.py            # POST /transcribe
│   │   ├── extract_skills.py        # POST /extract-skills
│   │   ├── process.py               # POST /process (master endpoint)
│   │   ├── validate.py              # POST /generate-question · POST /validate-answer
│   │   ├── employer_mcq.py          # POST /employer-mcq · GET /employer-mcqs/:name
│   │   ├── nsqf_map.json            # NSQF skill mapping (40+ occupations)
│   │   └── NLP_PIPELINE.md          # Track A documentation
│   │
│   └── Nikhil/                      # Track B — Credential & Verification
│       ├── database.py              # SQLAlchemy models + DB setup
│       ├── hasher.py                # SHA256 hashing helper
│       ├── credential.py            # POST /generate-credential · /update-skills · /complete-interview
│       ├── verify.py                # POST /verify · GET /worker/:id
│       ├── trust.py                 # POST /add-review · /trust-score · /fraud-check · GET /stats
│       ├── passport.py              # POST /generate-passport (PDF download)
│       ├── community.py             # POST /community-verify · GET /endorsements/:name
│       ├── auth.py                  # POST /signup · /login · /logout · GET /me
│       └── API_CONTRACT.md          # Track B documentation
│
└── Frontend/
    ├── index.html                   # Landing page with live stats
    ├── login.html                   # Auth: login
    ├── signup.html                  # Auth: signup (worker / employer role)
    ├── stats.html                   # Platform stats dashboard
    ├── css/style.css                # Global design system
    ├── js/api.js                    # Shared API base URL + neevFetch helper
    ├── Worker/
    │   ├── record.html              # Voice recording → POST /process
    │   ├── confirm.html             # Skill confirmation + removal
    │   ├── credential.html          # Passport display + interview gate + skill update
    │   └── interview.html           # AI skill interview flow
    └── Employer/
        ├── verify.html              # QR scanner (camera + upload) → POST /verify
        ├── review.html              # 4-question MCQ employer review
        └── endorse.html             # Community endorsement form + lookup
```

---

## 🔌 API Endpoints


### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register new worker or employer account |
| POST | `/login` | Login and receive session token |
| POST | `/logout` | Invalidate token |
| GET | `/me` | Get current user info from token |

### Track A — Voice & Skill Extraction
| Method | Endpoint | Description |
|---|---|---|
| POST | `/transcribe` | Audio file → Hindi/Hinglish transcript |
| POST | `/extract-skills` | Transcript → skill list + NSQF mapping |
| POST | `/process` | Audio + name → full credential + QR (master endpoint) |
| POST | `/generate-question` | Skill name → AI interview question (Hindi/English) |
| POST | `/validate-answer` | Audio answer → confidence score + verified flag |
| POST | `/employer-mcq` | Submit 4-question employer MCQ review |
| GET | `/employer-mcqs/:worker_name` | Fetch all MCQ reviews for a worker |

### Track B — Credential & Verification
| Method | Endpoint | Description |
|---|---|---|
| POST | `/generate-credential` | Skills → permanent QR + worker_id (idempotent) |
| POST | `/update-skills` | Update skills in DB — QR unchanged |
| POST | `/complete-interview` | Mark interview done, save AI score |
| POST | `/verify` | worker_id → full verified profile + trust score + fraud check |
| GET | `/worker/:worker_id` | Fetch public worker profile by ID |
| POST | `/add-review` | Submit text employer review |
| POST | `/trust-score` | Calculate blended trust score |
| POST | `/fraud-check` | Check for skill claim inconsistencies |
| POST | `/generate-passport` | Generate downloadable PDF passport |
| POST | `/community-verify` | Submit community endorsement |
| GET | `/endorsements/:worker_name` | Fetch all endorsements for a worker |
| GET | `/stats` | Platform-wide stats (reviews, verifications, fraud cases) |

---

## 🗃️ Database Schema

| Table | Key Columns | Purpose |
|---|---|---|
| `workers` | `worker_id` (UUID), `name`, `skills` (JSON), `nsqf_levels` (JSON), `trust_score`, `ai_validation_score`, `qr_base64`, `interview_completed` | Core worker profile |
| `employer_mcqs` | `worker_name`, `employer_name`, `q1_satisfaction`, `q2_unexpected`, `q3_would_rehire`, `q4_skill_accuracy`, `created_at` | Structured employer reviews with recency weighting |
| `verifications` | `worker_id`, `worker_name`, `verified_at` | Log of every QR scan |
| `endorsements` | `worker_name`, `endorser_name`, `endorser_role`, `relationship_duration`, `comment` | Community vouches |
| `reviews` | `worker_name`, `rating`, `feedback`, `skill_level` | Free-text employer reviews |
| `auth_users` | `email`, `password_hash`, `role` | Auth accounts (worker / employer) |

---

## 📊 Impact Potential

| Dimension | Metric |
|---|---|
| Target Users | 450M+ informal workers in India |
| Language Support | Hindi + Hinglish at launch |
| Credential Standard | SHA256 tamper-proof + NSQF aligned |
| NSQF Coverage | 40+ occupations across 10 sectors |
| Policy Alignment | Skill India Mission, NEP 2020 RPL, NSQF Framework |

**For Workers:** Portable skill identity → faster hiring → higher income access

**For Employers:** Verified candidate pool with trust scores → reduced screening cost → lower hiring risk

**For the Ecosystem:** Workforce formalization → data layer for government skilling programs

---

## 🗺️ Roadmap

| Phase | Milestone |
|---|---|
| **Phase 1** *(Current)* | Voice → skill extraction → AI interview → QR credential + trust score MVP |
| **Phase 2** | Bhashini integration, 12-language support |
| **Phase 3** | Skill India / NSDC API integration, RPL certification pathway |
| **Phase 4** | AI job matching, employer endorsements, trust scoring |
| **Phase 5** | Government & NGO partnerships, digital employment history ledger |

---

## 👥 Team SANKALP

> Building the foundation for a future where every skill is recognized, verified, and valued.

| Name | Role |
|---|---|
| Aayush | Voice & Skill Extraction, AI Interview, Employer MCQ (Backend Track A) |
| Nikhil | Credential, Verification, Trust Score, Auth, PDF Passport (Backend Track B) |
| Laiba | Frontend & UI Development |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/nikhil11690/NEEV.git
cd NEEV

# Backend setup
cd Backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

# Run DB migrations (safe to re-run)
python migrate.py

# Start backend
uvicorn main:app --reload

# Frontend setup
# Open Frontend/index.html with VS Code Live Server
# OR serve with: python -m http.server 5500 (from Frontend/)
```

> ⚠️ Environment variables required: Create a `.env` file inside `Backend/` with:
> ```
> GROQ_API_KEY=your_groq_key_here
> ```

---

*Built for Build For Good 2026 · A Sama Initiative · Theme: ROZGAAR*
