# app/ui/landing_page.py (continued)
def display_register_form():
    """Display registration form"""
    st.subheader("Create Account")
    
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if name and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # In a real app, register with Firebase
                    from app.auth.firebase_auth import FirebaseAuth
                    auth = FirebaseAuth()
                    success, result = auth.sign_up(email, password, name)
                    
                    if success:
                        st.success("Registration successful! Please sign in.")
                        st.session_state.show_form = "signin"
                        st.experimental_rerun()
                    else:
                        st.error(f"Registration failed: {result}")
            else:
                st.error("Please fill in all fields.")
    
    if st.button("Back to Home"):
        st.session_state.pop("show_form", None)
        st.experimental_rerun()


# app/ui/dashboard.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

def display_dashboard(user_data=None):
    """Display the user dashboard"""
    st.title(f"Welcome, {st.session_state.get('username', 'User')}!")
    
    # Tabs for different dashboard sections
    tabs = st.tabs(["Overview", "Recent Interviews", "Practice Setup"])
    
    with tabs[0]:
        display_overview(user_data)
    
    with tabs[1]:
        display_recent_interviews(user_data)
    
    with tabs[2]:
        display_practice_setup()

def display_overview(user_data):
    """Display dashboard overview"""
    st.subheader("Your Interview Progress")
    
    # Mock data for demonstration
    if st.session_state.user_role == "guest":
        st.info("Sign in to track your progress and access all features.")
        return
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Completed Interviews", "5")
    
    with col2:
        st.metric("Average Performance", "76%", delta="3%")
    
    with col3:
        st.metric("Hours Practiced", "2.5")
    
    # Progress chart
    st.subheader("Performance Trend")
    
    # Mock performance data
    dates = [datetime.now() - timedelta(days=x) for x in range(14, -1, -1)]
    performances = [65, 68, 0, 0, 72, 74, 0, 0, 71, 73, 0, 75, 0, 78, 81]
    
    # Create DataFrame
    data = pd.DataFrame({
        'date': dates,
        'performance': performances
    })
    
    # Filter out zeros
    data = data[data['performance'] > 0]
    
    # Create chart
    chart = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('performance:Q', scale=alt.Scale(domain=[50, 100]), title='Performance Score'),
        tooltip=['date:T', 'performance:Q']
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Skill breakdown
    st.subheader("Skill Assessment")
    
    skills = pd.DataFrame({
        'Skill': ['Technical Knowledge', 'Communication', 'Problem Solving', 'Culture Fit', 'Experience Relevance'],
        'Score': [82, 70, 78, 85, 75]
    })
    
    skill_chart = alt.Chart(skills).mark_bar().encode(
        y=alt.Y('Skill:N', sort='-x'),
        x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Skill:N', legend=None),
        tooltip=['Skill', 'Score']
    ).properties(height=250)
    
    st.altair_chart(skill_chart, use_container_width=True)

def display_recent_interviews(user_data):
    """Display recent interviews section"""
    st.subheader("Your Recent Interviews")
    
    if st.session_state.user_role == "guest":
        st.info("Sign in to view your interview history.")
        st.button("Try a Sample Interview", on_click=navigate_to_upload)
        return
    
    # Mock data for demonstration
    recent_interviews = [
        {"id": "int-001", "date": "Apr 23, 2025", "position": "Senior Python Developer", "company": "TechCorp", "score": 81, "duration": "18 min"},
        {"id": "int-002", "date": "Apr 18, 2025", "position": "Data Scientist", "company": "DataInsights", "score": 75, "duration": "22 min"},
        {"id": "int-003", "date": "Apr 12, 2025", "position": "Machine Learning Engineer", "company": "AI Solutions", "score": 78, "duration": "25 min"},
        {"id": "int-004", "date": "Apr 8, 2025", "position": "Python Developer", "company": "WebServices Inc", "score": 73, "duration": "20 min"},
        {"id": "int-005", "date": "Apr 3, 2025", "position": "Backend Developer", "company": "Cloud Systems", "score": 68, "duration": "15 min"}
    ]
    
    for interview in recent_interviews:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{interview['position']}** at {interview['company']}")
            st.caption(f"{interview['date']} • {interview['duration']}")
        
        with col2:
            score_color = "green" if interview['score'] >= 75 else "orange" if interview['score'] >= 65 else "red"
            st.markdown(f"<h4 style='color: {score_color};'>{interview['score']}%</h4>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Replay", key=f"replay_{interview['id']}"):
                st.session_state.selected_interview = interview['id']
                navigate_to_replay()
        
        with col4:
            if st.button("Analysis", key=f"analysis_{interview['id']}"):
                st.session_state.selected_interview = interview['id']
                navigate_to_analysis()
        
        st.divider()
    
    st.button("Start New Interview", on_click=navigate_to_upload, type="primary")

