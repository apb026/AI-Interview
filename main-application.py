# main.py - Main application entry point
import streamlit as st
import os
from dotenv import load_dotenv
import json
import uuid
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Import UI components
from app.ui.landing_page import display_landing_page
from app.ui.dashboard import display_dashboard
from app.ui.upload_page import display_upload_page
from app.ui.interview_room import display_interview_room

# Import backend services
from app.services.livekit_service import LiveKitService
from app.services.transcription_service import TranscriptionService
from app.services.ai_service import AIService
from app.services.user_service import UserService
from app.services.storage_service import StorageService

# Import utilities
from app.utils.resume_parser import ResumeParser
from app.utils.job_analyzer import JobDescriptionAnalyzer
from app.utils.question_generator import QuestionGenerator
from app.utils.feedback_engine import FeedbackEngine

# Configure Streamlit page
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    livekit_service = LiveKitService(
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        ws_url=os.getenv("LIVEKIT_WS_URL")
    )
    transcription_service = TranscriptionService()
    ai_service = AIService(api_key=os.getenv("OPENAI_API_KEY"))
    user_service = UserService()
    storage_service = StorageService()
    
    return {
        "livekit": livekit_service,
        "transcription": transcription_service,
        "ai": ai_service,
        "user": user_service,
        "storage": storage_service
    }

# Helper functions
def setup_session_state():
    """Initialize session state variables if they don't exist"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "landing"
    
    if "interview_active" not in st.session_state:
        st.session_state.interview_active = False
    
    if "interview_data" not in st.session_state:
        st.session_state.interview_data = {
            "id": None,
            "start_time": None,
            "end_time": None,
            "job_description": None,
            "resume_data": None,
            "interview_type": None,
            "questions": [],
            "transcript": [],
            "feedback": None
        }
    
    if "room_name" not in st.session_state:
        st.session_state.room_name = None
        
    if "token" not in st.session_state:
        st.session_state.token = None

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

def start_interview(job_description, resume_data, interview_type):
    """Set up and start a new interview session"""
    services = initialize_services()
    
    # Create a new interview session
    interview_id = str(uuid.uuid4())
    room_name = f"interview-{interview_id}"
    
    # Generate token for the user
    token = services["livekit"].create_token(
        room_name=room_name,
        participant_name=st.session_state.user_id,
        participant_identity=st.session_state.user_id
    )
    
    # Parse resume and analyze job description
    resume_parser = ResumeParser(services["ai"])
    job_analyzer = JobDescriptionAnalyzer(services["ai"])
    
    with st.spinner("Analyzing resume and job description..."):
        parsed_resume = resume_parser.parse(resume_data)
        analyzed_job = job_analyzer.analyze(job_description)
    
    # Generate initial questions
    question_generator = QuestionGenerator(services["ai"])
    
    with st.spinner("Generating interview questions..."):
        initial_questions = question_generator.generate_initial_questions(
            parsed_resume, 
            analyzed_job,
            interview_type
        )
    
    # Set up interview data
    st.session_state.interview_data = {
        "id": interview_id,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "job_description": job_description,
        "resume_data": resume_data,
        "interview_type": interview_type,
        "questions": initial_questions,
        "transcript": [],
        "feedback": None
    }
    
    # Store token and room name
    st.session_state.room_name = room_name
    st.session_state.token = token
    st.session_state.interview_active = True
    
    # Save interview data
    services["storage"].save_interview_data(st.session_state.user_id, interview_id, st.session_state.interview_data)
    
    # Navigate to interview room
    navigate_to("interview")

def end_interview():
    """End the current interview session and generate feedback"""
    if not st.session_state.interview_active:
        return
    
    services = initialize_services()
    
    # Mark interview as ended
    st.session_state.interview_data["end_time"] = datetime.now().isoformat()
    st.session_state.interview_active = False
    
    # Generate feedback
    feedback_engine = FeedbackEngine(services["ai"])
    
    with st.spinner("Generating interview feedback..."):
        feedback = feedback_engine.generate_feedback(
            st.session_state.interview_data["transcript"],
            st.session_state.interview_data["job_description"],
            st.session_state.interview_data["resume_data"]
        )
    
    # Update interview data with feedback
    st.session_state.interview_data["feedback"] = feedback
    
    # Save final interview data
    services["storage"].save_interview_data(
        st.session_state.user_id, 
        st.session_state.interview_data["id"], 
        st.session_state.interview_data
    )
    
    # Navigate to dashboard
    navigate_to("dashboard")

def save_transcript_update(transcript_entry):
    """Save a new transcript entry during the interview"""
    if not st.session_state.interview_active:
        return
    
    services = initialize_services()
    
    # Add transcript entry
    st.session_state.interview_data["transcript"].append(transcript_entry)
    
    # Save updated interview data
    services["storage"].save_interview_data(
        st.session_state.user_id, 
        st.session_state.interview_data["id"], 
        st.session_state.interview_data
    )

def main():
    """Main application entry point"""
    # Initialize session state
    setup_session_state()
    
    # Initialize services
    services = initialize_services()
    
    # Display the appropriate page based on session state
    if st.session_state.current_page == "landing":
        display_landing_page(navigate_to)
        
    elif st.session_state.current_page == "dashboard":
        # Get user's interview history
        interview_history = services["storage"].get_user_interviews(st.session_state.user_id)
        display_dashboard(interview_history, navigate_to, start_interview)
        
    elif st.session_state.current_page == "upload":
        display_upload_page(navigate_to, start_interview)
        
    elif st.session_state.current_page == "interview":
        # Check if interview is active
        if not st.session_state.interview_active:
            st.error("No active interview session found")
            st.button("Return to Dashboard", on_click=lambda: navigate_to("dashboard"))
        else:
            # Display interview room with LiveKit integration
            display_interview_room(
                room_name=st.session_state.room_name,
                token=st.session_state.token,
                interview_data=st.session_state.interview_data,
                end_interview_callback=end_interview,
                save_transcript_callback=save_transcript_update
            )

if __name__ == "__main__":
    main()