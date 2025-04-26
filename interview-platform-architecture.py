# Project Structure
"""
interview_platform/
│
├── main.py                     # Main application entry point
├── requirements.txt            # Project dependencies
│
├── app/                        # Main application directory
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── auth/                   # Authentication functionality
│   │   ├── __init__.py
│   │   ├── routes.py           # Auth routes (login, register, etc.)
│   │   └── models.py           # User models
│   │
│   ├── document_processing/    # Resume and JD processing
│   │   ├── __init__.py
│   │   ├── resume_parser.py    # Resume parsing logic
│   │   ├── jd_parser.py        # Job description parsing
│   │   └── web_scraper.py      # Web scraping for JD links
│   │
│   ├── interview/              # Interview system
│   │   ├── __init__.py
│   │   ├── rag_engine.py       # RAG implementation
│   │   ├── question_generator.py  # Interview question generation
│   │   ├── personas.py         # AI interviewer personas
│   │   └── session_recorder.py # Interview recording functionality
│   │
│   ├── static/                 # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   └── templates/              # HTML templates for the UI
│       ├── landing.html
│       ├── dashboard.html
│       ├── upload.html
│       └── interview_room.html
│
└── database/                   # Database operations
    ├── __init__.py
    ├── firebase_client.py      # Firebase integration
    └── models.py               # Data models
"""

# main.py - Entry point of the application
import streamlit as st
from app.auth.routes import setup_auth_routes
from app.document_processing.resume_parser import setup_document_routes
from app.interview.rag_engine import setup_interview_routes
from app.config import setup_app_config

