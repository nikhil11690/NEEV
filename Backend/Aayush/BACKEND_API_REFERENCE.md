# NEEV Backend — API Reference

Track owner: Aayush (voice pipeline, skill extraction, employer MCQ)  
Base URL (local dev): `http://127.0.0.1:8000`  
Environment: `GROQ_API_KEY=your_groq_key_here`

---

## Architecture Overview

NEEV's backend has **5 endpoints** across 4 modules. `/process` is the master pipeline for the frontend demo; the other endpoints are modular and can be called independently.

```
┌─────────────────────────────────────────────────────────┐
│                    NEEV Backend API                     │
├─────────────────────────────────────────────────────────┤
│  VOICE PIPELINE (Aayush)                                │
│  POST /transcribe        → audio → Hindi transcript     │
│  POST /extract-skills    → transcript → skills + NSQF   │
│  POST /process           → audio → full credential + QR │
├─────────────────────────────────────────────────────────┤
│  AI VALIDATION (Aayush)                                 │
│  POST /generate-question → skill → interview question   │
│  POST /validate-answer   → audio answer → AI score      │
├─────────────────────────────────────────────────────────┤
│  EMPLOYER REVIEW (Aayush)                               │
│  POST /employer-mcq      → MCQ → trust score update     │
│  GET  /employer-mcqs/{worker_name} → fetch all reviews  │
└─────────────────────────────────────────────────────────┘
```

---

## Master Pipeline — `/process`

The full credential generation flow in a single call. This is what the frontend uses for the demo.

```
Audio + Worker Name
       ↓
  Groq Whisper (whisper-large-v3)
  audio → Hindi/Hinglish transcript
       ↓
  LLaMA 3.3-70b
  transcript → [{skill, years, confidence}]
       ↓
  NSQF Mapper (nsqf_map.json)
  skills → levels + sectors
       ↓
  SHA256 Hasher (Nikhil/hasher.py)
  payload → tamper-proof hash
       ↓
  QR Generator (qrcode lib)
  payload + hash → base64 PNG
       ↓
  Single JSON Response
```

**`POST /process`**

Request — `multipart/form-data`

| Field | Type | Notes |
|---|---|---|
| `name` | string (query param) | Worker's full name |
| `audio` | file | wav, mp3, webm, mp4, ogg |

```bash
curl -X POST "http://127.0.0.1:8000/process?name=Raju" \
  -F "audio=@recording.mp3;type=audio/mpeg"
```

Response — 200 OK

```json
{
  "success": true,
  "name": "Raju",
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ",
  "skills": ["plastering", "painting", "driving"],
  "years": [5, 5, 0],
  "confidence": ["high", "high", "medium"],
  "nsqf_mapping": [
    { "skill": "plastering", "nsqf_level": 4, "sector": "Construction" },
    { "skill": "painting",   "nsqf_level": 3, "sector": "Construction" },
    { "skill": "driving",    "nsqf_level": 3, "sector": "Transportation" }
  ],
  "hash": "63795c4f21e80d2cc57401812de7ec351c14d54a730a1cc9d250277a6b1d5087",
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUg..."
}
```

> **Note:** The old API reference omitted `years` and `confidence` from the response schema. Both are now returned.

**QR payload** (what a scanner reads):

```json
{
  "data": { "name": "Raju", "skills": ["plastering", "painting", "driving"], "nsqf_levels": [4, 3, 3] },
  "hash": "63795c4f..."
}
```

Render the QR in HTML: `<img src="data:image/png;base64,{qr_code_base64}" />`

---

## Voice Module

### `POST /transcribe`
Source: `Aayush/transcribe.py`

Transcribes an audio file using Groq Whisper. Language is auto-detected (no `language` param — Whisper detects it).

Request — `multipart/form-data`

| Field | Type | Notes |
|---|---|---|
| `audio` | file | wav, mp3, webm, mp4, ogg |

Response:
```json
{ "success": true, "transcript": "मैं 8 साल से plastering करता हूँ" }
```

---

### `POST /extract-skills`
Source: `Aayush/extract_skills.py`

Runs LLaMA skill extraction + NSQF mapping on a raw transcript string. Use this if you already have a transcript and don't need Whisper.

Request — `application/json`
```json
{ "transcript": "मैं 8 साल से plastering करता हूँ, painting भी आती है" }
```

Response:
```json
{
  "success": true,
  "transcript": "...",
  "skills": ["plastering", "painting"],
  "years": [8, 0],
  "confidence": ["high", "medium"],
  "nsqf_mapping": [
    { "skill": "plastering", "nsqf_level": 4, "sector": "Construction" },
    { "skill": "painting",   "nsqf_level": 3, "sector": "Construction" }
  ]
}
```

**NSQF matching logic:** exact match → partial substring match → fallback to `{ nsqf_level: "N/A", sector: "General" }`.

---

## AI Validation Module

### `POST /generate-question`
Source: `Aayush/validate.py`

