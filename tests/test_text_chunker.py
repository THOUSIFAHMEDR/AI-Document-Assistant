import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.text_chunker import chunk_documents


def test_chunking():

    pages = [
        {
            "page_number": 1,
            "text": "Artificial Intelligence " * 50
        }
    ]

    chunks = chunk_documents(
        pages,
        chunk_size=200,
        overlap=50
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk["page_number"] == 1
        assert len(chunk["text"]) <= 200

    print("SUCCESS: Text chunking is working!")
    print("Total chunks:", len(chunks))
    print("First chunk:", chunks[0]["text"])


if __name__ == "__main__":
    test_chunking()