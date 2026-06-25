# NEEV Backend — NLP Pipeline

Track owner: Aayush  
Files: `transcribe.py` · `extract_skills.py` · `nsqf_map.json`  
Base URL (local dev): `http://127.0.0.1:8000`

---

## Overview

This track handles everything between the worker's voice and the extracted skill list. It takes raw audio in Hindi or Hinglish, converts it to text using Groq Whisper, then uses LLaMA to extract occupational skills (with years of experience and confidence level) and maps them to government-recognized NSQF levels.

```
Audio File → /transcribe → Transcript → /extract-skills → Skills + Years + Confidence + NSQF Levels
```

These two endpoints can be called individually, or the entire pipeline can be triggered in one shot via `/process` (see PROCESS_PIPELINE.md).

---

## Models Used

| Model | Provider | Purpose |
|---|---|---|
| `whisper-large-v3` | Groq | Audio → transcript (auto-detects language) |
| `llama-3.3-70b-versatile` | Groq | Transcript → skill list + years + confidence (JSON) |

---

## 1. Transcribe Audio

Converts a Hindi or Hinglish audio file into text.

**File:** `transcribe.py`  
**Endpoint:** `POST /transcribe`

### Request
- Content-Type: `multipart/form-data`
- Field: `audio` — audio file (wav, mp3, webm, mp4, ogg)

### Example curl
```bash
curl -X POST "http://127.0.0.1:8000/transcribe" \
  -F "audio=@recording.webm;type=audio/webm"
```

### Response — 200 OK
```json
{
  "success": true,
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ"
}
```

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | Always true on 200 |
| `transcript` | string | Raw text from Whisper. May be Hindi, English, or mixed Hinglish. |

### Response — 400
```json
{ "detail": "Invalid file type. Send wav, mp3, webm, or ogg." }
```

### Response — 500
```json
{ "detail": "Groq Whisper error: ..." }
```

### Implementation Notes
- **No `language` parameter is passed** — Whisper auto-detects the language. This handles Hinglish (mixed Hindi + English) better than forcing `language="hi"`.
- Audio file is written to a temp file on disk (`temp_{filename}`), passed to Whisper, then deleted immediately in the `finally` block.
- Supported content types: `audio/wav`, `audio/mpeg`, `audio/webm`, `audio/mp4`, `audio/ogg`.

---

## 2. Extract Skills

Takes a transcript and returns occupational skills with years of experience, confidence level, and NSQF mapping.

**File:** `extract_skills.py`  
**Endpoint:** `POST /extract-skills`

### Request Body
```json
{
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ, driving भी जानता हूँ"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `transcript` | string | Yes | Raw text from `/transcribe` or typed manually |

### Response — 200 OK
```json
{
  "success": true,
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ, driving भी जानता हूँ",
  "skills": ["plastering", "painting", "driving"],
  "years": [5, 5, 0],
  "confidence": ["high", "high", "medium"],
  "nsqf_mapping": [
    { "skill": "plastering", "nsqf_level": 4, "sector": "Construction" },
    { "skill": "painting",   "nsqf_level": 3, "sector": "Construction" },
    { "skill": "driving",    "nsqf_level": 3, "sector": "Transportation" }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | Always true on 200 |
| `transcript` | string | Echoed back for reference |
| `skills` | list[string] | Skill names extracted by LLaMA, always in English |
| `years` | list[int] | Years of experience per skill. `0` if not mentioned. |
| `confidence` | list[string] | `"high"` / `"medium"` / `"low"` per skill |
| `nsqf_mapping` | list[object] | Each skill matched to NSQF level + sector |

### NSQF Mapping Object
| Field | Type | Notes |
|---|---|---|
| `skill` | string | Skill name as extracted by LLaMA |
| `nsqf_level` | int or `"N/A"` | 1 (entry) to 8 (expert). `"N/A"` if not in map. |
| `sector` | string | Industry sector. `"General"` if not in map. |

### Confidence Level Rules (from LLaMA system prompt)
| Value | Condition |
|---|---|
| `"high"` | Skill mentioned multiple times or with specific details |
| `"medium"` | Skill mentioned once clearly |
| `"low"` | Skill only briefly mentioned |

### Response — 400
```json
{ "detail": "Transcript is empty." }
```

### Response — 500
```json
{ "detail": "Skill extraction error: ..." }
{ "detail": "Could not parse skills from AI response." }
```

### Implementation Notes

**LLaMA prompt** asks for a JSON array in this format:
```json
[{"skill": "plastering", "years": 8, "confidence": "high"}, ...]
```

**Backward compatibility:** The code handles the old format where LLaMA returned a plain `["skill1", "skill2"]` array — if the first item is a string, `years` defaults to `[0, ...]` and `confidence` defaults to `["medium", ...]`.

**NSQF matching logic** (in `match_nsqf()`):
1. Direct lowercase match against `nsqf_map.json` keys
2. Partial match — checks if the map key is a substring of the skill, or vice versa
3. No match → `nsqf_level: "N/A"`, `sector: "General"` (skill still included in response)

**LLaMA temperature is set to `0.1`** — low temperature for deterministic, structured JSON output.

---

## NSQF Map

**File:** `nsqf_map.json`  
40 occupations across 10 sectors. NSQF levels range from 1 (entry-level) to 4 (skilled trade).

| Sector | Skills |
|---|---|
| Construction | plastering (4), painting (3), welding (4), carpentry (4), electrical wiring (4), plumbing (4), masonry (3) |
| Transportation | driving (3), truck driving (3), auto rickshaw driving (2) |
| Hospitality | cooking (3), food preparation (2), catering (3) |
| Facility Management | cleaning (1), housekeeping (2), sweeping (1) |
| Apparel | tailoring (3), stitching (2), embroidery (3) |
| Agriculture | farming (2), harvesting (1), irrigation (2) |
| Security | security guard (2), watchman (1) |
| Domestic Work | childcare (2), elder care (3), washing (1), babysitting (2) |
| Logistics | loading (1), unloading (1), delivery (2), packing (1) |
| Electronics | mobile repair (4), ac repair (4), refrigerator repair (4) |
| Beauty & Wellness | hair cutting (3), mehndi (2), beauty parlour (3) |
| IT | data entry (3) |
| Handicraft | pottery (3) |

---

## Typical Flow

```
1. record.html  →  POST /transcribe        →  transcript
2. transcript   →  POST /extract-skills    →  skills + years + confidence + nsqf_mapping
3. confirm.html →  worker reviews, removes incorrect skills
4. POST /generate-credential               →  permanent QR + worker_id
```

For the demo, steps 1–2 are combined into `POST /process` (see PROCESS_PIPELINE.md).

---

## Environment Variables Required

```
GROQ_API_KEY=your_groq_key_here
```

Add to `Backend/.env`. Never push to GitHub.
