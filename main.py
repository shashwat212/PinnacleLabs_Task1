import re
import os
import shutil
import pdfplumber
import spacy
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

# ---------------- INITIAL SETUP ---------------- #

try:
    nlp = spacy.load("en_core_web_sm")
except:
    raise RuntimeError("spaCy model not found. Run: python -m spacy download en_core_web_sm")

app = FastAPI(title="AI Resume Parser API")

SKILL_SET = [
    "python", "java", "c++", "sql", "machine learning",
    "deep learning", "nlp", "fastapi", "django",
    "react", "node", "aws", "docker", "flask",
    "pandas", "numpy", "tensorflow", "pytorch"
]

# ---------------- PDF TEXT EXTRACTION ---------------- #

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception:
        raise HTTPException(status_code=400, detail="Error reading PDF file.")

# ---------------- FIELD EXTRACTION ---------------- #

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"\+?\d[\d -]{8,}\d", text)
    return match.group(0) if match else None

def extract_name(text):
    doc = nlp(text[:1000])  # Focus on top of resume
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text):
    text_lower = text.lower()
    found_skills = [skill for skill in SKILL_SET if skill in text_lower]
    return list(set(found_skills))

# ---------------- MATCHING ENGINE ---------------- #

def calculate_match(resume_skills, job_description):
    job_text = job_description.lower()

    job_skills = [skill for skill in SKILL_SET if skill in job_text]
    matched = [skill for skill in job_skills if skill in resume_skills]

    if not job_skills:
        return 0, [], job_skills

    score = (len(matched) / len(job_skills)) * 100
    return round(score, 2), matched, job_skills

# ---------------- API ENDPOINT ---------------- #

@app.post("/parse-resume/")
async def parse_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_file_path = "temp_resume.pdf"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_pdf(temp_file_path)

        if not text:
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")

        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)

        score, matched_skills, job_skills = calculate_match(skills, job_description)

        return {
            "candidate_name": name,
            "email": email,
            "phone": phone,
            "skills_found": skills,
            "job_required_skills": job_skills,
            "matched_skills": matched_skills,
            "match_score_percent": score
        }

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# ---------------- SIMPLE FRONTEND ---------------- #

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Parser</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                width: 400px;
            }
            h2 {
                text-align: center;
                margin-bottom: 20px;
            }
            input, textarea {
                width: 100%;
                padding: 8px;
                margin-bottom: 15px;
                border-radius: 5px;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            button {
                width: 100%;
                padding: 10px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            button:hover {
                background: #0056b3;
            }
            .note {
                text-align: center;
                font-size: 12px;
                color: gray;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>AI Resume Parser</h2>
            <form action="/parse-resume/" method="post" enctype="multipart/form-data">
                <label>Upload Resume (PDF)</label>
                <input type="file" name="file" required>

                <label>Job Description</label>
                <textarea name="job_description" rows="4" required></textarea>

                <button type="submit">Analyze Resume</button>
            </form>
            <div class="note">
                Use /docs for Swagger API testing
            </div>
        </div>
    </body>
    </html>
    """
