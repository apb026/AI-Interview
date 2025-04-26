# app/services/livekit_service.py
import jwt
import time
from typing import Dict, Any, Optional
import requests

class LiveKitService:
    """Service for managing LiveKit room and token creation"""
    
    def __init__(self, api_key: str, api_secret: str, ws_url: str):
        """
        Initialize LiveKit service
        
        Args:
            api_key: LiveKit API key
            api_secret: LiveKit API secret
            ws_url: LiveKit websocket URL
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = ws_url
        # Extract host from ws URL for REST API calls
        self.api_url = ws_url.replace("ws://", "http://").replace("wss://", "https://")
        if self.api_url.endswith("/ws"):
            self.api_url = self.api_url[:-3]
            
    def create_token(self, room_name: str, participant_name: str, participant_identity: str, 
                    ttl: int = 86400, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a JWT token for LiveKit room access
        
        Args:
            room_name: Name of the room to join
            participant_name: Display name of the participant
            participant_identity: Unique identifier for the participant
            ttl: Time to live in seconds (default: 24 hours)
            metadata: Additional metadata to include in the token
            
        Returns:
            JWT token string
        """
        now = int(time.time())
        
        payload = {
            "exp": now + ttl,
            "iss": self.api_key,
            "nbf": now - 60,  # Valid from 1 minute ago
            "video": {
                "room": room_name,
                "roomJoin": True,
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
            },
            "metadata": metadata or {},
            "name": participant_name,
            "sub": participant_identity
        }
        
        token = jwt.encode(payload, self.api_secret, algorithm="HS256")
        return token
    
    def create_room(self, room_name: str, empty_timeout: int = 300) -> Dict[str, Any]:
        """
        Create a new LiveKit room
        
        Args:
            room_name: Name of the room to create
            empty_timeout: Time in seconds before closing empty room
            
        Returns:
            Room information
        """
        # Create authorization token for API request
        at = self._create_admin_token()
        
        # Create room
        response = requests.post(
            f"{self.api_url}/twirp/livekit.RoomService/CreateRoom",
            json={
                "name": room_name,
                "empty_timeout": empty_timeout,
                "metadata": json.dumps({"created_at": int(time.time())})
            },
            headers={
                "Authorization": f"Bearer {at}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create room: {response.text}")
            
        return response.json()
    
    def delete_room(self, room_name: str) -> Dict[str, Any]:
        """
        Delete a LiveKit room
        
        Args:
            room_name: Name of the room to delete
            
        Returns:
            Response information
        """
        # Create authorization token for API request
        at = self._create_admin_token()
        
        # Delete room
        response = requests.post(
            f"{self.api_url}/twirp/livekit.RoomService/DeleteRoom",
            json={"name": room_name},
            headers={
                "Authorization": f"Bearer {at}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to delete room: {response.text}")
            
        return response.json()
    
    def list_participants(self, room_name: str) -> Dict[str, Any]:
        """
        List participants in a LiveKit room
        
        Args:
            room_name: Name of the room
            
        Returns:
            List of participants
        """
        # Create authorization token for API request
        at = self._create_admin_token()
        
        # List participants
        response = requests.post(
            f"{self.api_url}/twirp/livekit.RoomService/ListParticipants",
            json={"room": room_name},
            headers={
                "Authorization": f"Bearer {at}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list participants: {response.text}")
            
        return response.json()
    
    def _create_admin_token(self) -> str:
        """
        Create an admin token for LiveKit API access
        
        Returns:
            JWT token string
        """
        now = int(time.time())
        
        payload = {
            "exp": now + 600,  # 10 minutes
            "iss": self.api_key,
            "nbf": now - 60,  # Valid from 1 minute ago
            "video": {
                "roomCreate": True,
                "roomList": True,
                "roomRecord": True,
                "roomAdmin": True
            }
        }
        
        token = jwt.encode(payload, self.api_secret, algorithm="HS256")
        return token