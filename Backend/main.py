from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Aayush.transcribe import router as transcribe_router
from Aayush.extract_skills import router as skills_router
from Aayush.process import router as process_router
from Nikhil.credential import router as credential_router
from Nikhil.verify import router as verify_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from Nikhil.trust import router as trust_router
from Aayush.validate import router as validate_router
from Nikhil.passport import router as passport_router
from Nikhil.community import router as community_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router)
app.include_router(skills_router)
app.include_router(process_router)
app.include_router(credential_router)
app.include_router(verify_router)
app.include_router(trust_router)
app.include_router(validate_router)
app.include_router(passport_router)
app.include_router(community_router)


app.mount("/static", StaticFiles(directory="../Frontend", html=True), name="frontend")

@app.get("/")
def root():
    return {"status": "working", "project": "NEEV Skill Passport"}

@app.get("/ping")
def ping():
    return {"message": "pong"}