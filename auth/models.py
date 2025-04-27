from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class User:
    """User model representing a user in the system"""
    user_id: str
    email: str
    display_name: Optional[str] = None
    email_verified: bool = False
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @staticmethod
    def from_dict(user_id: str, data: Dict[str, Any]) -> 'User':
        """
        Create a User object from a dictionary
        
        Args:
            user_id: User ID
            data: Dictionary containing user data
            
        Returns:
            User object
        """
        return User(
            user_id=user_id,
            email=data.get('email'),
            display_name=data.get('display_name'),
            email_verified=data.get('email_verified', False),
            photo_url=data.get('photo_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            last_login=data.get('last_login')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert User object to a dictionary
        
        Returns:
            Dictionary representation of the User
        """
        return {
            'email': self.email,
            'display_name': self.display_name,
            'email_verified': self.email_verified,
            'photo_url': self.photo_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }


@dataclass
class UserPreferences:
    """User preferences model for storing user-specific settings"""
    user_id: str
    notification_settings: Dict[str, bool] = None
    theme: str = 'light'
    language: str = 'en'
    timezone: str = 'UTC'
    dashboard_layout: Dict[str, Any] = None
    
    @staticmethod
    def from_dict(user_id: str, data: Dict[str, Any]) -> 'UserPreferences':
        """
        Create a UserPreferences object from a dictionary
        
        Args:
            user_id: User ID
            data: Dictionary containing user preferences data
            
        Returns:
            UserPreferences object
        """
        return UserPreferences(
            user_id=user_id,
            notification_settings=data.get('notification_settings', {
                'email': True,
                'web': True
            }),
            theme=data.get('theme', 'light'),
            language=data.get('language', 'en'),
            timezone=data.get('timezone', 'UTC'),
            dashboard_layout=data.get('dashboard_layout', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert UserPreferences object to a dictionary
        
        Returns:
            Dictionary representation of the UserPreferences
        """
        return {
            'notification_settings': self.notification_settings or {
                'email': True,
                'web': True
            },
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'dashboard_layout': self.dashboard_layout or {}
        }


@dataclass
class UserSession:
    """User session model for tracking authentication sessions"""
    session_id: str
    user_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    @staticmethod
    def from_dict(session_id: str, data: Dict[str, Any]) -> 'UserSession':
        """
        Create a UserSession object from a dictionary
        
        Args:
            session_id: Session ID
            data: Dictionary containing session data
            
        Returns:
            UserSession object
        """
        return UserSession(
            session_id=session_id,
            user_id=data.get('user_id'),
            token=data.get('token'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            is_active=data.get('is_active', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert UserSession object to a dictionary
        
        Returns:
            Dictionary representation of the UserSession
        """
        return {
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active
        }