from firebase_admin import firestore
import uuid
import time
from datetime import datetime

class BaseModel:
    """Base model for all database models"""
    
    collection_name = None
    
    @classmethod
    def create(cls, data):
        """Create a new document"""
        db = firestore.client()
        doc_id = str(uuid.uuid4())
        
        # Add timestamps
        now = int(time.time())
        data['created_at'] = now
        data['updated_at'] = now
        data['id'] = doc_id
        
        # Save to database
        db.collection(cls.collection_name).document(doc_id).set(data)
        return data
    
    @classmethod
    def get(cls, doc_id):
        """Get a document by ID"""
        db = firestore.client()
        doc = db.collection(cls.collection_name).document(doc_id).get()
        
        if not doc.exists:
            return None
        
        return doc.to_dict()
    
    @classmethod
    def update(cls, doc_id, data):
        """Update a document"""
        db = firestore.client()
        
        # Add updated timestamp
        data['updated_at'] = int(time.time())
        
        # Update database
        db.collection(cls.collection_name).document(doc_id).update(data)
        return True
    
    @classmethod
    def delete(cls, doc_id):
        """Delete a document"""
        db = firestore.client()
        db.collection(cls.collection_name).document(doc_id).delete()
        return True
    
    @classmethod
    def query(cls, filters=None, order_by=None, direction='ASCENDING', limit=None):
        """Query collection with filters"""
        db = firestore.client()
        query = db.collection(cls.collection_name)
        
        # Apply filters
        if filters:
            for field, op, value in filters:
                query = query.where(field, op, value)
        
        # Apply ordering
        if order_by:
            direction_value = firestore.Query.DESCENDING if direction.upper() == 'DESCENDING' else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction_value)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        result = []
        
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict['id'] = doc.id
            result.append(doc_dict)
        
        return result

class Resume(BaseModel):
    """Resume model"""
    collection_name = 'resumes'
    
    @classmethod
    def get_user_resumes(cls, user_id):
        """Get all resumes for a user"""
        return cls.query(filters=[('user_id', '==', user_id)], order_by='created_at', direction='DESCENDING')
    
    @classmethod
    def get_latest_resume(cls, user_id):
        """Get the latest resume for a user"""
        resumes = cls.query(
            filters=[('user_id', '==', user_id)], 
            order_by='created_at', 
            direction='DESCENDING',
            limit=1
        )
        
        return resumes[0] if resumes else None

class JobDescription(BaseModel):
    """Job description model"""
    collection_name = 'job_descriptions'
    
    @classmethod
    def get_user_job_descriptions(cls, user_id):
        """Get all job descriptions for a user"""
        return cls.query(filters=[('user_id', '==', user_id)], order_by='created_at', direction='DESCENDING')

class InterviewSession(BaseModel):
    """Interview session model"""
    collection_name = 'interview_sessions'
    
    @classmethod
    def get_user_sessions(cls, user_id, limit=10):
        """Get interview sessions for a user"""
        return cls.query(
            filters=[('user_id', '==', user_id)], 
            order_by='created_at', 
            direction='DESCENDING',
            limit=limit
        )
    
    @classmethod
    def get_session_questions(cls, session_id):
        """Get questions for an interview session"""
        db = firestore.client()
        questions = db.collection('interview_sessions').document(session_id).collection('questions').stream()
        
        result = []
        for q in questions:
            q_dict = q.to_dict()
            q_dict['id'] = q.id
            result.append(q_dict)
        
        return result
    
    @classmethod
    def get_session_answers(cls, session_id):
        """Get answers for an interview session"""
        db = firestore.client()
        answers = db.collection('interview_sessions').document(session_id).collection('answers').stream()
        
        result = []
        for a in answers:
            a_dict = a.to_dict()
            a_dict['id'] = a.id
            result.append(a_dict)
        
        return result
    
    @classmethod
    def get_session_feedback(cls, session_id):
        """Get feedback for an interview session"""
        db = firestore.client()
        feedback = db.collection('interview_sessions').document(session_id).collection('feedback').stream()
        
        result = []
        for f in feedback:
            f_dict = f.to_dict()
            f_dict['id'] = f.id
            result.append(f_dict)
        
        return result