# NEEV Backend — NLP Pipeline

Track owner: Aayush  
Base URL (local dev): `http://127.0.0.1:8000`

---

## Overview

This track handles everything between the worker's voice and the extracted skill list. It takes raw audio in Hindi or Hinglish, converts it to text using Groq Whisper, then uses LLaMA to extract occupational skills and maps them to government-recognized NSQF levels.

```
Audio File → /transcribe → Transcript → /extract-skills → Skills + NSQF Levels
```

---

## Models Used

| Model | Provider | Purpose |
|---|---|---|
| `whisper-large-v3` | Groq | Audio → Hindi transcript |
| `llama-3.3-70b-versatile` | Groq | Transcript → skill list (JSON) |

---

## 1. Transcribe Audio

Converts a Hindi or Hinglish audio file into text.

**Endpoint:** `POST /transcribe`

### Request
- Content-Type: `multipart/form-data`
- Field: `audio` — an audio file (wav, mp3, webm, mp4, ogg)

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
| `transcript` | string | Raw text output from Whisper. May be Hindi, English, or mixed. |

### Response — 400
```json
{
  "detail": "Invalid file type. Send wav, mp3, webm, or ogg."
}
```

### Response — 500
```json
{
  "detail": "Groq Whisper error: ..."
}
```

### Notes
- Language is set to `hi` (Hindi) but Whisper handles Hinglish automatically.
- Audio file is saved temporarily on disk, passed to Whisper, then deleted immediately.
- Supports any Hindi accent or dialect — Whisper is robust to this.

---

## 2. Extract Skills

Takes a transcript and returns a list of occupational skills mapped to NSQF levels and sectors.

**Endpoint:** `POST /extract-skills`

### Request Body
```json
{
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ, driving भी जानता हूँ"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `transcript` | string | Yes | Raw text from /transcribe or typed manually |

### Response — 200 OK
```json
{
  "success": true,
  "transcript": "मैं पिछले 5 साल से plastering और painting का काम करता हूँ, driving भी जानता हूँ",
  "skills": [
    "plastering",
    "painting",
    "driving"
  ],
  "nsqf_mapping": [
    {
      "skill": "plastering",
      "nsqf_level": 4,
      "sector": "Construction"
    },
    {
      "skill": "painting",
      "nsqf_level": 3,
      "sector": "Construction"
    },
    {
      "skill": "driving",
      "nsqf_level": 3,
      "sector": "Transportation"
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | Always true on 200 |
| `transcript` | string | Echoed back for reference |
| `skills` | list of strings | Raw skill names extracted by LLaMA, in English |
| `nsqf_mapping` | list of objects | Each skill matched to NSQF level + sector |

### NSQF Mapping Object
| Field | Type | Notes |
|---|---|---|
| `skill` | string | Skill name as extracted by LLaMA |
| `nsqf_level` | integer or "N/A" | 1 (basic) to 8 (expert). "N/A" if skill not found in map. |
| `sector` | string | Industry sector. "General" if skill not found in map. |

### Response — 400
```json
{
  "detail": "Transcript is empty."
}
```

### Response — 500
```json
{
  "detail": "Skill extraction error: ..."
}
```

### Notes
- LLaMA is prompted to return skills in English only, even if transcript is Hindi.
- Matching uses direct lookup first, then partial string matching as fallback.
- Skills not found in `nsqf_map.json` are still returned with `nsqf_level: "N/A"`.

---

## NSQF Map

Stored in `Aayush/nsqf_map.json`. Currently covers 40 occupations across 10 sectors:

| Sector | Example Skills |
|---|---|
| Construction | plastering, painting, welding, carpentry, plumbing |
| Transportation | driving, truck driving, auto rickshaw driving |
| Hospitality | cooking, food preparation, catering |
| Facility Management | cleaning, housekeeping, sweeping |
| Apparel | tailoring, stitching, embroidery |
| Agriculture | farming, harvesting, irrigation |
| Security | security guard, watchman |
| Domestic Work | childcare, elder care, washing |
| Logistics | loading, delivery, packing |
| Electronics | mobile repair, ac repair |

---

## Typical Flow

1. Frontend records worker audio → sends to `/transcribe` → gets transcript
2. Transcript passed to `/extract-skills` → gets skill list + NSQF mapping
3. Skills and NSQF levels passed to Nikhil's `/generate-credential` → gets QR code

---

## Environment Variables Required

```
GROQ_API_KEY=your_groq_key_here
```

Add to `Backend/.env`. Never push to GitHub.