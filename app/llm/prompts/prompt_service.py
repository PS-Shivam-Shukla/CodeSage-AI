from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate


class PromptService:
    """
    Loads and builds prompts from template files.
    """

    TEMPLATE_PATH = (
        Path(__file__).parent / "repository_qa.txt"
    )

    @classmethod
    def build_prompt(cls) -> ChatPromptTemplate:

        template = cls.TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )

        return ChatPromptTemplate.from_template(template)