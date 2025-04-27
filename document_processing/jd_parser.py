import re
import os
from typing import Dict, List, Any
import PyPDF2
import docx
import openai
from app.config import OPENAI_API_KEY, OPENAI_MODEL

openai.api_key = OPENAI_API_KEY

class JobDescriptionParser:
    """
    Class to parse job descriptions from various formats (PDF, DOCX, TXT)
    and extract structured information.
    """
    
    def __init__(self):
        self.sections = {
            'job_title': '',
            'company': '',
            'location': '',
            'job_summary': '',
            'responsibilities': [],
            'requirements': {
                'required_skills': [],
                'preferred_skills': [],
                'education': [],
                'experience': []
            },
            'benefits': [],
            'additional_info': ''
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text content from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file based on its extension"""
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension.lower() == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension.lower() == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def parse_using_ai(self, text: str) -> Dict[str, Any]:
        """Use OpenAI to parse job description text into structured data"""
        try:
            prompt = """
            Extract the following information from this job description into a structured JSON format:

            1. job_title: The title of the job position
            2. company: The company offering the position
            3. location: Where the job is located (including remote options)
            4. job_summary: A brief summary of what the job entails
            5. responsibilities: A list of key responsibilities
            6. requirements:
               a. required_skills: List of mandatory skills
               b. preferred_skills: List of optional/preferred skills
               c. education: Educational requirements
               d. experience: Experience requirements
            7. benefits: List of benefits offered
            8. additional_info: Any other relevant information

            Return the information as a valid JSON object with these keys.

            Job Description:
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a job description parser that extracts structured information from job descriptions accurately."},
                    {"role": "user", "content": prompt + text}
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = response.choices[0].message.content
            
            # Process the returned JSON string
            import json
            return json.loads(parsed_data)
            
        except Exception as e:
            print(f"Error parsing job description with AI: {e}")
            # Return basic structure with the raw text as fallback
            return {
                "job_title": "Not detected",
                "company": "Not detected",
                "location": "Not detected",
                "job_summary": text[:500] + "...",  # First 500 chars as summary
                "responsibilities": [],
                "requirements": {
                    "required_skills": [],
                    "preferred_skills": [],
                    "education": [],
                    "experience": []
                },
                "benefits": [],
                "additional_info": ""
            }
    
    def extract_keywords(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from parsed job description"""
        keywords = []
        
        # Extract from required skills
        if "requirements" in parsed_data and "required_skills" in parsed_data["requirements"]:
            keywords.extend(parsed_data["requirements"]["required_skills"])
        
        # Extract from preferred skills
        if "requirements" in parsed_data and "preferred_skills" in parsed_data["requirements"]:
            keywords.extend(parsed_data["requirements"]["preferred_skills"])
            
        # Extract additional keywords from responsibilities
        if "responsibilities" in parsed_data:
            # Use AI to extract technical terms and skills from responsibilities
            try:
                resp_text = "\n".join(parsed_data["responsibilities"]) if isinstance(parsed_data["responsibilities"], list) else parsed_data["responsibilities"]
                
                response = openai.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "Extract technical skills, tools, methodologies, and important keywords from the job responsibilities provided."},
                        {"role": "user", "content": resp_text}
                    ],
                    response_format={"type": "json_object"}
                )
                
                import json
                resp_keywords = json.loads(response.choices[0].message.content)
                if "keywords" in resp_keywords and isinstance(resp_keywords["keywords"], list):
                    keywords.extend(resp_keywords["keywords"])
            except Exception as e:
                print(f"Error extracting keywords from responsibilities: {e}")
        
        # Remove duplicates and normalize
        return list(set([keyword.lower().strip() for keyword in keywords]))
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a job description file and return structured information
        
        Args:
            file_path: Path to the job description file
            
        Returns:
            Dictionary containing parsed job description data
        """
        # Extract raw text from file
        text = self.extract_text(file_path)
        
        if not text.strip():
            raise ValueError("No text could be extracted from the job description file")
        
        # Parse the text using AI
        parsed_data = self.parse_using_ai(text)
        
        # Extract keywords
        keywords = self.extract_keywords(parsed_data)
        
        # Add raw text and keywords to the result
        parsed_data["raw_text"] = text
        parsed_data["keywords"] = keywords
        
        return parsed_data
    
    def parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse job description from raw text
        
        Args:
            text: Raw job description text
            
        Returns:
            Dictionary containing parsed job description data
        """
        if not text.strip():
            raise ValueError("Empty job description text provided")
        
        # Parse the text using AI
        parsed_data = self.parse_using_ai(text)
        
        # Extract keywords
        keywords = self.extract_keywords(parsed_data)
        
        # Add raw text and keywords to the result
        parsed_data["raw_text"] = text
        parsed_data["keywords"] = keywords
        
        return parsed_data
    
    def parse_from_url(self, url: str) -> Dict[str, Any]:
        """
        Parse job description from a URL (requires web_scraper.py implementation)
        
        Args:
            url: URL to the job posting
            
        Returns:
            Dictionary containing parsed job description data
        """
        try:
            # Import here to avoid circular imports
            from app.document_processing.web_scraper import WebScraper
            
            # Scrape text from URL
            scraper = WebScraper()
            text = scraper.scrape_job_description(url)
            
            if not text.strip():
                raise ValueError(f"No text could be scraped from the URL: {url}")
                
            # Parse the scraped text
            return self.parse_text(text)
            
        except Exception as e:
            print(f"Error parsing job description from URL: {e}")
            raise