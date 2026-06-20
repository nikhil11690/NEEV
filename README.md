# NEEV — नींव
### A Voice-First Verifiable Skill Passport for Bharat's Workforce

> **"Where Skills Become Opportunity."**

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Theme](https://img.shields.io/badge/Theme-ROZGAAR%20%7C%20Build%20For%20Good%202026-blue)
![Language](https://img.shields.io/badge/Languages-12%2B%20Indian%20Languages-green)

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
- Supports 12+ Indian languages via Bhashini API
- Conversational interface — no forms, no typing, no resume
- Accessible to users with zero digital literacy

### 🧠 AI-Based Skill Extraction
- Voice → Text via OpenAI Whisper / Bhashini ASR
- LLM-based NLP extracts: skills, tools, tasks, experience duration, proficiency signals
- Generates a structured work profile automatically from conversation

### 📊 NSQF Skill Mapping
- Extracted skills mapped to **National Skills Qualification Framework (NSQF)** levels 1–8
- Produces government-recognized, standardized skill records
- Aligned with Skill India Mission and NEP 2020 RPL mandates

### 🔐 Verifiable Digital Credential
- QR-linked skill passport generated per worker
- Digitally signed — tamper-resistant
- Stored on IPFS for decentralized, persistent access
- Shareable via WhatsApp, SMS, or printed QR

### 📱 Offline-First Architecture
- Core voice capture and profile generation works on 2G / no connectivity
- Auto-syncs credentials to cloud when internet is available
- Designed for Tier 3/4 India infrastructure realities

### 🏢 Employer Verification Portal
- Employers scan QR → view verified skills, NSQF level, and trust score
- No app installation required on employer side (web-based)
- Reduces hiring friction for blue-collar and skilled-trade roles

---

## 🏗️ System Architecture

```
Worker Voice Input (Hindi / Regional Language)
        ↓
Speech Recognition — Whisper API / Bhashini ASR
        ↓
NLP Pipeline — Skill Extraction (LangChain + LLM)
        ↓
NSQF Mapping Layer — Skill → Level Classification
        ↓
Credential Generation — Digitally Signed JSON-LD
        ↓
IPFS Storage + QR Code Generation
        ↓
Employer Verification Portal (Web, QR Scan)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Tailwind CSS |
| Backend | FastAPI, Python |
| Speech Recognition | OpenAI Whisper, Bhashini ASR API |
| NLP / Skill Extraction | LangChain, LLM (GPT / open-source) |
| NSQF Mapping | Custom Classification Layer |
| Database | PostgreSQL |
| Credential Storage | IPFS, Digital Signatures (W3C VC standard) |
| QR Generation | Python `qrcode` library |
| Deployment | Docker, Render / AWS |

---

## 📊 Impact Potential

| Dimension | Metric |
|---|---|
| Target Users | 450M+ informal workers in India |
| Language Coverage | 12+ Indian languages at launch |
| Connectivity Requirement | Works on 2G / offline |
| Credential Standard | W3C Verifiable Credentials + NSQF aligned |
| Policy Alignment | Skill India Mission, NEP 2020 RPL, NSQF Framework |

**For Workers:** Portable skill identity → faster hiring → higher income access → credit eligibility via income history

**For Employers:** Verified candidate pool → reduced screening cost → lower hiring risk for blue-collar roles

**For the Ecosystem:** Workforce formalization → data layer for government skilling programs → economic mobility at scale

---

## 🗺️ Roadmap

| Phase | Milestone |
|---|---|
| **Phase 1** *(Current)* | Voice input → Skill extraction → QR credential MVP |
| **Phase 2** | Bhashini full integration, 12-language support, offline sync |
| **Phase 3** | Skill India / NSDC API integration, RPL certification pathway |
| **Phase 4** | AI job matching, employer endorsements, trust scoring |
| **Phase 5** | Government & NGO partnerships, digital employment history ledger |

---

## 👥 Team SANKALP

> Building the foundation for a future where every skill is recognized, verified, and valued.

| Name | Role |
|---|---|
| Aayush | Voice & Skill Extraction |
| Nikhil | Credential & Verification |
| Laiba | Frontend & UI Development |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/[your-username]/neev.git
cd neev

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev
```

> ⚠️ Environment variables required: See `.env.example` for Bhashini API key, Whisper API key, PostgreSQL connection string, and IPFS config.

---

*Built for Build For Good 2026 · A Sama Initiative · Theme: ROZGAAR*
