# AI Document Assistant

An AI-powered PDF document assistant that allows users to upload PDF documents, ask questions about their contents, and receive context-aware answers with relevant source references and page citations.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents before generating answers using Google's Gemini API.

## Features

- **PDF Upload:** Upload and process PDF documents through an interactive dashboard.
- **Text Extraction:** Extract text and page information using PyMuPDF.
- **Structured Table Extraction:** Detect PDF tables and preserve relationships between student records and vertically merged guide cells.
- **Text Chunking:** Divide extracted document text into smaller overlapping chunks for efficient retrieval.
- **Semantic Embeddings:** Generate document embeddings using Google's Gemini embedding model.
- **Vector Search:** Retrieve relevant document content using FAISS similarity search.
- **AI Question Answering:** Generate context-aware answers using Gemini based on retrieved document information.
- **Source References:** Display relevant document excerpts, similarity scores, and page references.
- **Document Management:** View and access previously uploaded PDF documents.
- **PDF Viewer:** View original uploaded documents alongside AI-generated answers.
- **Persistent Storage:** Store uploaded PDFs, FAISS indexes, and document metadata locally.
- **Interactive Interface:** Use a Streamlit dashboard for document uploads, document viewing, and AI-powered question answering.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Frontend Framework | Streamlit |
| AI Model | Google Gemini |
| Embedding Model | gemini-embedding-001 |
| Answer Generation Model | gemini-3.5-flash-lite |
| Vector Database | FAISS |
| PDF Processing | PyMuPDF |
| Numerical Processing | NumPy |
| API Communication | Requests |
| Environment Management | Python Virtual Environment |
| Containerization | Docker |
| Version Control | Git and GitHub |

## System Architecture

The application follows a Retrieval-Augmented Generation (RAG) architecture.

### Document Processing Workflow

1. The user uploads a PDF through the Streamlit interface.
2. The frontend sends the document to the FastAPI backend.
3. PyMuPDF extracts text and page information.
4. PDF tables are detected, and supported merged-cell relationships are preserved.
5. Extracted content is divided into overlapping text chunks.
6. Gemini generates semantic embeddings for the chunks.
7. FAISS stores the embeddings and associated metadata.
8. The original PDF and vector index are saved locally.

### Question Answering Workflow

1. The user submits a question about an uploaded document.
2. The question is converted into an embedding using Gemini.
3. FAISS searches for the most relevant document chunks.
4. Retrieved document content is passed to Gemini as context.
5. Gemini generates an answer using the supplied document context.
6. The application displays the answer with relevant source references and page numbers.

### Architecture Diagram

```text
                 USER
                   |
                   v
          STREAMLIT FRONTEND
                   |
                   v
            FASTAPI BACKEND
                   |
          +--------+--------+
          |                 |
          v                 v
      PDF UPLOAD       USER QUESTION
          |                 |
          v                 v
    TEXT EXTRACTION    QUERY EMBEDDING
          |                 |
          v                 v
   TABLE DETECTION      FAISS SEARCH
          |                 |
          v                 v
     TEXT CHUNKING    RELEVANT CHUNKS
          |
          v
   GEMINI EMBEDDINGS
          |
          v
    FAISS VECTOR STORE
          |
          +-----------------+
                            |
                            v
                   DOCUMENT CONTEXT
                            |
                            v
                  GEMINI GENERATION
                            |
                            v
                  ANSWER + CITATIONS
                            |
                            v
                   STREAMLIT UI
```

## Project Structure

```text
AI-Document-Assistant/
|
|-- app/
|   |-- main.py
|   |
|   |-- services/
|   |   |-- document_service.py
|   |   |-- embedding_service.py
|   |   |-- pdf_processor.py
|   |   |-- qa_service.py
|   |   |-- text_chunker.py
|   |   |-- vector_store.py
|   |
|   |-- utils/
|
|-- tests/
|   |-- test_backend_and_frontend.py
|   |-- test_pdf_processor.py
|   |-- test_text_chunker.py
|   |-- test_validation.py
|   |-- test_vector_store.py
|
|-- uploads/
|-- vectorstore/
|-- .streamlit/
|
|-- frontend.py
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- .dockerignore
|-- .gitignore
|-- README.md
```

## Installation and Setup

### Prerequisites

- Python 3.12
- Git
- Google Gemini API key
- Internet connection for Gemini API requests

### 1. Clone the Repository

