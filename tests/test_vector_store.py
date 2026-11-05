import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.vector_store import FaissVectorStore


def test_vector_store():

    store = FaissVectorStore(dimension=3)

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.9, 0.1, 0.0]
    ]

    metadata = [
        {"page_number": 1, "text": "Artificial Intelligence"},
        {"page_number": 2, "text": "Machine Learning"},
        {"page_number": 3, "text": "AI applications"}
    ]

    store.add_embeddings(embeddings, metadata)

    results = store.search(
        [1.0, 0.0, 0.0],
        top_k=2
    )

    assert len(results) == 2
    assert results[0]["metadata"]["page_number"] == 1

    print("SUCCESS: FAISS vector search is working!")
    print("Total vectors:", store.index.ntotal)
    print("Top result:", results[0]["metadata"]["text"])


if __name__ == "__main__":
    test_vector_store()