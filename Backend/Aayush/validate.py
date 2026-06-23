import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class SkillInput(BaseModel):
    skill: str
    language: str = "hi"

@router.post("/generate-question")
async def generate_question(data: SkillInput):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an AI interviewer for Indian informal workers. 
Generate ONE practical scenario-based question to test the worker's skill.
Language: {data.language}
Rules:
- Ask in simple Hindi if language is 'hi', English if 'en'
- Question must be practical, not theoretical
- No MCQ, no written answers needed
- Worker will answer verbally
- Keep question short (1-2 sentences)
Return ONLY the question, nothing else."""
                },
                {
                    "role": "user",
                    "content": f"Generate a skill validation question for: {data.skill}"
                }
            ],
            temperature=0.7
        )

        question = response.choices[0].message.content.strip()

        return {
            "success": True,
            "skill": data.skill,
            "question": question,
            "language": data.language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation error: {str(e)}")
@router.post("/validate-answer")
async def validate_answer(
    skill: str,
    question: str,
    audio: UploadFile = File(...)
):
    allowed_types = ["audio/wav", "audio/mpeg", "audio/webm", "audio/mp4", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    audio_bytes = await audio.read()
    temp_path = f"temp_validate_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    try:
        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi"
            )
        answer_text = transcript.text

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI skill evaluator for Indian informal workers.
Evaluate the worker's answer and return ONLY a JSON object like this:
{
  "confidence_score": 85,
  "verified": true,
  "feedback": "Worker showed good practical knowledge",
  "level": "intermediate"
}
Rules:
- confidence_score: 0-100
- verified: true if score >= 60, false otherwise
- feedback: one line in simple Hindi or English
- level: beginner/intermediate/expert based on answer quality"""
                },
                {
                    "role": "user",
                    "content": f"Skill: {skill}\nQuestion asked: {question}\nWorker's answer: {answer_text}\nEvaluate this answer."
                }
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        raw = raw[raw.find("{"):raw.rfind("}")+1]
        result = json.loads(raw)

        return {
            "success": True,
            "skill": skill,
            "question": question,
            "worker_answer": answer_text,
            "confidence_score": result["confidence_score"],
            "verified": result["verified"],
            "feedback": result["feedback"],
            "level": result["level"]
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Could not parse AI evaluation.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)