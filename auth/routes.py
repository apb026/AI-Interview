from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import auth as firebase_auth
import pyrebase
import os
from functools import wraps
from datetime import datetime
from database.firebase_client import FirebaseClient

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# Firebase client
firebase_client = FirebaseClient()

# Helper functions
def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def is_email_verified(user_id):
    """Check if user email is verified"""
    try:
        user = firebase_auth.get_user(user_id)
        return user.email_verified
    except Exception as e:
        print(f"Error checking email verification: {e}")
        return False

# Authentication routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Authenticate user
            user = firebase_client.pb_auth.sign_in_with_email_and_password(email, password)
            
            # Get user info from Firebase
            user_info = firebase_client.pb_auth.get_account_info(user['idToken'])
            user_id = user_info['users'][0]['localId']
            
            # Store user data in session
            session['user_id'] = user_id
            session['email'] = email
            session['token'] = user['idToken']
            
            # Update user's last login timestamp
            firebase_client.update_user(user_id, {
                'last_login': datetime.now()
            })
            
            # Check if user has verified email
            if not is_email_verified(user_id):
                flash('Please verify your email address to access all features', 'warning')
            
            # Redirect to dashboard or the next URL
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            error_message = str(e)
            if 'INVALID_PASSWORD' in error_message:
                flash('Invalid email or password', 'danger')
            elif 'EMAIL_NOT_FOUND' in error_message:
                flash('Email not found', 'danger')
            else:
                flash(f'Login failed: {error_message}', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        display_name = request.form.get('display_name')
        
        # Validate input
        if not email or not password or not display_name:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
            
        try:
            # Create user in Firebase
            user_id = firebase_client.create_user(email, password, display_name)
            
            # Send email verification
            firebase_client.pb_auth.send_email_verification(session['token'])
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            error_message = str(e)
            if 'EMAIL_EXISTS' in error_message:
                flash('Email already in use', 'danger')
            else:
                flash(f'Registration failed: {error_message}', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    # Clear session data
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Display and update user profile"""
    user_id = session.get('user_id')
    
    # Get user data
    user_data = firebase_client.get_user(user_id)
    
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update display name
        if display_name and display_name != user_data.get('display_name'):
            try:
                firebase_client.update_user(user_id, {'display_name': display_name})
                flash('Profile updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'danger')
        
        # Update password
        if current_password and new_password:
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters', 'danger')
            else:
                try:
                    # Re-authenticate user
                    user = firebase_client.pb_auth.sign_in_with_email_and_password(session['email'], current_password)
                    
                    # Update password
                    firebase_client.pb_auth.update_profile(user['idToken'], password=new_password)
                    flash('Password updated successfully', 'success')
                except Exception as e:
                    flash(f'Error updating password: {str(e)}', 'danger')
    
    return render_template('profile.html', user=user_data)

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Handle password reset request"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        try:
            firebase_client.pb_auth.send_password_reset_email(email)
            flash('Password reset email sent. Please check your inbox.', 'info')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error sending password reset email: {str(e)}', 'danger')
    
    return render_template('reset_password.html')

@auth_bp.route('/verify-email')
@login_required
def verify_email():
    """Resend email verification"""
    try:
        firebase_client.pb_auth.send_email_verification(session['token'])
        flash('Verification email sent. Please check your inbox.', 'info')
    except Exception as e:
        flash(f'Error sending verification email: {str(e)}', 'danger')
        
    return redirect(url_for('auth.profile'))

# API endpoints for authentication
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
        
    try:
        # Authenticate user
        user = firebase_client.pb_auth.sign_in_with_email_and_password(data['email'], data['password'])
        
        # Get user info
        user_info = firebase_client.pb_auth.get_account_info(user['idToken'])
        user_id = user_info['users'][0]['localId']
        
        # Update user's last login timestamp
        firebase_client.update_user(user_id, {
            'last_login': datetime.now()
        })
        
        return jsonify({
            'token': user['idToken'],
            'user_id': user_id,
            'email': data['email'],
            'refresh_token': user['refreshToken'],
            'expires_in': user['expiresIn']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('display_name'):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        # Create user
        user_id = firebase_client.create_user(data['email'], data['password'], data['display_name'])
        
        # Log in the user
        user = firebase_client.pb_auth.sign_in_with_email_and_password(data['email'], data['password'])
        
        # Send verification email
        firebase_client.pb_auth.send_email_verification(user['idToken'])
        
        return jsonify({
            'user_id': user_id,
            'message': 'Registration successful. Please verify your email.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400