```bash
git clone https://github.com/THOUSIFAHMEDR/AI-Document-Assistant.git
cd AI-Document-Assistant
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Obtain an API key from [Google AI Studio](https://aistudio.google.com/).

**Security:** Never commit your `.env` file or expose your API key publicly.

## Running the Application

The application runs using two separate services: FastAPI for the backend and Streamlit for the frontend.

### 1. Start the Backend

Open the first terminal, activate the virtual environment, and execute:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend URL:

http://127.0.0.1:8000

FastAPI Swagger documentation:

http://127.0.0.1:8000/docs

### 2. Start the Frontend

Open a second terminal, activate the same virtual environment, and execute:

```powershell
python -m streamlit run frontend.py
```

Frontend URL:

http://localhost:8501

### 3. Using the Application

1. Open the Streamlit dashboard.
2. Upload a PDF document.
3. Wait for document processing to complete.
4. Open the uploaded document.
5. Enter a question related to the document.
6. View the AI-generated answer.
7. Expand the Sources section to inspect retrieved document excerpts and page references.

## API Endpoints

The backend provides the following REST API endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/upload` | Upload and process a PDF document |
| POST | `/ask` | Ask questions about an uploaded document |
| GET | `/documents` | Retrieve uploaded document information |
| GET | `/documents/{document_id}/pdf` | Access the original PDF |

For detailed request parameters and response formats, open the FastAPI Swagger documentation:

http://127.0.0.1:8000/docs

## Data Storage

The application uses local file-based persistence.

| Directory | Purpose |
|---|---|
| `uploads/` | Stores original uploaded PDF documents |
| `vectorstore/` | Stores FAISS vector indexes and document metadata |

Each processed document has its own vector-store directory containing its index and associated metadata.

Uploaded PDFs and generated vector data are excluded from Git using `.gitignore`.

## Testing

The project uses **pytest** for automated testing.

Run the complete test suite:

```powershell
python -m pytest -v
```

### Test Coverage

The current automated test suite contains six tests:

| Test | Description |
|---|---|
| Full RAG Pipeline | Tests the document question-answering workflow |
| PDF Extraction | Verifies PDF text extraction |
| Merged Table Mapping | Tests student-to-guide mapping in vertically merged PDF table cells |
| Text Chunking | Verifies text chunk creation and overlap |
| Backend Validation | Tests backend input validation |
| FAISS Vector Store | Tests embedding storage and similarity search |

**Latest local test result: 6 passed.**

## Docker Setup

Docker configuration is included in the repository.

To run the application using Docker:

1. Install Docker Desktop.
2. Start the Docker engine.
3. Configure the `.env` file with your Gemini API key.
4. Execute:

```bash
docker compose up --build
```

Expected service addresses:

- Frontend: http://localhost:8501
- Backend: http://localhost:8000

**Note:** Docker build and container runtime verification are pending. The application has been tested using a local Python virtual environment.

## Security Considerations

- Store API keys in environment variables.
- Never commit `.env` files.
- Keep uploaded documents and generated vector indexes out of public repositories.
- Avoid exposing private credentials in source code.
- Validate uploaded documents before processing.

## Limitations

- The application currently processes text-based PDFs; scanned documents without an OCR-readable text layer are not supported.
- Answer quality depends on PDF extraction, chunking, embedding quality, and retrieval relevance.
- Structured table relationship extraction depends on successful table detection and the expected table headers.
- Gemini API access requires a valid API key and internet connectivity.
- Document files and vector indexes are stored locally rather than in a cloud database.

## Future Enhancements

- Add OCR support for scanned PDF documents.
- Improve retrieval using hybrid search and reranking.
- Support additional document formats such as DOCX and TXT.
- Add user authentication and document-level access control.
- Introduce cloud-based document storage.
- Improve table extraction for more complex PDF layouts.
- Add conversation history and multi-document question answering.

## Project Status

The core AI Document Assistant functionality has been implemented.

Completed components:

- PDF upload and text extraction.
- Structured PDF table extraction for supported merged-cell layouts.
- Text chunking and semantic embedding generation.
- FAISS-based vector storage and similarity retrieval.
- Gemini-powered question answering.
- Source references and page citations.
- FastAPI backend and Streamlit frontend.
- Local document persistence.
- Automated test suite with six passing tests.
- GitHub version control and project documentation.

Docker configuration is available, with container execution still pending verification.

## Repository

**GitHub Repository:**

https://github.com/THOUSIFAHMEDR/AI-Document-Assistant

---

**AI Document Assistant**

*Built using Python, FastAPI, Streamlit, Google Gemini, PyMuPDF and FAISS.*