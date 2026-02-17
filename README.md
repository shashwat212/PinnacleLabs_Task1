# AI Resume Parser & Skill Matching API

An AI-powered Resume Parsing and Skill Matching system built using **FastAPI** and **spaCy**.  
The application extracts structured information from resumes, detects technical skills, and matches them against job descriptions to assist in recruitment workflows.

---

## Features

- Extracts **Name, Email, Phone** from PDF resumes  
- Detects technical skills automatically  
- Matches resume skills against job description requirements  
- Returns structured **JSON output**  
- Provides clean UI with integrated **Swagger documentation**  

---

## Tech Stack

- **Programming Language:** Python  
- **Framework:** FastAPI  
- **NLP Library:** spaCy  
- **PDF Processing:** pdfplumber  
- **Server:** Uvicorn  

---

## How to Run

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

3. Start the application:
```bash
uvicorn main:app --reload
```

4. Open in browser:
```
http://127.0.0.1:8000/
```

---

## Author

**Shashwat Gupta**  
Developed as part of an AI/ML internship project, showcasing applied skills in NLP and API development.  
GitHub: `https://github.com/shashwat212` [(github.com in Bing)](https://www.bing.com/search?q="https%3A%2F%2Fgithub.com%2Fshashwat212")
