"""
Base Agent Class
Core agent functionality for interacting with Gemini API
"""
import google.generativeai as genai
import time
from typing import Optional
from config import Config


class BaseAgent:
    """
    Base class for all investment analysis agents.
    Handles Gemini API interaction and common functionality.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model_name: str = None,
        temperature: float = None
    ):
        """
        Initialize an investment agent
        
        Args:
            name: Agent's display name (e.g., "Value Hunter")
            role: Brief role description
            system_prompt: Detailed instructions for analysis
            model_name: Gemini model to use (default from config)
            temperature: Creativity level (default from config)
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.temperature = temperature or Config.AGENT_TEMPERATURE
        
        # Initialize Gemini API
        self._initialize_gemini()
        
    def _initialize_gemini(self):
        """Configure and initialize Google Gemini API"""
        # Validate configuration before using API
        Config.validate()
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Configure generation settings
        generation_config = {
            "temperature": self.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config
        )
        
        print(f"✅ {self.name} initialized with {self.model_name}")
    
    def analyze(self, context: str, additional_context: Optional[str] = None) -> str:
        """
        Analyze financial data and return insights
        
        Uses "Long Context" strategy - all data in one prompt
        
        Args:
            context: Primary financial data
            additional_context: Optional extra context
        
        Returns:
            Analysis report as string
        """
        print(f"\n🤖 {self.name} is analyzing...")
        print(f"   Role: {self.role}")
        
        try:
            # Construct full prompt
            full_prompt = f"""
{self.system_prompt}

FINANCIAL DATA TO ANALYZE:
{context}
"""
            
            if additional_context:
                full_prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"
            
            full_prompt += """

Please provide your analysis now. Be specific, cite numbers from the data, and stay true to your role.
"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            analysis = response.text
            
            print(f"✅ {self.name} completed analysis")
            
            return analysis
            
        except Exception as e:
            error_msg = f"❌ Error during {self.name}'s analysis: {str(e)}"
            print(error_msg)
            return error_msg
    
    def __str__(self):
        return f"{self.name} ({self.role}) using {self.model_name}"
