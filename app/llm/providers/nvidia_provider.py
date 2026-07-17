from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.llm.config import (
    MODEL_NAME,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS,
)
from app.utils.retry_handler import retry_on_rate_limit


class NVIDIAProvider:
    """
    Responsible only for communicating with the NVIDIA API.
    Includes automatic retry logic for rate limiting and transient failures.
    """

    def __init__(self) -> None:

        self.client = ChatNVIDIA(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=MAX_TOKENS,
        )

    @retry_on_rate_limit(max_retries=5, initial_delay=2.0)
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the NVIDIA model with automatic retry on rate limits.
        
        Automatically retries up to 5 times with exponential backoff if rate limited (429 error).
        Initial delay: 2 seconds, doubles on each retry up to 60 seconds max.
        """

        response = self.client.invoke(prompt)

        return response.content