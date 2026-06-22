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
| 🌐 Live Prototype | `[Coming Soon]` |
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
- LLaMA 3.3-70b extracts occupational skills from natural speech
- Generates a structured skill profile automatically from conversation

### 📊 NSQF Skill Mapping
- Extracted skills mapped to **National Skills Qualification Framework (NSQF)** levels 1–8
- Produces government-recognized, standardized skill records
- Aligned with Skill India Mission and NEP 2020 RPL mandates

### 🔐 Verifiable Digital Credential
- QR-linked skill passport generated per worker
- SHA256 hash ensures tamper-resistance — any modification to worker data invalidates the credential
- Shareable via screenshot, download, or printed QR

### 🏢 Employer Verification Portal
- Employers scan QR → view verified skills, NSQF level, and validity status
- No app installation required on employer side (web-based)
- Reduces hiring friction for blue-collar and skilled-trade roles

---

## 🏗️ System Architecture

```
Worker Voice Input (Hindi / Hinglish)
        ↓
Speech Recognition — Groq Whisper (whisper-large-v3)
        ↓
NLP Pipeline — Skill Extraction (LLaMA 3.3-70b via Groq)
        ↓
NSQF Mapping Layer — nsqf_map.json (40+ occupations)
        ↓
Credential Generation — SHA256 signed JSON payload
        ↓
QR Code Generation (base64 PNG)
        ↓
Employer Verification Portal (Web, QR Scan)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | FastAPI, Python |
| Speech Recognition | Groq Whisper (whisper-large-v3) |
| Skill Extraction | LLaMA 3.3-70b via Groq API |
| NSQF Mapping | Custom JSON classification layer |
| Credential Security | SHA256 cryptographic hashing |
| QR Generation | Python `qrcode` library |
| Deployment | Render.com |

---

## 📁 Project Structure

```
NEEV/
├── Backend/
│   ├── main.py                      # Entry point — all routers combined
│   ├── requirements.txt
│   ├── .env                         # API keys (never pushed to GitHub)
│   ├── render.yaml                  # Render deployment config
│   │
│   ├── Aayush/                      # Track A — Voice & Skill Extraction
│   │   ├── transcribe.py            # POST /transcribe
│   │   ├── extract_skills.py        # POST /extract-skills
│   │   ├── process.py               # POST /process (master endpoint)
│   │   ├── nsqf_map.json            # NSQF skill mapping data
│   │   ├── NLP_PIPELINE.md          # Track A documentation
│   │   └── PROCESS_PIPELINE.md      # /process endpoint documentation
│   │
│   └── Nikhil/                      # Track B — Credential & Verification
│       ├── hasher.py                # SHA256 hashing helper
│       ├── credential.py            # POST /generate-credential
│       ├── verify.py                # POST /verify
│       └── API_CONTRACT.md          # Track B documentation
│
└── Frontend/                        # Laiba — UI & Frontend
    ├── index.html                   # Landing page
    ├── FRONTEND.md                  # Frontend documentation
    ├── Worker/
    │   ├── record.html              # Voice recording → calls /process
    │   ├── confirm.html             # Skill confirmation
    │   └── credential.html          # QR passport display
    └── Employer/
        └── scan.html                # QR scanner → calls /verify
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/transcribe` | Audio file → Hindi transcript |
| POST | `/extract-skills` | Transcript → skill list + NSQF mapping |
| POST | `/process` | Audio + name → full credential + QR (master endpoint) |
| POST | `/generate-credential` | Skills → QR code (base64 PNG) + hash |
| POST | `/verify` | QR payload → valid/invalid + worker data |

---

## 📊 Impact Potential

| Dimension | Metric |
|---|---|
| Target Users | 450M+ informal workers in India |
| Language Support | Hindi + Hinglish at launch |
| Credential Standard | SHA256 tamper-proof + NSQF aligned |
| Policy Alignment | Skill India Mission, NEP 2020 RPL, NSQF Framework |

**For Workers:** Portable skill identity → faster hiring → higher income access

**For Employers:** Verified candidate pool → reduced screening cost → lower hiring risk

**For the Ecosystem:** Workforce formalization → data layer for government skilling programs

---

## 🗺️ Roadmap

| Phase | Milestone |
|---|---|
| **Phase 1** *(Current)* | Voice input → Skill extraction → QR credential MVP |
| **Phase 2** | Bhashini integration, 12-language support |
| **Phase 3** | Skill India / NSDC API integration, RPL certification pathway |
| **Phase 4** | AI job matching, employer endorsements, trust scoring |
| **Phase 5** | Government & NGO partnerships, digital employment history ledger |

---

## 👥 Team SANKALP

> Building the foundation for a future where every skill is recognized, verified, and valued.

| Name | Role |
|---|---|
| Aayush | Voice & Skill Extraction (Backend Track A) |
| Nikhil | Credential & Verification (Backend Track B) |
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
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
# Open Frontend/index.html with VS Code Live Server
```

> ⚠️ Environment variables required: Create a `.env` file inside `Backend/` with:
> ```
> GROQ_API_KEY=your_groq_key_here
> ```

---

*Built for Build For Good 2026 · A Sama Initiative · Theme: ROZGAAR*