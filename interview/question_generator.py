import openai
import random
from typing import List, Dict, Any
from app.config import OPENAI_API_KEY, OPENAI_MODEL, MAX_QUESTIONS
from app.document_processing.resume_parser import ResumeParser
from app.document_processing.jd_parser import JobDescriptionParser

openai.api_key = OPENAI_API_KEY

class QuestionGenerator:
    """
    Class to generate interview questions based on resume and job description
    using OpenAI GPT models.
    """
    
    def __init__(self):
        self.question_types = {
            "technical": {
                "weight": 0.4,  # 40% of questions will be technical
                "description": "Technical questions related to skills and technologies mentioned in the resume and job description"
            },
            "behavioral": {
                "weight": 0.3,  # 30% of questions will be behavioral
                "description": "Questions about past behavior and experiences relevant to the job"
            },
            "situational": {
                "weight": 0.2,  # 20% of questions will be situational
                "description": "Hypothetical scenarios to assess problem-solving and job-specific skills"
            },
            "company_culture": {
                "weight": 0.1,  # 10% of questions will be about company culture
                "description": "Questions to assess cultural fit with the company"
            }
        }
    
    def analyze_match(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the match between resume and job description to identify
        areas to focus on during the interview.
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
            
        Returns:
            Dictionary containing match analysis data
        """
        try:
            # Extract skills from resume and job description
            resume_skills = set([s.lower() for s in resume_data.get("skills", [])])
            
            jd_required_skills = set([s.lower() for s in jd_data.get("requirements", {}).get("required_skills", [])])
            jd_preferred_skills = set([s.lower() for s in jd_data.get("requirements", {}).get("preferred_skills", [])])
            
            # Calculate matches and gaps
            matching_required_skills = resume_skills.intersection(jd_required_skills)
            matching_preferred_skills = resume_skills.intersection(jd_preferred_skills)
            missing_required_skills = jd_required_skills - resume_skills
            missing_preferred_skills = jd_preferred_skills - resume_skills
            additional_skills = resume_skills - jd_required_skills - jd_preferred_skills
            
            # Calculate match percentage for required skills
            required_match_percentage = 0
            if jd_required_skills:
                required_match_percentage = (len(matching_required_skills) / len(jd_required_skills)) * 100
            
            # Generate overall match assessment using AI
            prompt = f"""
            Analyze the match between a candidate's resume and a job description based on the following data:

            Job Title: {jd_data.get('job_title', 'Not specified')}
            
            Matching Required Skills: {list(matching_required_skills)}
            Missing Required Skills: {list(missing_required_skills)}
            Matching Preferred Skills: {list(matching_preferred_skills)}
            Missing Preferred Skills: {list(missing_preferred_skills)}
            Additional Candidate Skills: {list(additional_skills)}
            
            Required Skills Match Percentage: {required_match_percentage:.1f}%
            
            Job Summary: {jd_data.get('job_summary', 'Not provided')}
            
            Candidate Experience: {resume_data.get('experience', 'Not provided')}
            
            Provide a brief assessment of:
            1. Overall match (numeric rating 1-10)
            2. Strengths of the candidate relative to the job
            3. Areas where the candidate may need development
            4. Key topics to focus on during the interview
            
            Return the results as a JSON object with keys: 'overall_match_score', 'strengths', 'development_areas', and 'interview_focus_areas'.
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst who specializes in matching candidates to job requirements."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            assessment = json.loads(response.choices[0].message.content)
            
            # Create the final analysis result
            match_analysis = {
                "matching_required_skills": list(matching_required_skills),
                "missing_required_skills": list(missing_required_skills),
                "matching_preferred_skills": list(matching_preferred_skills),
                "missing_preferred_skills": list(missing_preferred_skills),
                "additional_skills": list(additional_skills),
                "required_match_percentage": required_match_percentage,
                "assessment": assessment
            }
            
            return match_analysis
            
        except Exception as e:
            print(f"Error analyzing resume-job match: {e}")
            return {
                "matching_required_skills": [],
                "missing_required_skills": [],
                "matching_preferred_skills": [],
                "missing_preferred_skills": [],
                "additional_skills": [],
                "required_match_percentage": 0,
                "assessment": {
                    "overall_match_score": 0,
                    "strengths": ["Unable to analyze strengths"],
                    "development_areas": ["Unable to analyze development areas"],
                    "interview_focus_areas": ["General job requirements"]
                }
            }
    
    def generate_technical_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any], 
                                    match_analysis: Dict[str, Any], num_questions: int = 3) -> List[Dict[str, Any]]:
        """Generate technical questions based on skills and job requirements"""
        try:
            # Create a prompt that focuses on technical skills
            technical_prompt = f"""
            Generate {num_questions} in-depth technical interview questions based on the following information:

            Job Title: {jd_data.get('job_title', 'Not specified')}
            
            Job Required Skills: {jd_data.get('requirements', {}).get('required_skills', [])}
            Job Preferred Skills: {jd_data.get('requirements', {}).get('preferred_skills', [])}
            
            Candidate Skills: {resume_data.get('skills', [])}
            
            Matching Required Skills: {match_analysis.get('matching_required_skills', [])}
            Missing Required Skills: {match_analysis.get('missing_required_skills', [])}
            
            Interview Focus Areas: {match_analysis.get('assessment', {}).get('interview_focus_areas', [])}
            
            For each question:
            1. Focus on validating the candidate's technical skills
            2. Include questions about both matching skills (to verify depth) and missing skills (to gauge familiarity)
            3. Make questions specific, challenging, and relevant to the job
            4. Include follow-up questions to dig deeper into their knowledge
            5. Suggest what a good answer would include
            
            Return the results as a JSON array of objects, each with keys: 'question', 'follow_ups', 'good_answer_includes', 'evaluation_criteria', and 'skill_being_tested'.
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer for roles in technology and engineering."},
                    {"role": "user", "content": technical_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            questions = json.loads(response.choices[0].message.content)
            
            # Ensure proper formatting of the response
            formatted_questions = []
            if "questions" in questions:
                questions_list = questions["questions"]
            else:
                # If the model didn't use the "questions" key, use whatever is in the root
                questions_list = questions if isinstance(questions, list) else []
            
            for q in questions_list:
                formatted_questions.append({
                    "type": "technical",
                    "question": q.get("question", ""),
                    "follow_ups": q.get("follow_ups", []),
                    "good_answer_includes": q.get("good_answer_includes", ""),
                    "evaluation_criteria": q.get("evaluation_criteria", ""),
                    "skill_being_tested": q.get("skill_being_tested", "")
                })
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error generating technical questions: {e}")
            return [{"type": "technical", "question": "Could not generate technical questions due to an error"}]
    
    def generate_behavioral_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any],
                                     match_analysis: Dict[str, Any], num_questions: int = 3) -> List[Dict[str, Any]]:
        """Generate behavioral questions based on job responsibilities and candidate experience"""
        try:
            behavioral_prompt = f"""
            Generate {num_questions} behavioral interview questions based on the following information:

            Job Title: {jd_data.get('job_title', 'Not specified')}
            
            Job Responsibilities: {jd_data.get('responsibilities', [])}
            
            Candidate Experience: {resume_data.get('experience', [])}
            
            Strengths: {match_analysis.get('assessment', {}).get('strengths', [])}
            Development Areas: {match_analysis.get('assessment', {}).get('development_areas', [])}
            
            For each question:
            1. Use the STAR method framework (Situation, Task, Action, Result)
            2. Focus on relevant past experiences that demonstrate key skills
            3. Make questions specific to the job responsibilities
            4. Include follow-up questions to probe deeper
            5. Include what makes a good response
            
            Return the results as a JSON array of objects, each with keys: 'question', 'follow_ups', 'good_answer_includes', 'evaluation_criteria', and 'trait_being_tested'.
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert behavioral interviewer with experience in HR and recruiting."},
                    {"role": "user", "content": behavioral_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            questions = json.loads(response.choices[0].message.content)
            
            # Ensure proper formatting of the response
            formatted_questions = []
            if "questions" in questions:
                questions_list = questions["questions"]
            else:
                # If the model didn't use the "questions" key, use whatever is in the root
                questions_list = questions if isinstance(questions, list) else []
            
            for q in questions_list:
                formatted_questions.append({
                    "type": "behavioral",
                    "question": q.get("question", ""),
                    "follow_ups": q.get("follow_ups", []),
                    "good_answer_includes": q.get("good_answer_includes", ""),
                    "evaluation_criteria": q.get("evaluation_criteria", ""),
                    "trait_being_tested": q.get("trait_being_tested", "")
                })
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error generating behavioral questions: {e}")
            return [{"type": "behavioral", "question": "Could not generate behavioral questions due to an error"}]
def generate_situational_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any],
                                      match_analysis: Dict[str, Any], num_questions: int = 2) -> List[Dict[str, Any]]:
        """Generate situational questions based on job requirements and responsibilities"""
        try:
            situational_prompt = f"""
            Generate {num_questions} situational interview questions based on the following information:

            Job Title: {jd_data.get('job_title', 'Not specified')}
            
            Job Responsibilities: {jd_data.get('responsibilities', [])}
            Job Requirements: {jd_data.get('requirements', {})}
            
            Development Areas: {match_analysis.get('assessment', {}).get('development_areas', [])}
            Interview Focus Areas: {match_analysis.get('assessment', {}).get('interview_focus_areas', [])}
            
            For each question:
            1. Create hypothetical but realistic scenarios that the candidate might face in this role
            2. Focus on problem-solving and decision-making abilities
            3. Make scenarios specific to the job context
            4. Include follow-up questions to explore their thinking process
            5. Include what makes a good response
            
            Return the results as a JSON array of objects, each with keys: 'question', 'scenario', 'follow_ups', 'good_answer_includes', 'evaluation_criteria', and 'skills_being_tested'.
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who specializes in situational and case-based interviews."},
                    {"role": "user", "content": situational_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            questions = json.loads(response.choices[0].message.content)
            
            # Ensure proper formatting of the response
            formatted_questions = []
            if "questions" in questions:
                questions_list = questions["questions"]
            else:
                # If the model didn't use the "questions" key, use whatever is in the root
                questions_list = questions if isinstance(questions, list) else []
            
            for q in questions_list:
                formatted_questions.append({
                    "type": "situational",
                    "question": q.get("question", ""),
                    "scenario": q.get("scenario", ""),
                    "follow_ups": q.get("follow_ups", []),
                    "good_answer_includes": q.get("good_answer_includes", ""),
                    "evaluation_criteria": q.get("evaluation_criteria", ""),
                    "skills_being_tested": q.get("skills_being_tested", "")
                })
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error generating situational questions: {e}")
            return [{"type": "situational", "question": "Could not generate situational questions due to an error"}]
    
    def generate_company_culture_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any],
                                         num_questions: int = 1) -> List[Dict[str, Any]]:
        """Generate questions about company culture and fit"""
        try:
            culture_prompt = f"""
            Generate {num_questions} company culture fit interview questions based on the following information:

            Job Title: {jd_data.get('job_title', 'Not specified')}
            Company: {jd_data.get('company', 'Not specified')}
            
            Job Summary: {jd_data.get('job_summary', '')}
            Additional Info: {jd_data.get('additional_info', '')}
            
            For each question:
            1. Focus on assessing cultural alignment and work style preferences
            2. Include questions about teamwork, communication, and work environment preferences
            3. Make questions specific to the company's potential culture based on the job description
            4. Include follow-up questions
            5. Include what makes a good response
            
            Return the results as a JSON array of objects, each with keys: 'question', 'follow_ups', 'good_answer_includes', 'evaluation_criteria', and 'aspect_being_tested'.
            """
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who specializes in assessing company culture fit."},
                    {"role": "user", "content": culture_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            questions = json.loads(response.choices[0].message.content)
            
            # Ensure proper formatting of the response
            formatted_questions = []
            if "questions" in questions:
                questions_list = questions["questions"]
            else:
                # If the model didn't use the "questions" key, use whatever is in the root
                questions_list = questions if isinstance(questions, list) else []
            
            for q in questions_list:
                formatted_questions.append({
                    "type": "company_culture",
                    "question": q.get("question", ""),
                    "follow_ups": q.get("follow_ups", []),
                    "good_answer_includes": q.get("good_answer_includes", ""),
                    "evaluation_criteria": q.get("evaluation_criteria", ""),
                    "aspect_being_tested": q.get("aspect_being_tested", "")
                })
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error generating company culture questions: {e}")
            return [{"type": "company_culture", "question": "Could not generate company culture questions due to an error"}]
    
    def generate_questions(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any], 
                          total_questions: int = MAX_QUESTIONS) -> Dict[str, Any]:
        """
        Generate a complete set of interview questions based on the resume and job description
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
            total_questions: Total number of questions to generate
            
        Returns:
            Dictionary with match analysis and generated questions
        """
        # Analyze the match between resume and job description
        match_analysis = self.analyze_match(resume_data, jd_data)
        
        # Calculate the number of questions for each type
        question_counts = {}
        remaining_questions = total_questions
        
        for q_type, data in self.question_types.items():
            if q_type == list(self.question_types.keys())[-1]:
                # For the last question type, use all remaining questions
                question_counts[q_type] = remaining_questions
            else:
                # Calculate based on weight
                count = int(total_questions * data["weight"])
                question_counts[q_type] = max(1, count)  # Ensure at least 1 question per type
                remaining_questions -= question_counts[q_type]
        
        # Generate questions for each type
        technical_questions = self.generate_technical_questions(
            resume_data, jd_data, match_analysis, question_counts["technical"]
        )
        
        behavioral_questions = self.generate_behavioral_questions(
            resume_data, jd_data, match_analysis, question_counts["behavioral"]
        )
        
        situational_questions = self.generate_situational_questions(
            resume_data, jd_data, match_analysis, question_counts["situational"]
        )
        
        culture_questions = self.generate_company_culture_questions(
            resume_data, jd_data, question_counts["company_culture"]
        )
        
        # Combine all questions
        all_questions = []
        all_questions.extend(technical_questions)
        all_questions.extend(behavioral_questions)
        all_questions.extend(situational_questions)
        all_questions.extend(culture_questions)
        
        # Add a unique identifier to each question
        for i, question in enumerate(all_questions):
            question["id"] = f"q{i+1}"
        
        # Return the complete interview data
        return {
            "match_analysis": match_analysis,
            "questions": all_questions
        }
    
    def generate_from_resume_and_jd_files(self, resume_file_path: str, jd_file_path: str) -> Dict[str, Any]:
        """
        Generate interview questions from resume and job description files
        
        Args:
            resume_file_path: Path to the resume file
            jd_file_path: Path to the job description file
            
        Returns:
            Dictionary with match analysis and generated questions
        """
        # Parse resume and job description
        resume_parser = ResumeParser()
        jd_parser = JobDescriptionParser()
        
        resume_data = resume_parser.parse(resume_file_path)
        jd_data = jd_parser.parse(jd_file_path)
        
        # Generate questions
        return self.generate_questions(resume_data, jd_data)
    
    def generate_from_parsed_data(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interview questions from already parsed resume and job description data
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
            
        Returns:
            Dictionary with match analysis and generated questions
        """
        return self.generate_questions(resume_data, jd_data)