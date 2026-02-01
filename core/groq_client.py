"""
Groq Client with Automatic Model Fallback

When a model hits rate limits (429 error), automatically switches to the next
available model and retries the request.

Models are ordered by capability (best first):
1. llama-3.3-70b-versatile (best quality, 300K TPM)
2. openai/gpt-oss-120b (good quality, 250K TPM)
3. openai/gpt-oss-20b (decent quality, 250K TPM)
4. llama-3.1-8b-instant (fast, 250K TPM)
"""

import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Models ordered by preference (best quality first)
GROQ_MODELS = [
    {
        "id": "llama-3.3-70b-versatile",
        "name": "Llama 3.3 70B",
        "max_tokens": 32768,
    },
    {
        "id": "openai/gpt-oss-120b",
        "name": "GPT OSS 120B",
        "max_tokens": 65536,
    },
    {
        "id": "openai/gpt-oss-20b",
        "name": "GPT OSS 20B",
        "max_tokens": 65536,
    },
    {
        "id": "llama-3.1-8b-instant",
        "name": "Llama 3.1 8B",
        "max_tokens": 131072,
    },
]


class GroqClient:
    """
    Groq client with automatic model fallback on rate limits.

    Usage:
        client = GroqClient()
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=1000
        )
        print(response["content"])
        print(f"Used model: {response['model']}")
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set in environment")

        self.client = Groq(api_key=self.api_key)
        self.models = GROQ_MODELS.copy()
        self.current_model_index = 0

        # Track rate-limited models to skip them temporarily
        self.rate_limited_models: Dict[str, float] = {}
        self.rate_limit_cooldown = 60  # seconds before retrying a rate-limited model

    def _get_available_model(self) -> Optional[Dict]:
        """Get the next available model that isn't rate-limited."""
        current_time = time.time()

        for model in self.models:
            model_id = model["id"]

            # Check if model was rate-limited recently
            if model_id in self.rate_limited_models:
                cooldown_until = self.rate_limited_models[model_id]
                if current_time < cooldown_until:
                    continue  # Skip this model, still in cooldown
                else:
                    # Cooldown expired, remove from rate-limited list
                    del self.rate_limited_models[model_id]

            return model

        # All models are rate-limited, return the one with shortest cooldown
        if self.rate_limited_models:
            soonest_model_id = min(
                self.rate_limited_models, key=self.rate_limited_models.get
            )
            wait_time = self.rate_limited_models[soonest_model_id] - current_time
            if wait_time > 0:
                print(f"  ⏳ All models rate-limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time + 1)
            del self.rate_limited_models[soonest_model_id]
            return next(m for m in self.models if m["id"] == soonest_model_id)

        return self.models[0]  # Fallback to first model

    def _mark_rate_limited(self, model_id: str, retry_after: int = 60):
        """Mark a model as rate-limited."""
        self.rate_limited_models[model_id] = time.time() + retry_after
        print(f"  ⚠️  Model {model_id} rate-limited, switching...")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        max_retries: int = 4,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request with automatic model fallback.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            max_retries: Number of times to retry with different models

        Returns:
            Dict with 'content', 'model', and 'usage'

        Raises:
            Exception if all models fail
        """

        last_error = None

        for attempt in range(max_retries):
            model_info = self._get_available_model()
            if not model_info:
                raise Exception("No Groq models available")

            model_id = model_info["id"]
            model_max_tokens = model_info["max_tokens"]

            # Ensure max_tokens doesn't exceed model limit
            actual_max_tokens = min(max_tokens, model_max_tokens)

            try:
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=actual_max_tokens,
                    temperature=temperature,
                )

                return {
                    "content": response.choices[0].message.content,
                    "model": model_id,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                }

            except Exception as e:
                error_str = str(e)
                last_error = e

                # Check if it's a rate limit error (429)
                if "429" in error_str or "rate_limit" in error_str.lower():
                    # Try to extract retry-after time
                    retry_after = 60  # default
                    if "try again in" in error_str.lower():
                        # Parse time from error message
                        import re

                        match = re.search(r"(\d+)m(\d+)", error_str)
                        if match:
                            minutes = int(match.group(1))
                            seconds = int(match.group(2))
                            retry_after = minutes * 60 + seconds
                        else:
                            match = re.search(r"(\d+)s", error_str)
                            if match:
                                retry_after = int(match.group(1))

                    self._mark_rate_limited(model_id, retry_after)
                    continue  # Try next model
                else:
                    # Non-rate-limit error, raise it
                    raise e

        # All retries exhausted
        raise Exception(
            f"All Groq models failed after {max_retries} attempts. Last error: {last_error}"
        )


# Singleton instance for easy import
_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Get or create the singleton Groq client."""
    global _client
    if _client is None:
        _client = GroqClient()
    return _client


def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Convenience function for chat completion with automatic fallback.

    Usage:
        from core.groq_client import chat_completion

        response = chat_completion([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a haiku about coffee."}
        ])
        print(response["content"])
    """
    client = get_groq_client()
    return client.chat_completion(messages, max_tokens, temperature)