def display_practice_setup():
    """Display practice setup section"""
    st.subheader("Prepare for Your Next Interview")
    
    st.markdown("""
    Get started with your interview preparation in three simple steps:
    
    1. Upload your resume
    2. Provide the job description
    3. Begin your AI-powered interview
    """)
    
    st.button("Let's Start", on_click=navigate_to_upload, type="primary")
    
    # Quick practice options
    st.subheader("Quick Practice")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("General Software Engineer", use_container_width=True):
            st.session_state.quick_template = "software_engineer"
            navigate_to_interview()
    
    with col2:
        if st.button("Data Scientist", use_container_width=True):
            st.session_state.quick_template = "data_scientist"
            navigate_to_interview()
    
    with col3:
        if st.button("Product Manager", use_container_width=True):
            st.session_state.quick_template = "product_manager"
            navigate_to_interview()

def navigate_to_upload():
    """Navigate to upload page"""
    st.session_state.page = "upload"

def navigate_to_interview():
    """Navigate to interview page"""
    st.session_state.page = "interview"

def navigate_to_replay():
    """Navigate to interview replay page"""
    st.session_state.page = "replay"

def navigate_to_analysis():
    """Navigate to interview analysis page"""
    st.session_state.page = "analysis"


# app/ui/upload_page.py
import streamlit as st

def display_upload_page():
    """Display the document upload page"""
    st.title("Upload Your Documents")
    
    tabs = st.tabs(["Resume Upload", "Job Description", "Interview Settings"])
    
    with tabs[0]:
        display_resume_upload()
    
    with tabs[1]:
        display_jd_upload()
    
    with tabs[2]:
        display_interview_settings()
    
    # Only show the continue button if both resume and JD are uploaded
    if "resume_uploaded" in st.session_state and "jd_uploaded" in st.session_state:
        if st.button("Continue to Interview", type="primary"):
            # In a real application, we would process the documents here
            st.session_state.page = "interview"
            st.experimental_rerun()

def display_resume_upload():
    """Display resume upload section"""
    st.subheader("Upload Your Resume/CV")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"], key="resume_file")
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1]
        
        st.success(f"Resume uploaded successfully ({file_type.upper()} format)")
        
        # Display file preview based on type
        if file_type == "txt":
            st.text_area("Resume Preview", uploaded_file.getvalue().decode(), height=300)
        else:
            st.info(f"Uploaded {uploaded_file.name}")
        
        # Store in session state
        st.session_state.resume_file = uploaded_file
        st.session_state.resume_uploaded = True
        
        # Parse resume - in a real app
        if st.button("Parse Resume"):
            with st.spinner("Parsing resume..."):
                # Mock processing delay
                import time
                time.sleep(2)
                
                st.success("Resume parsed successfully!")
                st.session_state.resume_parsed = True

def display_jd_upload():
    """Display job description upload section"""
    st.subheader("Job Description")
    
    # Option selection
    jd_method = st.radio("Choose an option", ["Upload JD Document", "Paste JD Text", "Enter Job URL"])
    
    if jd_method == "Upload JD Document":
        uploaded_jd = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"], key="jd_file")
        
        if uploaded_jd is not None:
            st.success(f"Job Description uploaded successfully")
            st.session_state.jd_file = uploaded_jd
            st.session_state.jd_uploaded = True
    
    elif jd_method == "Paste JD Text":
        jd_text = st.text_area("Paste the job description here", height=300)
        
        if jd_text and st.button("Save Job Description"):
            st.success("Job Description saved")
            st.session_state.jd_text = jd_text
            st.session_state.jd_uploaded = True
    
    elif jd_method == "Enter Job URL":
        jd_url = st.text_input("Enter job posting URL")
        
        if jd_url and st.button("Fetch Job Description"):
            with st.spinner("Fetching job description..."):
                # Mock processing delay
                import time
                time.sleep(2)
                
                st.success("Job Description fetched successfully!")
                st.session_state.jd_url = jd_url
                st.session_state.jd_uploaded = True
    
    # If JD uploaded but no location detected
    if "jd_uploaded" in st.session_state and "jd_location_set" not in st.session_state:
        st.subheader("Additional Information")
        st.info("We couldn't detect the job location from the description. Please specify:")
        
        country = st.selectbox("Target Country", [
            "United States", "United Kingdom", "Canada", "Australia", 
            "India", "Singapore", "Germany", "Other"
        ])
        
        if country == "Other":
            other_country = st.text_input("Specify Country")
            if other_country:
                country = other_country
        
        if st.button("Save Location"):
            st.session_state.jd_country = country
            st.session_state.jd_location_set = True
            st.success(f"Location set to {country}")

