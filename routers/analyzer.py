import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from routers.extractor import extract_text_from_bytes
from routers.engine import analyze_resume

router = APIRouter()


@router.post("/analyze")
async def analyze(resume: UploadFile = File(...), job_description: str = Form(...)):
    filename = resume.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await resume.read()

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(status_code=400, detail="Job description too short")

    try:
        resume_text = extract_text_from_bytes(content, resume.filename)
        result = analyze_resume(resume_text, job_description)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles")
async def get_roles():
    return {
        "roles": [
            {"id": "swe_intern",      "label": "SWE Intern",      "icon": "💻", "company": "Tech / FAANG"},
            {"id": "full_stack",      "label": "Full Stack Dev",   "icon": "🌐", "company": "Startup / Product"},
            {"id": "data_scientist",  "label": "Data Scientist",   "icon": "🔬", "company": "Analytics / ML"},
            {"id": "ml_engineer",     "label": "ML Engineer",      "icon": "🤖", "company": "AI / Research"},
            {"id": "product_manager", "label": "Product Manager",  "icon": "📊", "company": "SaaS / Consumer"},
            {"id": "devops",          "label": "DevOps Engineer",  "icon": "☁️", "company": "Cloud / Infra"},
            {"id": "ui_ux",           "label": "UI/UX Designer",   "icon": "🎨", "company": "Design / Agency"},
            {"id": "cybersecurity",   "label": "Cybersecurity",    "icon": "🔐", "company": "Security / Defense"},
        ]
    }
