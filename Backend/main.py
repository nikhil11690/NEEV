from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Aayush.transcribe import router as transcribe_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router)

@app.get("/")
def root():
    return {"status": "working", "project": "ROZGAAR Skill Passport"}

@app.get("/ping")
def ping():
    return {"message": "pong"}