def display_interview_settings():
    """Display interview settings"""
    st.subheader("Interview Settings")
    
    # Define interview settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.interviewer_accent = st.selectbox(
            "Interviewer Accent",
            ["American (US)", "British (UK)", "Australian", "Indian", "Chinese"]
        )
        
        st.session_state.interviewer_gender = st.radio("Interviewer Voice", ["Male", "Female"])
        
        st.session_state.show_subtitles = st.checkbox("Show subtitles", value=True)
    
    with col2:
        st.session_state.technical_focus = st.slider(
            "Technical vs. Behavioral",
            0, 100, 50,
            help="0 = Fully behavioral, 100 = Fully technical"
        )
        
        st.session_state.interview_duration = st.slider(
            "Interview Duration (minutes)",
            10, 60, 20
        )
        
        st.session_state.difficulty = st.select_slider(
            "Interview Difficulty",
            options=["Easy", "Medium", "Hard", "Expert"],
            value="Medium"
        )


# app/ui/interview_room.py
import streamlit as st
import time
from PIL import Image
import numpy as np

def display_interview_room():
    """Display the interview room"""
    st.title("Interview Room")
    
    # Initialize interview state if not exists
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
        st.session_state.current_question_idx = 0
        st.session_state.interview_complete = False
        
        # Mock questions for demo - in a real app these would come from RAG
        st.session_state.interview_questions = [
            "Tell me about yourself and your background.",
            "What interests you about this position?",
            "Can you describe your experience with Python and Django?",
            "Tell me about a challenging project you worked on recently.",
            "How do you approach testing your code?",
            "Explain how you would implement a RESTful API using Flask.",
            "How do you stay updated with the latest technologies?",
            "What questions do you have for me about the position or company?"
        ]
    
    # Pre-interview setup
    if not st.session_state.interview_started:
        display_interview_setup()
    else:
        # Active interview
        if not st.session_state.interview_complete:
            display_active_interview()
        else:
            display_interview_completed()

def display_interview_setup():
    """Display interview setup screen"""
    st.subheader("Ready to Begin Your Interview")
    
    # Interview details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Interview Details")
        st.write(f"**Duration:** {st.session_state.get('interview_duration', 20)} minutes")
        st.write(f"**Focus:** {st.session_state.get('technical_focus', 50)}% Technical")
        st.write(f"**Difficulty:** {st.session_state.get('difficulty', 'Medium')}")
    
    with col2:
        st.markdown("#### Interviewer")
        accent = st.session_state.get('interviewer_accent', 'American (US)')
        gender = st.session_state.get('interviewer_gender', 'Male')
        st.write(f"**Accent:** {accent}")
        st.write(f"**Voice:** {gender}")
        st.write(f"**Subtitles:** {'Enabled' if st.session_state.get('show_subtitles', True) else 'Disabled'}")
    
    # Tips for the interview
    with st.expander("Interview Tips"):
        st.markdown("""
        - Speak clearly and at a moderate pace
        - Take a moment to think before answering
        - Use specific examples from your experience
        - Keep answers concise (1-2 minutes per question)
        - Ask for clarification if needed
        """)
    
    # Technical setup check
    st.subheader("Technical Setup")
    
    setup_col1, setup_col2 = st.columns(2)
    
    with setup_col1:
        st.markdown("#### Camera Preview")
        # Mock camera preview with placeholder
        st.image("https://via.placeholder.com/320x240.png?text=Camera+Preview", use_column_width=True)
        
        if st.button("Test Camera"):
            st.success("Camera is working properly")
    
    with setup_col2:
        st.markdown("#### Microphone Test")
        st.write("Click to test your microphone:")
        if st.button("Test Microphone"):
            with st.spinner("Testing microphone..."):
                time.sleep(1.5)
                st.success("Microphone is working properly")
    
    # Start interview button
    st.markdown("---")
    if st.button("Start Interview", type="primary"):
        st.session_state.interview_started = True
        st.session_state.interview_start_time = time.time()
        st.experimental_rerun()

