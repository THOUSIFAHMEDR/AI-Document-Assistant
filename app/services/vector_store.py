import faiss
import numpy as np
import json
from pathlib import Path


class FaissVectorStore:

    def __init__(self, dimension=1536):

        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = []

    def add_embeddings(self, embeddings, metadata):

        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata count mismatch.")

        if not embeddings:
            return

        vectors = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError("Invalid embedding dimensions.")

        if not np.isfinite(vectors).all():
            raise ValueError("Embeddings contain invalid values.")

        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_embedding, top_k=3):

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if self.index.ntotal == 0:
            return []

        query = np.asarray(
            [query_embedding],
            dtype=np.float32
        )

        if query.shape[1] != self.dimension:
            raise ValueError("Invalid query embedding dimensions.")

        if not np.isfinite(query).all():
            raise ValueError("Query embedding contains invalid values.")

        faiss.normalize_L2(query)

        scores, indices = self.index.search(
            query,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            results.append({
                "score": float(score),
                "metadata": self.metadata[idx]
            })

        return results

    def save(self, directory="vectorstore"):

        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(path / "document.index")
        )

        with open(path / "metadata.json", "w", encoding="utf-8") as file:
            json.dump(self.metadata, file, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, directory="vectorstore"):

        path = Path(directory)

        index = faiss.read_index(
            str(path / "document.index")
        )

        store = cls(index.d)

        with open(path / "metadata.json", "r", encoding="utf-8") as file:
            store.metadata = json.load(file)

        if len(store.metadata) != index.ntotal:
            raise ValueError("Vector index and metadata are inconsistent.")

        store.index = index

        return store