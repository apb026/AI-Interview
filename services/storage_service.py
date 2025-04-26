# app/services/storage_service.py
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class StorageService:
    """Service for data storage and retrieval"""
    
    def __init__(self, db_path: str = "app_data.db"):
        """
        Initialize storage service
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            created_at TEXT,
            last_login TEXT
        )
        ''')
        
        # Create interviews table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TEXT,
            end_time TEXT,
            interview_type TEXT,
            data TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user(self, user_data: Dict[str, Any]) -> str:
        """
        Save user data to the database
        
        Args:
            user_data: User information
            
        Returns:
            User ID
        """
        user_id = user_data.get("id") or str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO users (id, username, email, created_at, last_login)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            user_data.get("username", ""),
            user_data.get("email", ""),
            user_data.get("created_at", datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from the database
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def save_interview_data(self, user_id: str, interview_id: str, 
                           interview_data: Dict[str, Any]) -> str:
        """
        Save interview data to the database
        
        Args:
            user_id: User ID
            interview_id: Interview ID
            interview_data: Interview data
            
        Returns:
            Interview ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO interviews (id, user_id, start_time, end_time, interview_type, data)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            interview_id,
            user_id,
            interview_data.get("start_time", datetime.now().isoformat()),
            interview_data.get("end_time", None),
            interview_data.get("interview_type", "general"),
            json.dumps(interview_data)
        ))
        
        conn.commit()
        conn.close()
        
        return interview_id
    
    def get_interview_data(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """
        Get interview data from the database
        
        Args:
            interview_id: Interview ID
            
        Returns:
            Interview data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM interviews WHERE id = ?', (interview_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            result = dict(row)
            result["data"] = json.loads(result["data"])
            return result
        return None
    
    def get_user_interviews(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all interviews for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of interviews to return
            
        Returns:
            List of interview data
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM interviews 
        WHERE user_id = ? 
        ORDER BY start_time DESC
        LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            interview = dict(row)
            interview["data"] = json.loads(interview["data"])
            results.append(interview)
            
        return results
    
    def delete_interview(self, interview_id: str) -> bool:
        """
        Delete an interview from the database
        
        Args:
            interview_id: Interview ID
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM interviews WHERE id = ?', (interview_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user and interview data
        """
        user = self.get_user(user_id)
        interviews = self.get_user_interviews(user_id, limit=1000)
        
        return {
            "user": user,
            "interviews": interviews,
            "export_date": datetime.now().isoformat()
        }
    
    def save_to_file(self, data: Dict[str, Any], filename: str) -> str:
        """
        Save data to a JSON file
        
        Args:
            data: Data to save
            filename: Filename to save to
            
        Returns:
            Full path to the saved file
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        return os.path.abspath(filename)
    
    def load_from_file(self, filename: str) -> Dict[str, Any]:
        """
        Load data from a JSON file
        
        Args:
            filename: Filename to load from
            
        Returns:
            Loaded data
        """
        with open(filename, 'r') as f:
            return json.load(f)