def display_active_interview():
    """Display active interview screen"""
    # Get current question
    current_idx = st.session_state.current_question_idx
    questions = st.session_state.interview_questions
    current_question = questions[current_idx] if current_idx < len(questions) else None
    
    if current_question:
        # Interviewer area
        st.subheader("Your Interviewer")
        
        # Mock interviewer display
        interviewer_col1, interviewer_col2 = st.columns([1, 3])
        
        with interviewer_col1:
            # Display interviewer avatar
            gender = st.session_state.get('interviewer_gender', 'Male')
            accent = st.session_state.get('interviewer_accent', 'American (US)')
            
            # Generate a placeholder avatar (in real app, use proper images)
            avatar_text = f"{gender[0]}{accent[0]}"
            avatar = Image.new('RGB', (200, 200), color=(100, 149, 237))
            
            st.image(avatar, use_column_width=True)
        
        with interviewer_col2:
            # Question display
            st.markdown(f"### Question {current_idx + 1} of {len(questions)}")
            
            # Display question with "speaking" animation
            with st.container():
                st.markdown(f"**{current_question}**")
                
                # Show subtitles if enabled
                if st.session_state.get('show_subtitles', True):
                    st.caption(current_question)
        
        # User response area
        st.markdown("---")
        st.subheader("Your Response")
        
        # Mock video feed
        response_col1, response_col2 = st.columns([3, 1])
        
        with response_col1:
            st.image("https://via.placeholder.com/640x360.png?text=Your+Video+Feed", use_column_width=True)
        
        with response_col2:
            # Audio level indicator (mock)
            st.write("Audio Level")
            audio_level = np.random.randint(10, 80)
            st.progress(audio_level)
            
            # Recording time
            elapsed = time.time() - st.session_state.get('interview_start_time', time.time())
            minutes, seconds = divmod(int(elapsed), 60)
            st.write(f"Recording: {minutes:02d}:{seconds:02d}")
        
        # Next question button
        if st.button("Next Question"):
            st.session_state.current_question_idx += 1
            
            # Check if interview is complete
            if st.session_state.current_question_idx >= len(questions):
                st.session_state.interview_complete = True
            
            st.experimental_rerun()
        
        # End interview early button
        if st.button("End Interview"):
            st.session_state.interview_complete = True
            st.experimental_rerun()
    else:
        st.session_state.interview_complete = True
        st.experimental_rerun()

