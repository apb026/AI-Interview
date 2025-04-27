import os
import re
import logging
from pathlib import Path
import docx2txt
import PyPDF2
import spacy
from collections import defaultdict

class JobDescriptionParser:
    """
    Parser for extracting structured information from job descriptions
    """
    
    def __init__(self):
        """Initialize the job description parser"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logging.warning("Spacy model not found. Downloading...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Define sections to extract
        self.sections = [
            "requirements", "responsibilities", "qualifications", "benefits",
            "company", "about", "description", "skills"
        ]
        
        # Regex patterns for sections
        self.section_patterns = {
            "requirements": re.compile(r"requirements|what you'll need|qualifications", re.IGNORECASE),
            "responsibilities": re.compile(r"responsibilities|what you'll do|duties|role", re.IGNORECASE),
            "qualifications": re.compile(r"qualifications|experience required|requirements", re.IGNORECASE),
            "benefits": re.compile(r"benefits|perks|what we offer|compensation", re.IGNORECASE),
            "company": re.compile(r"about the company|who we are|about us", re.IGNORECASE),
            "about": re.compile(r"about the role|about the position|overview", re.IGNORECASE),
            "description": re.compile(r"job description|position description|summary", re.IGNORECASE),
            "skills": re.compile(r"skills|technologies|technical requirements", re.IGNORECASE)
        }
    
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
        elif file_extension == '.