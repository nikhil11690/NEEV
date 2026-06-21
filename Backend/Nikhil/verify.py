from fastapi import FastAPI
from pydantic import BaseModel
from hasher import hash_dict

app = FastAPI()

class VerifyPayload(BaseModel):
    data: dict
    hash: str

@app.post("/verify")
def verify_credential(payload: VerifyPayload):
     recalculated_hash = hash_dict(payload.data)
     is_valid = recalculated_hash == payload.hash
     return {
        "valid": is_valid,
        "worker_data": payload.data
    }
