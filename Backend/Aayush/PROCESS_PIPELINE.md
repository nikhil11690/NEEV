# NEEV Backend — Process Pipeline

Track owner: Aayush  
Base URL (local dev): `http://127.0.0.1:8000`

---

## Overview

`/process` is the master endpoint. It chains the entire backend pipeline in a single API call — from raw audio to a scannable QR credential. This is the endpoint the frontend uses for the demo.

```
Audio + Worker Name
       ↓
  /process
       ↓
  Groq Whisper
  (audio → Hindi transcript)
       ↓
  LLaMA 3.3-70b
  (transcript → skill list)
       ↓
  NSQF Mapper
  (skills → levels + sectors)
       ↓
  SHA256 Hasher
  (payload → tamper-proof hash)
       ↓
  QR Generator
  (payload + hash → base64 PNG)
       ↓
  Single JSON Response
  (transcript + skills + NSQF + hash + QR)
```

---

## Endpoint

**`POST /process`**

### Request
- Content-Type: `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | Yes | Worker's full name — passed as a query parameter |
| `audio` | file | Yes | Audio file (wav, mp3, webm, mp4, ogg) |

### Example curl
```bash
curl -X POST "http://127.0.0.1:8000/process?name=Raju" \
  -F "audio=@recording.mp3;type=audio/mpeg"
```

---

### Response — 200 OK

```json
{
  "success": true,
  "name": "Raju",
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
  ],
  "hash": "63795c4f21e80d2cc57401812de7ec351c14d54a730a1cc9d250277a6b1d5087",
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUg..."
}
```

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | Always true on 200 |
| `name` | string | Worker name echoed back |
| `transcript` | string | Hindi/Hinglish text from Whisper |
| `skills` | list of strings | Occupational skills extracted by LLaMA, in English |
| `nsqf_mapping` | list of objects | Each skill with NSQF level and sector |
| `hash` | string | SHA256 hash of the credential payload. Embedded inside QR. |
| `qr_code_base64` | string | The worker's QR credential as a base64 PNG image |

---

## How Frontend Uses the QR

The `qr_code_base64` field is a complete PNG image encoded as text. Frontend renders it as a real scannable QR with one line:

```html
<img src="data:image/png;base64,{qr_code_base64}" />
```

The worker sees a real QR code on screen — they can screenshot it, download it, or show it directly to an employer for scanning.

---

## What the QR Contains

When scanned, the QR decodes to this JSON payload:

```json
{
  "data": {
    "name": "Raju",
    "skills": ["plastering", "painting", "driving"],
    "nsqf_levels": [4, 3, 3]
  },
  "hash": "63795c4f21e80d2cc57401812de7ec351c14d54a730a1cc9d250277a6b1d5087"
}
```

This payload is sent to `/verify` to confirm the credential is untampered.

---

## Tamper Detection

The hash is a SHA256 of the worker data computed at credential generation time. If anyone modifies the worker's name, skills, or NSQF levels after the QR is generated, the hash will not match when `/verify` recomputes it — returning `valid: false`.

This is the cryptographic security hook of the entire system.

---

## Error Responses

| Code | Reason |
|---|---|
| 400 | Invalid audio file type |
| 500 | Whisper transcription failed |
| 500 | LLaMA skill extraction failed |
| 500 | Could not parse skills from AI response |

---

## Dependencies

| Module | Source |
|---|---|
| Groq Whisper | `Aayush/transcribe.py` logic |
| LLaMA + NSQF | `Aayush/extract_skills.py` logic |
| SHA256 Hasher | `Nikhil/hasher.py` |
| QR Generator | `qrcode` Python library |

---

## Environment Variables Required

```
GROQ_API_KEY=your_groq_key_here
```