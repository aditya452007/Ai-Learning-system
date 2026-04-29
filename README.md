# MultiRAG Learning System

MultiRAG is a source-grounded AI learning workspace inspired by NotebookLM. It allows users to import various knowledge sources (PDFs, Markdown, Text, URLs), index them using a hybrid retrieval architecture, and interact with the content through a grounded chat interface and a conceptual graph explorer.

## 🌟 Features

- **Multi-Source Ingestion:** Supports PDF, Markdown, Text, and Live URLs.
- **Hybrid Retrieval:** Combines Semantic Search (Vector), Keyword Search (BM25), and Graph-based retrieval for maximum accuracy.
- **Grounded Answers:** Generates responses with clear citations and source cards to eliminate hallucinations.
- **Knowledge Graph:** Visualizes relationships between concepts, allowing users to explore their material spatially.
- **Workspace Isolation:** Maintains separate indexes, caches, and metadata per workspace.
- **Provider Agnostic:** Modular architecture allowing easy replacement of LLMs, Embedding models, and Vector stores.

## 🛠️ Technical Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI/ML:** Google Gemini (LLM), Sentence-Transformers (Embeddings), FAISS (Vector Store)
- **Retrieval:** Hybrid RRF (Reciprocal Rank Fusion), BM25
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, GSAP (Animations)

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Installation & Setup
1. Clone the repository.
2. Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn python-multipart langchain-google-genai langchain-community langchain-text-splitters langchain-core sentence-transformers faiss-cpu pymupdf requests beautifulsoup4 numpy torch python-dotenv
   ```

### 3. Running the System
**Start the Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

**Launch the Frontend:**
Open the `index.html` file (located in the project root or the specified frontend folder) directly in your web browser.

### 4. Testing
To run the backend test suite:
```powershell
cd backend
python -m pytest
```

## 📂 Project Structure
- `backend/`: Core logic, API routes, and RAG pipeline.
- `docs/`: Detailed engineering specifications and architecture blueprints.
- `scripts/`: Utility scripts for seeding demo workspaces.
- `MultRAG System/`: Legacy prototype files.

## 📜 License
MIT License
