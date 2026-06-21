# NEEV Backend — API Contract

Backend owner: Nikhil
Base URLs (local dev): `http://127.0.0.1:8000` (credential service), `http://127.0.0.1:8001` (verify service)

---

## 1. Generate Credential

Creates a worker credential, hashes it, and returns a QR code encoding the data + hash.

**Endpoint:** `POST /generate-credential`

### Request Body
```json
{
  "name": "Raju",
  "skills": ["plastering"],
  "nsqf_levels": [3]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | Yes | Worker's full name |
| `skills` | list of strings | Yes | One or more skill names |
| `nsqf_levels` | list of integers | Yes | NSQF level for each skill, same order as `skills` |

### Response — 200 OK
```json
{
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "hash": "9a11cf815e79ef07c5ae04f76e0d0756c6ac9fdbcc8ca1436a1c4a48c480ce27"
}
```

| Field | Type | Notes |
|---|---|---|
| `qr_code_base64` | string | PNG image, base64-encoded. Render directly as `<img src="data:image/png;base64,{qr_code_base64}">` |
| `hash` | string | SHA256 hash (64 hex characters) of the worker data. Same hash is embedded inside the QR code itself. |

### Response — 422 Unprocessable Content
Returned if a required field is missing or has the wrong type. FastAPI returns a `detail` array describing what's wrong.

---

## 2. Verify Credential

Takes a worker's data + hash (typically extracted by scanning the QR code) and checks whether the data has been tampered with.

**Endpoint:** `POST /verify`

### Request Body
```json
{
  "data": {
    "name": "Raju",
    "skills": ["plastering"],
    "nsqf_levels": [3]
  },
  "hash": "9a11cf815e79ef07c5ae04f76e0d0756c6ac9fdbcc8ca1436a1c4a48c480ce27"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `data` | object | Yes | The worker data exactly as decoded from the QR payload |
| `hash` | string | Yes | The hash that was embedded alongside `data` in the QR code |

### Response — 200 OK
```json
{
  "valid": true,
  "worker_data": {
    "name": "Raju",
    "skills": ["plastering"],
    "nsqf_levels": [3]
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `valid` | boolean | `true` if `data` re-hashes to match `hash`. `false` if anything in `data` was altered. |
| `worker_data` | object | Echoes back the `data` that was sent in, for convenience |

---

## Typical Flow

1. Frontend calls `/generate-credential` with worker details → gets back a QR image + hash.
2. QR is printed / displayed to the worker.
3. Later, someone scans the QR → gets the JSON `{ data, hash }` payload back.
4. That payload is sent to `/verify` → response tells you if it's still trustworthy (`valid: true/false`).

---

## Notes for Integration

- Both services currently run on separate ports during local development (`8000` and `8001`). They'll likely be merged behind a single `main.py` entrypoint later — endpoint paths (`/generate-credential`, `/verify`) won't change either way.
- All hashing uses SHA256 over a canonical (`sort_keys=True`) JSON serialization, so field order in `data` never affects the hash.
- No authentication/rate-limiting implemented yet — out of scope for this stage.