Generates one practical scenario-based voice interview question for a given skill, in Hindi or English.

Request — `application/json`
```json
{ "skill": "plastering", "language": "hi" }
```

Response:
```json
{
  "success": true,
  "skill": "plastering",
  "question": "अगर दीवार पर plastering करते वक्त crack आ जाए, तो आप क्या करेंगे?",
  "language": "hi"
}
```

---

### `POST /validate-answer`
Source: `Aayush/validate.py`

Worker records a voice answer → Whisper transcribes it → LLaMA scores it against the question. Returns a 0–100 AI confidence score, verification status, feedback, and skill level.

Request — `multipart/form-data`

| Field | Type | Notes |
|---|---|---|
| `skill` | string (query param) | Skill being tested |
| `question` | string (query param) | The question that was asked |
| `audio` | file | Worker's recorded answer |

Response:
```json
{
  "success": true,
  "skill": "plastering",
  "question": "...",
  "worker_answer": "पहले crack को साफ करके...",
  "confidence_score": 82,
  "verified": true,
  "feedback": "Worker showed good practical knowledge",
  "level": "intermediate"
}
```

Verification rule: `verified = true` if `confidence_score >= 60`.  
`ai_validation_score` from this endpoint feeds into the trust score formula in `/employer-mcq`.

---

## Employer Review Module

### `POST /employer-mcq`
Source: `Aayush/employer_mcq.py`

Employer submits 4 MCQ answers after hiring a worker. Trust score is recalculated immediately with **recency weighting** — newer reviews carry more weight.

**Trust Score Formula:**
```
weight per MCQ   = 1 / (days_since_submission + 1)
mcq_score        = ((q1_satisfaction/5 + q4_skill_accuracy/5) / 2 × 100) + (10 if rehire else 0), capped at 100
employer_score   = weighted average of all MCQ scores
final_trust      = (ai_validation_score × 0.30) + (employer_score × 0.70)
```

Request — `application/json`
```json
{
  "worker_name": "Raju",
  "employer_name": "Sharma Construction",
  "q1_satisfaction": 4,
  "q2_unexpected": "He handled a waterproofing issue on his own without asking",
  "q3_would_rehire": true,
  "q4_skill_accuracy": 5
}
```

Validation: `q1_satisfaction` and `q4_skill_accuracy` must be 1–5 (returns 400 otherwise).

Response:
```json
{
  "success": true,
  "worker_name": "Raju",
  "new_trust_score": 87.5,
  "total_mcq_reviews": 3,
  "message": "Review submitted and trust score updated."
}
```

---

### `GET /employer-mcqs/{worker_name}`
Source: `Aayush/employer_mcq.py`

Fetch all MCQ reviews for a worker (used on the verify/profile page). Returns newest first.

```bash
curl http://127.0.0.1:8000/employer-mcqs/Raju
```

Response:
```json
{
  "worker_name": "Raju",
  "total": 3,
  "reviews": [
    {
      "employer": "Sharma Construction",
      "satisfaction": 4,
      "skill_accuracy": 5,
      "would_rehire": true,
      "unexpected_handling": "He handled a waterproofing issue on his own",
      "date": "Jun 2026"
    }
  ]
}
```

---

## Tamper Detection

The SHA256 hash in `/process` is computed over `{ name, skills, nsqf_levels }`. If the QR is scanned and any field is modified, `/verify` recomputes the hash and returns `valid: false`. This is the cryptographic anchor of the credential system.

---

## NSQF Map

`Aayush/nsqf_map.json` — 40+ skills across 12 sectors (Construction, Transportation, Hospitality, Apparel, Agriculture, Security, Domestic Work, Logistics, IT, Electronics, Beauty & Wellness, Handicraft). NSQF levels range from 1 (unskilled) to 4 (semi-skilled specialist).

---

## Error Reference

| Code | Endpoint | Reason |
|---|---|---|
| 400 | `/process`, `/transcribe`, `/validate-answer` | Invalid audio file type |
| 400 | `/employer-mcq` | q1/q4 out of 1–5 range |
| 404 | `/employer-mcq` | Worker not found in DB |
| 500 | any | Whisper transcription failed |
| 500 | any | LLaMA response could not be parsed as JSON |

---

## Module Map

| File | Owner | Endpoints |
|---|---|---|
| `Aayush/transcribe.py` | Aayush | `POST /transcribe` |
| `Aayush/extract_skills.py` | Aayush | `POST /extract-skills` |
| `Aayush/process.py` | Aayush | `POST /process` |
| `Aayush/validate.py` | Aayush | `POST /generate-question`, `POST /validate-answer` |
| `Aayush/employer_mcq.py` | Aayush | `POST /employer-mcq`, `GET /employer-mcqs/{name}` |
| `Aayush/nsqf_map.json` | Aayush | shared by extract-skills + process |
| `Nikhil/hasher.py` | Nikhil | used by process |
| `Nikhil/database.py` | Nikhil | used by employer-mcq |