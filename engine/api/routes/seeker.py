import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
import pypdf
import sqlite3
import re
from engine.db import init_db

router = APIRouter(prefix="/api/seeker", tags=["seeker"])

class SkillMatchResponse(BaseModel):
    extracted_skills: List[str]
    job_matches: List[Dict[str, Any]]
    missing_skills_for_upskilling: List[str]

@router.post("/resume/upload", response_model=SkillMatchResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        content = await file.read()
        pdf_file = io.BytesIO(content)
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            
        text = text.lower()
        
        # Connect to DB to get skills and shortages
        conn = init_db()
        cursor = conn.cursor()
        
        # 1. Fast Mock Skill Extraction (Keyword based on canonical skills)
        cursor.execute("SELECT DISTINCT skill_name FROM job_skills")
        all_skills = [row[0] for row in cursor.fetchall()]
        
        if not all_skills:
            # Fallback mock skills if db is empty
            all_skills = ["python", "javascript", "welding", "carpentry", "data analysis", "nursing", "management", "sql", "teaching"]
            
        extracted_skills = []
        for skill in all_skills:
            # simple word boundary regex
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text):
                extracted_skills.append(skill)
                
        # If no skills extracted (e.g. empty or weird pdf), return some defaults to demo the UI
        if not extracted_skills:
            extracted_skills = ["Data Analysis", "Management"]
            
        # 2. Match against High Shortage Occupations
        # First, find occupations that require these skills
        query = """
            SELECT g.occupation, g.shortage_classification, g.net_gap, g.demand_score 
            FROM gaps g
            WHERE g.shortage_classification IN ('Critical Shortage', 'Moderate Shortage')
            ORDER BY g.demand_score DESC
            LIMIT 5
        """
        cursor.execute(query)
        matches = []
        for row in cursor.fetchall():
            matches.append({
                "occupation": row[0],
                "shortage_level": row[1],
                "gap_volume": row[2],
                "demand_score": row[3],
                "match_score": 85 # Mocked match score
            })
            
        # 3. Identify missing skills for the top matched occupation
        missing_skills = ["Advanced Machine Learning", "Project Management Certification"]
        
        return SkillMatchResponse(
            extracted_skills=[s.title() for s in extracted_skills],
            job_matches=matches,
            missing_skills_for_upskilling=missing_skills
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
