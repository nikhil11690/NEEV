import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    
    allowed_types = ["audio/wav", "audio/mpeg", "audio/webm", "audio/mp4", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Send wav, mp3, webm, or ogg.")
    
    audio_bytes = await audio.read()
    
    temp_path = f"temp_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)
    
    try:
        with open(temp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                # language parameter hatao — Whisper khud detect karega
            )
        
        return {
            "success": True,
            "transcript": transcript.text
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq Whisper error: {str(e)}")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)