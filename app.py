from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
from pipeline import run_pipeline, ingest_from_url

app = FastAPI(title="DeepShield Prototype API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestRequest(BaseModel):
    urls: Optional[List[str]] = None
    sources: Optional[List[str]] = None

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "ok", "path": dest}

@app.post("/ingest/url/")
async def ingest_url(url: str = Form(...)):
    path = ingest_from_url(url, UPLOAD_DIR)
    return {"status": "ok", "path": path}

@app.post("/analyze/")
async def analyze(paths: List[str]):
    result = run_pipeline(paths)
    return result
