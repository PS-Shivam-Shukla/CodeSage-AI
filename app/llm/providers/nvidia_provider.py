from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.llm.config import (
    MODEL_NAME,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS,
)


class NVIDIAProvider:
    """
    Responsible only for communicating with the NVIDIA API.
    """

    def __init__(self) -> None:

        self.client = ChatNVIDIA(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=MAX_TOKENS,
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the NVIDIA model.
        """

        response = self.client.invoke(prompt)

        return response.content