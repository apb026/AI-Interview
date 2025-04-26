# app/ui/landing_page.py
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json

def load_lottie_animation(url):
    """Load Lottie animation from URL"""
    try:
        response = requests.get(url)
        return json.loads(response.text)
    except:
        return None

def display_landing_page():
    """Display the landing page with interactive elements"""
    # Page configuration
    st.set_page_config(
        page_title="Interview Coach AI",
        page_icon="👔",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Hero section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.title("Interview Coach AI")
        st.subheader("Ace Your Next Job Interview with AI-Powered Practice")
        
        st.markdown("""
        Prepare confidently for your upcoming interviews with our AI interview simulator. 
        Upload your resume and job description to get personalized interview questions and feedback.
        """)
        
        # Authentication options
        auth_col1, auth_col2, auth_col3 = st.columns(3)
        
        with auth_col1:
            if st.button("Sign In", use_container_width=True):
                st.session_state.show_form = "signin"
        
        with auth_col2:
            if st.button("Register", use_container_width=True):
                st.session_state.show_form = "register"
        
        with auth_col3:
            if st.button("Try as Guest", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_role = "guest"
                st.session_state.username = "Guest User"
                st.experimental_rerun()
    
    with col2:
        # Animation for visual appeal
        lottie_interview = load_lottie_animation("https://assets5.lottiefiles.com/packages/lf20_zruymzpt.json")
        if lottie_interview:
            st_lottie(lottie_interview, height=400)
    
    # Features section
    st.markdown("---")
    st.subheader("💪 Features")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("🎯 **Personalized Interviews**")
        st.markdown("""
        Our AI analyzes your resume and the job description to create targeted interview questions relevant to the position.
        """)
    
    with feat_col2:
        st.markdown("🌎 **Diverse Interviewer Personas**")
        st.markdown("""
        Practice with interviewers from different backgrounds and accents: US, UK, Australian, Indian, and Chinese.
        """)
    
    with feat_col3:
        st.markdown("📊 **Performance Analytics**")
        st.markdown("""
        Review your recorded interviews and get insights on your performance to improve your interview skills.
        """)
    
    # Display authentication forms if requested
    if "show_form" in st.session_state:
        st.markdown("---")
        if st.session_state.show_form == "signin":
            display_signin_form()
        elif st.session_state.show_form == "register":
            display_register_form()

def display_signin_form():
    """Display sign in form"""
    st.subheader("Sign In")
    
    with st.form("signin_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
        
        if submitted:
            if email and password:
                # In a real app, authenticate with Firebase
                from app.auth.firebase_auth import FirebaseAuth
                auth = FirebaseAuth()
                success, user_data = auth.sign_in(email, password)
                
                if success:
                    st.success("Signed in successfully!")
                    st.session_state.authenticated = True
                    st.session_state.user_role = "registered"
                    st.session_state.user_data = user_data
                    st.session_state.username = email.split('@')[0]
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Please fill in all fields.")
    
    if st.button("Back to Home"):
        st.session_state.pop("show_form", None)
        st.experimental_rerun()

def display_register_form():
    """Display registration form"""
    st.subheader("Create Account")
    
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email