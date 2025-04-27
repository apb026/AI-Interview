import os
import json
import time
import datetime
from firebase_admin import firestore
from app.auth.models import User

class InterviewSessionRecorder:
    """
    Records and manages interview sessions including questions, answers, and feedback.
    """
    
    def __init__(self, user_id, job_id=None):
        """
        Initialize the session recorder.
        
        Args:
            user_id (str): The ID of the user taking the interview
            job_id (str, optional): The ID of the job position
        """
        self.user_id = user_id
        self.job_id = job_id
        self.session_id = f"{user_id}_{int(time.time())}"
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.questions = []
        self.answers = []
        self.feedback = []
        self.metrics = {
            "total_questions": 0,
            "avg_response_time": 0,
            "completion_rate": 0,
            "technical_score": 0,
            "communication_score": 0,
            "overall_score": 0
        }
        self.db = firestore.client()
        
    def start_session(self, job_title=None, resume_path=None, jd_path=None):
        """
        Start a new interview session
        
        Args:
            job_title (str, optional): Title of the job
            resume_path (str, optional): Path to the resume file
            jd_path (str, optional): Path to the job description file
        
        Returns:
            str: Session ID
        """
        session_data = {
            "user_id": self.user_id,
            "job_id": self.job_id,
            "job_title": job_title,
            "start_time": self.start_time,
            "status": "active",
            "resume_path": resume_path,
            "jd_path": jd_path
        }
        
        # Save session to database
        self.db.collection('interview_sessions').document(self.session_id).set(session_data)
        
        return self.session_id
    
    def record_question(self, question, question_type="technical", difficulty=1):
        """
        Record a question asked during the interview
        
        Args:
            question (str): The question text
            question_type (str): Type of question (technical, behavioral, etc.)
            difficulty (int): Difficulty level (1-5)
            
        Returns:
            int: Question index
        """
        question_data = {
            "text": question,
            "type": question_type,
            "difficulty": difficulty,
            "timestamp": datetime.datetime.now()
        }
        
        self.questions.append(question_data)
        question_idx = len(self.questions) - 1
        
        # Update database
        self.db.collection('interview_sessions').document(self.session_id).collection(
            'questions').document(str(question_idx)).set(question_data)
        
        return question_idx
    
    def record_answer(self, question_idx, answer, response_time=None):
        """
        Record the candidate's answer to a question
        
        Args:
            question_idx (int): Index of the question being answered
            answer (str): The candidate's answer
            response_time (float, optional): Time taken to respond in seconds
            
        Returns:
            int: Answer index
        """
        answer_data = {
            "question_idx": question_idx,
            "text": answer,
            "response_time": response_time,
            "timestamp": datetime.datetime.now()
        }
        
        self.answers.append(answer_data)
        answer_idx = len(self.answers) - 1
        
        # Update database
        self.db.collection('interview_sessions').document(self.session_id).collection(
            'answers').document(str(answer_idx)).set(answer_data)
        
        return answer_idx
    
    def record_feedback(self, question_idx, answer_idx, feedback_text, score=None):
        """
        Record feedback for an answer
        
        Args:
            question_idx (int): Index of the question
            answer_idx (int): Index of the answer
            feedback_text (str): Feedback on the answer
            score (float, optional): Score for the answer (0-10)
            
        Returns:
            int: Feedback index
        """
        feedback_data = {
            "question_idx": question_idx,
            "answer_idx": answer_idx,
            "text": feedback_text,
            "score": score,
            "timestamp": datetime.datetime.now()
        }
        
        self.feedback.append(feedback_data)
        feedback_idx = len(self.feedback) - 1
        
        # Update database
        self.db.collection('interview_sessions').document(self.session_id).collection(
            'feedback').document(str(feedback_idx)).set(feedback_data)
        
        return feedback_idx
    
    def end_session(self, calculate_metrics=True):
        """
        End the interview session and calculate final metrics
        
        Args:
            calculate_metrics (bool): Whether to calculate final metrics
            
        Returns:
            dict: Session summary with metrics
        """
        self.end_time = datetime.datetime.now()
        
        if calculate_metrics:
            self._calculate_metrics()
        
        session_summary = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (self.end_time - self.start_time).total_seconds(),
            "total_questions": len(self.questions),
            "metrics": self.metrics,
            "status": "completed"
        }
        
        # Update database
        self.db.collection('interview_sessions').document(self.session_id).update({
            "end_time": self.end_time,
            "duration": (self.end_time - self.start_time).total_seconds(),
            "metrics": self.metrics,
            "status": "completed"
        })
        
        return session_summary
    
    def _calculate_metrics(self):
        """Calculate interview performance metrics based on answers and feedback"""
        if not self.answers:
            return
        
        # Calculate total questions and completion rate
        self.metrics["total_questions"] = len(self.questions)
        self.metrics["completion_rate"] = len(self.answers) / len(self.questions) if self.questions else 0
        
        # Calculate average response time
        response_times = [a.get("response_time", 0) for a in self.answers if a.get("response_time")]
        self.metrics["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate scores from feedback
        if self.feedback:
            technical_scores = []
            communication_scores = []
            
            for f in self.feedback:
                score = f.get("score")
                if score is not None:
                    q_idx = f.get("question_idx")
                    if q_idx is not None and q_idx < len(self.questions):
                        q_type = self.questions[q_idx].get("type")
                        if q_type == "technical":
                            technical_scores.append(score)
                        else:
                            communication_scores.append(score)
            
            if technical_scores:
                self.metrics["technical_score"] = sum(technical_scores) / len(technical_scores)
            
            if communication_scores:
                self.metrics["communication_score"] = sum(communication_scores) / len(communication_scores)
            
            # Calculate overall score
            if technical_scores or communication_scores:
                tech_weight = 0.7  # Technical questions weighted more
                comm_weight = 0.3
                
                if not technical_scores:
                    self.metrics["overall_score"] = self.metrics["communication_score"]
                elif not communication_scores:
                    self.metrics["overall_score"] = self.metrics["technical_score"]
                else:
                    self.metrics["overall_score"] = (
                        tech_weight * self.metrics["technical_score"] + 
                        comm_weight * self.metrics["communication_score"]
                    )
    
    def get_session_transcript(self):
        """
        Generate a transcript of the interview session
        
        Returns:
            list: Transcript of questions, answers and feedback
        """
        transcript = []
        
        for i, question in enumerate(self.questions):
            q_entry = {
                "type": "question",
                "text": question["text"],
                "timestamp": question["timestamp"]
            }
            transcript.append(q_entry)
            
            # Find corresponding answer
            answer = next((a for a in self.answers if a["question_idx"] == i), None)
            if answer:
                a_entry = {
                    "type": "answer",
                    "text": answer["text"],
                    "timestamp": answer["timestamp"]
                }
                transcript.append(a_entry)
                
                # Find corresponding feedback
                feedback = next((f for f in self.feedback if f["answer_idx"] == i), None)
                if feedback:
                    f_entry = {
                        "type": "feedback",
                        "text": feedback["text"],
                        "timestamp": feedback["timestamp"]
                    }
                    transcript.append(f_entry)
        
        return transcript
    
    def export_session(self, format="json", output_path=None):
        """
        Export the interview session data
        
        Args:
            format (str): Export format (json, pdf, txt)
            output_path (str, optional): Path to save the export
            
        Returns:
            str: Path to the exported file or the data string
        """
        session_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time) if self.end_time else None,
            "questions": self.questions,
            "answers": self.answers,
            "feedback": self.feedback,
            "metrics": self.metrics,
            "transcript": self.get_session_transcript()
        }
        
        if format == "json":
            # Convert datetime objects to strings
            export_data = json.dumps(session_data, default=str, indent=2)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(export_data)
                return output_path
            else:
                return export_data
        
        elif format == "txt":
            # Generate plain text format
            transcript = self.get_session_transcript()
            text_output = f"Interview Session: {self.session_id}\n"
            text_output += f"Date: {self.start_time.strftime('%Y-%m-%d')}\n"
            text_output += f"Duration: {(self.end_time - self.start_time).total_seconds() / 60:.2f} minutes\n\n"
            
            for item in transcript:
                item_type = item["type"].capitalize()
                timestamp = item["timestamp"].strftime('%H:%M:%S')
                text_output += f"[{timestamp}] {item_type}: {item['text']}\n\n"
            
            text_output += f"\nMetrics:\n"
            for metric, value in self.metrics.items():
                text_output += f"{metric.replace('_', ' ').title()}: {value}\n"
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(text_output)
                return output_path
            else:
                return text_output
                
        else:
            raise ValueError(f"Unsupported export format: {format}")