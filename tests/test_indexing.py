from app.indexing import IndexingService


def main():

    indexer = IndexingService()

    indexer.index_repository(
        "./data/sample_repo"
    )


if __name__ == "__main__":
    main()