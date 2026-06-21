import os
import json
from fastapi import APIRouter, HTTPException
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load NSQF map
with open("Aayush/nsqf_map.json", "r") as f:
    nsqf_map = json.load(f)

class TranscriptInput(BaseModel):
    transcript: str

def match_nsqf(skills: list) -> list:
    matched = []
    for skill in skills:
        skill_lower = skill.lower().strip()
        # Direct match
        if skill_lower in nsqf_map:
            matched.append({
                "skill": skill,
                "nsqf_level": nsqf_map[skill_lower]["level"],
                "sector": nsqf_map[skill_lower]["sector"]
            })
        else:
            # Partial match — check if any key is contained in the skill
            found = False
            for key in nsqf_map:
                if key in skill_lower or skill_lower in key:
                    matched.append({
                        "skill": skill,
                        "nsqf_level": nsqf_map[key]["level"],
                        "sector": nsqf_map[key]["sector"]
                    })
                    found = True
                    break
            # If no match found, still include skill with unknown level
            if not found:
                matched.append({
                    "skill": skill,
                    "nsqf_level": "N/A",
                    "sector": "General"
                })
    return matched

@router.post("/extract-skills")
async def extract_skills(data: TranscriptInput):
    
    if not data.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is empty.")
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a skill extractor for Indian informal workers. Extract only occupational skills from the given text. Return a JSON array of skill strings in English only. Example: [\"plastering\", \"painting\", \"driving\"]. Return ONLY the JSON array, nothing else."
                },
                {
                    "role": "user",
                    "content": f"Extract skills from this text: {data.transcript}"
                }
            ],
            temperature=0.1
        )
        
        # Parse the response
        raw = response.choices[0].message.content.strip()
        
        # Clean up in case model adds extra text
        raw = raw[raw.find("["):raw.rfind("]")+1]
        skills = json.loads(raw)
        
        # Match to NSQF
        nsqf_results = match_nsqf(skills)
        
        return {
            "success": True,
            "transcript": data.transcript,
            "skills": skills,
            "nsqf_mapping": nsqf_results
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Could not parse skills from AI response.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill extraction error: {str(e)}")