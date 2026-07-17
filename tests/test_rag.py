from app.rag import RAGPipeline


def main():

    rag = RAGPipeline()

    answer = rag.ask(
        "How does JWT authentication work?"
    )

    print()

    print("=" * 100)

    print(answer)

    print("=" * 100)


if __name__ == "__main__":
    main()