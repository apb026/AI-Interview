import os
import openai
from typing import List, Dict, Any, Optional, Tuple
import logging
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    """Retrieval-Augmented Generation (RAG) engine for contextual interview questions."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the RAG engine.
        
        Args:
            openai_api_key: OpenAI API key for embeddings and generation
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        openai.api_key = self.openai_api_key
        
        # Default embedding model
        self.embedding_model = "text-embedding-3-small"
        
        # Default completion model
        self.completion_model = "gpt-4"
        
        # In-memory vector store for small applications
        # For production, consider using Pinecone, Weaviate, or other vector DBs
        self.document_store = []
        self.document_embeddings = []
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a document to the RAG system.
        
        Args:
            doc_id: Unique identifier for the document
            content: Text content of the document
            metadata: Additional information about the document
        """
        try:
            # Generate embedding for the document
            embedding = self._get_embedding(content)
            
            # Store document and its embedding
            document = {
                "id": doc_id,
                "content": content,
                "metadata": metadata or {}
            }
            self.document_store.append(document)
            self.document_embeddings.append(embedding)
            
            logger.info(f"Added document {doc_id} to RAG engine")
        except Exception as e:
            logger.error(f"Error adding document to RAG engine: {str(e)}")
            raise
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for a text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        text = text.replace("\n", " ")
        response = openai.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def _compute_similarity(self, query_embedding: List[float], document_embedding: List[float]) -> float:
        """Compute cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Query embedding vector
            document_embedding: Document embedding vector
            
        Returns:
            Cosine similarity score
        """
        # Convert to numpy arrays for easier computation
        vec1 = np.array(query_embedding)
        vec2 = np.array(document_embedding)
        
        # Compute cosine similarity
        cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(cos_sim)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            top_k: Number of top documents to retrieve
            
        Returns:
            List of relevant documents with similarity scores
        """
        if not self.document_store:
            logger.warning("No documents in the store for retrieval")
            return []
        
        try:
            # Generate embedding for the query
            query_embedding = self._get_embedding(query)
            
            # Compute similarity scores
            similarities = [
                self._compute_similarity(query_embedding, doc_embedding)
                for doc_embedding in self.document_embeddings
            ]
            
            # Get indices of top-k documents
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Return top-k documents with similarity scores
            result = []
            for idx in top_indices:
                result.append({
                    **self.document_store[idx],
                    "similarity": similarities[idx]
                })
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def generate_response(self, query: str, context: List[Dict[str, Any]], interview_stage: str) -> str:
        """Generate a response based on the query and retrieved contexts.
        
        Args:
            query: User query
            context: Retrieved relevant contexts
            interview_stage: Current stage of the interview (e.g., 'technical', 'behavioral')
            
        Returns:
            Generated response
        """
        try:
            # Format context for inclusion in the prompt
            formatted_context = "\n\n".join([
                f"Document {i+1} (Relevance: {doc['similarity']:.2f}):\n{doc['content']}"
                for i, doc in enumerate(context)
            ])
            
            # Generate prompt based on query and context
            prompt = f"""
            You are an AI interviewer assessing a candidate.
            
            Current interview stage: {interview_stage}
            
            Relevant information from the candidate's resume and job description:
            {formatted_context}
            
            Based on this context, respond to the following or generate an appropriate interview question:
            {query}
            """
            
            # Generate completion using OpenAI
            response = openai.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": "You are an AI interviewer assistant that helps generate relevant and insightful interview questions based on job descriptions and candidate resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I'm sorry, I couldn't generate a response due to an error: {str(e)}"
    
    def generate_question(self, 
                        resume_text: str, 
                        job_description: str, 
                        question_type: str, 
                        previous_questions: List[str] = None) -> str:
        """Generate an interview question based on resume and job description.
        
        Args:
            resume_text: Candidate's resume text
            job_description: Job description text
            question_type: Type of question (technical, behavioral, etc.)
            previous_questions: List of previously asked questions to avoid repetition
            
        Returns:
            Generated interview question
        """
        previous_questions = previous_questions or []
        
        try:
            prompt = f"""
            You are an AI-powered interviewer. Generate a relevant {question_type} interview question 
            based on the candidate's resume and the job description.
            
            Resume:
            {resume_text[:1000]}...
            
            Job Description:
            {job_description[:1000]}...
            
            Previously asked questions (avoid asking similar questions):
            {', '.join(previous_questions)}
            
            Generate a single, specific {question_type} interview question that evaluates the candidate's 
            fit for this role based on their background and the job requirements.
            """
            
            response = openai.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": "You are an AI interviewer that generates relevant interview questions based on candidate resumes and job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return "Tell me about your experience and how it relates to this role."
    
    def evaluate_answer(self, 
                       question: str, 
                       answer: str, 
                       resume_text: str, 
                       job_description: str) -> Dict[str, Any]:
        """Evaluate a candidate's answer to an interview question.
        
        Args:
            question: The interview question asked
            answer: Candidate's answer to the question
            resume_text: Candidate's resume text for context
            job_description: Job description text for context
            
        Returns:
            Evaluation results with feedback and score
        """
        try:
            prompt = f"""
            You are an AI interviewer evaluating a candidate's response.
            
            Question asked: {question}
            
            Candidate's answer: {answer}
            
            Context from resume:
            {resume_text[:500]}...
            
            Context from job description:
            {job_description[:500]}...
            
            Evaluate the candidate's answer on a scale of 1-10, where:
            1-3: Poor response, does not address the question or demonstrate relevant skills/experience
            4-6: Average response, partially addresses the question with some relevant points
            7-8: Good response, thoroughly addresses the question with relevant examples
            9-10: Excellent response, exceeds expectations with comprehensive, insightful answer
            
            Provide:
            1. Numerical score (1-10)
            2. Brief feedback explaining the score (2-3 sentences)
            3. Key strengths in the response
            4. Areas for improvement
            
            Format your response as a JSON object with keys: score, feedback, strengths, improvements
            """
            
            response = openai.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": "You are an AI interviewer evaluating candidate responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            evaluation = response.choices[0].message.content
            
            # If the response is a string representation of JSON, convert it
            import json
            if isinstance(evaluation, str):
                evaluation = json.loads(evaluation)
                
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            return {
                "score": 5,
                "feedback": "Unable to provide detailed feedback due to an error.",
                "strengths": ["N/A"],
                "improvements": ["N/A"]
            }