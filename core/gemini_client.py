"""
Gemini Client via Vertex AI (Google Cloud Credits)

Replaces Groq with Google's Gemini models - covered by $410 Google Cloud credits.
Uses same interface as groq_client.py for easy drop-in replacement.

Models available:
1. gemini-2.0-flash-exp (fastest, recommended - $0.10/1M in, $0.40/1M out)
2. gemini-1.5-flash (fast, cheap - $0.075/1M in, $0.30/1M out)  
3. gemini-1.5-pro (best quality - $1.25/1M in, $5.00/1M out)
"""

import os
import time
from typing import Any, Dict, List, Optional

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv

load_dotenv()

# Models ordered by preference (fastest/cheapest first for AdBoard use case)
GEMINI_MODELS = [
    {
        "id": "gemini-2.0-flash-exp",
        "name": "Gemini 2.0 Flash",
        "max_tokens": 8192,
        "cost_per_1m_input": 0.10,
        "cost_per_1m_output": 0.40,
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "max_tokens": 8192,
        "cost_per_1m_input": 0.075,
        "cost_per_1m_output": 0.30,
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "max_tokens": 8192,
        "cost_per_1m_input": 1.25,
        "cost_per_1m_output": 5.00,
    },
]


class GeminiClient:
    """
    Gemini client with automatic model fallback.
    
    Compatible interface with GroqClient for easy replacement.
    """

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID not set in environment")
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        self.models = GEMINI_MODELS.copy()
        self.current_model_index = 0
        
        # Track rate-limited models
        self.rate_limited_models: Dict[str, float] = {}
        self.rate_limit_cooldown = 60

    def _get_available_model(self) -> Optional[Dict]:
        """Get the next available model that isn't rate-limited."""
        current_time = time.time()

        for model in self.models:
            model_id = model["id"]

            # Check if model was rate-limited recently
            if model_id in self.rate_limited_models:
                cooldown_until = self.rate_limited_models[model_id]
                if current_time < cooldown_until:
                    continue
                else:
                    del self.rate_limited_models[model_id]

            return model

        # All models rate-limited
        if self.rate_limited_models:
            soonest_model_id = min(
                self.rate_limited_models, key=self.rate_limited_models.get
            )
            wait_time = self.rate_limited_models[soonest_model_id] - current_time
            if wait_time > 0:
                print(f"  ⏳ All Gemini models rate-limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time + 1)
            del self.rate_limited_models[soonest_model_id]
            return next(m for m in self.models if m["id"] == soonest_model_id)

        return self.models[0]

    def _mark_rate_limited(self, model_id: str, retry_after: int = 60):
        """Mark a model as rate-limited."""
        self.rate_limited_models[model_id] = time.time() + retry_after
        print(f"  ⚠️  Gemini model {model_id} rate-limited, switching...")

    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, str]]) -> tuple:
        """
        Convert OpenAI-style messages to Gemini format.
        
        Returns: (system_instruction, contents)
        """
        system_instruction = None
        contents = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": content}]})
        
        return system_instruction, contents

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request with automatic model fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-2.0)
            max_retries: Number of times to retry with different models
        
        Returns:
            Dict with 'content', 'model', and 'usage' (compatible with Groq format)
        """
        
        last_error = None

        for attempt in range(max_retries):
            model_info = self._get_available_model()
            if not model_info:
                raise Exception("No Gemini models available")

            model_id = model_info["id"]
            model_max_tokens = model_info["max_tokens"]
            
            # Ensure max_tokens doesn't exceed model limit
            actual_max_tokens = min(max_tokens, model_max_tokens)

            try:
                # Convert messages to Gemini format
                system_instruction, contents = self._convert_messages_to_gemini_format(messages)
                
                # Create model instance
                model = GenerativeModel(
                    model_id,
                    system_instruction=system_instruction if system_instruction else None,
                )
                
                # Configure generation
                generation_config = GenerationConfig(
                    max_output_tokens=actual_max_tokens,
                    temperature=temperature,
                )
                
                # Generate content
                response = model.generate_content(
                    contents,
                    generation_config=generation_config,
                )
                
                # Extract text from response
                response_text = response.text
                
                # Gemini doesn't provide exact token counts easily, estimate them
                # (This is approximate - Gemini uses different tokenization)
                prompt_tokens = sum(len(m.get("content", "").split()) * 1.3 for m in messages)
                completion_tokens = len(response_text.split()) * 1.3
                
                return {
                    "content": response_text,
                    "model": model_id,
                    "usage": {
                        "prompt_tokens": int(prompt_tokens),
                        "completion_tokens": int(completion_tokens),
                        "total_tokens": int(prompt_tokens + completion_tokens),
                    },
                }

            except Exception as e:
                error_str = str(e)
                last_error = e

                # Check for rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    self._mark_rate_limited(model_id, 60)
                    continue
                else:
                    # Non-rate-limit error, raise it
                    print(f"  ❌ Gemini error: {error_str}")
                    raise e

        # All retries exhausted
        raise Exception(
            f"All Gemini models failed after {max_retries} attempts. Last error: {last_error}"
        )


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the singleton Gemini client."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Convenience function for chat completion with Gemini.
    
    Drop-in replacement for groq_client.chat_completion()
    
    Usage:
        from core.gemini_client import chat_completion
        
        response = chat_completion([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a script for a sushi ad."}
        ])
        print(response["content"])
        print(f"Model used: {response['model']}")
    """
    client = get_gemini_client()
    return client.chat_completion(messages, max_tokens, temperature)
