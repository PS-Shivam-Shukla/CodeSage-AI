from app.embeddings.embedding_service import EmbeddingService

service = EmbeddingService()

vector = service.embed_query("Explain user authentication.")

print(type(vector))
print(len(vector))
print(vector[:10])