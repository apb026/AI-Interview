import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewSession:
    """Represents an interview session with metadata and QA pairs."""
    
    def __init__(self, 
               session_id: Optional[str] = None,
               candidate_id: Optional[str] = None,
               job_id: Optional[str] = None,
               interviewer_persona_id: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None):
        """Initialize an interview session.
        
        Args:
            session_id: Unique identifier for the session
            candidate_id: ID of the candidate
            job_id: ID of the job position
            interviewer_persona_id: ID of the interviewer persona
            metadata: Additional session metadata
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.candidate_id = candidate_id
        self.job_id = job_id
        self.interviewer_persona_id = interviewer_persona_id
        self.metadata = metadata or {}
        
        # Initialize session data
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.questions = []
        self.answers = []
        self.evaluations = []
        self.notes = []
        self.overall_score = None
        self.status = "in_progress"  # in_progress, completed, canceled
    
    def add_question(self, question: Dict[str, Any]) -> None:
        """Add a question to the session.
        
        Args:
            question: Question data with text and metadata
        """
        question_entry = {
            "question_id": len(self.questions) + 1,
            "text": question["question"],
            "category": question.get("category", "general"),
            "timestamp": time.time(),
            "metadata": question.get("metadata", {})
        }
        self.questions.append(question_entry)
    
    def add_answer(self, question_id: int, answer_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an answer to a question.
        
        Args:
            question_id: ID of the question being answered
            answer_text: Text of the candidate's answer
            metadata: Additional metadata about the answer
        """
        answer_entry = {
            "question_id": question_id,
            "text": answer_text,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.answers.append(answer_entry)
    
    def add_evaluation(self, question_id: int, evaluation: Dict[str, Any]) -> None:
        """Add an evaluation for an answer.
        
        Args:
            question_id: ID of the question being evaluated
            evaluation: Evaluation data including scores and feedback
        """
        eval_entry = {
            "question_id": question_id,
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", ""),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("improvements", []),
            "timestamp": time.time()
        }
        self.evaluations.append(eval_entry)
    
    def add_note(self, note: str, note_type: str = "general") -> None:
        """Add a note to the session.
        
        Args:
            note: Note text
            note_type: Type of note (general, observation, etc.)
        """
        note_entry = {
            "text": note,
            "type": note_type,
            "timestamp": time.time()
        }
        self.notes.append(note_entry)
    
    def end_session(self, overall_score: Optional[float] = None) -> None:
        """End the interview session.
        
        Args:
            overall_score: Overall score for the interview
        """
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = "completed"
        self.overall_score = overall_score
    
    def cancel_session(self, reason: Optional[str] = None) -> None:
        """Cancel the interview session.
        
        Args:
            reason: Reason for cancellation
        """
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = "canceled"
        if reason:
            self.add_note(reason, "cancellation_reason")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary representation.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "interviewer_persona_id": self.interviewer_persona_id,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "questions": self.questions,
            "answers": self.answers,
            "evaluations": self.evaluations,
            "notes": self.notes,
            "overall_score": self.overall_score,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a session from a dictionary.
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            New InterviewSession instance
        """
        session = cls(
            session_id=data.get("session_id"),
            candidate_id=data.get("candidate_id"),
            job_id=data.get("job_id"),
            interviewer_persona_id=data.get("interviewer_persona_id"),
            metadata=data.get("metadata", {})
        )
        
        session.start_time = data.get("start_time", time.time())
        session.end_time = data.get("end_time")
        session.duration = data.get("duration")
        session.questions = data.get("questions", [])
        session.answers = data.get("answers", [])
        session.evaluations = data.get("evaluations", [])
        session.notes = data.get("notes", [])
        session.overall_score = data.get("overall_score")
        session.status = data.get("status", "in_progress")
        
        return session


class SessionRecorder:
    """Record and manage interview sessions."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the session recorder.
        
        Args:
            storage_dir: Directory for storing session data
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "interview_sessions")
        self.active_sessions = {}
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def create_session(self, 
                     candidate_id: Optional[str] = None,
                     job_id: Optional[str] = None,
                     interviewer_persona_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> InterviewSession:
        """Create a new interview session.
        
        Args:
            candidate_id: ID of the candidate
            job_id: ID of the job position
            interviewer_persona_id: ID of the interviewer persona
            metadata: Additional session metadata
            
        Returns:
            New InterviewSession instance
        """
        session = InterviewSession(
            candidate_id=candidate_id,
            job_id=job_id,
            interviewer_persona_id=interviewer_persona_id,
            metadata=metadata
        )
        
        # Add to active sessions
        self.active_sessions[session.session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            InterviewSession if found, None otherwise
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Try to load from storage
        try:
            session_path = os.path.join(self.storage_dir, f"{session_id}.json")
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
                return InterviewSession.from_dict(session_data)
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
        
        return None
    
    def save_session(self, session: InterviewSession) -> bool:
        """Save a session to storage.
        
        Args:
            session: Session to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            session_path = os.path.join(self.storage_dir, f"{session.session_id}.json")
            with open(session_path, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {str(e)}")
            return False
    
    def end_and_save_session(self, session_id: str, overall_score: Optional[float] = None) -> bool:
        """End a session and save it to storage.
        
        Args:
            session_id: ID of the session to end
            overall_score: Overall score for the interview
            
        Returns:
            True if ended and saved successfully, False otherwise
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found in active sessions")
            return False
        
        session = self.active_sessions[session_id]
        session.end_session(overall_score)
        
        # Save to storage
        success = self.save_session(session)
        
        # Remove from active sessions if saved successfully
        if success:
            del self.active_sessions[session_id]
        
        return success
    
    def get_session_transcript(self, session_id: str) -> List[Dict[str, Any]]:
        """Get a chronological transcript of the session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of question-answer pairs in chronological order
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Create a merged list of questions and answers
        transcript = []
        
        # Add questions to transcript
        for q in session.questions:
            transcript.append({
                "type": "question",
                "timestamp": q["timestamp"],
                "question_id": q["question_id"],
                "text": q["text"],
                "category": q.get("category", "general")
            })
        
        # Add answers to transcript
        for a in session.answers:
            transcript.append({
                "type": "answer",
                "timestamp": a["timestamp"],
                "question_id": a["question_id"],
                "text": a["text"]
            })
        
        # Sort by timestamp
        transcript.sort(key=lambda x: x["timestamp"])
        
        return transcript
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate a summary of the interview session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Summary data for the session
        """
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}