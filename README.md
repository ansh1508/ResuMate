# 🧠 AI Resume Analyzer
### by Ansh Chawla · FastAPI + Intelligent Rule Engine

A production-ready resume analysis web app built on **FastAPI**. No external AI API needed —
the analysis engine uses sophisticated rule-based scoring with natural language output that reads
like genuine AI feedback.

---

## 📁 Project Structure

```
ai-resume-analyzer/
├── main.py                    ← FastAPI app entry point
├── requirements.txt           ← Python dependencies
├── routers/
│   ├── __init__.py
│   ├── analyzer.py            ← /api/analyze and /api/roles endpoints
│   ├── engine.py              ← Core scoring & NL generation engine
│   └── extractor.py          ← PDF (PyMuPDF) + DOCX text extraction
├── templates/
│   └── index.html             ← Jinja2 template (all 4 screens)
└── static/
    ├── css/style.css          ← Full dark-theme stylesheet
    └── js/app.js              ← Frontend logic + Chart.js rendering
```

---

## 🚀 Setup & Run

### 1. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in browser
```
http://localhost:8000
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | **FastAPI** |
| ASGI Server | **Uvicorn** |
| PDF Parsing | **PyMuPDF (fitz)** |
| DOCX Parsing | **python-docx** |
| File Uploads | **python-multipart** |
| ML Utilities | **scikit-learn** |
| Templating | **Jinja2** |
| Charts | **Chart.js** (CDN) |
| Fonts | **Google Fonts** (Syne + DM Sans) |

---

## 🎯 Analysis Engine

The engine (`routers/engine.py`) scores resumes across **7 dimensions**:

| Dimension | Weight | What it measures |
|---|---|---|
| Keywords | 28% | Match rate of role-specific tech terms |
| Experience | 20% | Action verbs, timelines, role history |
| Impact | 15% | Quantified metrics, numbers, achievements |
| Formatting | 12% | Section headers, structure, length |
| Skills | 13% | Dedicated skills section + keyword density |
| Education | 7% | Degree, GPA, academic content |
| Projects | 5% | Project mentions, GitHub links |

### Role Coverage
The engine recognizes and optimizes keyword scoring for:
- Software Engineering (Intern / Senior)
- Full Stack Development
- Data Science / ML Engineering
- Product Management
- DevOps / Cloud Engineering
- Cybersecurity
- UI/UX Design
- Android / iOS Development
- Backend Engineering
- Data Analysis / Cloud Engineering

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the main web app |
| POST | `/api/analyze` | Analyze a resume (multipart/form-data) |
| GET | `/api/roles` | Get list of quick-select roles |
| GET | `/health` | Health check |

### POST /api/analyze

**Request:** `multipart/form-data`
- `resume`: File (PDF or DOCX, max 10MB)
- `job_description`: String (min 10 chars)

**Response:** JSON with full analysis

```json
{
  "ats_score": 74,
  "verdict": "Good",
  "verdict_description": "...",
  "overall_impression": "...",
  "candidate_name": "John Doe",
  "target_role": "Software Engineer",
  "sections": {
    "keywords": 80,
    "formatting": 75,
    "experience": 70,
    "impact": 55,
    "skills": 85,
    "education": 90,
    "projects": 65
  },
  "matched_keywords": [...],
  "missing_keywords": [...],
  "suggestions": [...],
  "strengths": [...],
  "quick_wins": [...],
  "ats_tips": [...]
}
```

---

## 📝 License
Built by **Ansh Chawla**. Free to use, modify, and deploy.
