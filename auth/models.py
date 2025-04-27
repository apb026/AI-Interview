from flask_login import UserMixin
from firebase_admin import firestore
from werkzeug.security import generate_password_hash, check_password_hash
import time
import uuid

class User(UserMixin):
    """User model for authentication and profile management"""
    
    def __init__(self, user_id, email, first_name=None, last_name=None, role='user', 
                 created_at=None, last_login=None, profile_data=None):
        self.id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.created_at = created_at or int(time.time())
        self.last_login = last_login
        self.profile_data = profile_data or {}
        
    @property
    def full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return "User"
    
    @staticmethod
    def create_user(email, password, first_name=None, last_name=None, role='user'):
        """
        Create a new user in the database
        
        Args:
            email (str): User's email address
            password (str): User's password
            first_name (str, optional): User's first name
            last_name (str, optional): User's last name
            role (str, optional): User's role (default: 'user')
            
        Returns:
            User: The created user object
        """
        # Check if user already exists
        db = firestore.client()
        existing_user = db.collection('users').where('email', '==', email).limit(1).get()
        if len(existing_user) > 0:
            raise ValueError(f"User with email {email} already exists")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Create user data
        now = int(time.time())
        user_data = {
            'id': user_id,
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'created_at': now,
            'last_login': now,
            'profile_data': {}
        }
        
        # Save to database
        db.collection('users').document(user_id).set(user_data)
        
        # Return user object
        return User(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            created_at=now,
            last_login=now
        )
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get a user by ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            User: User object or None if not found
        """
        db = firestore.client()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return None
        
        user_data = user_doc.to_dict()
        return User(
            user_id=user_data['id'],
            email=user_data['email'],
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            role=user_data.get('role', 'user'),
            created_at=user_data.get('created_at'),
            last_login=user_data.get('last_login'),
            profile_data=user_data.get('profile_data', {})
        )
    
    @staticmethod
    def get_by_email(email):
        """
        Get a user by email
        
        Args:
            email (str): User email
            
        Returns:
            User: User object or None if not found
        """
        db = firestore.client()
        users = db.collection('users').where('email', '==', email).limit(1).get()
        
        if not users:
            return None
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            return User(
                user_id=user_data['id'],
                email=user_data['email'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                role=user_data.get('role', 'user'),
                created_at=user_data.get('created_at'),
                last_login=user_data.get('last_login'),
                profile_data=user_data.get('profile_data', {})
            )
        
        return None
    
    @staticmethod
    def authenticate(email, password):
        """
        Authenticate a user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            User: Authenticated user or None if authentication failed
        """
        db = firestore.client()
        users = db.collection('users').where('email', '==', email).limit(1).get()
        
        if not users:
            return None
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            if check_password_hash(user_data.get('password_hash', ''), password):
                # Update last login
                now = int(time.time())
                db.collection('users').document(user_data['id']).update({'last_login': now})
                
                return User(
                    user_id=user_data['id'],
                    email=user_data['email'],
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    role=user_data.get('role', 'user'),
                    created_at=user_data.get('created_at'),
                    last_login=now,
                    profile_data=user_data.get('profile_data', {})
                )
        
        return None
    
    def update_profile(self, data):
        """
        Update user profile data
        
        Args:
            data (dict): Profile data to update
            
        Returns:
            bool: True if successful
        """
        db = firestore.client()
        
        # Update only allowed fields
        allowed_fields = ['first_name', 'last_name', 'profile_data']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if 'profile_data' in data and isinstance(data['profile_data'], dict):
            # Merge profile data instead of replacing
            current_profile = self.profile_data or {}
            updated_profile = {**current_profile, **data['profile_data']}
            update_data['profile_data'] = updated_profile
        
        # Update object attributes
        for key, value in update_data.items():
            setattr(self, key, value)
        
        # Update in database
        db.collection('users').document(self.id).update(update_data)
        return True
    
    def change_password(self, current_password, new_password):
        """
        Change user password
        
        Args:
            current_password (str): Current password
            new_password (str): New password
            
        Returns:
            bool: True if successful, False if current password is incorrect
        """
        db = firestore.client()
        user_doc = db.collection('users').document(self.id).get()
        
        if not user_doc.exists:
            return False
        
        user_data = user_doc.to_dict()
        
        # Verify current password
        if not check_password_hash(user_data.get('password_hash', ''), current_password):
            return False
        
        # Update password
        db.collection('users').document(self.id).update({
            'password_hash': generate_password_hash(new_password)
        })
        
        return True
    
    def get_interview_history(self):
        """
        Get user's interview history
        
        Returns:
            list: List of interview sessions
        """
        db = firestore.client()
        sessions = db.collection('interview_sessions').where('user_id', '==', self.id).order_by(
            'start_time', direction='DESCENDING').limit(50).get()
        
        result = []
        for session in sessions:
            session_data = session.to_dict()
            result.append(session_data)
        
        return result