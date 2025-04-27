import os
import re
import logging
from pathlib import Path
import docx2txt
import PyPDF2
import spacy
from collections import defaultdict

class ResumeParser:
    """
    Parser for extracting structured information from resumes
    """
    
    def __init__(self):
        """Initialize the resume parser"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logging.warning("Spacy model not found. Downloading...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Define sections to extract
        self.sections = [
            "education", "experience", "skills", "projects", 
            "certifications", "summary", "contact", "languages"
        ]
        
        # Regex patterns for sections
        self.section_patterns = {
            "education": re.compile(r"education|academic|qualification", re.IGNORECASE),
            "experience": re.compile(r"experience|employment|work|job", re.IGNORECASE),
            "skills": re.compile(r"skills|expertise|technologies|technical", re.IGNORECASE),
            "projects": re.compile(r"projects|portfolio", re.IGNORECASE),
            "certifications": re.compile(r"certifications|certificates|courses", re.IGNORECASE),
            "summary": re.compile(r"summary|profile|objective|about", re.IGNORECASE),
            "contact": re.compile(r"contact|address|phone|email", re.IGNORECASE),
            "languages": re.compile(r"languages|linguistic", re.IGNORECASE)
        }
        
        # Email pattern
        self.email_pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        
        # Phone pattern (simple version)
        self.phone_pattern = re.compile(r"(\+\d{1,3}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}")
        
        # LinkedIn pattern
        self.linkedin_pattern = re.compile(r"linkedin\.com/in/[\w-]+")
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path):
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error extracting text from TXT: {e}")
            return ""
    
    def extract_text(self, file_path):
        """Extract text from file based on extension"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            logging.error(f"Unsupported file format: {file_extension}")
            return ""
    
    def extract_contact_info(self, text):
        """Extract contact information from text"""
        contact_info = {}
        
        # Extract email
        email_matches = self.email_pattern.findall(text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract phone
        phone_matches = self.phone_pattern.findall(text)
        if phone_matches:
            contact_info['phone'] = phone_matches[0][0] + phone_matches[0][1] + phone_matches[0][2]
        
        # Extract LinkedIn
        linkedin_matches = self.linkedin_pattern.findall(text)
        if linkedin_matches:
            contact_info['linkedin'] = linkedin_matches[0]
        
        return contact_info
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        doc = self.nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if ent.label_ in ["ORG", "GPE", "PERSON", "DATE", "SKILL"]:
                entities[ent.label_].append(ent.text)
        
        return dict(entities)
    
    def extract_skills(self, text):
        """Extract skills from text"""
        # Common programming languages and technologies
        tech_skills = [
            "python", "java", "javascript", "js", "typescript", "c\\+\\+", "c#", "ruby", "php",
            "html", "css", "sql", "nosql", "react", "angular", "vue", "node", "express",
            "django", "flask", "spring", "aws", "azure", "gcp", "docker", "kubernetes",
            "git", "jenkins", "ci/cd", "agile", "scrum", "machine learning", "deep learning",
            "ai", "data science", "big data", "hadoop", "spark", "tableau", "power bi",
            "excel", "word", "powerpoint", "photoshop", "illustrator", "figma", "sketch"
        ]
        
        # Create a pattern to match skills
        pattern = r'\b(' + '|'.join(tech_skills) + r')\b'
        skill_pattern = re.compile(pattern, re.IGNORECASE)
        
        # Find matches
        skill_matches = skill_pattern.findall(text)
        
        # Remove duplicates and standardize case
        skills = list(set([skill.lower() for skill in skill_matches]))
        
        return skills
    
    def split_text_into_sections(self, text):
        """Split resume text into sections"""
        sections = {}
        
        # Find potential section headers
        lines = text.split('\n')
        current_section = "unknown"
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            is_header = False
            for section_name, pattern in self.section_patterns.items():
                if pattern.search(line) and len(line) < 50:  # Section headers are usually short
                    current_section = section_name
                    sections[current_section] = []
                    is_header = True
                    break
            
            if not is_header:
                sections[current_section].append(line)
        
        # Convert lists of lines back to text
        for section in sections:
            sections[section] = '\n'.join(sections[section])
        
        return sections
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        # Look for common degree abbreviations and education keywords
        degree_pattern = re.compile(r'\b(BS|BA|B\.S\.|B\.A\.|BSc|MSc|MS|MA|M\.S\.|M\.A\.|PhD|Ph\.D\.|Bachelor|Master|Doctor|Diploma|Certificate)\b', re.IGNORECASE)
        
        # Split text into paragraphs which likely represent different education entries
        paragraphs = re.split(r'\n\s*\n', text)
        
        for paragraph in paragraphs:
            if degree_pattern.search(paragraph):
                # Try to extract degree, institution, and date
                degree_match = degree_pattern.search(paragraph)
                degree = degree_match.group(0) if degree_match else ""
                
                # Try to find date range (YYYY-YYYY or YYYY to YYYY or similar)
                date_pattern = re.compile(r'(19|20)\d{2}\s*(-|to|–|\s)\s*(19|20)\d{2}|(19|20)\d{2}\s*(-|to|–|\s)\s*Present', re.IGNORECASE)
                date_match = date_pattern.search(paragraph)
                date = date_match.group(0) if date_match else ""
                
                # The rest might be institution and additional details
                education_entry = {
                    "degree": degree,
                    "date": date,
                    "details": paragraph.strip()
                }
                
                education.append(education_entry)
        
        return education
    
    def extract_experience(self, text):
        """Extract work experience information"""
        experience = []
        
        # Split text into paragraphs which likely represent different job entries
        paragraphs = re.split(r'\n\s*\n', text)
        
        for paragraph in paragraphs:
            # Try to find date range (YYYY-YYYY or YYYY to YYYY or similar)
            date_pattern = re.compile(r'(19|20)\d{2}\s*(-|to|–|\s)\s*(19|20)\d{2}|(19|20)\d{2}\s*(-|to|–|\s)\s*Present', re.IGNORECASE)
            date_match = date_pattern.search(paragraph)
            
            if date_match:
                date = date_match.group(0)
                
                # Try to extract company/organization
                lines = paragraph.split('\n')
                title = ""
                company = ""
                
                for line in lines:
                    if line and line not in date:
                        # First non-empty line that's not the date might be the job title or company
                        title_company = line.strip()
                        
                        # Try to split title and company if they're on the same line
                        title_company_split = re.split(r'\s*[,|]\s*|\s+at\s+', title_company, maxsplit=1)
                        if len(title_company_split) > 1:
                            title = title_company_split[0].strip()
                            company = title_company_split[1].strip()
                        else:
                            title = title_company
                        
                        break
                
                # The rest is description
                description = paragraph.replace(title, "").replace(company, "").replace(date, "").strip()
                
                experience_entry = {
                    "title": title,
                    "company": company,
                    "date": date,
                    "description": description
                }
                
                experience.append(experience_entry)
        
        return experience
    
    def parse_resume(self, file_path):
        """
        Parse a resume file and extract structured information
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            dict: Structured resume data
        """
        # Extract text from file
        text = self.extract_text(file_path)
        
        if not text:
            return {"error": "Could not extract text from file"}
        
        # Extract contact information
        contact_info = self.extract_contact_info(text)
        
        # Split text into sections
        sections = self.split_text_into_sections(text)
        
        # Extract skills
        skills = self.extract_skills(text if "skills" not in sections else sections["skills"])
        
        # Extract education
        education = self.extract_education(text if "education" not in sections else sections["education"])
        
        # Extract experience
        experience = self.extract_experience(text if "experience" not in sections else sections["experience"])
        
        # Extract entities (organizations, locations, etc.)
        entities = self.extract_entities(text)
        
        # Create structured resume data
        resume_data = {
            "contact_info": contact_info,
            "skills": skills,
            "education": education,
            "experience": experience,
            "entities": entities,
            "sections": sections,
            "full_text": text
        }
        
        return resume_data