def main():
    st.set_page_config(
        page_title="AI Interview Preparation Platform",
        page_icon="👔",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # App configuration
    app_config = setup_app_config()
    
    # Main page routing based on authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
    
    if not st.session_state.authenticated:
        show_landing_page()
    else:
        show_main_application()

def show_landing_page():
    st.title("Interview Coach AI")
    st.subheader("Prepare for your dream job with AI-powered interviews")
    
    cols = st.columns(3)
    
    with cols[0]:
        if st.button("Sign In", use_container_width=True):
            st.session_state.page = "signin"
    
    with cols[1]:
        if st.button("Register", use_container_width=True):
            st.session_state.page = "register"
    
    with cols[2]:
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = "guest"
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Handle authentication flows
    if 'page' in st.session_state:
        if st.session_state.page == "signin":
            show_signin_form()
        elif st.session_state.page == "register":
            show_registration_form()

def show_signin_form():
    st.subheader("Sign In")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        # Authenticate with Firebase
        from app.auth.routes import authenticate_user
        success, user_data = authenticate_user(email, password)
        
        if success:
            st.session_state.authenticated = True
            st.session_state.user_role = "registered"
            st.session_state.user_data = user_data
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
    
    if st.button("Back"):
        st.session_state.pop("page")
        st.rerun()

def show_registration_form():
    st.subheader("Register")
    
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
            return
            
        # Register with Firebase
        from app.auth.routes import register_user
        success, user_data = register_user(name, email, password)
        
        if success:
            st.success("Registration successful! Please sign in.")
            st.session_state.page = "signin"
            st.rerun()
        else:
            st.error("Registration failed. Please try again.")
    
    if st.button("Back"):
        st.session_state.pop("page")
        st.rerun()

def show_main_application():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Upload Documents", "Interview Room", "Past Sessions"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Documents":
        show_upload_page()
    elif page == "Interview Room":
        show_interview_room()
    elif page == "Past Sessions":
        show_past_sessions()

def show_dashboard():
    st.title("Welcome to Interview Coach AI")
    
    st.write("Prepare for your upcoming interviews with our AI-powered platform.")
    
    # Dashboard stats and quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Stats")
        if st.session_state.user_role == "registered":
            st.metric("Completed Interviews", "5")
            st.metric("Average Performance", "76%")
        else:
            st.info("Sign in to track your interview performance over time.")
    
    with col2:
        st.subheader("Quick Actions")
        st.button("Upload Resume", on_click=lambda: set_page("Upload Documents"))
        st.button("Start New Interview", on_click=lambda: set_page("Interview Room"))

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def show_upload_page():
    st.title("Upload Your Documents")
    
    tab1, tab2 = st.tabs(["Resume/CV", "Job Description"])
    
    with tab1:
        st.subheader("Upload your Resume/CV")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
        
        if uploaded_file is not None:
            # Process resume
            from app.document_processing.resume_parser import parse_resume
            resume_data = parse_resume(uploaded_file)
            
            if resume_data:
                st.success("Resume uploaded and processed successfully!")
                st.session_state.resume_data = resume_data
    
    with tab2:
        st.subheader("Job Description")
        
        jd_method = st.radio("Job Description Source", ["Upload File", "Paste Text", "Enter URL"])
        
        if jd_method == "Upload File":
            jd_file = st.file_uploader("Choose a JD file", type=["pdf", "docx", "txt"])
            
            if jd_file is not None:
                # Process JD file
                from app.document_processing.jd_parser import parse_jd_file
                jd_data = parse_jd_file(jd_file)
                
                if jd_data:
                    st.success("Job description uploaded and processed successfully!")
                    st.session_state.jd_data = jd_data
        
        elif jd_method == "Paste Text":
            jd_text = st.text_area("Paste the job description here", height=300)
            
            if st.button("Process Job Description") and jd_text:
                # Process JD text
                from app.document_processing.jd_parser import parse_jd_text
                jd_data = parse_jd_text(jd_text)
                
                if jd_data:
                    st.success("Job description processed successfully!")
                    st.session_state.jd_data = jd_data
        
        elif jd_method == "Enter URL":
            jd_url = st.text_input("Enter the job posting URL")
            
            if st.button("Fetch Job Description") and jd_url:
                # Scrape and process JD from URL
                from app.document_processing.web_scraper import scrape_job_description
                jd_data = scrape_job_description(jd_url)
                
                if jd_data:
                    st.success("Job description fetched and processed successfully!")
                    st.session_state.jd_data = jd_data
                else:
                    st.error("Failed to extract job description from the provided URL.")
    
    # Display country selection if JD doesn't specify
    if hasattr(st.session_state, 'jd_data') and 'country' not in st.session_state.jd_data:
        st.subheader("Additional Information")
        country = st.selectbox("Select target country for the job", 
                              ["United States", "United Kingdom", "Australia", "Canada", "India", "Singapore", "Germany"])
        
        if st.button("Save Country"):
            st.session_state.jd_data['country'] = country
            st.success(f"Set target country to {country}")
    
    # Proceed to interview setup
    if hasattr(st.session_state, 'resume_data') and hasattr(st.session_state, 'jd_data'):
        if st.button("Proceed to Interview"):
            st.session_state.page = "Interview Room"
            st.rerun()

def show_interview_room():
    st.title("Interview Room")
    
    # Check if resume and JD data are available
    if not hasattr(st.session_state, 'resume_data') or not hasattr(st.session_state, 'jd_data'):
        st.warning("Please upload your resume and job description first.")
        if st.button("Go to Upload Page"):
            st.session_state.page = "Upload Documents"
            st.rerun()
        return
    
    # Interview configuration
    st.subheader("Interview Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        interviewer_accent = st.selectbox(
            "Interviewer Accent",
            ["American (US)", "British (UK)", "Australian", "Indian", "Chinese"]
        )
        
        interviewer_gender = st.radio("Interviewer Voice", ["Male", "Female"])
        
        show_subtitles = st.checkbox("Show subtitles", value=True)
    
    with col2:
        st.subheader("Interview Focus")
        technical_focus = st.slider("Technical vs. Behavioral", 0, 100, 50,
                                  help="0 = Fully behavioral, 100 = Fully technical")
        
        interview_duration = st.slider("Interview Duration (minutes)", 10, 60, 20)
    
    # Start interview button
    if st.button("Start Interview", type="primary"):
        # Initialize interview session
        from app.interview.question_generator import initialize_interview
        from app.interview.personas import get_interviewer_persona
        
        persona = get_interviewer_persona(interviewer_accent, interviewer_gender)
        interview_config = {
            "technical_focus": technical_focus,
            "duration": interview_duration,
            "show_subtitles": show_subtitles,
            "persona": persona
        }
        
        interview_session = initialize_interview(
            st.session_state.resume_data,
            st.session_state.jd_data,
            interview_config
        )
        
        st.session_state.interview_session = interview_session
        st.session_state.interview_active = True
        st.rerun()
    
    # Show active interview if it's ongoing
    if hasattr(st.session_state, 'interview_active') and st.session_state.interview_active:
        show_active_interview()

def show_active_interview():
    st.subheader("Interview in Progress")
    
    # Here we would integrate with LiveKit for video interview
    # Placeholder for the LiveKit integration
    st.write("This is where the video interview would be rendered.")
    
    # Display the current question
    if 'current_question' not in st.session_state:
        # Get first question from the interview session
        from app.interview.question_generator import get_next_question
        st.session_state.current_question = get_next_question(st.session_state.interview_session)
        st.session_state.question_number = 1
    
    st.subheader(f"Question {st.session_state.question_number}")
    st.write(st.session_state.current_question)
    
    # Subtitles if enabled
    if st.session_state.interview_session['config']['show_subtitles']:
        st.markdown("---")
        st.caption(st.session_state.current_question)
    
    # For demo purposes - next question button
    if st.button("Next Question"):
        from app.interview.question_generator import get_next_question
        next_question = get_next_question(st.session_state.interview_session)
        
        if next_question:
            st.session_state.current_question = next_question
            st.session_state.question_number += 1
            st.rerun()
        else:
            # Interview completed
            st.session_state.interview_active = False
            st.session_state.interview_completed = True
            st.rerun()
    
    # End interview button
    if st.button("End Interview"):
        st.session_state.interview_active = False
        st.rerun()

def show_past_sessions():
    st.title("Past Interview Sessions")
    
    if st.session_state.user_role == "guest":
        st.info("Please sign in to view your past interview sessions.")
        return
    
    # Placeholder - in a real app, we would load this from the database
    sample_sessions = [
        {"id": "001", "date": "2025-04-20", "job_title": "Senior Python Developer", "score": 82},
        {"id": "002", "date": "2025-04-15", "job_title": "Data Scientist", "score": 78},
        {"id": "003", "date": "2025-04-10", "job_title": "Machine Learning Engineer", "score": 91}
    ]
    
    for session in sample_sessions:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.subheader(session["job_title"])
            st.caption(f"Interview Date: {session['date']}")
        
        with col2:
            st.metric("Performance Score", f"{session['score']}%")
        
        with col3:
            st.button("View Details", key=f"view_{session['id']}")
        
        st.divider()

if __name__ == "__main__":
    main()
