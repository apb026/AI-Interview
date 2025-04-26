# app/services/ai_service.py
import os
from typing import List, Dict, Any, Optional
import openai
import json

class AIService:
    """Service for AI-powered features using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize AI service
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        openai.api_key = self.api_key
        self.model = model
    
    async def generate_text(self, prompt: str, max_tokens: int = 500, 
                     temperature: float = 0.7) -> str:
        """
        Generate text using OpenAI API
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description to extract key information
        
        Args:
            job_description: Job description text
            
        Returns:
            Dictionary with analyzed job information
        """
        prompt = f"""
        Please analyze the following job description and extract key information:
        
        {job_description}
        
        Extract and organize the following information in JSON format:
        - job_title: The title of the position
        - company: The company name if mentioned
        - required_skills: List of required technical skills
        - preferred_skills: List of preferred or optional skills
        - experience_level: Junior, Mid-level, Senior, etc.
        - education_requirements: Any educational requirements
        - responsibilities: List of key responsibilities
        - key_qualities: Personal qualities or soft skills they're looking for
        
        Return ONLY the JSON object without any additional text.
        """
        
        try:
            result = await self.generate_text(prompt, max_tokens=1000, temperature=0.0)
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback to a more basic structure if parsing fails
            return {
                "job_title": "Unknown",
                "company": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "Unknown",
                "education_requirements": "Unknown",
                "responsibilities": [],
                "key_qualities": []
            }
    
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze a resume to extract key information
        
        Args:
            resume_text: Resume text content
            
        Returns:
            Dictionary with analyzed resume information
        """
        prompt = f"""
        Please analyze the following resume and extract key information:
        
        {resume_text}
        
        Extract and organize the following information in JSON format:
        - name: The candidate's name
        - contact: Contact information
        - education: List of education entries
        - work_experience: List of work experiences with company, role, and dates
        - skills: List of technical and soft skills
        - certifications: List of certifications if any
        - achievements: List of notable achievements
        
        Return ONLY the JSON object without any additional text.
        """
        
        try:
            result = await self.generate_text(prompt, max_tokens=1500, temperature=0.0)
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback to a more basic structure if parsing fails
            return {
                "name": "Unknown",
                "contact": {},
                "education": [],
                "work_experience": [],
                "skills": [],
                "certifications": [],
                "achievements": []
            }
    
    async def generate_interview_questions(self, job_data: Dict[str, Any], 
                                    resume_data: Dict[str, Any], 
                                    interview_type: str,
                                    num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on job and resume data
        
        Args:
            job_data: Analyzed job description data
            resume_data: Analyzed resume data
            interview_type: Type of interview (technical, behavioral, etc.)
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        # Convert input data to JSON strings for the prompt
        job_json = json.dumps(job_data, indent=2)
        resume_json = json.dumps(resume_data, indent=2)
        
        prompt = f"""
        Generate {num_questions} {interview_type} interview questions for the following candidate and job:
        
        JOB DATA:
        {job_json}
        
        CANDIDATE DATA:
        {resume_json}
        
        INTERVIEW TYPE: {interview_type}
        
        For each question, provide:
        1. The question text
        2. The expected answer areas or key points that should be addressed
        3. The skills or qualities being assessed with this question
        4. Follow-up questions if the candidate's answer is incomplete
        
        Return a JSON array where each question is an object with these fields:
        - "question": The question text
        - "expected_answer_areas": Array of key points to cover
        - "skills_assessed": Array of skills being evaluated
        - "follow_ups": Array of follow-up questions
        
        Return ONLY the JSON array without any additional text.
        """
        
        try:
            result = await self.generate_text(prompt, max_tokens=2500, temperature=0.5)
            questions = json.loads(result)
            
            # Ensure proper formatting and add question IDs
            for i, question in enumerate(questions):
                question["id"] = i + 1
                
            return questions
        except json.JSONDecodeError:
            # Fallback to a simple question set if parsing fails
            default_questions = []
            for i in range(num_questions):
                default_questions.append({
                    "id": i + 1,
                    "question": f"Generic {interview_type} question #{i+1}",
                    "expected_answer_areas": ["Communication", "Problem-solving"],
                    "skills_assessed": ["Communication", "Technical knowledge"],
                    "follow_ups": ["Can you elaborate more?"]
                })
            return default_questions
    
    async def generate_feedback(self, transcript: List[Dict[str, Any]], 
                         job_data: Dict[str, Any], 
                         resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate feedback based on interview transcript and job/resume data
        
        Args:
            transcript: List of transcript entries from the interview
            job_data: Analyzed job description data
            resume_data: Analyzed resume data
            
        Returns:
            Dictionary with feedback information
        """
        # Prepare transcript text
        transcript_text = ""
        for entry in transcript:
            speaker = "AI" if entry.get("is_ai", False) else "Candidate"
            transcript_text += f"{speaker}: {entry.get('text', '')}\n\n"
        
        # Convert job and resume data to JSON strings for the prompt
        job_json = json.dumps(job_data, indent=2)
        resume_json = json.dumps(resume_data, indent=2)
        
        prompt = f"""
        Analyze the following interview transcript and provide comprehensive feedback for the candidate.
        
        JOB DATA:
        {job_json}
        
        CANDIDATE DATA:
        {resume_json}
        
        INTERVIEW TRANSCRIPT:
        {transcript_text}
        
        Provide detailed feedback in JSON format with the following sections:
        - "overall_assessment": Brief summary of the candidate's performance
        - "strengths": Array of strengths demonstrated in the interview
        - "areas_for_improvement": Array of areas that need improvement
        - "technical_skills": Assessment of technical skills relevant to the job
        - "communication_skills": Assessment of communication and presentation
        - "cultural_fit": Assessment of potential cultural fit with the company
        - "recommended_resources": Resources the candidate could use to improve
        - "final_recommendation": Hire, Consider, or Do Not Hire
        - "confidence_score": A score from 0-100 indicating confidence in this assessment
        
        Return ONLY the JSON object without any additional text.
        """
        
        try:
            result = await self.generate_text(prompt, max_tokens=3000, temperature=0.3)
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback to a basic feedback structure if parsing fails
            return {
                "overall_assessment": "Feedback generation failed. Please review the transcript manually.",
                "strengths": [],
                "areas_for_improvement": [],
                "technical_skills": "Not assessed",
                "communication_skills": "Not assessed",
                "cultural_fit": "Not assessed",
                "recommended_resources": [],
                "final_recommendation": "Consider",
                "confidence_score": 0
            }