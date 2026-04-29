# 🛠️ Technological Stack & Features

This document provides a comprehensive overview of the technologies powering the **MultiRAG Learning System** and the key features it offers to users.

---

## 🏗️ Technological Stack

The system is built with a modern, high-performance architecture that separates concern between a robust Python-based AI backend and a highly responsive Vanilla JS frontend.

### 🔹 Backend (The Brain)
*   **Core Engine:** [Python 3.10+](https://www.python.org/)
*   **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) - Utilized for its high performance, asynchronous capabilities, and automatic OpenAPI documentation.
*   **Production Server:** [Uvicorn](https://www.uvicorn.org/) - An ASGI web server implementation for Python.
*   **AI/ML Orchestration:** 
    *   [LangChain](https://www.langchain.com/) - Used for document loading, text splitting, and managing complex RAG chains.
    *   [Google Gemini API](https://ai.google.dev/) - Primary LLM provider for grounded generation.
    *   [NVIDIA AI Foundation Models](https://www.nvidia.com/en-us/ai-data-science/foundation-models/) - Integrated for high-performance inference.
*   **Retrieval & Search:**
    *   [Sentence-Transformers](https://www.sbert.net/) - Generates local semantic embeddings.
    *   [FAISS](https://github.com/facebookresearch/faiss) / [ChromaDB](https://www.trychroma.com/) - High-performance vector stores for semantic search.
    *   **BM25:** Traditional keyword-based retrieval for exact match accuracy.
*   **Data Processing:**
    *   [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) - For high-fidelity PDF text and metadata extraction.
    *   [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Requests](https://requests.readthedocs.io/) - For scraping and parsing web content.

### 🔹 Frontend (The Interface)
*   **Core:** [HTML5](https://developer.mozilla.org/en-US/docs/Web/HTML) & [Vanilla JavaScript (ES6+)](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Zero-dependency core logic for maximum speed and control.
*   **Styling:** [Vanilla CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS) - Custom design system with glassmorphism, responsive layouts, and a premium "dark-mode" aesthetic.
*   **Animations:** [GSAP (GreenSock Animation Platform)](https://greensock.com/gsap/) - Powering smooth transitions and micro-interactions.
*   **Icons:** SVG Sprites for crisp, scalable iconography.

---

## 🚀 Key Features

The MultiRAG system is designed to transform static documents into dynamic, interactive learning environments.

### 1. Multi-Source Ingestion
*   **File Support:** Import PDFs, Markdown (`.md`), Plain Text (`.txt`), and various code files (`.py`, `.js`, `.ts`, etc.).
*   **Live Web Sync:** Provide any URL, and the system will scrape and index the content in seconds.
*   **Drag-and-Drop:** Intuitive file uploading directly into the workspace.

### 2. Hybrid Retrieval Architecture
*   **Semantic Search:** Finds information based on meaning and context, even if keywords don't match.
*   **Keyword Search:** Ensures precise retrieval for specific terms, names, or codes.
*   **Graph-Based Discovery:** Uses a Knowledge Graph to identify relationships between concepts across different sources.
*   **Reciprocal Rank Fusion (RRF):** Intelligently merges results from all search modes for the most relevant context.

### 3. Grounded Chat Interface
*   **Evidence-Based Answers:** Every response generated is grounded in your uploaded sources.
*   **Interactive Citations:** Click on citations to see the exact text "chunks" used to generate the answer.
*   **Source Cards:** Visual cards in the sidebar showing the origin of retrieved information.

### 4. Knowledge Graph Explorer
*   **Spatial Mapping:** Visualize your learning material as a concept map.
*   **Relationship Discovery:** See how ideas are linked across multiple documents.
*   **Interactive Navigation:** Click graph nodes to jump to related sections or ask specific questions.

### 5. Advanced Workspace Management
*   **Isolation:** Each workspace maintains its own isolated index, cache, and metadata.
*   **Real-time Diagnostics:** Monitor backend health, source counts, and indexing progress through the UI.
*   **Model Control:** Switch between different LLM providers (Gemini, NVIDIA) and fine-tune parameters like `Top P`, `Top K`, and `Temperature`.

---

## 🛠️ Development & Testing
*   **Modular Architecture:** Easy to swap LLMs, embedding models, or vector databases.
*   **Testing Suite:** Robust backend testing using `pytest` and `httpx`.
*   **Environment Driven:** Configuration managed via `.env` for secure API key handling.
