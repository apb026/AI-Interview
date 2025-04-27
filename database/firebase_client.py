import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    # Check if already initialized
    if len(firebase_admin._apps) > 0:
        return firestore.client()
    
    # Get credentials
    cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    
    if cred_path and os.path.exists(cred_path):
        # Use service account file
        cred = credentials.Certificate(cred_path)
    else:
        # Check for JSON credentials in environment variable
        cred_json = os.environ.get('FIREBASE_CREDENTIALS')
        if cred_json:
            try:
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            except (json.JSONDecodeError, ValueError):
                raise ValueError("Invalid Firebase credentials JSON")
        else:
            # Use application default credentials
            cred = credentials.ApplicationDefault()
    
    # Initialize app
    firebase_admin.initialize_app(cred)
    return firestore.client()

class FirebaseClient:
    """Firebase client for database operations"""
    
    def __init__(self):
        """Initialize the Firebase client"""
        self.db = firestore.client()
    
    def document_to_dict(self, doc):
        """Convert Firestore document to dictionary"""
        if not doc.exists:
            return None
        
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id
        
        # Convert Firestore timestamps to Python datetime
        for key, value in doc_dict.items():
            if isinstance(value, firestore.firestore.SERVER_TIMESTAMP):
                doc_dict[key] = datetime.now()
        
        return doc_dict
    
    def collection_to_list(self, collection):
        """Convert Firestore collection to list of dictionaries"""
        result = []
        for doc in collection:
            doc_dict = self.document_to_dict(doc)
            if doc_dict:
                result.append(doc_dict)
        return result
    
    # User operations
    def get_user(self, user_id):
        """Get user by ID"""
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        return self.document_to_dict(doc)
    
    def create_user(self, user_data):
        """Create a new user"""
        # Check if user with email already exists
        email = user_data.get('email')
        if email:
            query = self.db.collection('users').where('email', '==', email).limit(1)
            if len(list(query.stream())) > 0:
                raise ValueError(f"User with email {email} already exists")
        
        # Add timestamp
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        
        # Add to database
        doc_ref = self.db.collection('users').document()
        doc_ref.set(user_data)
        
        # Return with ID
        return {**user_data, 'id': doc_ref.id}
    
    def update_user(self, user_id, update_data):
        """Update user data"""
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.update(update_data)
        return True
    
    # Interview session operations
    def create_interview_session(self, session_data):
        """Create a new interview session"""
        # Add timestamp
        session_data['created_at'] = firestore.SERVER_TIMESTAMP
        session_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Add to database
        doc_ref = self.db.collection('interview_sessions').document()
        doc_ref.set(session_data)
        
        # Return with ID
        return {**session_data, 'id': doc_ref.id}
    
    def get_interview_session(self, session_id):
        """Get interview session by ID"""
        doc_ref = self.db.collection('interview_sessions').document(session_id)
        doc = doc_ref.get()
        return self.document_to_dict(doc)
    
    def update_interview_session(self, session_id, update_data):
        """Update interview session data"""
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref = self.db.collection('interview_sessions').document(session_id)
        doc_ref.update(update_data)
        return True
    
    def get_user_sessions(self, user_id, limit=10):
        """Get interview sessions for a user"""
        query = self.db.collection('interview_sessions')\
            .where('user_id', '==', user_id)\
            .order_by('created_at', direction='DESCENDING')\
            .limit(limit)
        
        return self.collection_to_list(query.stream())
    
    # Document operations
    def save_document(self, collection, data):
        """Save a document to a collection"""
        # Add timestamps
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Add to database
        doc_ref = self.db.collection(collection).document()
        doc_ref.set(data)
        
        # Return with ID
        return {**data, 'id': doc_ref.id}
    
    def get_document(self, collection, doc_id):
        """Get a document by ID"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        return self.document_to_dict(doc)
    
    def update_document(self, collection, doc_id, update_data):
        """Update a document"""
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.update(update_data)
        return True
    
    def delete_document(self, collection, doc_id):
        """Delete a document"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.delete()
        return True
    
    def query_collection(self, collection, filters=None, order_by=None, limit=None):
        """Query a collection with filters"""
        query = self.db.collection(collection)
        
        # Apply filters
        if filters:
            for field, op, value in filters:
                query = query.where(field, op, value)
        
        # Apply ordering
        if order_by:
            field, direction = order_by if isinstance(order_by, tuple) else (order_by, 'ASCENDING')
            direction = firestore.Query.DESCENDING if direction.upper() == 'DESCENDING' else firestore.Query.ASCENDING
            query = query.order_by(field, direction=direction)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        return self.collection_to_list(query.stream())