import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid, logging
from datetime import datetime
from pipeline import run_pipeline, run_comparison

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Intelligence API", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Datathon API is running"}

jobs: Dict[str, Dict[str, Any]] = {}

class AnalyzeRequest(BaseModel):
    query: str
    max_per_site: Optional[int] = 5

class CompareRequest(BaseModel):
    job_id: str
    seller_brand: str

def _run_job(job_id: str, query: str, max_per_site: int):
    jobs[job_id]["status"] = "running"
    try:
        result = run_pipeline(query, max_per_site=max_per_site)
        jobs[job_id].update({"status": "done", "result": result, "completed_at": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        jobs[job_id].update({"status": "error", "error": str(e), "completed_at": datetime.now().isoformat()})

@app.get("/health")
def health():
    groq = bool(os.getenv("GROQ_API_KEY"))
    openai = bool(os.getenv("OPENAI_API_KEY"))
    scraper_api = bool(os.getenv("SCRAPER_API_KEY"))
    serpapi = bool(os.getenv("SERPAPI_KEY"))
    return {
        "status": "ok",
        "version": "2.0.0",
        "groq_configured": groq,
        "openai_configured": openai,
        "scraper_api_configured": scraper_api,
        "serpapi_configured": serpapi,
        "scraping_mode": (
            "serpapi" if serpapi else
            "scraperapi_enhanced" if scraper_api else
            "direct_ebay_walmart"
        ),
        "llm_mode": "groq" if groq else ("openai" if openai else "keyword_only"),
        "ready": groq or openai,
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id, "status": "pending", "result": None,
        "error": None, "created_at": datetime.now().isoformat(), "completed_at": None
    }
    background_tasks.add_task(_run_job, job_id, req.query.strip(), req.max_per_site)
    return jobs[job_id]

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/jobs")
def list_jobs():
    return {"jobs": list(jobs.values())}

@app.post("/compare")
def compare(req: CompareRequest):
    """Run gap analysis for a selected seller brand against competitors."""
    if req.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[req.job_id]
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    if not job.get("result"):
        raise HTTPException(status_code=400, detail="No result available")
    result = run_comparison(job["result"], req.seller_brand)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/analyze/sync")
def analyze_sync(req: AnalyzeRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return run_pipeline(req.query.strip(), max_per_site=req.max_per_site)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
