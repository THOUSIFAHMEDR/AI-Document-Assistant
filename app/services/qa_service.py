import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.embedding_service import generate_embeddings

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def answer_question(store, question: str, top_k: int = 3):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is missing from .env")

    # Step 1: Generate question embedding
    query_embedding = generate_embeddings(
        [question],
        task_type="RETRIEVAL_QUERY"
    )[0]

    # Step 2: Search FAISS
    results = store.search(
        query_embedding,
        top_k=top_k
    )

    if not results:
        return {
            "answer": "No relevant information found in the document.",
            "sources": []
        }

    # Step 3: Prepare context
    context_parts = []
    sources = []

    for result in results:

        metadata = result["metadata"]

        context_parts.append(
            f"Page {metadata['page_number']}:\n{metadata['text']}"
        )

        sources.append({
            "page_number": metadata["page_number"],
            "text": metadata["text"],
            "score": result["score"]
        })

    context = "\n\n".join(context_parts)

    # Step 4: Generate answer using Gemini
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=(
            f"""
            You are an AI Document Assistant.

            Answer the question using ONLY the supplied document context.

            Rules:
            1. Do not invent information.
            2. If the answer is unavailable, say so clearly.
            3. Explain answers in simple, understandable language.
            4. Mention relevant page numbers.

            DOCUMENT CONTEXT:
            {context}

            USER QUESTION:
            {question}
            """
        ),
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )

    answer = response.text

    if not answer:
        raise RuntimeError("Gemini returned an empty response.")

    return {
        "answer": answer,
        "sources": sources
    }