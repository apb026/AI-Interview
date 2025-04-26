# main.py - Main application entry point
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import UI components
from app.ui.landing_page import display_landing_page
from app.ui.dashboard import display_dashboard
from app.ui.upload_page import display_upload_page
from app.ui.interview_room import display_interview_room