def display_interview_completed():
    """Display interview completed screen"""
    st.success("Interview Completed!")
    
    # Interview summary
    st.subheader("Interview Summary")
    
    # Mock data
    questions_asked = len(st.session_state.interview_questions)
    interview_duration = time.time() - st.session_state.get('interview_start_time', time.time())
    minutes, seconds = divmod(int(interview_duration), 60)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Questions", questions_asked)
    
    with col2:
        st.metric("Duration", f"{minutes}m {seconds}s")
    
    with col3:
        st.metric("Completion", "100%")
    
    # Next steps
    st.subheader("Next Steps")
    
    next_col1, next_col2 = st.columns(2)
    
    with next_col1:
        if st.button("View Analysis", use_container_width=True):
            st.session_state.page = "analysis"
            st.experimental_rerun()
    
    with next_col2:
        if st.button("New Interview", use_container_width=True):
            # Reset interview state
            for key in ['interview_started', 'current_question_idx', 'interview_complete', 
                       'interview_questions', 'interview_start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Go to upload page
            st.session_state.page = "upload"
            st.experimental_rerun()
    
    # Share results button
    if st.button("Save & Share Results"):
        with st.spinner("Saving interview results..."):
            time.sleep(2)
            st.success("Interview saved! Share link copied to clipboard.")


# app/ui/interview_analysis.py
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime

def display_interview_analysis():
    """Display interview analysis page"""
    st.title("Interview Analysis")
    
    # Mock interview data
    interview_id = st.session_state.get('selected_interview', 'int-001')
    
    # Interview overview
    st.subheader("Interview Overview")
    
    overview_col1, overview_col2 = st.columns(2)
    
    with overview_col1:
        st.markdown("#### Position Details")
        st.write("**Position:** Senior Python Developer")
        st.write("**Company:** TechCorp")
        st.write("**Date:** Apr 23, 2025")
        st.write("**Duration:** 18 minutes")
    
    with overview_col2:
        st.markdown("#### Performance")
        st.metric("Overall Score", "81%")
        
        # Performance breakdown
        performance = {
            "Technical Knowledge": 85,
            "Communication": 78,
            "Problem Solving": 82,
            "Confidence": 76,
            "Relevance": 84
        }
        
        performance_df = pd.DataFrame({
            'Category': list(performance.keys()),
            'Score': list(performance.values())
        })
        
        perf_chart = alt.Chart(performance_df).mark_bar().encode(
            y=alt.Y('Category:N', sort='-x'),
            x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100])),
            color=alt.Color('Category:N', legend=None),
            tooltip=['Category', 'Score']
        ).properties(height=200)
        
        st.altair_chart(perf_chart, use_container_width=True)
    
    # Question analysis
    st.markdown("---")
    st.subheader("Question Analysis")
    
    # Mock question data
    questions = [
        {
            "number": 1,
            "text": "Tell me about yourself and your background.",
            "type": "Ice breaker",
            "score": 86,
            "feedback": "Strong introduction, good overview of experience. Could highlight achievements more."
        },
        {
            "number": 2,
            "text": "What interests you about this position?",
            "type": "Behavioral",
            "score": 82,
            "feedback": "Good alignment with job requirements. Be more specific about company knowledge."
        },
        {
            "number": 3,
            "text": "Can you describe your experience with Python and Django?",
            "type": "Technical",
            "score": 90,
            "feedback": "Excellent technical details. Good examples of past projects."
        },
        {
            "number": 4,
            "text": "Tell me about a challenging project you worked on recently.",
            "type": "Behavioral",
            "score": 78,
            "feedback": "Good problem description. Could improve on explaining your specific role and impact."
        },
        {
            "number": 5,
            "text": "How do you approach testing your code?",
            "type": "Technical",
            "score": 84,
            "feedback": "Strong understanding of testing principles. Could mention more specific testing tools."
        },
        {
            "number": 6,
            "text": "Explain how you would implement a RESTful API using Flask.",
            "type": "Technical",
            "score": 80,
            "feedback": "Good overview of Flask API implementation. More details on authentication would help."
        },
        {
            "number": 7,
            "text": "How do you stay updated with the latest technologies?",
            "type": "Behavioral",
            "score": 75,
            "feedback": "Mentioned good resources. Could be more specific about learning practices."
        },
        {
            "number": 8,
            "text": "What questions do you have for me about the position or company?",
            "type": "Ice breaker",
            "score": 73,
            "feedback": "Asked thoughtful questions. Consider preparing more strategic questions about growth."
        }
    ]
    
    # Display each question with expandable details
    for q in questions:
        score_color = "green" if q['score'] >= 80 else "orange" if q['score'] >= 70 else "red"
        
        expander = st.expander(f"Q{q['number']}: {q['text']} ({q['type']})")
        with expander:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("**Your Response:**")
                # In a real app, this would be the actual response
                st.write("*[Transcription of your answer would appear here]*")
                
                st.write("**Feedback:**")
                st.write(q['feedback'])
            
            with col2:
                st.markdown(f"<h2 style='color: {score_color};'>{q['score']}%</h2>", unsafe_allow_html=True)
                
                # Replay button
                if st.button("Replay Answer", key=f"replay_q{q['number']}"):
                    st.info("In a real app, this would play back your recorded answer.")
    
    # Word cloud of frequently used words
    st.markdown("---")
    st.subheader("Speech Analysis")
    
    speech_col1, speech_col2 = st.columns(2)
    
    with speech_col1:
        st.markdown("#### Word Usage")
        # Placeholder for word cloud
        st.image("https://via.placeholder.com/400x300.png?text=Word+Cloud", use_column_width=True)
    
    with speech_col2:
        st.markdown("#### Speech Metrics")
        
        # Mock speech metrics
        speech_metrics = {
            "Speaking Rate": 155,  # words per minute
            "Filler Words": 12,    # um, uh, like, etc.
            "Technical Terms": 28, # domain-specific terms used
            "Confident Terms": 15, # definitive statements
            "Uncertain Terms": 8   # hedging language
        }
        
        for metric, value in speech_metrics.items():
            st.write(f"**{metric}:** {value}")
    
    # Recommendations
    st.markdown("---")
    st.subheader("Improvement Recommendations")
    
    # Mock recommendations
    recommendations = [
        "**Highlight specific achievements** when describing your experience",
        "**Research the company more thoroughly** to show genuine interest",
        "**Prepare more examples** of technical problem-solving",
        "**Reduce filler words** (um, uh, like) to sound more confident",
        "**Ask more strategic questions** about company growth and team dynamics"
    ]
    
    for i, rec in enumerate(recommendations):
        st.write(f"{i+1}. {rec}")
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Practice Again", type="primary", use_container_width=True):
            # Reset interview state
            for key in ['interview_started', 'current_question_idx', 'interview_complete', 
                       'interview_questions', 'interview_start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Go to upload page
            st.session_state.page = "upload"
            st.experimental_rerun()
    
    with col2:
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.experimental_rerun()
