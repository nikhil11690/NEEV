# NEEV Frontend

Frontend owner: Nikhil  
Built with: Plain HTML, CSS, Vanilla JavaScript  
Served via: VS Code Live Server (local) / Static hosting (production)

---

## Overview

The frontend has two user journeys — Worker and Employer. All communication with the backend happens via `fetch()` calls to the FastAPI server.

```
index.html
├── Worker Journey
│   ├── Worker/record.html       → records audio + sends to /process
│   ├── Worker/confirm.html      → confirms extracted skills
│   └── Worker/credential.html   → shows QR code + download
│
└── Employer Journey
    └── Employer/scan.html       → scans QR → calls /verify → shows skill card
```

---

## Pages

### 1. `index.html` — Landing Page

Entry point for all users. Two cards — Worker and Employer. No API calls.

**Links to:**
- `Worker/record.html`
- `Employer/scan.html`

---

### 2. `Worker/record.html` — Voice Recording

Worker enters their name and records a voice note describing their skills.

**What it does:**
- Takes worker name as text input
- Records audio via browser `MediaRecorder` API
- On submit: sends audio + name to backend via `POST /process`
- Saves full API response to `sessionStorage` as `neev_process_result`
- Redirects to `confirm.html`

**API call:**
```javascript
POST http://127.0.0.1:8000/process?name={workerName}
Content-Type: multipart/form-data
Body: audio file (webm)
```

**Response saved to sessionStorage:**
```json
{
  "success": true,
  "name": "Raju",
  "transcript": "...",
  "skills": ["plastering", "painting"],
  "nsqf_mapping": [...],
  "hash": "...",
  "qr_code_base64": "..."
}
```

---

### 3. `Worker/confirm.html` — Skill Confirmation

Worker reviews extracted skills and removes any incorrect ones before the QR is generated.

**What it does:**
- Reads `neev_process_result` from `sessionStorage`
- Displays transcript so worker can verify what was heard
- Shows each skill as a chip with ✕ button to remove
- Shows NSQF level and sector for each skill
- On confirm: sends only the approved skills to `POST /generate-credential`
- Saves final credential result to `sessionStorage` as `neev_result`
- Redirects to `credential.html`

**API call:**
```javascript
POST http://127.0.0.1:8000/generate-credential
Content-Type: application/json
Body: {
  "name": "Raju",
  "skills": ["plastering"],
  "nsqf_levels": [4]
}
```

---

### 4. `Worker/credential.html` — Skill Passport

Displays the worker's final verified skill passport with QR code.

**What it does:**
- Reads `neev_result` from `sessionStorage`
- Shows worker name, skill chips, NSQF mapping
- Renders QR code from `qr_code_base64` as an `<img>` tag
- Shows SHA256 security hash
- Download button saves QR as PNG file
- No API calls on this page

**How QR is rendered:**
```html
<img src="data:image/png;base64,{qr_code_base64}" />
```

---

### 5. `Employer/scan.html` — Credential Verification

Employer scans or uploads worker's QR code to verify their credential.

**What it does:**
- Reads QR code via camera or image upload using jsQR library
- Extracts JSON payload from QR
- Sends payload to `POST /verify`
- Shows verified skill card if valid
- Shows tampered warning if invalid

**API call:**
```javascript
POST http://127.0.0.1:8000/verify
Content-Type: application/json
Body: {
  "data": { "name": "Raju", "skills": [...], "nsqf_levels": [...] },
  "hash": "..."
}
```

**Response:**
```json
{
  "valid": true,
  "worker_data": { "name": "Raju", "skills": [...], "nsqf_levels": [...] }
}
```

---

## Data Flow Between Pages

```
record.html
  └── sessionStorage.setItem('neev_process_result', data)
        ↓
confirm.html
  ├── sessionStorage.getItem('neev_process_result')
  └── sessionStorage.setItem('neev_result', finalData)
        ↓
credential.html
  └── sessionStorage.getItem('neev_result')
```

sessionStorage is used instead of localStorage because data should not persist after the browser tab is closed.

---

## Backend URL

Currently set to `http://127.0.0.1:8000` for local development.

After deployment, replace all instances of `http://127.0.0.1:8000` with the live Render URL across these files:
- `Worker/record.html`
- `Worker/confirm.html`
- `Employer/scan.html`

---

## Environment

| Tool | Purpose |
|---|---|
| VS Code Live Server | Serves frontend locally at `http://127.0.0.1:5500` |
| jsQR | QR code reading from camera/image in browser |
| MediaRecorder API | Built-in browser API for audio recording |
| sessionStorage | Passes data between pages without a database |

---

## Notes

- Frontend has zero build step — open `index.html` with Live Server and it works.
- All styling is inline CSS per file — no external CSS framework.
- JavaScript is vanilla — no React, no Vue, no dependencies except jsQR for scan.html.
- Backend must be running locally for API calls to work during development.