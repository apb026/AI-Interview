# app/services/user_service.py
import os
import json
import uuid
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime

class UserService:
    """Service for user authentication and management"""
    
    def __init__(self, storage_dir: str = "app_data/users"):
        """
        Initialize user service
        
        Args:
            storage_dir: Directory for user data storage
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: User's username
            email: User's email
            password: User's password
            
        Returns:
            User data
        """
        # Check if email already exists
        if self._email_exists(email):
            raise ValueError("Email already registered")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Create salt and hash password
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        # Create user data
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "interviews": []
        }
        
        # Save user data
        self._save_user(user_data)
        
        # Return user data without sensitive information
        return self._clean_user_data(user_data)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            User data if authentication is successful, None otherwise
        """
        # Get user data
        user_data = self._get_user_by_email(email)
        if not user_data:
            return None
        
        # Verify password
        salt = user_data.get("salt", "")
        stored_hash = user_data.get("password_hash", "")
        input_hash = self._hash_password(password, salt)
        
        if input_hash != stored_hash:
            return None
        
        # Update last login time
        user_data["last_login"] = datetime.now().isoformat()
        self._save_user(user_data)
        
        # Return user data without sensitive information
        return self._clean_user_data(user_data)
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data if found, None otherwise
        """
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(user_file):
            return None
        
        with open(user_file, "r") as f:
            user_data = json.load(f)
        
        return self._clean_user_data(user_data)
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user data
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated user data if successful, None otherwise
        """
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(user_file):
            return None
        
        with open(user_file, "r") as f:
            user_data = json.load(f)
        
        # Handle password update separately
        if "password" in updates:
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(updates["password"], salt)
            user_data["password_hash"] = password_hash
            user_data["salt"] = salt
            del updates["password"]
        
        # Update other fields
        for key, value in updates.items():
            if key not in ["id", "password_hash", "salt", "created_at"]:
                user_data[key] = value
        
        # Save updated user data
        self._save_user(user_data)
        
        return self._clean_user_data(user_data)
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(user_file):
            return False
        
        try:
            os.remove(user_file)
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def _email_exists(self, email: str) -> bool:
        """
        Check if an email already exists
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        # This is inefficient for a large number of users
        # In a production system, use a database with indexing
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json"):
                continue
                
            file_path = os.path.join(self.storage_dir, filename)
            with open(file_path, "r") as f:
                try:
                    user_data = json.load(f)
                    if user_data.get("email") == email:
                        return True
                except json.JSONDecodeError:
                    continue
        
        return False
    
    def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by email
        
        Args:
            email: User's email
            
        Returns:
            User data if found, None otherwise
        """
        # This is inefficient for a large number of users
        # In a production system, use a database with indexing
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json"):
                continue
                
            file_path = os.path.join(self.storage_dir, filename)
            with open(file_path, "r") as f:
                try:
                    user_data = json.load(f)
                    if user_data.get("email") == email:
                        return user_data
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _hash_password(self, password: str, salt: str) -> str:
        """
        Hash a password with a salt
        
        Args:
            password: Password to hash
            salt: Salt to use
            
        Returns:
            Hashed password
        """
        pw_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000  # Number of iterations
        )
        return pw_hash.hex()
    
    def _save_user(self, user_data: Dict[str, Any]):
        """
        Save user data to a file
        
        Args:
            user_data: User data to save
        """
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("User data must have an ID")
            
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, "w") as f:
            json.dump(user_data, f, indent=2)
    
    def _clean_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from user data
        
        Args:
            user_data: User data to clean
            
        Returns:
            Cleaned user data
        """
        clean_data = user_data.copy()
        clean_data.pop("password_hash", None)
        clean_data.pop("salt", None)
        return clean_data