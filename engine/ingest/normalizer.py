import re
from typing import Dict, Tuple, List, Optional

STATE_MAPPINGS: Dict[str, str] = {
    "pune": "Maharashtra",
    "mumbai": "Maharashtra",
    "nagpur": "Maharashtra",
    "nashik": "Maharashtra",
    "thane": "Maharashtra",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mysore": "Karnataka",
    "hyderabad": "Telangana",
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "delhi": "Delhi",
    "noida": "Uttar Pradesh",
    "gurgaon": "Haryana",
    "gurugram": "Haryana",
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "pune area": "Maharashtra",
    "mumbai area": "Maharashtra",
}

NCO_CODE_BOOTSTRAP: Dict[str, Tuple[str, str]] = {
    "software engineer": ("2512.0100", "Software Developer"),
    "data scientist": ("2511.0100", "Data Analyst / Scientist"),
    "data analyst": ("2511.0100", "Data Analyst / Scientist"),
    "machine learning engineer": ("2512.0200", "AI/ML Specialist"),
    "python developer": ("2512.0100", "Software Developer"),
    "full stack developer": ("2512.0100", "Software Developer"),
    "frontend developer": ("2512.0300", "Web Developer"),
    "backend developer": ("2512.0100", "Software Developer"),
    "devops engineer": ("2519.0100", "Systems Administrator / DevOps"),
    "automotive technician": ("7231.0100", "Motor Vehicle Mechanic"),
    "electric vehicle engineer": ("2144.0200", "Automotive Engineer"),
    "solar technician": ("7411.0200", "Solar Photovoltaic Installer"),
    "electrician": ("7411.0100", "Electrician"),
    "welder": ("7212.0100", "Welder and Flame Cutter"),
    "cnc operator": ("7223.0100", "CNC Machine Operator"),
    "nurse": ("2221.0100", "Registered Nurse"),
    "pharmacist": ("2262.0100", "Pharmacist"),
}

SKILL_LEXICON: List[str] = [
    "Python", "Java", "SQL", "C++", "JavaScript", "React", "Node.js", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Pandas", "Scikit-Learn", "FastAPI", "Django", "Git", "Linux", "AutoCAD", "PLC",
    "CNC Programming", "Electric Vehicle", "Battery Management System", "Solar Energy",
    "Welding", "Quality Control", "ISO 9001", "Supply Chain", "Six Sigma"
]

class LocationNormalizer:
    @staticmethod
    def normalize(location_raw: str) -> Tuple[Optional[str], Optional[str]]:
        if not location_raw or not isinstance(location_raw, str):
            return "Unspecified", "Unspecified"
            
        text = location_raw.lower().strip()
        for key, state in STATE_MAPPINGS.items():
            if key in text:
                district = key.title() if key in ["pune", "mumbai", "nagpur", "nashik", "bengaluru", "hyderabad", "chennai"] else "Unspecified"
                return state, district
                
        if "maharashtra" in text:
            return "Maharashtra", "Unspecified"
        if "karnataka" in text:
            return "Karnataka", "Unspecified"
        if "tamil nadu" in text:
            return "Tamil Nadu", "Unspecified"
        if "telangana" in text:
            return "Telangana", "Unspecified"
        if "delhi" in text:
            return "Delhi", "Delhi"
            
        return "All India", "Unspecified"

class NCOMapper:
    @staticmethod
    def map_title_to_nco(job_title: str) -> Tuple[str, str]:
        if not job_title or not isinstance(job_title, str):
            return "9999.0000", "Unclassified Occupation"
            
        title_lower = job_title.lower().strip()
        for key, (code, canonical_title) in NCO_CODE_BOOTSTRAP.items():
            if key in title_lower:
                return code, canonical_title
                
        return "2512.9900", "Other Information Technology Professional"

class SkillExtractor:
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        if not text or not isinstance(text, str):
            return []
            
        found_skills = []
        for skill in SKILL_LEXICON:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)
                
        return list(set(found_skills))
