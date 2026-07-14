from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.indexing import IndexingService
from app.rag import RAGPipeline


def main():

    print("=" * 80)
    print("CodeSage AI")
    print("=" * 80)

    repository = input("\nEnter repository path:\n> ").strip()

    if not Path(repository).exists():
        print("\nRepository not found.")
        return

    print("\nIndexing repository...\n")

    indexer = IndexingService()
    indexer.index_repository(repository)

    print("\nRepository indexed successfully.")

    rag = RAGPipeline()

    while True:

        question = input("\nAsk a question (type 'exit' to quit):\n> ").strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        print("\nThinking...\n")

        answer = rag.ask(question)

        print("=" * 80)
        print(answer)
        print("=" * 80)


if __name__ == "__main__":
    main()