import random
from typing import Dict, List, Optional, Any
import logging
import os
import json
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewerPersona:
    """Define and manage interviewer personas with distinct traits and styles."""
    
    def __init__(self, 
               persona_id: str,
               name: str,
               role: str,
               traits: List[str],
               communication_style: str,
               description: str,
               tone: Optional[str] = None,
               openai_api_key: Optional[str] = None):
        """Initialize an interviewer persona.
        
        Args:
            persona_id: Unique identifier for the persona
            name: Name of the interviewer persona
            role: Role of the interviewer (e.g., "Technical Lead", "HR Manager")
            traits: List of personality traits
            communication_style: Description of communication style
            description: Detailed description of the persona
            tone: Overall tone of the persona
            openai_api_key: OpenAI API key for text generation
        """
        self.persona_id = persona_id
        self.name = name
        self.role = role
        self.traits = traits
        self.communication_style = communication_style
        self.description = description
        self.tone = tone or "professional"
        
        # Set OpenAI API key
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Default model for text generation
        self.completion_model = "gpt-4"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary representation.
        
        Returns:
            Dictionary representation of the persona
        """
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "role": self.role,
            "traits": self.traits,
            "communication_style": self.communication_style,
            "description": self.description,
            "tone": self.tone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], openai_api_key: Optional[str] = None):
        """Create a persona from a dictionary.
        
        Args:
            data: Dictionary containing persona attributes
            openai_api_key: OpenAI API key for text generation
            
        Returns:
            New InterviewerPersona instance
        """
        return cls(
            persona_id=data.get("persona_id", "default"),
            name=data.get("name", "Interviewer"),
            role=data.get("role", "Hiring Manager"),
            traits=data.get("traits", ["professional"]),
            communication_style=data.get("communication_style", "formal"),
            description=data.get("description", "A professional interviewer"),
            tone=data.get("tone", "professional"),
            openai_api_key=openai_api_key
        )
    
    def rephrase_question(self, original_question: str) -> str:
        """Rephrase a question according to the persona's style.
        
        Args:
            original_question: Original interview question
            
        Returns:
            Rephrased question in the persona's style
        """
        try:
            # If OpenAI API key is not available, return original question
            if not self.openai_api_key:
                return original_question
            
            # Create prompt for rephrasing
            prompt = f"""
            You are {self.name}, a {self.role} with the following traits: {', '.join(self.traits)}.
            Your communication style is {self.communication_style}.
            
            Please rephrase the following interview question in your own style, maintaining the same core question:
            
            Original question: "{original_question}"
            
            Your rephrased question:
            """
            
            response = openai.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": f"You are {self.name}, {self.description}. Speak in a {self.tone} tone."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            rephrased = response.choices[0].message.content.strip()
            
            # Remove quotation marks if present
            rephrased = rephrased.strip('"')
            
            return rephrased
        except Exception as e:
            logger.error(f"Error rephrasing question: {str(e)}")
            return original_question
    
    def generate_response(self, context: str, question: str = None) -> str:
        """Generate a response based on the persona and context.
        
        Args:
            context: Context for the response
            question: Optional question to respond to
            
        Returns:
            Generated response in the persona's style
        """
        try:
            if not self.openai_api_key:
                return "I'm sorry, I can't generate a personalized response at this time."
            
            # Create prompt for response generation
            prompt = f"""
            You are {self.name}, a {self.role} with the following traits: {', '.join(self.traits)}.
            Your communication style is {self.communication_style}.
            
            Context:
            {context}
            
            """
            
            if question:
                prompt += f"Question: {question}\n\nYour response:"
            else:
                prompt += "Generate a response in your unique style:"
            
            response = openai.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": f"You are {self.name}, {self.description}. Speak in a {self.tone} tone."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I couldn't generate a response due to an error."


class PersonaManager:
    """Manage a collection of interviewer personas."""
    
    def __init__(self, personas_file: Optional[str] = None, openai_api_key: Optional[str] = None):
        """Initialize the persona manager.
        
        Args:
            personas_file: Path to a JSON file containing persona definitions
            openai_api_key: OpenAI API key for text generation
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.personas = {}
        
        # Load default personas
        self._load_default_personas()
        
        # Load personas from file if specified
        if personas_file:
            self.load_personas_from_file(personas_file)
    
    def _load_default_personas(self) -> None:
        """Load default personas."""
        default_personas = [
            {
                "persona_id": "technical_lead",
                "name": "Alex Chen",
                "role": "Technical Lead",
                "traits": ["analytical", "detail-oriented", "knowledgeable"],
                "communication_style": "clear and technical",
                "description": "A seasoned technical lead with 12 years of industry experience. Focuses on technical depth and practical problem-solving.",
                "tone": "technical but approachable"
            },
            {
                "persona_id": "hr_manager",
                "name": "Sarah Johnson",
                "role": "HR Manager",
                "traits": ["empathetic", "observant", "people-focused"],
                "communication_style": "warm and professional",
                "description": "An experienced HR professional specializing in talent acquisition and development. Values cultural fit and interpersonal skills.",
                "tone": "friendly and encouraging"
            },
            {
                "persona_id": "startup_ceo",
                "name": "Raj Patel",
                "role": "Startup CEO",
                "traits": ["visionary", "direct", "innovative"],
                "communication_style": "casual but challenging",
                "description": "A dynamic entrepreneur leading a fast-growing startup. Looking for adaptable team players who can handle ambiguity.",
                "tone": "energetic and straightforward"
            },
            {
                "persona_id": "senior_engineer",
                "name": "Maya Rodriguez",
                "role": "Senior Software Engineer",
                "traits": ["methodical", "precise", "experienced"],
                "communication_style": "technical and thorough",
                "description": "A veteran software engineer with a focus on clean code and scalable architecture. Values deep technical knowledge and best practices.",
                "tone": "serious and detail-oriented"
            },
            {
                "persona_id": "product_manager",
                "name": "James Wilson",
                "role": "Product Manager",
                "traits": ["strategic", "user-focused", "collaborative"],
                "communication_style": "conversational and practical",
                "description": "A product-focused professional interested in how candidates approach product problems. Values user empathy and business acumen.",
                "tone": "balanced and inquisitive"
            }
        ]
        
        for persona_data in default_personas:
            persona = InterviewerPersona.from_dict(persona_data, self.openai_api_key)
            self.personas[persona.persona_id] = persona
    
    def load_personas_from_file(self, file_path: str) -> None:
        """Load personas from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing persona definitions
        """
        try:
            with open(file_path, 'r') as f:
                personas_data = json.load(f)
            
            for persona_data in personas_data:
                persona = InterviewerPersona.from_dict(persona_data, self.openai_api_key)
                self.personas[persona.persona_id] = persona
                
            logger.info(f"Loaded {len(personas_data)} personas from {file_path}")
        except Exception as e:
            logger.error(f"Error loading personas from file: {str(e)}")
    
    def save_personas_to_file(self, file_path: str) -> None:
        """Save current personas to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
        """
        try:
            personas_data = [persona.to_dict() for persona in self.personas.values()]
            
            with open(file_path, 'w') as f:
                json.dump(personas_data, f, indent=2)
                
            logger.info(f"Saved {len(personas_data)} personas to {file_path}")
        except Exception as e:
            logger.error(f"Error saving personas to file: {str(e)}")
    
    def get_persona(self, persona_id: str) -> Optional[InterviewerPersona]:
        """Get a persona by ID.
        
        Args:
            persona_id: ID of the persona to retrieve
            
        Returns:
            Persona object if found, None otherwise
        """
        return self.personas.get(persona_id)
    
    def add_persona(self, persona: InterviewerPersona) -> None:
        """Add a new persona.
        
        Args:
            persona: InterviewerPersona object to add
        """
        self.personas[persona.persona_id] = persona
    
    def create_persona(self, 
                     persona_id: str,
                     name: str,
                     role: str,
                     traits: List[str],
                     communication_style: str,
                     description: str,
                     tone: Optional[str] = None) -> InterviewerPersona:
        """Create and add a new persona.
        
        Args:
            persona_id: Unique identifier for the persona
            name: Name of the interviewer persona
            role: Role of the interviewer
            traits: List of personality traits
            communication_style: Description of communication style
            description: Detailed description of the persona
            tone: Overall tone of the persona
            
        Returns:
            Newly created InterviewerPersona
        """
        persona = InterviewerPersona(
            persona_id=persona_id,
            name=name,
            role=role,
            traits=traits,
            communication_style=communication_style,
            description=description,
            tone=tone,
            openai_api_key=self.openai_api_key
        )
        self.add_persona(persona)
        return persona
    
    def get_random_persona(self) -> InterviewerPersona:
        """Get a random persona from the collection.
        
        Returns:
            Random InterviewerPersona
        """
        if not self.personas:
            # Create a default persona if none exist
            return InterviewerPersona(
                persona_id="default",
                name="Interviewer",
                role="Hiring Manager",
                traits=["professional"],
                communication_style="formal",
                description="A professional interviewer",
                tone="professional",
                openai_api_key=self.openai_api_key
            )
        
        return random.choice(list(self.personas.values()))
    
    def generate_new_persona(self, industry: str, role: str) -> InterviewerPersona:
        """Generate a new persona based on industry and role.
        
        Args:
            industry: Industry context for the persona
            role: Role context for the persona
            
        Returns:
            Newly generated InterviewerPersona
        """
        try:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required to generate personas")
            
            prompt = f"""
            Create a unique interviewer persona for a {role} position in the {industry} industry.
            
            Generate a JSON object with the following fields:
            - persona_id: A unique identifier (use snake_case)
            - name: A realistic full name
            - role: A specific job title related to {role}
            - traits: An array of 3-5 personality traits
            - communication_style: A brief description of communication style
            - description: A 1-2 sentence background description
            - tone: A brief description of the overall tone
            
            Ensure the persona is realistic, professional, and appropriate for interviewing candidates.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates realistic interviewer personas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            persona_data = json.loads(response.choices[0].message.content)
            
            # Create and add the persona
            persona = InterviewerPersona.from_dict(persona_data, self.openai_api_key)
            self.add_persona(persona)
            
            return persona
        except Exception as e:
            logger.error(f"Error generating new persona: {str(e)}")
            # Return a generic fallback persona
            fallback_id = f"{industry}_{role}".lower().replace(" ", "_")
            return self.create_persona(
                persona_id=fallback_id,
                name=f"{industry.title()} Interviewer",
                role=role.title(),
                traits=["professional", "knowledgeable"],
                communication_style="standard professional",
                description=f"An interviewer for {role} positions in the {industry} industry.",
                tone="professional"
            )