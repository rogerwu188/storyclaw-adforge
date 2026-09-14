from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json, uuid

app = FastAPI(title="StoryClaw AdForge", version="0.1.0")
DATA = Path("data/projects"); DATA.mkdir(parents=True, exist_ok=True)

class CreativeBrief(BaseModel):
    creative_idea: str
    product: str
    audience: str = "泛用户"
    selling_points: list[str] = []
    language: str = "中文"
    aspect_ratio: str = "16:9"
    duration_seconds: int = 60

@app.get("/healthz")
def healthz(): return {"status":"ok","service":"storyclaw-adforge"}

@app.post("/v1/projects")
def create_project(brief: CreativeBrief):
    pid = uuid.uuid4().hex
    payload = {"project_id": pid, "brief": brief.model_dump(), "status": "BRIEF_READY"}
    (DATA / f"{pid}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload
