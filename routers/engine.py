"""
AI Resume Analysis Engine — by Ansh Chawla
Rule-based intelligent scoring with AI-like natural language output.
Analyzes resume text against job descriptions and produces rich structured feedback.
"""

import re
import random
from typing import Optional


# ─────────────────────────────────────────────
#  KEYWORD BANKS  (role → required skills)
# ─────────────────────────────────────────────

ROLE_KEYWORD_MAP = {
    "software engineer": [
        "python", "java", "c++", "javascript", "typescript", "data structures",
        "algorithms", "system design", "git", "rest api", "microservices",
        "sql", "docker", "linux", "problem solving", "agile", "oop",
        "testing", "debugging", "leetcode", "competitive programming"
    ],
    "swe intern": [
        "python", "java", "c++", "data structures", "algorithms", "git",
        "object oriented", "sql", "javascript", "rest api", "github",
        "problem solving", "internship", "open source", "projects", "gpa"
    ],
    "full stack": [
        "react", "node.js", "express", "mongodb", "sql", "javascript",
        "typescript", "rest api", "html", "css", "docker", "aws",
        "git", "postgresql", "redis", "graphql", "next.js", "vue"
    ],
    "data scientist": [
        "python", "machine learning", "tensorflow", "pytorch", "pandas",
        "numpy", "scikit-learn", "sql", "statistics", "r", "jupyter",
        "data visualization", "matplotlib", "seaborn", "nlp", "deep learning",
        "feature engineering", "model deployment", "a/b testing", "big data"
    ],
    "machine learning": [
        "python", "tensorflow", "pytorch", "scikit-learn", "deep learning",
        "neural networks", "nlp", "computer vision", "mlops", "model deployment",
        "feature engineering", "pandas", "numpy", "transformers", "llm",
        "reinforcement learning", "data pipeline", "aws sagemaker", "docker"
    ],
    "product manager": [
        "product roadmap", "agile", "scrum", "user research", "a/b testing",
        "stakeholder", "jira", "confluence", "data analysis", "sql",
        "figma", "ux", "go-to-market", "kpi", "metrics", "prioritization",
        "cross-functional", "product strategy", "customer discovery"
    ],
    "devops": [
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd",
        "terraform", "ansible", "jenkins", "linux", "bash", "python",
        "monitoring", "grafana", "prometheus", "helm", "git", "nginx"
    ],
    "cybersecurity": [
        "penetration testing", "network security", "siem", "vulnerability",
        "incident response", "firewall", "python", "linux", "encryption",
        "comptia", "ethical hacking", "forensics", "risk assessment",
        "owasp", "threat analysis", "ids/ips", "compliance", "iso 27001"
    ],
    "ui ux": [
        "figma", "adobe xd", "sketch", "prototyping", "wireframing",
        "user research", "usability testing", "design systems", "accessibility",
        "css", "html", "interaction design", "information architecture",
        "responsive design", "typography", "color theory", "user journey"
    ],
    "android": [
        "kotlin", "java", "android sdk", "jetpack compose", "mvvm",
        "retrofit", "room", "firebase", "play store", "xml layouts",
        "gradle", "coroutines", "dependency injection", "hilt", "git"
    ],
    "ios": [
        "swift", "swiftui", "uikit", "xcode", "objective-c",
        "cocoapods", "spm", "mvvm", "combine", "core data",
        "app store", "firebase", "rest api", "git", "arkit"
    ],
    "backend": [
        "python", "java", "node.js", "go", "rust", "spring boot",
        "fastapi", "django", "rest api", "graphql", "sql", "nosql",
        "redis", "kafka", "microservices", "docker", "kubernetes", "aws"
    ],
    "data analyst": [
        "sql", "excel", "python", "tableau", "power bi", "pandas",
        "data visualization", "statistics", "r", "google analytics",
        "looker", "etl", "data cleaning", "reporting", "a/b testing"
    ],
    "cloud engineer": [
        "aws", "gcp", "azure", "terraform", "kubernetes", "docker",
        "lambda", "s3", "ec2", "vpc", "iam", "devops", "ci/cd",
        "cloudformation", "networking", "security", "cost optimization"
    ],
}

GENERIC_KEYWORDS = [
    "communication", "teamwork", "leadership", "problem solving",
    "time management", "project management", "collaboration",
    "analytical", "critical thinking", "presentation", "bachelor",
    "master", "degree", "gpa", "internship", "experience", "skills"
]

# ATS-critical formatting indicators
SECTION_HEADERS = [
    "education", "experience", "skills", "projects", "certifications",
    "achievements", "summary", "objective", "work experience", "publications",
    "volunteer", "awards", "languages", "interests", "references"
]

STRONG_ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "engineered", "created",
    "launched", "deployed", "optimized", "reduced", "increased", "improved",
    "led", "managed", "architected", "delivered", "automated", "integrated",
    "refactored", "analyzed", "researched", "collaborated", "mentored", "scaled"
]

QUANTIFICATION_PATTERNS = [
    r'\d+\s*%', r'\d+x', r'\$[\d,]+', r'\d+\s*(million|billion|thousand|k)\b',
    r'reduced.{0,30}\d+', r'increased.{0,30}\d+', r'\d+\s*(users|customers|clients)',
    r'\d+\s*(projects|applications|systems)', r'\d+\s*(team|people|engineers)',
    r'top\s*\d+', r'\d+\s*(awards|publications|papers)'
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e",
    "b.sc", "m.sc", "mba", "degree", "university", "college", "institute",
    "cgpa", "gpa", "percentage", "honors", "distinction", "graduated"
]

CERTIFICATION_KEYWORDS = [
    "certified", "certification", "aws certified", "google cloud", "azure",
    "comptia", "pmp", "scrum", "oracle", "cisco", "coursera", "udemy",
    "hackerrank", "leetcode", "kaggle", "microsoft certified"
]


# ─────────────────────────────────────────────
#  AI-STYLE MESSAGE BANKS
# ─────────────────────────────────────────────

VERDICT_MESSAGES = {
    "Excellent": [
        "Your resume demonstrates exceptional alignment with this role. The technical depth, quantified achievements, and well-structured narrative position you as a strong top-tier candidate. Minor refinements could push you to the very top of the applicant pool.",
        "This is a highly competitive resume. You've effectively showcased relevant experience with strong evidence of impact. The keyword density is solid and your profile reads like someone who has genuinely lived the role requirements.",
        "Outstanding profile. Your resume ticks nearly every box a hiring manager would look for — from technical keywords to quantified results. With a few targeted tweaks, this could be a near-perfect submission."
    ],
    "Good": [
        "You have a solid foundation with relevant skills and experience. The resume covers most key requirements but misses some specific keywords and impact metrics that top candidates typically highlight. Strategic additions will significantly boost your ATS ranking.",
        "A competent resume that clearly communicates your background. However, to stand out in a competitive applicant pool, you'll need to sharpen the language, add missing technical keywords, and quantify your contributions more precisely.",
        "Good alignment with the role, but there's noticeable room to strengthen your candidacy. The core story is there — it just needs tighter execution: stronger action verbs, more metrics, and filling keyword gaps that ATS systems prioritize."
    ],
    "Needs Work": [
        "Your resume has the raw material but lacks the polish and precision that modern ATS systems demand. Several critical keywords are absent, achievements are stated without impact metrics, and the structure may confuse automated parsers. A focused revision will make a real difference.",
        "While your background shows potential, this resume isn't yet optimized for the role you're targeting. Key technical skills appear to be missing or buried, and the narrative doesn't clearly connect your experience to the job's core requirements.",
        "There's a meaningful gap between what your resume currently communicates and what this role demands. The good news: most issues are fixable with targeted keyword additions and restructuring your experience bullets to lead with impact."
    ],
    "Weak": [
        "This resume needs significant work before submission. Critical skills and keywords required for this role are largely absent, there are few quantifiable achievements, and the structure may not parse well through ATS systems. A comprehensive rewrite is strongly recommended.",
        "As currently written, this resume is unlikely to pass initial ATS screening for this role. The skill gap appears substantial, and the document lacks the impact statements and industry-specific language that hiring algorithms prioritize. Consider a full revision starting with the skills section.",
        "The resume does not adequately represent your potential fit for this position. Core technical requirements are unaddressed, and the overall narrative lacks the specificity modern hiring systems expect. This needs a strategic overhaul focused on role-specific keywords and achievement-driven bullets."
    ]
}

IMPRESSION_LINES = {
    "Excellent": [
        "A polished, ATS-ready resume that signals genuine readiness for this role.",
        "Strong technical credibility backed by clear, impactful evidence.",
        "This candidate looks the part — on paper and in substance."
    ],
    "Good": [
        "A solid application that could rank highly with targeted refinements.",
        "Good bones — needs keyword optimization and stronger quantification.",
        "Competitive, but the top 10% of applicants will have sharper profiles."
    ],
    "Needs Work": [
        "The experience is there, but the presentation isn't doing it justice.",
        "Needs a focused ATS overhaul before this can compete effectively.",
        "The resume undersells the candidate — a common but fixable problem."
    ],
    "Weak": [
        "Significant gaps between the resume's current state and role requirements.",
        "Needs a ground-up revision to become ATS-competitive for this role.",
        "This resume will struggle to clear automated screening as-is."
    ]
}

SUGGESTION_POOL = {
    "no_metrics": {
        "priority": "high", "icon": "🔴",
        "title": "Add Quantified Impact to Every Bullet",
        "text": "Your experience bullets are mostly descriptive rather than achievement-focused. Recruiters and ATS systems heavily favor statements like 'Reduced API latency by 40%' over 'Worked on backend services.' Go through each bullet and ask: what changed because of my work, and by how much?"
    },
    "weak_verbs": {
        "priority": "high", "icon": "🔴",
        "title": "Replace Passive Language with Strong Action Verbs",
        "text": "Several bullet points start with weak phrases like 'Responsible for' or 'Helped with.' These dilute your impact. Start every bullet with a powerful action verb: Engineered, Deployed, Architected, Optimized, Delivered. This signals ownership and initiative immediately."
    },
    "missing_summary": {
        "priority": "medium", "icon": "🟡",
        "title": "Add a Targeted Professional Summary",
        "text": "A 2–3 line summary at the top is your first impression — both to the ATS and the human recruiter. It should mirror the job title, include 2–3 core skills, and hint at your biggest achievement. Think of it as the tweet-length pitch for your candidacy."
    },
    "keyword_gap": {
        "priority": "high", "icon": "🔴",
        "title": "Close Critical Keyword Gaps",
        "text": "Several high-priority keywords from the job description are missing from your resume. ATS systems use exact or near-exact keyword matching — if the JD says 'Kubernetes' and you only write 'container orchestration,' you may not pass the filter. Add the missing terms naturally within your experience or skills section."
    },
    "no_projects": {
        "priority": "medium", "icon": "🟡",
        "title": "Strengthen the Projects Section",
        "text": "For technical roles, projects are often weighted as heavily as internship experience — especially for early-career candidates. Each project should mention: the problem solved, the technologies used, and a measurable outcome. Link to GitHub or a live demo when possible."
    },
    "no_certifications": {
        "priority": "low", "icon": "🟢",
        "title": "Consider Adding Relevant Certifications",
        "text": "Role-specific certifications signal commitment and validated knowledge to hiring teams. For this type of role, certifications from AWS, Google, Coursera, or HackerRank can give you an edge — especially if your formal experience in a technology is limited."
    },
    "education_weak": {
        "priority": "medium", "icon": "🟡",
        "title": "Enrich Your Education Section",
        "text": "Your education section appears thin. Consider adding: CGPA/GPA (if above 7.5/3.5), relevant coursework, academic projects, honors, or clubs/societies related to the field. These details matter for campus recruiting and help ATS parse your academic background accurately."
    },
    "format_issue": {
        "priority": "high", "icon": "🔴",
        "title": "Optimize Resume Structure for ATS Parsing",
        "text": "ATS software can struggle with non-standard layouts, tables, headers/footers, and columns. Use a clean single-column format, standard section headings (Education, Experience, Skills), and avoid placing critical information in text boxes or graphics which parsers often skip entirely."
    },
    "skills_section": {
        "priority": "medium", "icon": "🟡",
        "title": "Create a Dedicated, Scannable Skills Section",
        "text": "A clearly labeled 'Technical Skills' or 'Skills' section near the top of your resume helps ATS systems instantly match your profile to job requirements. Group skills by category: Languages, Frameworks, Tools, Databases. Avoid rating bars or star systems — they mean nothing to ATS."
    },
    "generic_language": {
        "priority": "low", "icon": "🟢",
        "title": "Eliminate Generic Filler Phrases",
        "text": "Phrases like 'hardworking team player,' 'passionate about technology,' or 'excellent communication skills' appear on thousands of resumes and add no signal. Replace every generic claim with a specific, evidence-backed statement that demonstrates the trait instead of asserting it."
    },
    "one_page": {
        "priority": "low", "icon": "🟢",
        "title": "Aim for a Tight One-Page Format (for <5 yrs experience)",
        "text": "For candidates with fewer than 5 years of experience, a one-page resume is the industry standard. Trim older or less-relevant bullets, consolidate similar roles, and cut anything that doesn't directly support your candidacy for this specific role. Every line should earn its spot."
    },
    "contact_info": {
        "priority": "medium", "icon": "🟡",
        "title": "Verify Contact & Profile Links are Complete",
        "text": "Ensure your resume includes: a professional email, phone number, LinkedIn URL, and GitHub/portfolio link (for technical roles). Missing or broken links are a surprisingly common reason candidates get dropped. Triple-check that every URL is live and correctly formatted."
    }
}

ATS_TIPS_POOL = [
    "Use standard fonts like Arial, Calibri, or Times New Roman — decorative fonts can break ATS parsing.",
    "Save your resume as a .docx or simple PDF without embedded fonts or images for best ATS compatibility.",
    "Mirror the exact job title from the posting somewhere in your resume — ATS systems often rank this highly.",
    "Avoid putting critical information in headers, footers, or text boxes — many ATS systems skip these entirely.",
    "Use both the spelled-out form and acronym for key terms, e.g., 'Machine Learning (ML)' to maximize keyword matching.",
    "Tailor your resume for each application — a generic resume typically scores 20-30 points lower on ATS than a targeted one.",
    "Keep file names professional: 'FirstName_LastName_Resume.pdf' is far better than 'resume_final_v3.pdf'.",
    "Use bullet points, not paragraphs — ATS systems and human readers both process lists faster and more accurately.",
]

STRENGTH_TEMPLATES = {
    "has_metrics": "Demonstrates measurable impact — quantified achievements signal results-oriented thinking to recruiters.",
    "has_projects": "Strong project portfolio that goes beyond coursework and shows initiative and practical application.",
    "has_certifications": "Relevant certifications validate technical knowledge and show commitment to continuous learning.",
    "has_github": "GitHub/portfolio link provides recruiters with tangible evidence of technical capability.",
    "has_education": "Educational background is clearly presented and easy for ATS to parse and score.",
    "has_summary": "Professional summary effectively frames the candidate's value proposition upfront.",
    "strong_verbs": "Strong action verbs throughout give bullet points energy and convey ownership.",
    "good_length": "Resume length appears appropriate — comprehensive without being overwhelming.",
    "has_skills_section": "Dedicated skills section makes it easy for ATS to extract and match technical competencies.",
    "has_linkedin": "LinkedIn profile linked — recruiters almost always verify this and it adds credibility.",
    "keyword_density": "Good keyword density for the target role, increasing likelihood of passing ATS filters.",
    "multiple_sections": "Well-organized structure with clear section headings aids both ATS parsing and human readability.",
}

QUICK_WIN_TEMPLATES = [
    "Add the top 5 missing keywords from the job description naturally within your existing bullet points — this alone can boost your ATS score by 15–25 points.",
    "Convert 3–4 descriptive bullets into achievement statements using the formula: 'Action Verb + Task + Result + Metric.'",
    "Paste your resume into a plain text editor — if it looks garbled, your ATS formatting needs work before submission.",
    "Add a 2-line technical summary at the top that includes your target role title and your strongest 3 skills.",
    "Move your most impressive project or achievement to the top of the relevant section — recruiters spend ~6 seconds on a first pass.",
    "Spell-check every technical term — a misspelled technology name (e.g., 'Pyhton' instead of 'Python') will fail keyword matching.",
    "Add GitHub/LinkedIn if missing — 87% of recruiters check profiles before interview decisions.",
    "Consolidate your skills into a scannable grid or comma-separated list under clear categories.",
    "Remove graduation year if you graduated more than 5 years ago to avoid age bias from automated filters.",
    "Ensure every section uses a standard heading name — 'Work History' is better recognized by ATS than 'Where I've Been.'",
]


# ─────────────────────────────────────────────
#  CORE ANALYSIS ENGINE
# ─────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Main analysis function. Scores the resume across multiple dimensions
    and returns a rich structured response.
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # ── 1. Detect target role ──
    target_role = _detect_role(jd_lower)
    role_keywords = _get_role_keywords(target_role, jd_lower)

    # ── 2. Extract candidate name ──
    candidate_name = _extract_name(resume_text)

    # ── 3. Score individual sections ──
    keyword_score = _score_keywords(resume_lower, role_keywords)
    formatting_score = _score_formatting(resume_text, resume_lower)
    experience_score = _score_experience(resume_lower)
    impact_score = _score_impact(resume_text, resume_lower)
    skills_score = _score_skills(resume_lower, role_keywords)
    education_score = _score_education(resume_lower)
    projects_score = _score_projects(resume_lower)

    sections = {
        "keywords": keyword_score,
        "formatting": formatting_score,
        "experience": experience_score,
        "impact": impact_score,
        "skills": skills_score,
        "education": education_score,
        "projects": projects_score,
    }

    # ── 4. Composite ATS Score ──
    weights = {
        "keywords": 0.28,
        "formatting": 0.12,
        "experience": 0.20,
        "impact": 0.15,
        "skills": 0.13,
        "education": 0.07,
        "projects": 0.05,
    }
    raw_score = sum(sections[k] * weights[k] for k in weights)
    # Add small random variance to feel less mechanical
    variance = random.uniform(-2.5, 2.5)
    ats_score = max(10, min(98, round(raw_score + variance)))

    # ── 5. Verdict ──
    verdict = _get_verdict(ats_score)

    # ── 6. Keywords ──
    matched, missing = _get_keywords(resume_lower, role_keywords)

    # ── 7. Suggestions ──
    suggestions = _build_suggestions(resume_text, resume_lower, jd_lower, matched, missing, sections)

    # ── 8. Strengths ──
    strengths = _build_strengths(resume_text, resume_lower, sections, matched)

    # ── 9. Quick Wins ──
    quick_wins = _build_quick_wins(resume_lower, missing, sections)

    # ── 10. ATS Tips ──
    ats_tips = random.sample(ATS_TIPS_POOL, 3)

    # ── 11. Natural Language Messages ──
    verdict_description = random.choice(VERDICT_MESSAGES[verdict])
    overall_impression = random.choice(IMPRESSION_LINES[verdict])

    return {
        "ats_score": ats_score,
        "verdict": verdict,
        "verdict_description": verdict_description,
        "overall_impression": overall_impression,
        "candidate_name": candidate_name,
        "target_role": _format_role(target_role),
        "sections": sections,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "strengths": strengths,
        "quick_wins": quick_wins,
        "ats_tips": ats_tips,
    }


# ─────────────────────────────────────────────
#  SCORING FUNCTIONS
# ─────────────────────────────────────────────

def _score_keywords(resume_lower: str, role_keywords: list) -> int:
    if not role_keywords:
        return 55
    found = sum(1 for kw in role_keywords if kw in resume_lower)
    ratio = found / len(role_keywords)
    score = int(ratio * 100)
    return max(10, min(98, score))


def _score_formatting(resume_text: str, resume_lower: str) -> int:
    score = 40
    # Section headers present
    headers_found = sum(1 for h in SECTION_HEADERS if h in resume_lower)
    score += min(headers_found * 7, 35)
    # Reasonable length (400–1500 words is ideal)
    words = len(resume_text.split())
    if 300 <= words <= 800:
        score += 15
    elif 200 <= words < 300 or 800 < words <= 1200:
        score += 8
    # Has bullet points (common indicators)
    bullet_indicators = resume_text.count('•') + resume_text.count('-') + resume_text.count('*')
    if bullet_indicators >= 5:
        score += 10
    return max(20, min(95, score))


def _score_experience(resume_lower: str) -> int:
    score = 30
    # Action verbs
    found_verbs = sum(1 for v in STRONG_ACTION_VERBS if v in resume_lower)
    score += min(found_verbs * 4, 30)
    # Year mentions (work timeline)
    years = re.findall(r'\b(20[0-2]\d|19[89]\d)\b', resume_lower)
    if len(years) >= 2:
        score += 20
    elif len(years) == 1:
        score += 10
    # Role-related terms
    exp_terms = ["experience", "worked", "position", "role", "responsibilities", "duties"]
    found_exp = sum(1 for t in exp_terms if t in resume_lower)
    score += min(found_exp * 3, 20)
    return max(15, min(95, score))


def _score_impact(resume_text: str, resume_lower: str) -> int:
    score = 20
    # Quantification patterns
    metrics_found = 0
    for pattern in QUANTIFICATION_PATTERNS:
        if re.search(pattern, resume_lower):
            metrics_found += 1
    score += min(metrics_found * 8, 50)
    # Action verbs
    found_verbs = sum(1 for v in STRONG_ACTION_VERBS if v in resume_lower)
    score += min(found_verbs * 3, 30)
    return max(10, min(95, score))


def _score_skills(resume_lower: str, role_keywords: list) -> int:
    score = 20
    # Has a skills section
    if any(h in resume_lower for h in ["skills", "technical skills", "technologies", "tech stack"]):
        score += 25
    # Keyword overlap
    if role_keywords:
        found = sum(1 for kw in role_keywords if kw in resume_lower)
        score += int((found / len(role_keywords)) * 55)
    return max(15, min(97, score))


def _score_education(resume_lower: str) -> int:
    score = 20
    found = sum(1 for kw in EDUCATION_KEYWORDS if kw in resume_lower)
    score += min(found * 8, 60)
    # GPA mention
    if re.search(r'(gpa|cgpa|percentage|%)\s*[:\-]?\s*[\d.]+', resume_lower):
        score += 15
    return max(20, min(97, score))


def _score_projects(resume_lower: str) -> int:
    score = 20
    if "project" in resume_lower:
        score += 30
    # GitHub
    if "github" in resume_lower or "git" in resume_lower:
        score += 20
    # Number of project-like entries
    project_count = len(re.findall(r'project\b', resume_lower))
    score += min(project_count * 8, 30)
    return max(10, min(95, score))


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _detect_role(jd_lower: str) -> str:
    best_role = "software engineer"
    best_count = 0
    for role, keywords in ROLE_KEYWORD_MAP.items():
        count = sum(1 for kw in [role] + role.split() if kw in jd_lower)
        if count > best_count:
            best_count = count
            best_role = role
    return best_role


def _get_role_keywords(role: str, jd_lower: str) -> list:
    base = ROLE_KEYWORD_MAP.get(role, ROLE_KEYWORD_MAP["software engineer"])
    # Also extract any tech terms from the JD directly
    extra = []
    common_techs = [
        "react", "angular", "vue", "python", "java", "node", "django", "flask",
        "fastapi", "spring", "aws", "azure", "gcp", "docker", "kubernetes",
        "postgres", "mysql", "mongodb", "redis", "kafka", "spark", "hadoop",
        "tensorflow", "pytorch", "numpy", "pandas", "scikit", "git", "linux",
        "typescript", "graphql", "rest", "grpc", "microservices", "agile", "scrum"
    ]
    for tech in common_techs:
        if tech in jd_lower and tech not in base:
            extra.append(tech)
    return list(set(base + extra + GENERIC_KEYWORDS))


def _get_keywords(resume_lower: str, role_keywords: list) -> tuple:
    matched = []
    missing = []
    # Only pick meaningful keywords (not super generic)
    meaningful = [kw for kw in role_keywords if len(kw) > 3 and kw not in GENERIC_KEYWORDS]
    for kw in meaningful:
        if kw in resume_lower:
            matched.append(kw)
        else:
            missing.append(kw)
    # Limit display lists
    random.shuffle(matched)
    random.shuffle(missing)
    return matched[:10], missing[:10]


def _extract_name(resume_text: str) -> str:
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    if not lines:
        return "Candidate"
    first_line = lines[0]
    # Heuristic: first line, 2-4 words, all words start with capital
    words = first_line.split()
    if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
        return first_line
    return "Candidate"


def _get_verdict(score: int) -> str:
    if score >= 78:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 42:
        return "Needs Work"
    return "Weak"


def _format_role(role: str) -> str:
    role_display = {
        "software engineer": "Software Engineer",
        "swe intern": "SWE Intern",
        "full stack": "Full Stack Developer",
        "data scientist": "Data Scientist",
        "machine learning": "ML Engineer",
        "product manager": "Product Manager",
        "devops": "DevOps / Cloud Engineer",
        "cybersecurity": "Cybersecurity Analyst",
        "ui ux": "UI/UX Designer",
        "android": "Android Developer",
        "ios": "iOS Developer",
        "backend": "Backend Engineer",
        "data analyst": "Data Analyst",
        "cloud engineer": "Cloud Engineer",
    }
    return role_display.get(role, role.title())


def _build_suggestions(resume_text, resume_lower, jd_lower, matched, missing, sections) -> list:
    pool = []

    if sections["impact"] < 55:
        pool.append(SUGGESTION_POOL["no_metrics"])
    if sum(1 for v in STRONG_ACTION_VERBS if v in resume_lower) < 5:
        pool.append(SUGGESTION_POOL["weak_verbs"])
    if "summary" not in resume_lower and "objective" not in resume_lower:
        pool.append(SUGGESTION_POOL["missing_summary"])
    if len(missing) >= 5:
        pool.append(SUGGESTION_POOL["keyword_gap"])
    if sections["projects"] < 50:
        pool.append(SUGGESTION_POOL["no_projects"])
    if not any(c in resume_lower for c in CERTIFICATION_KEYWORDS):
        pool.append(SUGGESTION_POOL["no_certifications"])
    if sections["education"] < 50:
        pool.append(SUGGESTION_POOL["education_weak"])
    if sections["formatting"] < 55:
        pool.append(SUGGESTION_POOL["format_issue"])
    if "skills" not in resume_lower and "technologies" not in resume_lower:
        pool.append(SUGGESTION_POOL["skills_section"])
    if any(ph in resume_lower for ph in ["hardworking", "passionate", "team player", "quick learner"]):
        pool.append(SUGGESTION_POOL["generic_language"])
    if len(resume_text.split()) > 700:
        pool.append(SUGGESTION_POOL["one_page"])
    if "linkedin" not in resume_lower or "github" not in resume_lower:
        pool.append(SUGGESTION_POOL["contact_info"])

    # Deduplicate and return top 5
    seen = set()
    result = []
    for s in pool:
        key = s["title"]
        if key not in seen:
            seen.add(key)
            result.append(s)
        if len(result) == 5:
            break

    # Pad if fewer than 5
    all_suggestions = list(SUGGESTION_POOL.values())
    random.shuffle(all_suggestions)
    for s in all_suggestions:
        if len(result) >= 5:
            break
        if s["title"] not in seen:
            seen.add(s["title"])
            result.append(s)

    return result[:5]


def _build_strengths(resume_text, resume_lower, sections, matched) -> list:
    strengths = []
    metrics_found = sum(1 for p in QUANTIFICATION_PATTERNS if re.search(p, resume_lower))
    if metrics_found >= 2:
        strengths.append(STRENGTH_TEMPLATES["has_metrics"])
    if "project" in resume_lower and sections["projects"] >= 50:
        strengths.append(STRENGTH_TEMPLATES["has_projects"])
    if any(c in resume_lower for c in CERTIFICATION_KEYWORDS):
        strengths.append(STRENGTH_TEMPLATES["has_certifications"])
    if "github" in resume_lower:
        strengths.append(STRENGTH_TEMPLATES["has_github"])
    if sections["education"] >= 60:
        strengths.append(STRENGTH_TEMPLATES["has_education"])
    if "summary" in resume_lower or "objective" in resume_lower:
        strengths.append(STRENGTH_TEMPLATES["has_summary"])
    if sum(1 for v in STRONG_ACTION_VERBS if v in resume_lower) >= 5:
        strengths.append(STRENGTH_TEMPLATES["strong_verbs"])
    if "skills" in resume_lower or "technologies" in resume_lower:
        strengths.append(STRENGTH_TEMPLATES["has_skills_section"])
    if "linkedin" in resume_lower:
        strengths.append(STRENGTH_TEMPLATES["has_linkedin"])
    if len(matched) >= 6:
        strengths.append(STRENGTH_TEMPLATES["keyword_density"])
    if sum(1 for h in SECTION_HEADERS if h in resume_lower) >= 4:
        strengths.append(STRENGTH_TEMPLATES["multiple_sections"])

    random.shuffle(strengths)
    # Always return at least 2
    if len(strengths) < 2:
        strengths = [
            STRENGTH_TEMPLATES["multiple_sections"],
            STRENGTH_TEMPLATES["has_education"]
        ]
    return strengths[:4]


def _build_quick_wins(resume_lower, missing, sections) -> list:
    wins = list(QUICK_WIN_TEMPLATES)
    random.shuffle(wins)
    return wins[:4]
