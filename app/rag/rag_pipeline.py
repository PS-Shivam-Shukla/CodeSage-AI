from app.llm import LLMService
from app.retriever.retrieval_service import RetrievalService


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    Workflow:
        Question
            ↓
        Retrieve Documents
            ↓
        Build Context
            ↓
        Generate Answer
    """

    def __init__(self) -> None:

        self.retriever = RetrievalService()

        self.llm = LLMService()

    def ask(
        self,
        question: str,
        k: int = 5,
    ) -> str:
        """
        Answer a user question.

        Args:
            question: User question.
            k: Number of retrieved chunks.

        Returns:
            Generated answer.
        """

        documents = self.retriever.retrieve(
            query=question,
            k=k,
        )

        context = self._build_context(documents)

        return self.llm.generate_answer(
            question=question,
            context=context,
        )

    @staticmethod
    def _build_context(
        documents,
    ) -> str:
        """
        Convert retrieved documents into a single context string.
        """

        return "\n\n".join(
            document.page_content
            for document in documents
        )