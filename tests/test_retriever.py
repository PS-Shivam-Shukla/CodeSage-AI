from app.retriever.retrieval_service import RetrievalService


def main():
    retriever = RetrievalService()

    results = retriever.retrieve(
        "How is JWT authentication implemented?",
        k=3,
    )

    for i, document in enumerate(results, start=1):
        print("=" * 80)
        print(f"Result {i}")
        print("=" * 80)

        print("Metadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content)
        print()


if __name__ == "__main__":
    main()