from pathlib import Path
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from .config import QDRANT_PATH, COLLECTION_NAME, EMBEDDING_MODEL

class CodeIndex:
    def __init__(self):
        QDRANT_PATH.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(QDRANT_PATH))
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)

    def index_chunks(self, chunks: list[dict]) -> int:
        if not chunks:
            return 0

        # Rebuild the collection on each indexing run to avoid stale/deleted files.
        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)

        dimension = self.encoder.get_sentence_embedding_dimension()
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=dimension,
                distance=models.Distance.COSINE
            )
        )

        texts = [item["text"] for item in chunks]
        vectors = self.encoder.encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        ).tolist()

        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            payload = {k: v for k, v in chunk.items() if k != "text"}
            payload["text"] = chunk["text"]
            points.append(models.PointStruct(id=idx + 1, vector=vector, payload=payload))

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)
        return len(points)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not self.client.collection_exists(COLLECTION_NAME):
            return []
        vector = self.encoder.encode(query, normalize_embeddings=True).tolist()
        hits = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit,
            with_payload=True
        ).points
        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append({
                "score": float(hit.score),
                "path": payload.get("path", ""),
                "symbol": payload.get("symbol", ""),
                "kind": payload.get("kind", ""),
                "start_line": payload.get("start_line"),
                "end_line": payload.get("end_line"),
                "text": payload.get("text", ""),
            })
        return results

    def close(self):
        self.client.close()
