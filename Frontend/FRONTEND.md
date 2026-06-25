# NEEV Frontend — Documentation

Frontend owner: Laiba  
Files: `css/style.css` · `js/api.js` · `index.html` · `login.html` · `signup.html` · `stats.html` · `Worker/record.html` · `Worker/confirm.html` · `Worker/credential.html` · `Worker/interview.html` · `Employer/verify.html` · `Employer/review.html` · `Employer/endorse.html`  
Live URL: `https://neev-1.onrender.com`

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Shared Utilities — api.js](#2-shared-utilities--apijs)
3. [Design System — style.css](#3-design-system--stylecss)
4. [Page Reference](#4-page-reference)
   - [index.html — Landing](#indexhtml--landing)
   - [login.html — Login](#loginhtml--login)
   - [signup.html — Signup](#signuphtml--signup)
   - [stats.html — Platform Stats](#statshtml--platform-stats)
   - [Worker/record.html — Voice Recording](#workerrecordhtml--voice-recording)
   - [Worker/confirm.html — Confirm Skills](#workerconfirmhtml--confirm-skills)
   - [Worker/credential.html — Passport](#workercredentialhtml--passport)
   - [Worker/interview.html — AI Interview](#workerinterviewhtml--ai-interview)
   - [Employer/verify.html — Verify Worker](#employerverifyhtml--verify-worker)
   - [Employer/review.html — Submit Review](#employerreviewhtml--submit-review)
   - [Employer/endorse.html — Endorse Worker](#employerendorsehtml--endorse-worker)
5. [SessionStorage Keys](#5-sessionstorage-keys)
6. [Complete User Flows](#6-complete-user-flows)
7. [CSS Component Cheatsheet](#7-css-component-cheatsheet)

---

## 1. Folder Structure

```
Frontend/
├── css/
│   └── style.css              # Global design system — "Nayi Subah" theme
├── js/
│   └── api.js                 # Shared backend URL + neevFetch helper
├── index.html                 # Landing page (public)
├── login.html                 # Auth: login
├── signup.html                # Auth: signup
├── stats.html                 # Platform stats dashboard
├── Worker/
│   ├── record.html            # Step 1: Voice recording
│   ├── confirm.html           # Step 2: Review + confirm skills
│   ├── credential.html        # Step 3: Passport display + interview gate
│   └── interview.html         # Step 4: AI skill interview
└── Employer/
    ├── verify.html            # QR scan + worker profile display
    ├── review.html            # 4-question MCQ employer review
    └── endorse.html           # Community endorsement form + lookup
```

---

## 2. Shared Utilities — `api.js`

**Path:** `js/api.js`  
Loaded via `<script src="../js/api.js">` (or `js/api.js` from root pages).

```js
const NEEV_API = "https://neev-1.onrender.com";

async function neevFetch(path, options = {}) {
  const res = await fetch(`${NEEV_API}${path}`, options);
  if (!res.ok) {
    let detail = "";
    try { detail = JSON.stringify(await res.json()); } catch (e) {}
    throw new Error(`${res.status} ${res.statusText} ${detail}`);
  }
  return res.json();
}
```

- `NEEV_API` — base URL. Change this for local dev: `http://127.0.0.1:8000`
- `neevFetch(path, options)` — thin wrapper around `fetch`. Throws a descriptive `Error` on any non-2xx response so callers can `catch(err)` and show `err.message` directly in the UI
- Pages that need raw `FormData` (audio uploads) call `fetch(${NEEV_API}/endpoint, ...)` directly since `neevFetch` sets no `Content-Type` override
- `NEEV_API` is also available as the global `window.NEEV_API` alias used in some pages

---

## 3. Design System — `style.css`

**Theme name:** "Nayi Subah" (New Dawn)  
**Philosophy:** Dignity, hope, trust. A sunrise palette for India's invisible workforce.  
**Approach:** Mobile-first, max-width 560px shell, warm ivory + saffron + deep blue.

### CSS Variables (Design Tokens)

#### Palette
| Variable | Value | Usage |
|---|---|---|
| `--bg` | `#FFF9ED` | Page background — warm ivory |
| `--bg-raised` | `#FFF4DC` | Slightly deeper ivory for raised surfaces |
| `--bg-card` | `#FFFFFF` | Card backgrounds — clean, trustworthy |
| `--line` | `#E8DCC8` | Borders and dividers |
| `--line-soft` | `#F0E8D5` | Subtle internal dividers |
| `--ink` | `#2D2D2D` | Primary text — near-black |
| `--ink-dim` | `#666666` | Secondary text |
| `--ink-faint` | `#999999` | Placeholders, captions |
| `--saffron` | `#FFB703` | Primary brand — CTA, sunrise, hope |
| `--saffron-dim` | `#E09F00` | Hover/active state |
| `--saffron-bg` | `#FFF8E1` | Saffron tint backgrounds |
| `--blue` | `#1E6091` | Trust, verified, government-grade |
| `--blue-bg` | `#EBF4FA` | Blue tint backgrounds |
| `--green` | `#52B788` | Success, verified, growth |
| `--green-dim` | `#3D9A6F` | Active green |
| `--green-bg` | `#EDFBF4` | Green tint backgrounds |
| `--bad` | `#E63946` | Fraud risk, errors |
| `--bad-bg` | `#FFF0F1` | Error tint backgrounds |
| `--amber` | `#F4A261` | Warning, medium risk |
| `--amber-bg` | `#FFF5EC` | Warning tint backgrounds |

#### Typography
| Variable | Value | Usage |
|---|---|---|
| `--display` | `'Tiro Devanagari Hindi', Georgia, serif` | Headings, worker name, passport title |
| `--body` | `'Hind', 'Inter', sans-serif` | All body text |
| `--mono` | `'JetBrains Mono', monospace` | Hash values |

**Google Fonts loaded:** Hind (400/500/600/700), Tiro Devanagari Hindi (0;1), Inter (400/500/600)

#### Radii & Shadows
| Variable | Value |
|---|---|
| `--radius-lg` | `20px` |
| `--radius-md` | `14px` |
| `--radius-sm` | `10px` |
| `--shadow-sm` | `0 2px 8px rgba(45,35,10,0.07)` |
| `--shadow-md` | `0 4px 20px rgba(45,35,10,0.10)` |
| `--shadow-card` | `0 2px 12px rgba(45,35,10,0.08)` |

### Layout Classes

| Class | Description |
|---|---|
| `.shell` | Main content wrapper. `max-width: 560px`, centered, `padding: 24px 20px 80px` |
| `.topbar` | Flex row: brandmark left, back-link right |
| `.brandmark` | NEEV logo text with saffron dot |
| `.back-link` | "← Back" link, grays to blue on hover |
| `nav.crumbs` | Breadcrumb trail. Active step uses `.on` class |

### Card & Passport

| Class | Description |
|---|---|
| `.card` | White card with warm border, `border-radius: 20px`, card shadow |
| `.passport` | Special golden card for the worker's credential. Saffron border, warm gradient background, decorative radial glow |

### Seal Badge

The trust score badge / NEEV seal.

| Class | Description |
|---|---|
| `.seal` | Circular badge, saffron border, radial gradient background, inner dashed ring |
| `.seal.stamp` | Adds `stampIn` animation — scale+rotate reveal on load |
| `.seal.good` | Green variant — score ≥ 70 |
| `.seal.bad` | Red variant — score < 45 |
| `.seal.brass` | Saffron variant — default / medium score |
| `.seal-mark` | Text inside the seal (score number or "N") |

### Typography Classes

| Class | Description |
|---|---|
| `h1` | Display font, 28px, bold |
| `.lede` | Subtitle paragraph below h1, dimmed, max-width 440px |
| `.eyebrow` | Section label — 10.5px, uppercase, letter-spaced, with auto line after |

### UI Components

| Class | Description |
|---|---|
| `.ledger-row` | Skill row: name left, pill(s) right. Divider on bottom. `.muted` for removed items |
| `.ledger-skill` | Skill name inside a ledger row |
| `.pill` | Small tag/badge. Variants: `.level` (blue), `.good` (green), `.bad` (red), `.brass` (saffron) |
| `.chip` | Removable skill chip with ✕ button. `.removed` strikes it out |
| `.chips` | Grid container for `.chip` elements |
| `.btn` | Base button — full width, 50px height, bold |
| `.btn-primary` | Saffron CTA button |
| `.btn-good` | Green confirm button |
| `.btn-ghost` | Outlined secondary button |
| `.mic-btn` | Large circular microphone button. `.recording` adds red pulse animation |
| `.mic-wrap` | Centering wrapper for mic button |
| `.status-line` | Inline status message. `.success` = green, `.error` = red |
| `.banner` | Full-width alert strip. `.good` = green, `.bad` = red |
| `.field` | Form field wrapper with `label` + `input` styling |
| `.stat-grid` | 2-column grid of stat tiles |
| `.stat-tile` | Individual stat tile: `.num` (large blue number) + `.label` |
| `.opt-row` | Flex row for option toggle buttons (e.g. camera vs upload) |
| `.opt-btn` | Toggle button. `.active` highlights with saffron |
| `.upload-area` | Dashed upload dropzone, hover highlights saffron |
| `video` | Full-width, rounded border for camera preview |
| `.endorse-item` | Single endorsement block with `.who`, `.role`, `.dur`, `.cmt` |
| `.empty-state` | Centered placeholder text for empty lists |
| `.star-btn` | Star rating button. `.active` = saffron fill |
| `.mcq-btn` | MCQ option button. `.selected` = green highlight |
| `.qr-frame` | White framed QR display box with saffron border |
| `.hash-box` | Monospace hash display box |
| `.nav-card` | Navigation card with icon + title + arrow. Lifts on hover |

### Animations

| Animation | Used on | Effect |
|---|---|---|
| `stampIn` | `.seal.stamp` | Scale 2.2 → 1 with slight rotation — passport stamp feel |
| `sunrise` | `.hero-sun` | Translates up from below — sunrise reveal |
| `micPulse` | `.mic-btn.recording` | Red glow pulse while recording |

### Responsive Breakpoints

| Breakpoint | Changes |
|---|---|
| `max-width: 400px` | Reduced shell padding, h1 smaller (24px), tighter grid |
| `prefers-reduced-motion` | All animations and transitions disabled |

---

## 4. Page Reference

---

### `index.html` — Landing

**Route:** `/` (root)  
**Access:** Public  
**Backend calls:** `GET /stats`

The public landing page. Explains NEEV to first-time visitors, shows live platform stats, and routes users to the right flow.

#### Sections
1. **Nav** — sticky top bar with NEEV brandmark + "Get Started →" CTA
2. **Hero** — headline, subheadline, two primary CTAs (Worker / Employer)
3. **Stats bar** — live counts pulled from `/stats`: verifications, reviews, fraud cases
4. **How it works** — 3 numbered steps (Speak → AI verifies → Get passport)
5. **User cards** — Worker and Employer cards each listing features + CTA
6. **Quick links** — AI Interview + Endorse a Worker shortcuts
7. **Tech bar** — Groq Whisper · LLaMA 3.3-70b · NSQF · SHA256

#### Routing
| CTA | Destination |
|---|---|
| "I'm a Worker" | `Worker/record.html` |
| "I'm an Employer" | `Employer/verify.html` |
| "AI Skill Interview" | `Worker/interview.html` |
| "Endorse a Worker" | `Employer/endorse.html` |
| "Stats" | `stats.html` |

---

### `login.html` — Login

**Route:** `/login.html`  
**Access:** Public  
**Backend calls:** `POST /login`

#### Flow
1. User enters email + password (Enter key triggers submit)
2. `POST /login` called with JSON body
3. On success: token + user object saved to `sessionStorage`
4. Redirect: `worker` → `Worker/record.html`, `employer` → `Employer/verify.html`
5. On error: status line shows `err.message`

#### SessionStorage written
- `neev_token` — session token string
- `neev_user` — JSON object `{id, name, email, role}`

---

### `signup.html` — Signup

**Route:** `/signup.html`  
**Access:** Public  
**Backend calls:** `POST /signup`

#### Flow
1. User selects role via toggle (Worker / Employer) — default is Worker
2. Fills name, email, password (min 6 chars)
3. Avatar preview shows first letter of name in real-time (`oninput`)
4. `POST /signup` called with JSON body
5. On success: token + user saved to `sessionStorage`, role-based redirect
6. On error: status line with error detail

#### Validation (client-side)
- Name required
- Email required
- Password minimum 6 characters
- Role must be selected (always has a default)

---

### `stats.html` — Platform Stats

**Route:** `/stats.html`  
**Access:** Public  
**Backend calls:** `GET /stats`

Displays 4 live stat tiles:
- Total employer reviews
- Total verifications
- Fraud cases flagged
- Average employer rating

Also shows platform name and backend status from the `/stats` response. Includes a "↻ Refresh" button that reloads the page.

---

### `Worker/record.html` — Voice Recording

**Route:** `Worker/record.html`  
**Access:** Worker  
**Backend calls:** `POST /process`  
**Breadcrumb:** Worker / **Record** / Confirm / Passport

**Step 1 of the worker flow.** Worker enters their name and records a voice description of their skills in Hindi.

#### Flow
1. Worker types their name in the text field
2. Taps 🎙️ mic button → browser requests microphone permission
3. `MediaRecorder` starts recording (`audio/webm`)
4. Worker speaks their skills in Hindi (e.g. "Main 5 saal se plastering karta hoon...")
5. Taps ⏹️ to stop → `audioBlob` created → "Generate skill draft" button appears
6. Worker taps submit → `POST /process?name={name}` with audio as `FormData`
7. Response saved to `sessionStorage` as `neev_process_result`
8. Redirect to `confirm.html`

#### SessionStorage written
- `neev_process_result` — full `/process` response JSON

#### Error handling
- Mic permission denied → status line message
- No name entered → status line error
- Server unreachable → message noting server may be waking up (Render cold start)

---

### `Worker/confirm.html` — Confirm Skills

**Route:** `Worker/confirm.html`  
**Access:** Worker  
**Backend calls:** `POST /generate-credential`  
**Breadcrumb:** Worker / Record / **Confirm** / Passport

**Step 2 of the worker flow.** Worker reviews AI-extracted skills, removes incorrect ones, then generates their credential.

#### Flow
1. Reads `neev_process_result` from `sessionStorage` — redirects to `record.html` if missing
2. Displays worker name, transcript text, skill chips, and NSQF mapping rows
3. Worker taps ✕ on any chip to toggle it as removed — chip grays out, NSQF row dims
4. Confirm button disabled if all skills removed
5. Worker taps "This looks right — generate passport →"
6. `POST /generate-credential` called with confirmed skills + NSQF levels
7. Response + confirmed skill data saved to `sessionStorage` as `neev_credential`
8. Redirect to `credential.html`

#### Skill removal logic
- `removedIndices` Set tracks which skills to exclude
- Toggling a removed skill restores it
- Only non-removed skills are sent to `/generate-credential`
- `nsqf_level: "N/A"` → sent as `0` in the credential request

#### SessionStorage read
- `neev_process_result`

#### SessionStorage written
- `neev_credential` — `{worker_id, name, skills, nsqf_levels, nsqf_mapping, qr_code_base64, interview_completed, trust_score, ai_validation_score}`

---

### `Worker/credential.html` — Passport

**Route:** `Worker/credential.html`  
**Access:** Worker  
**Backend calls:** `POST /update-skills`  
**Breadcrumb:** Worker / Record / Confirm / **Passport**

**Step 3 of the worker flow.** Shows the worker's QR passport — but only after the AI interview is complete.

#### Interview Gate
On load, reads `neev_credential.interview_completed`:
- `false` → shows gate UI explaining the interview requirement + link to `interview.html?worker_id={id}`
- `true` → shows full passport UI

#### Passport Display (after interview)
- Seal badge showing trust score (colored by score: green ≥ 70, saffron medium, red low)
- Worker name + "AI Interview: Completed" tag
- Skills list with NSQF levels as green pills
- QR code image (`data:image/png;base64,...`)
- "QR will never change" caption

#### Actions
- **⬇ QR Download** — creates a temporary `<a>` and triggers download of the QR as PNG
- **🧠 Try another skill** — links to `interview.html`
- **Skill update form** — worker can add new skills (comma-separated), merged with existing skills, sent to `POST /update-skills`. QR is unchanged.

#### Skill update flow
1. Worker types new skills in input
2. New skills merged with existing (deduped via `Set`)
3. `POST /update-skills` called with merged list
4. `sessionStorage` updated with new skills
5. Passport re-rendered with updated skills — QR image stays same

#### SessionStorage read
- `neev_credential`
- `neev_worker_id`

#### SessionStorage written (on update)
- `neev_credential` — updated with new skills

---

### `Worker/interview.html` — AI Interview

**Route:** `Worker/interview.html`  
**Access:** Worker  
**Backend calls:** `POST /generate-question`, `POST /validate-answer`, `POST /complete-interview`  
**Breadcrumb:** Worker / **AI Interview**

**Step 4 (mandatory gate).** Worker picks a skill, gets a real-world question from LLaMA, records their answer, and receives a confidence score.

#### Flow
1. Worker types skill name + selects language (Hindi / English)
2. Taps "Generate question →" → `POST /generate-question` → question text shown
3. Skill card fades to 50% opacity, generate button hidden
4. Worker taps 🎙️ → records answer via `MediaRecorder`
5. Taps ⏹️ to stop → "Submit answer" button appears
6. Worker taps submit → `POST /validate-answer?skill=...&question=...` with audio
7. On result:
   - `POST /complete-interview?worker_id={id}&ai_score={score}` called
   - `sessionStorage.neev_credential` updated with `interview_completed: true` and `ai_validation_score`
   - Result card shown: score seal, question, worker's transcribed answer, level pill, AI feedback
8. Back link → `credential.html` (if `worker_id` available) or "Try another skill" (standalone)

#### URL parameter
- `?worker_id={uuid}` — passed from `credential.html` gate link. Also read from `sessionStorage.neev_worker_id`.

#### Result display
| Score | Seal color | `verified` |
|---|---|---|
| ≥ 60 | Green | `true` |
| < 60 | Red | `false` |

Level pill: `beginner` (red) · `intermediate` (saffron) · `expert` (green)

---

### `Employer/verify.html` — Verify Worker

**Route:** `Employer/verify.html`  
**Access:** Employer  
**Backend calls:** `POST /verify`, `GET /endorsements/{name}`  
**External library:** `jsQR` via CDN (`cdn.jsdelivr.net/npm/jsqr@1.4.0`)

The primary employer tool. Scans a worker's QR and displays their full verified profile.

#### Scan modes
| Mode | Description |
|---|---|
| 📷 Camera | Opens rear camera, scans via `setInterval` every 500ms using `jsQR` |
| 🖼️ Upload | File input → FileReader → canvas → `jsQR` decodes |

#### QR decoding logic
Handles both QR formats:
1. **New format (UUID only)** — if raw data matches UUID regex → sent directly as `{worker_id}`
2. **Old JSON format** — if `parsed.worker_id` exists → use it; if `parsed.data + parsed.hash` → legacy verify path

#### Result display
- ✓ Valid — shows full worker profile
- ✗ Invalid — shows tamper warning

**Valid result sections:**
- Worker identity: name + "NEEV Verified Worker" tag
- Skills table with NSQF levels
- Stat grid: trust score / 100 + fraud risk
- Fraud flags (if any) in red
- Employer reviews (text) list
- Community endorsements (loaded async via `GET /endorsements/{name}`)
- "Leave a review" CTA → `review.html?worker={name}`

#### Camera handling
- `stopCamera()` called when QR is found or user switches modes
- Stream tracks stopped to release camera hardware
- Scan interval cleared

---

### `Employer/review.html` — Submit Review

**Route:** `Employer/review.html`  
**Access:** Employer  
**Backend calls:** `POST /employer-mcq`

4-question structured MCQ review submitted by an employer after hiring a worker.

#### Questions
| # | Type | Field |
|---|---|---|
| Q1 | 1–5 star rating | `q1_satisfaction` — overall satisfaction |
| Q2 | 4-option MCQ | `q2_unexpected` — how worker handled unexpected situations |
| Q3 | Yes / No toggle | `q3_would_rehire` — would you hire again |
| Q4 | 1–5 star rating | `q4_skill_accuracy` — did skills match claims |

#### Star rating behavior
- `setRating(q, val)` highlights all stars up to `val` using `.active` class
- Labels update below each star row with descriptive text
- Q1 labels: Bilkul nahi → Bohot achha
- Q4 labels: Bilkul match nahi → Bilkul sahi thi

#### Validation (client-side)
All 4 questions must be answered before submit is enabled. Specific error messages for each missing field.

#### Result display
On success: shows the worker's updated trust score in a passport-style card with total MCQ review count.

---

### `Employer/endorse.html` — Endorse Worker

**Route:** `Employer/endorse.html`  
**Access:** Public (anyone can endorse)  
**Backend calls:** `POST /community-verify`, `GET /endorsements/{name}`

Two panels on one page:

#### Submit endorsement
- Fields: worker name, endorser name, role (contractor / supervisor / co-worker / client), duration, comment
- `POST /community-verify` → success message + button text changes to "Submitted ✓"

#### Look up endorsements
- Text input + "Look up" button
- `GET /endorsements/{name}` → renders list of `.endorse-item` blocks
- Shows count, endorser name, role, duration, comment

---

## 5. SessionStorage Keys

All state is stored in `sessionStorage` (cleared when tab/browser closes). No `localStorage` is used.

| Key | Set by | Read by | Contents |
|---|---|---|---|
| `neev_token` | `login.html`, `signup.html` | (auth check) | Session token string |
| `neev_user` | `login.html`, `signup.html` | (role check) | `{id, name, email, role}` JSON |
| `neev_process_result` | `record.html` | `confirm.html` | Full `/process` response |
| `neev_credential` | `confirm.html`, `interview.html` | `credential.html`, `interview.html` | `{worker_id, name, skills, nsqf_levels, nsqf_mapping, qr_code_base64, interview_completed, trust_score, ai_validation_score}` |
| `neev_worker_id` | `credential.html` | `interview.html`, `credential.html` | Permanent UUID string |

---

## 6. Complete User Flows

### Worker — Full onboarding

```
index.html  →  "I'm a Worker"
        ↓
signup.html  →  POST /signup  →  sessionStorage: token + user
        ↓
Worker/record.html
  Enter name + record Hindi audio (MediaRecorder → webm)
        ↓
POST /process?name={name}  →  transcript + skills + years + NSQF + QR
sessionStorage: neev_process_result
        ↓
Worker/confirm.html
  Review skills, tap ✕ to remove wrong ones
        ↓
POST /generate-credential  →  worker_id + QR base64
sessionStorage: neev_credential (interview_completed: false)
        ↓
Worker/credential.html
  ⚠ Interview gate — interview_completed is false
        ↓
Worker/interview.html?worker_id={uuid}
  1. Type skill + select language
  2. POST /generate-question  →  Hindi question shown
  3. Record answer (MediaRecorder)
  4. POST /validate-answer    →  confidence_score + verified + feedback
  5. POST /complete-interview →  interview_completed = true, ai_score saved
  sessionStorage: neev_credential updated (interview_completed: true)
        ↓
Worker/credential.html
  ✓ Passport shown: QR + skills + trust score
  Optional: add new skills → POST /update-skills
  Optional: download QR as PNG
```

### Employer — Verify + review

```
index.html  →  "I'm an Employer"
        ↓
signup.html / login.html
        ↓
Employer/verify.html
  Choose: 📷 Camera scan  OR  🖼️ Upload QR image
  jsQR decodes → extracts worker_id UUID
        ↓
POST /verify  →  worker profile + trust score + fraud risk + reviews + endorsements
  Result shown: skills, NSQF, trust score, fraud flags, reviews, endorsements
        ↓
"Leave a review for {name}" →
Employer/review.html
  Fill Q1–Q4  →  POST /employer-mcq
  Trust score updated immediately, shown on success screen
        ↓
Employer/endorse.html  (optional)
  Fill form  →  POST /community-verify
  Endorsement appears on next /verify for that worker
```

---

## 7. CSS Component Cheatsheet

Quick reference for adding new pages consistently.

### Page skeleton
```html
<div class="shell">
  <div class="topbar">
    <a href="../index.html" class="brandmark"><span class="seal-dot"></span>NEEV</a>
    <a href="previous.html" class="back-link">← Back</a>
  </div>
  <nav class="crumbs">Section <span class="sep">/</span> <span class="on">Current Page</span></nav>
  <h1>Page Title</h1>
  <p class="lede">Subtitle text here.</p>
  <!-- content -->
</div>
<script src="../js/api.js"></script>
```

### Card with eyebrow
```html
<div class="card">
  <div class="eyebrow">Section label</div>
  <!-- content -->
</div>
```

### Skill ledger row
```html
<div class="ledger-row">
  <span class="ledger-skill">Plastering</span>
  <div class="ledger-right">
    <span class="pill level">NSQF 4</span>
    <span class="pill good">Construction</span>
  </div>
</div>
```

### Trust seal
```html
<!-- Green (score ≥ 70) -->
<div class="seal stamp good"><span class="seal-mark">82</span></div>
<!-- Saffron (medium) -->
<div class="seal stamp brass"><span class="seal-mark">55</span></div>
<!-- Red (low) -->
<div class="seal stamp bad"><span class="seal-mark">30</span></div>
```

### Buttons
```html
<button class="btn btn-primary">Primary CTA →</button>
<button class="btn btn-good">Confirm / Submit</button>
<button class="btn btn-ghost">Secondary action</button>
```

### Status line
```html
<div class="status-line" id="status"></div>
<script>
function setStatus(msg, type) {
  const el = document.getElementById('status');
  el.innerText = msg;
  el.className = 'status-line ' + type; // type: 'success' | 'error' | ''
}
</script>
```

### Mic button
```html
<div class="mic-wrap">
  <button class="mic-btn" id="micBtn" onclick="toggleRecording()">🎙️</button>
</div>
<div class="status-line" id="recStatus">Tap to record</div>
```

### Banner alert
```html
<div class="banner good">✓ Verified successfully</div>
<div class="banner bad">✗ Credential invalid</div>
```

### Stat grid
```html
<div class="stat-grid">
  <div class="stat-tile">
    <div class="num">82</div>
    <div class="label">Trust Score / 100</div>
  </div>
  <div class="stat-tile">
    <div class="num" style="color:var(--green);">low</div>
    <div class="label">Fraud Risk</div>
  </div>
</div>
```

---

## Environment

To run locally:
1. Open `Frontend/index.html` with VS Code Live Server, **or**
2. `python -m http.server 5500` from the `Frontend/` directory

To point at local backend, change in `js/api.js`:
```js
const NEEV_API = "http://127.0.0.1:8000";
```