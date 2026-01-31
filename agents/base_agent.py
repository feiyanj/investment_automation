"""
Base Agent Class
Core agent functionality for interacting with Gemini and DeepSeek APIs
"""
import google.generativeai as genai
from openai import OpenAI
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
        temperature: float = None,
        agent_type: str = None
    ):
        """
        Initialize an investment agent
        
        Args:
            name: Agent's display name (e.g., "Value Hunter")
            role: Brief role description
            system_prompt: Detailed instructions for analysis
            model_name: Gemini model to use (default from config)
            temperature: Creativity level (if None, uses config based on agent_type)
            agent_type: Agent type for temperature lookup (e.g., 'value_hunter', 'cio_synthesizer')
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_name = model_name or Config.DEFAULT_MODEL
        
        # Determine provider based on model name
        self.provider = Config.get_model_provider(self.model_name)
        
        # Get temperature: explicit > agent_type config > old AGENT_TEMPERATURE fallback
        if temperature is not None:
            self.temperature = temperature
        elif agent_type is not None:
            self.temperature = Config.get_agent_temperature(agent_type, self.model_name)
        else:
            # Fallback for backward compatibility
            self.temperature = getattr(Config, 'AGENT_TEMPERATURE', 0.7)
        
        # Initialize appropriate API
        if self.provider == "deepseek":
            self._initialize_deepseek()
        else:
            self._initialize_gemini()
        
    def _initialize_gemini(self):
        """Configure and initialize Google Gemini API"""
        # Validate configuration before using API
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. Please add it to your .env file."
            )
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Configure generation settings
        generation_config = {
            "temperature": self.temperature,  # Now controlled via Config.AGENT_TEMPERATURES
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 32768,  # Increased for comprehensive DCF analysis with all sections
        }
        
        # Note: thinking_level parameter requires v1alpha API or new google.genai package
        # The current google.generativeai package (deprecated) may not support it
        # Gemini 3 defaults to 'high' thinking level if not specified
        # TODO: Migrate to google.genai package to explicitly set thinking_level="high"
        
        # For now, we rely on Gemini 3's default 'high' thinking level
        # Once migrated to google.genai:
        # if "gemini-3" in self.model_name:
        #     config = types.GenerateContentConfig(
        #         thinking_config=types.ThinkingConfig(thinking_level="high")
        #     )
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config
        )
        
        print(f"✅ {self.name} initialized with {self.model_name} (Gemini)")
        if "gemini-3" in self.model_name:
            print(f"   📊 Gemini 3 settings: temperature={self.temperature}, thinking_level=high (default)")
    
    def _initialize_deepseek(self):
        """Configure and initialize DeepSeek API"""
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY not found. Please add it to your .env file."
            )
        
        # Initialize OpenAI client with DeepSeek endpoint
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        print(f"✅ {self.name} initialized with {self.model_name} (DeepSeek)")
    
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
            
            # Generate response based on provider
            if self.provider == "deepseek":
                # Set max_tokens based on model type
                # DeepSeek Reasoner needs more tokens for reasoning chains + output
                max_tokens = 32768 if "reasoner" in self.model_name.lower() else 16384
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                analysis = response.choices[0].message.content
            else:
                # Gemini API
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
