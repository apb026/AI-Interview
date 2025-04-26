# app/utils/resume_parser.py
import os
import pytesseract
from PIL import Image
import PyPDF2
import docx
import io
from typing import Dict, Any, Optional

class ResumeParser:
    """Utility class for parsing resume files"""
    
    def __init__(self, ai_service=None):
        """
        Initialize resume parser
        
        Args:
            ai_service: AI service for text analysis
        """
        self.ai_service = ai_service
    
    def parse(self, file_data: bytes, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse resume file data
        
        Args:
            file_data: File data as bytes
            file_type: File type (pdf, docx, txt, png, jpg)
            
        Returns:
            Parsed resume data
        """
        if not file_type:
            # Try to determine file type from content
            if file_data.startswith(b'%PDF'):
                file_type = 'pdf'
            elif file_data.startswith(b'PK\x03\x04'):
                file_type = 'docx'
            elif file_data.startswith(b'\xff\xd8\xff'):
                file_type = 'jpg'
            elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):
                file_type = 'png'
            else:
                # Default to txt
                file_type = 'txt'
        
        # Extract text from file
        text = self._extract_text(file_data, file_type)
        
        # If AI service is available, use it to analyze the resume
        if self.ai_service:
            try:
                return self.ai_service.analyze_resume(text)
            except Exception as e:
                print(f"Error analyzing resume with AI service: {e}")
                # Fall back to basic parsing
        
        # Basic parsing (returns the text with some structure)
        return {
            "text": text,
            "sections": self._basic_section_extraction(text),
            "skills": self._extract_skills(text),
            "parsed_at": datetime.now().isoformat()
        }
    
    def _extract_text(self, file_data: bytes, file_type: str) -> str:
        """
        Extract text from file data
        
        Args:
            file_data: File data as bytes
            file_type: File type
            
        Returns:
            Extracted text
        """
        if file_type == 'pdf':
            return self._extract_from_pdf(file_data)
        elif file_type == 'docx':
            return self._extract_from_docx(file_data)
        elif file_type == 'png' or file_type == 'jpg':
            return self._extract_from_image(file_data)
        else:  # txt or unknown
            try:
                return file_data.decode('utf-8')
            except UnicodeDecodeError:
                # Try different encoding
                try:
                    return file_data.decode('latin-1')
                except UnicodeDecodeError:
                    return "Error: Could not decode text file."
    
    def _extract_from_pdf(self, file_data: bytes) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return "Error extracting text from PDF."
    
    def _extract_from_docx(self, file_data: bytes) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            docx_file = io.BytesIO(file_data)
            doc = docx.Document(docx_file)
            
            for para in doc.paragraphs:
                text += para.text + "\n"
                
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return "Error extracting text from DOCX."
    
    def _extract_from_image(self, file_data: bytes) -> str:
        """Extract text from image file using OCR"""
        try:
            image = Image.open(io.BytesIO(file_data))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return "Error extracting text from image."
    
    def _basic_section_extraction(self, text: str) -> Dict[str, str]:
        """
        Extract sections from resume text using simple heuristics
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of sections
        """
        lines = text.split('\n')
        sections = {}
        current_section = "header"
        sections[current_section] = []
        
        common_section_headers = [
            "education", "experience", "work experience", "skills", 
            "projects", "certifications", "awards", "publications",
            "interests", "activities", "references", "summary", "objective"
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = False
            line_lower = line.lower()
            
            for header in common_section_headers:
                if header in line_lower and (
                    line_lower.startswith(header) or 
                    all(c.isupper() for c in line if c.isalpha())
                ):
                    current_section = header
                    sections[current_section] = []
                    is_header = True
                    break
            
            if not is_header:
                sections[current_section].append(line)
        
        # Convert lists of lines back to text
        for section, lines in sections.items():
            sections[section] = "\n".join(lines)
            
        return sections
    
    def _extract_skills(self, text: str) -> list:
        """
        Extract skills from resume text using simple keyword matching
        
        Args:
            text: Resume text
            
        Returns:
            List of skills
        """
        # Basic list of common skills
        common_skills = [
            "python", "java", "javascript", "html", "css", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "ruby", "rails", "php", "laravel",
            "c++", "c#", ".net", "swift", "kotlin", "go", "rust", "sql", "mysql", 
            "postgresql", "mongodb", "oracle", "nosql", "aws", "azure", "gcp", "docker",
            "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "agile", "scrum",
            "jira", "confluence", "tensorflow", "pytorch", "machine learning", "data science",
            "artificial intelligence", "nlp", "computer vision", "tableau", "power bi",
            "excel", "word", "powerpoint", "photoshop", "illustrator", "figma", "sketch",
            "leadership", "communication", "teamwork", "problem solving", "critical thinking"
        ]
        
        # Find skills in text
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
                
        return found_skills

# app/utils/job_analyzer.py
import re
from typing import Dict, Any, List
from datetime import datetime

class JobDescriptionAnalyzer:
    """Utility class for analyzing job descriptions"""
    
    def __init__(self, ai_service=None):
        """
        Initialize job description analyzer
        
        Args:
            ai_service: AI service for text analysis
        """
        self.ai_service = ai_service
        
        # Common job skills for keyword extraction
        self.common_skills = [
            "python", "java", "javascript", "html", "css", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "ruby", "rails", "php", "laravel",
            "c++", "c#", ".net", "swift", "kotlin", "go", "rust", "sql", "mysql", 
            "postgresql", "mongodb", "oracle", "nosql", "aws", "azure", "gcp", "docker",
            "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "agile", "scrum",
            "jira", "confluence", "tensorflow", "pytorch", "machine learning", "data science",
            "artificial intelligence", "nlp", "computer vision", "tableau", "power bi"
        ]
        
        # Experience level terms
        self.experience_levels = {
            "junior": ["junior", "entry", "entry-level", "entry level", "0-2 years", "1-2 years", "beginner"],
            "mid-level": ["mid", "mid-level", "mid level", "intermediate", "2-5 years", "3-5 years", "associate"],
            "senior": ["senior", "sr", "sr.", "expert", "advanced", "5+ years", "lead", "principal"]
        }
    
    def analyze(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description
        
        Args:
            job_description: Job description text
            
        Returns:
            Analyzed job data
        """
        # If AI service is available, use it to analyze the job description
        if self.ai_service:
            try:
                return self.ai_service.analyze_job_description(job_description)
            except Exception as e:
                print(f"Error analyzing job with AI service: {e}")
                # Fall back to basic analysis
        
        # Basic analysis
        analysis = {
            "job_title": self._extract_job_title(job_description),
            "company": self._extract_company(job_description),
            "required_skills": self._extract_skills(job_description, required=True),
            "preferred_skills": self._extract_skills(job_description, required=False),
            "experience_level": self._extract_experience_level(job_description),
            "education_requirements": self._extract_education(job_description),
            "responsibilities": self._extract_responsibilities(job_description),
            "analyzed_at": datetime.now().isoformat()
        }
        
        return analysis
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description"""
        # Look for common patterns in job titles
        patterns = [
            r"(?:Job Title|Position|Title):\s*([^\n\r]+)",
            r"^([A-Z][A-Za-z0-9 ]+(?:Developer|Engineer|Manager|Designer|Analyst|Specialist|Associate|Director|Lead|Architect))(?:\n|$)",
            r"(?:hiring|seeking|looking for|for)\s+(?:a|an)\s+([A-Za-z0-9 ]+(?:Developer|Engineer|Manager|Designer|Analyst|Specialist|Associate|Director|Lead|Architect))"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Default title if not found
        return "Not specified"
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from job description"""
        # Look for common patterns for company names
        patterns = [
            r"(?:at|for|with|About|Company):\s*([A-Z][A-Za-z0-9 ]+)(?:is|are|,|\.|$)",
            r"About\s+([A-Z][A-Za-z0-9 ]+)(?:\n|$)",
            r"Welcome to\s+([A-Z][A-Za-z0-9 ]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                company = match.group(1).strip()
                return company
        
        return "Not specified"
    
    def _extract_skills(self, text: str, required: bool = True) -> List[str]:
        """Extract skills from job description"""
        text_lower = text.lower()
        
        # Different sections to look for skills
        if required:
            skill_sections = [
                self._extract_section(text, ["requirements", "required skills", "qualifications"]),
                self._extract_section(text, ["technical skills", "technical requirements"])
            ]
        else:
            skill_sections = [
                self._extract_section(text, ["preferred", "preferred skills", "nice to have", "plus"]),
                self._extract_section(text, ["bonus", "additional skills"])
            ]
        
        # Combine all sections for analysis
        combined_text = " ".join([s for s in skill_sections if s])
        if not combined_text:
            combined_text = text_lower
        
        # Find skills in text
        found_skills = []
        for skill in self.common_skills:
            if skill in combined_text:
                found_skills.append(skill)
        
        # Look for common skill patterns
        skill_patterns = [
            r"proficiency in\s+([A-Za-z0-9/# ]+)",
            r"experience with\s+([A-Za-z0-9/# ]+)",
            r"knowledge of\s+([A-Za-z0-9/# ]+)",
            r"familiarity with\s+([A-Za-z0-9/# ]+)"
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                skill_text = match.group(1).strip().lower()
                # Check if it's not just a generic term
                if len(skill_text) > 3 and "years" not in skill_text and "experience" not in skill_text:
                    found_skills.append(skill_text)
        
        return list(set(found_skills))
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level from job description"""
        text_lower = text.lower()
        
        # Check for specific experience level mentions
        for level, terms in self.experience_levels.items():
            for term in terms:
                if term in text_lower:
                    return level
        
        # Look for years of experience patterns
        year_patterns = [
            r"(\d+)\+?\s*(?:-\s*\d+\s*)?years?\s+(?:of\s+)?experience",
            r"(\d+)\s*(?:to|-)\s*(\d+)\s+years?\s+(?:of\s+)?experience"
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text_lower)
            if match:
                years = int(match.group(1))
                if years <= 2:
                    return "junior"
                elif years <= 5:
                    return "mid-level"
                else:
                    return "senior"
        
        # Default if no experience level found
        return "not specified"
    
    def _extract_education(self, text: str) -> str:
        """Extract education requirements from job description"""
        text_lower = text.lower()
        
        # Look for education section
        education_section = self._extract_section(text, ["education", "educational requirements"])
        
        if education_section:
            text_to_search = education_section
        else:
            text_to_search = text_lower
            
        # Look for degree patterns
        degree_patterns = [
            r"bachelor'?s?(?:\s+degree)?(?:\s+in\s+([A-Za-z0-9 ]+))?",
            r"master'?s?(?:\s+degree)?(?:\s+in\s+([A-Za-z0-9 ]+))?",
            r"ph\.?d\.?(?:\s+in\s+([A-Za-z0-9 ]+))?",
            r"b\.s\.(?:\s+in\s+([A-Za-z0-9 ]+))?",
            r"m\.s\.(?:\s+in\s+([A-Za-z0-9 ]+))?"
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text_to_search, re.IGNORECASE)
            if match:
                degree = match.group(0)
                field = match.group(1) if match.lastindex else ""
                if field:
                    return f"{degree} in {field}".strip()
                else:
                    return degree.strip()
        
        # Check for general education statements
        if "degree" in text_lower:
            return "Degree required (specifics not clear)"
        
        return "Not specified"
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities from job description"""
        # Look for responsibilities section
        resp_section = self._extract_section(
            text, 
            ["responsibilities", "duties", "what you'll do", "what you will do", "job duties"]
        )
        
        if not resp_section:
            return []
            
        # Look for bullet points or numbered lists
        responsibilities = []
        
        # Try to find bullet points
        bullet_matches = re.finditer(r"(?:^|\n)(?:[-•*]|\d+\.)\s*([^\n]+)", resp_section)
        for match in bullet_matches:
            responsibilities.append(match.group(1).strip())
        
        # If no bullet points found, try to split by sentences
        if not responsibilities:
            sentences = re.split(r'(?<=[.!?])\s+', resp_section)
            responsibilities = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Limit to reasonable number
        return responsibilities[:10]
    
    def _extract_section(self, text: str, section_names: List[str]) -> str:
        """
        Extract a section from the text based on section names
        
        Args:
            text: Full text
            section_names: Possible names for the section
            
        Returns:
            Section text if found, empty string otherwise
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        for name in section_names:
            # Try different patterns for section headers
            patterns = [
                f"(?:^|\n)(?:{name}):?([^\n]+(?:\n(?!(?:{self._generate_section_pattern(section_names)}):)[^\n]+)*)",
                f"(?:^|\n)(?:{name})(?:\n|\r\n?)+((?:(?!\n\n)[^\n])+(?:\n(?!(?:{self._generate_section_pattern(section_names)}):|\n\n)(?:(?!\n\n)[^\n])+)*)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip()
        
        return ""
    
    def _generate_section_pattern(self, ignore_sections: List[str]) -> str:
        """Generate regex pattern for common section headers to find section boundaries"""
        common_sections = [
            "requirements", "qualifications", "responsibilities", "duties", 
            "about us", "company", "benefits", "skills", "education",
            "experience", "preferred", "application", "salary", "compensation"
        ]
        
        # Add all sections except the ones we're looking for
        sections = [s for s in common_sections if s not in ignore_sections]
        return "|".join(sections)

# app/utils/question_generator.py
from typing import List, Dict, Any
import random

class QuestionGenerator:
    """Utility class for generating interview questions"""
    
    def __init__(self, ai_service=None):
        """
        Initialize question generator
        
        Args:
            ai_service: AI service for generating questions
        """
        self.ai_service = ai_service
        
        # Default questions by category
        self.default_questions = {
            "technical": [
                {
                    "id": 1,
                    "question": "Can you explain your experience with [technical_skill]?",
                    "expected_answer_areas": ["Technical knowledge", "Practical experience", "Project examples"],
                    "skills_assessed": ["Technical knowledge", "Communication"],
                    "follow_ups": ["What challenges did you face when using this technology?", "How did you overcome them?"]
                },
                {
                    "id": 2,
                    "question": "How would you approach [technical_problem]?",
                    "expected_answer_areas": ["Problem-solving methodology", "Technical concepts", "Practical solutions"],
                    "skills_assessed": ["Problem-solving", "Technical knowledge", "Critical thinking"],
                    "follow_ups": ["What alternatives would you consider?", "What are the trade-offs of your approach?"]
                },
                {
                    "id": 3,
                    "question": "Describe a technically challenging project you worked on.",
                    "expected_answer_areas": ["Project description", "Technical challenges", "Solutions implemented", "Results"],
                    "skills_assessed": ["Problem-solving", "Technical expertise", "Project management"],
                    "follow_ups": ["What would you do differently now?", "What did you learn from this experience?"]
                }
            ],
            "behavioral": [
                {
                    "id": 1,
                    "question": "Tell me about a time when you had to work under pressure to meet a deadline.",
                    "expected_answer_areas": ["Situation", "Task", "Action", "Result"],
                    "skills_assessed": ["Time management", "Stress management", "Prioritization"],
                    "follow_ups": ["How did you prioritize tasks?", "What would you do differently?"]
                },
                {
                    "id": 2,
                    "question": "Describe a situation where you had to work with a difficult team member.",
                    "expected_answer_areas": ["Situation", "Challenges", "Your approach", "Resolution", "Lessons learned"],
                    "skills_assessed": ["Conflict resolution", "Teamwork", "Communication"],
                    "follow_ups": ["How did this affect the team dynamics?", "What did you learn from this experience?"]
                },
                {
                    "id": 3, 
                    "question": "Give me an example of a time when you showed leadership skills.",
                    "expected_answer_areas": ["Situation", "Your role", "Actions taken", "Outcome", "Impact"],
                    "skills_assessed": ["Leadership", "Initiative", "Decision-making"],
                    "follow_ups": ["How did you motivate the team?", "What challenges did you face as a leader?"]
                }
            ],
            "general": [
    {
        "id": 1,
        "question": "Why are you interested in this position?",
        "expected_answer_areas": ["Career goals", "Interest in company", "Alignment with job role"],
        "skills_assessed": ["Motivation", "Cultural fit", "Communication"],
        "follow_ups": ["What excites you most about this role?", "How does this position fit into your long-term goals?"]
    },
    {
        "id": 2,
        "question": "Where do you see yourself in five years?",
        "expected_answer_areas": ["Career progression", "Skill development", "Personal vision"],
        "skills_assessed": ["Ambition", "Planning", "Self-awareness"],
        "follow_ups": ["What steps are you taking to achieve this vision?", "How does this role contribute to it?"]
    },
    {
        "id": 3,
        "question": "What are your strengths and weaknesses?",
        "expected_answer_areas": ["Self-awareness", "Balance", "Professional growth"],
        "skills_assessed": ["Honesty", "Growth mindset", "Self-assessment"],
        "follow_ups": ["How are you working on your weakness?", "Can you give an example where your strength helped you?"]
    },
    {
        "id": 4,
        "question": "Why should we hire you?",
        "expected_answer_areas": ["Unique value", "Relevance to role", "Impact potential"],
        "skills_assessed": ["Confidence", "Persuasion", "Value articulation"],
        "follow_ups": ["How do your past experiences prepare you for this role?", "What differentiates you from other candidates?"]
    },
    {
        "id": 5,
        "question": "What motivates you at work?",
        "expected_answer_areas": ["Drivers", "Work ethic", "Values"],
        "skills_assessed": ["Motivation", "Culture fit", "Self-awareness"],
        "follow_ups": ["Can you share a project that really motivated you?", "What type of work environment suits you best?"]
    }
]
