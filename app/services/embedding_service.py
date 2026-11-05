import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSION = 1536

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_embeddings(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT"
) -> list[list[float]]:

    if not texts:
        raise ValueError("No text provided for embedding.")

    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is missing from .env")

    embeddings = []
    batch_size = 100

    for start in range(0, len(texts), batch_size):

        batch = texts[start:start + batch_size]

        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )

        embeddings.extend(
            item.values for item in response.embeddings
        )

    return embeddings