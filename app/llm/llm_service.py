from app.llm.prompts.prompt_service import PromptService
from app.llm.providers.nvidia_provider import NVIDIAProvider


class LLMService:
    """
    Coordinates prompt creation and LLM generation.
    """

    def __init__(self) -> None:

        self.provider = NVIDIAProvider()

        self.prompt = PromptService.build_prompt()

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using the retrieved context.
        """

        prompt = self.prompt.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        return self.provider.generate(prompt)