import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from app.config import (
    FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_PROJECT_ID,
    FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID,
    FIREBASE_APP_ID, FIREBASE_DATABASE_URL
)
import pyrebase
import datetime

class FirebaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK and Pyrebase"""
        try:
            # Initialize Firebase Admin SDK with application default credentials
            # This assumes you've set up credentials, or are running in a Google Cloud environment
            try:
                firebase_admin.get_app()
            except ValueError:
                # If not already initialized
                cred = credentials.Certificate("firebase-service-account.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': FIREBASE_STORAGE_BUCKET
                })
            
            # Initialize Pyrebase for authentication
            self.pb_config = {
                "apiKey": FIREBASE_API_KEY,
                "authDomain": FIREBASE_AUTH_DOMAIN,
                "databaseURL": FIREBASE_DATABASE_URL,
                "projectId": FIREBASE_PROJECT_ID,
                "storageBucket": FIREBASE_STORAGE_BUCKET,
                "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
                "appId": FIREBASE_APP_ID
            }
            self.pb = pyrebase.initialize_app(self.pb_config)
            
            # Get services
            self.db = firestore.client()
            self.storage_bucket = storage.bucket()
            self.pb_auth = self.pb.auth()
            
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise
    
    # User Management Methods
    def create_user(self, email, password, display_name=None):
        """Create a new user in Firebase Authentication"""
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            # Create user document in Firestore
            user_data = {
                'email': email,
                'display_name': display_name,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            }
            self.db.collection('users').document(user.uid).set(user_data)
            
            return user.uid
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id):
        """Retrieve user data from Firestore"""
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            raise
    
    def update_user(self, user_id, data):
        """Update user document in Firestore"""
        try:
            data['updated_at'] = datetime.datetime.now()
            self.db.collection('users').document(user_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    
    # Document Storage Methods
    def upload_document(self, user_id, file_path, document_type):
        """Upload a document to Firebase Storage"""
        try:
            file_name = file_path.split('/')[-1]
            storage_path = f"{user_id}/{document_type}/{file_name}"
            blob = self.storage_bucket.blob(storage_path)
            blob.upload_from_filename(file_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Store document metadata in Firestore
            doc_data = {
                'user_id': user_id,
                'file_name': file_name,
                'document_type': document_type,
                'storage_path': storage_path,
                'public_url': blob.public_url,
                'uploaded_at': datetime.datetime.now()
            }
            
            # Add to user's documents collection
            self.db.collection('users').document(user_id).collection('documents').add(doc_data)
            
            return {
                'storage_path': storage_path,
                'public_url': blob.public_url
            }
        except Exception as e:
            print(f"Error uploading document: {e}")
            raise
    
    def get_user_documents(self, user_id, document_type=None):
        """Retrieve user's documents from Firestore"""
        try:
            docs_ref = self.db.collection('users').document(user_id).collection('documents')
            
            if document_type:
                query = docs_ref.where('document_type', '==', document_type)
            else:
                query = docs_ref
                
            results = []
            for doc in query.stream():
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                results.append(doc_data)
                
            return results
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            raise
    
    # Interview Session Methods
    def create_interview_session(self, user_id, resume_id, job_description_id, data=None):
        """Create a new interview session"""
        try:
            session_data = {
                'user_id': user_id,
                'resume_id': resume_id,
                'job_description_id': job_description_id,
                'status': 'created',
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            }
            
            if data:
                session_data.update(data)
                
            session_ref = self.db.collection('interview_sessions').add(session_data)
            return session_ref[1].id
        except Exception as e:
            print(f"Error creating interview session: {e}")
            raise
    
    def get_interview_session(self, session_id):
        """Retrieve interview session data"""
        try:
            session_doc = self.db.collection('interview_sessions').document(session_id).get()
            if session_doc.exists:
                return session_doc.to_dict()
            else:
                return None
        except Exception as e:
            print(f"Error retrieving interview session: {e}")
            raise
    
    def update_interview_session(self, session_id, data):
        """Update interview session data"""
        try:
            data['updated_at'] = datetime.datetime.now()
            self.db.collection('interview_sessions').document(session_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating interview session: {e}")
            raise
    
    def save_interview_question(self, session_id, question_data):
        """Save an interview question to the session"""
        try:
            question_data['created_at'] = datetime.datetime.now()
            self.db.collection('interview_sessions').document(session_id).collection('questions').add(question_data)
            return True
        except Exception as e:
            print(f"Error saving interview question: {e}")
            raise
    
    def save_interview_response(self, session_id, question_id, response_data):
        """Save a response to an interview question"""
        try:
            response_data['created_at'] = datetime.datetime.now()
            self.db.collection('interview_sessions').document(session_id).collection('questions').document(question_id).update({
                'response': response_data
            })
            return True
        except Exception as e:
            print(f"Error saving interview response: {e}")
            raise
    
    def get_interview_questions(self, session_id):
        """Get all questions for an interview session"""
        try:
            questions = []
            for doc in self.db.collection('interview_sessions').document(session_id).collection('questions').stream():
                question_data = doc.to_dict()
                question_data['id'] = doc.id
                questions.append(question_data)
            return questions
        except Exception as e:
            print(f"Error retrieving interview questions: {e}")
            raise