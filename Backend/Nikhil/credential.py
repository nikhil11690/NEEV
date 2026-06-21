from fastapi import FastAPI
from pydantic import BaseModel
import json
import qrcode
import io
import base64
from hasher import hash_dict

app = FastAPI()
class WorkerCredential(BaseModel):
    name: str
    skills: list[str]
    nsqf_levels: list[int]


@app.post("/generate-credential")
def generate_credential(worker: WorkerCredential):


    payload = {
        "name": worker.name,
        "skills": worker.skills,
        "nsqf_levels": worker.nsqf_levels
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
    img_bytes = buffer.getvalue()
    qr_base64 = base64.b64encode(img_bytes).decode("utf-8")

    return {
        "qr_code_base64": qr_base64,
        "hash": credential_hash
    }



