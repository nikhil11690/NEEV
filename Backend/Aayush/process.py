import os
import json
import qrcode
import io
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
from Nikhil.hasher import hash_dict

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("Aayush/nsqf_map.json", "r") as f:
    nsqf_map = json.load(f)

def match_nsqf(skills: list) -> tuple:
    matched_skills = []
    nsqf_levels = []
    nsqf_details = []

    for skill in skills:
        skill_lower = skill.lower().strip()
        if skill_lower in nsqf_map:
            matched_skills.append(skill)
            nsqf_levels.append(nsqf_map[skill_lower]["level"])
            nsqf_details.append({
                "skill": skill,
                "nsqf_level": nsqf_map[skill_lower]["level"],
                "sector": nsqf_map[skill_lower]["sector"]
            })
        else:
            found = False
            for key in nsqf_map:
                if key in skill_lower or skill_lower in key:
                    matched_skills.append(skill)
                    nsqf_levels.append(nsqf_map[key]["level"])
                    nsqf_details.append({
                        "skill": skill,
                        "nsqf_level": nsqf_map[key]["level"],
                        "sector": nsqf_map[key]["sector"]
                    })
                    found = True
                    break
            if not found:
                matched_skills.append(skill)
                nsqf_levels.append(0)
                nsqf_details.append({
                    "skill": skill,
                    "nsqf_level": "N/A",
                    "sector": "General"
                })

    return matched_skills, nsqf_levels, nsqf_details

@router.post("/process")
async def process_worker(name: str, audio: UploadFile = File(...)):

    # Step 1 — Transcribe
    allowed_types = ["audio/wav", "audio/mpeg", "audio/webm", "audio/mp4", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    audio_bytes = await audio.read()
    temp_path = f"temp_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    try:
        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi"
            )
        transcript_text = transcript.text

        # Step 2 — Extract Skills + Years + Confidence
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a skill extractor for Indian informal workers. Extract occupational skills, years of experience, and confidence level from the given text. Confidence is high if the worker mentions the skill multiple times or with specific details, medium if mentioned once clearly, low if only briefly mentioned. Return ONLY a JSON array like this: [{\"skill\": \"plastering\", \"years\": 8, \"confidence\": \"high\"}, {\"skill\": \"painting\", \"years\": 3, \"confidence\": \"medium\"}]. If years are not mentioned, set years to 0. Return ONLY the JSON array, no extra text."
                },
                {
                    "role": "user",
                    "content": f"Extract skills from this text: {transcript_text}"
                }
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        raw = raw[raw.find("["):raw.rfind("]")+1]
        parsed = json.loads(raw)

        # Handle both old format ["skill"] and new format [{"skill": "x", "years": 0}]
        if parsed and isinstance(parsed[0], str):
            skills = parsed
            years = [0] * len(skills)
            confidence = ["medium"] * len(skills)
        else:
            skills = [item["skill"] for item in parsed]
            years = [item.get("years", 0) for item in parsed]
            confidence = [item.get("confidence", "medium") for item in parsed]

        # Step 3 — NSQF Mapping
        matched_skills, nsqf_levels, nsqf_details = match_nsqf(skills)

        # Step 4 — Generate Credential + QR
        payload = {
            "name": name,
            "skills": matched_skills,
            "nsqf_levels": nsqf_levels
        }

        credential_hash = hash_dict(payload)

        qr_payload = {
            "data": payload,
            "hash": credential_hash
        }

        qr_data_str = json.dumps(qr_payload)
        qr_img = qrcode.make(qr_data_str)
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "success": True,
            "name": name,
            "transcript": transcript_text,
            "skills": matched_skills,
            "years": years,
            "confidence": confidence,
            "nsqf_mapping": nsqf_details,
            "hash": credential_hash,
            "qr_code_base64": qr_base64
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Could not parse skills from AI response.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)