# AI Document Assistant

An AI-powered PDF document assistant that allows users to upload PDF files, ask questions about their content, and receive context-aware answers with relevant source references and page citations.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents before generating answers using Google's Gemini API.

## Features

- **PDF Upload:** Upload and process PDF documents.
- **Text Extraction:** Extract text and page information using PyMuPDF.
- **Text Chunking:** Divide extracted text into smaller overlapping chunks.
- **Semantic Embeddings:** Generate document embeddings using Gemini.
- **Vector Search:** Retrieve relevant content using FAISS.
- **AI Question Answering:** Generate answers using Gemini based on retrieved document context.
- **Source References:** Display relevant excerpts and page references.
- **Persistent Storage:** Store uploaded PDFs, vector indexes and metadata locally.
- **Document Management:** View previously uploaded documents.
- **Interactive Interface:** Use a Streamlit dashboard with a PDF viewer and AI chat workspace.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Model | Google Gemini |
| Embeddings | gemini-embedding-001 |
| Answer Generation | gemini-3.5-flash-lite |
| Vector Database | FAISS |
| PDF Processing | PyMuPDF |
| API Communication | Requests |
| Containerization | Docker |
| Version Control | Git and GitHub |

## System Architecture

```text
              User
               |
               v
       Streamlit Frontend
               |
               v
          FastAPI Backend
               |
       PDF Upload / Questions
               |
               v
        PDF Text Extraction
               |
               v
          Text Chunking
               |
               v
        Gemini Embeddings
               |
               v
          FAISS Vector Store
               |
       Semantic Retrieval
               |
               v
       Relevant Document Context
               |
               v
       Gemini Answer Generation
               |
               v
       Answer + Source References
               |
               v
         Streamlit Interface
```

## Project Structure

```text
AI-Document-Assistant/
│
├── app/
│   ├── main.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── pdf_processor.py
│   │   ├── qa_service.py
│   │   ├── text_chunker.py
│   │   └── vector_store.py
│   └── utils/
│
├── tests/
│   ├── test_backend_and_frontend.py
│   ├── test_pdf_processor.py
│   ├── test_text_chunker.py
│   ├── test_validation.py
│   └── test_vector_store.py
│
├── uploads/
├── vectorstore/
├── .streamlit/
├── frontend.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/THOUSIFAHMEDR/AI-Document-Assistant.git
cd AI-Document-Assistant
```

### 2. Create a Virtual Environment

Using Python:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Obtain your API key from [Google AI Studio](https://aistudio.google.com/).

Never commit your `.env` file or expose your API key.

## Running the Application

The application uses two services.

### 1. Start the Backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 2. Start the Frontend

Open another terminal:

```bash
streamlit run frontend.py --server.port 8501
```

Frontend URL:

`http://localhost:8501`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/upload` | Upload and process a PDF |
| POST | `/ask` | Ask questions about documents |
| GET | `/documents` | Retrieve uploaded document information |
| GET | `/documents/{document_id}/pdf` | Access the original PDF |

For request and response details, use the FastAPI Swagger documentation at `/docs`.

## Data Storage

The application maintains document data locally.

- `uploads/` stores original PDF files.
- `vectorstore/` stores FAISS indexes and document metadata.
- Each document has its own storage directory and index.

These directories are excluded from Git to avoid uploading private documents and generated data.

## Running Tests

Run the automated test suite:

```bash
python -m pytest tests/ -v
```

The current local test suite contains five tests covering the RAG pipeline, PDF extraction, text chunking, backend validation and vector storage.

## Docker Setup

Docker configuration is included in the repository.

After Docker Desktop is installed and running, configure the `.env` file with your Gemini API key and execute:

```bash
docker compose up --build
```

Expected service addresses:

- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`

**Note:** Docker image building and container execution are pending verification.

## Security Notes

- Store API keys in environment variables.
- Do not commit `.env` files.
- Keep uploaded documents and vector indexes out of public repositories.
- Do not expose private API credentials in source code.

## Project Status

Core PDF processing, RAG functionality, semantic retrieval, AI question answering, document persistence and frontend implementation are completed.

The current local automated test suite passes all five tests.

Docker configuration has been prepared; container build and runtime verification remain pending.

## Repository

[GitHub – AI Document Assistant](https://github.com/THOUSIFAHMEDR/AI-Document-Assistant)

---

**AI Document Assistant** — Built with Python, FastAPI, Streamlit, Gemini and FAISS.