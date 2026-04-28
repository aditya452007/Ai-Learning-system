In 2025, developing agents to tackle virtually any challenge has captivated the tech world, becoming a revolutionary force in innovation. Sometimes it makes you wonder will Agents solve world peace and end all conflicts. That discussion is for another day.

I want to create a roadmap for setting up a agentic RAG system at a company that has documents. Users need to search and ask questions about the document. Typically I would talk to MLOps , Engineering, Search and ML teams to create such a roadmap. What if these teams don’t exist or they are not available. Let me see if Claude can help.

At first I need an architecture diagram. The first prompt I used is:
“Create an architecture diagram for reflective agentic RAG system description. List out the components, flow of information and the connection between components. Express it as an html with components drawn out. Use this as reference. https://www.galileo.ai/blog/mastering-rag-how-to-architect-an-enterprise-rag-system”

This was the response.

Key features of this architecture:

Self-reflection loop in retrieval stage for query refinement

Continuous learning system for optimization

Multi-stage validation with relevance scoring

Separate query understanding and processing pipeline

Need any specific component details?

There is an HTML architecture diagram alongside. I wanted to see if its possible to add more connections. So I added the prompt.
“Please show the connections between all the components”

Here is the response.

Key connections added:

Data flow between stages with relevant metadata

Feedback loops for system optimization

Cross-component dependencies

Quality control checkpoints

Performance monitoring touchpoints

At this point I was reasonably satisfied. Here is the html rendering for the architecture diagram.

Press enter or click to view image in full size

You can click on the code to get the html code. Not bad for the fact that I just typed up a few words to get it. Now if I created it would have connections and loops but this conveys what I need.

Let me ask a few more clarifying questions.
“Are there frameworks/models/APIs that should be used for embedding generation?”

For embedding generation in RAG systems, here are the most effective options:

Text Embeddings:

OpenAI’s text-embedding-3-small and text-embedding-3-large

Cohere Embed models

Hugging Face’s Sentence Transformers like all-MiniLM-L6-v2

BGE embeddings (particularly strong for multilingual)

Framework/APIs:

LangChain’s embeddings interface for standardized integration

LlamaIndex’s embedding modules

Chroma’s direct embedding support

Weaviate’s vectorization modules

Recommendation:

Start with OpenAI’s embedding-3-small for quality/cost balance

Use Sentence Transformers if you need open-source/self-hosted solution

Consider BGE for multilingual requirements

Key metrics to evaluate: dimensionality, semantic similarity accuracy, inference speed, and cost per token.

Next question: “For the retrieval system should we only use “Semantic Search” or is there a role for string match with BM25?”

A hybrid approach combining both semantic search and BM25 is optimal:

BM25 advantages:

Better exact match detection

Handles keywords/technical terms well

Computationally efficient

Works well with domain-specific terminology

Semantic Search advantages:

Understands context and meaning

Handles paraphrasing/synonyms

Better with natural language queries

Captures conceptual relationships

Implementation approach:

Run both retrievers in parallel

Use reciprocal rank fusion to combine results

Weight between methods based on query type

Use LangChain’s HyrbidRetriever or implement custom ensemble

This hybrid approach typically outperforms either method alone, especially for technical/enterprise applications.

Next Question: “What is the overhead in terms of hosting, code development, testing to add B25 to a system that is optimized for vector search?”

Infrastructure overhead:

Storage: BM25 index ~20–30% of original text size

Memory: Moderate RAM for index, less than vector DB

Compute: Minimal CPU impact vs vector operations

Development effort:

Integration: 2–3 days using Elasticsearch/OpenSearch

Testing: 1–2 days for relevance testing

Tuning: 2–3 days optimizing BM25 parameters

Fusion logic: 1–2 days implementing rank fusion

Maintenance:

Regular index updates alongside vector DB

Monitoring two retrieval systems

Tuning both systems separately

Total estimated overhead: 1–2 weeks development + ~30% increased infrastructure costs

Key consideration: Benefits often outweigh costs for technical/enterprise content where exact matching is crucial.

Next Question: “Would you suggest taking an iterative approach? ie creating one search system first and then adding the second one? If so for RAG pipeline is it advisable to do vector database before Elastic Search?”

Yes, iterative approach is recommended. Start with vector search because:

Vector DB advantages for initial deployment:

Better handles natural language queries

Easier integration with LLMs

Simpler relevance tuning

Clear optimization metrics

Add Elasticsearch later when:

System is stable

Clear use cases for exact matching emerge

Performance metrics show semantic gaps

Resources available for tuning both systems

This staging reduces initial complexity while maintaining option to add BM25 when needed.

Next Question: What type of compute would be necessary to host a vector store? What are your recommendations for Vector Store Platforms?

Vector Store Recommendations:

Weaviate: Self-hosted, high performance, good for production

Milvus: Distributed architecture, handles billions of vectors

Qdrant: Strong security, good for enterprise

Chroma: Simple setup, great for prototyping

FAISS: In-memory, fast but needs custom deployment

Compute Requirements:

Storage: 1KB-4KB per vector

RAM: 16GB minimum, 32GB+ recommended

CPU: 4+ cores for basic setup

GPU: Optional, speeds up similarity search

Scaling considerations:

1M vectors ≈ 4GB storage

Additional 8GB RAM per 1M vectors for performance

SSD storage strongly recommended

Consider managed solutions (Pinecone, Weaviate Cloud) to avoid infrastructure management

Next Question: What is the tooling for query processing?

Key query processing tools:

Understanding & Analysis:

LangChain Query Transformers

Haystack’s Query Pipeline

OpenAI’s Function Calling API

Llama Index’s Query Engine

Query Rewrites:

OpenAI Completions API

Query Expansion with Word2Vec/BERT

HyDE (Hypothetical Document Embeddings)

Preprocessing:

SpaCy for NER/parsing

NLTK for tokenization

Regex for pattern matching

Presidio for PII detection

Core recommendation: Start with LangChain’s Query Pipeline + OpenAI for rewrites, add complexity as needed.

Next Question:

For a standard RAG system, you typically don’t need to build in-house models initially. Here’s the breakdown:

Core Components — Use Existing:

Embeddings: Use OpenAI/Cohere APIs

Query Understanding: LangChain/Haystack

Vector Search: Weaviate/Qdrant

LLM: OpenAI/Anthropic APIs

Consider Custom Models For:

Domain-specific terminology

Specialized data formats

High security requirements

Cost optimization at scale

When to Build In-house:

Scale triggers:

$100k/month API costs

1M queries/day

Strict latency requirements

Domain triggers:

Highly specialized industry terms

Custom data formats

Regulatory requirements

Start with frameworks, then evaluate ROI for custom components after gathering usage data and performance metrics.

The main investment should be in:

Prompt engineering

System architecture

Integration logic

Monitoring/evaluation

Rather than model building initially.

Next Question: Given this requirement, what should be the composition (number of team members and their qualifications) of a team that needs to set up this RAG pipeline

Here’s a recommended team composition for setting up and maintaining a RAG pipeline:

Core Team (Minimum 4–5 members):

ML/LLM Engineer (1–2)

Strong Python, PyTorch/TensorFlow

Experience with embedding models

Understanding of LLM architectures

Vector DB expertise Responsibilities: Architecture, model integration, vector store setup

Backend Engineer (1)

Strong API design experience

Distributed systems knowledge

Performance optimization skills

Infrastructure/DevOps experience Responsibilities: API development, infrastructure, scaling

Data Engineer (1)

ETL pipeline experience

Data preprocessing expertise

Knowledge of text processing

Database management skills Responsibilities: Data ingestion, preprocessing, chunking

ML Ops Engineer (1)

Monitoring/observability expertise

CI/CD pipeline experience

Performance optimization skills

Cost optimization experience Responsibilities: Deployment, monitoring, maintenance

Optional Additional Roles (Based on scale):

Search Engineer (1)

Elasticsearch/Opensearch expertise

Information retrieval background

Query optimization experience Responsibilities: BM25 integration, hybrid search

Product Manager (1)

Technical background

Understanding of LLMs/RAG

Strong prioritization skills Responsibilities: Requirements, roadmap, stakeholder management

Domain Expert/Content Manager (1)

Subject matter expertise

Content organization skills

Quality assessment ability Responsibilities: Content strategy, evaluation

Key considerations:

Start with core team of 4–5

Scale team based on data volume/complexity

Cross-functional skills are valuable

Consider consultants for specialized needs (security, compliance)

Next Question: With the core team , assuming (1) all permissions to set up new machines and access to high compute is granted and (2) LLMs/co-pilots are available for code assist how long should it take to set up a (1) POC for RAG (2) a production system for RAG

Become a Medium member
Here’s a realistic timeline breakdown:

POC Timeline (4–6 weeks): Week 1–2:

Initial architecture setup

Basic vector store deployment

Simple data pipeline creation

Query processing setup

Week 3–4:

Basic retrieval implementation

Initial prompts/LLM integration

Simple evaluation metrics

Demo interface

Week 5–6 (Optional):

Basic monitoring

Initial performance tuning

Documentation

Stakeholder demos

Production Timeline (3–4 months): Month 1:

Production architecture design

Scalable data pipeline

Security implementation

Infrastructure setup

Month 2:

Robust retrieval system

Monitoring/logging

Error handling

Performance optimization

Month 3:

Testing (load/integration)

Documentation

CI/CD pipeline

User acceptance testing

Month 4 (Optional):

Production deployment

Performance tuning

Knowledge transfer

Maintenance procedures

Key Assumptions:

Team is familiar with RAG concepts

Data is relatively clean/structured

No major compliance requirements

Standard use cases (no extreme customization)

Timeline Accelerators:

Using managed services

Leveraging existing infrastructure

Clear requirements

Good data quality

Based on the recommendations from Claude a agentic RAG POC can be done in 4–6 weeks. Of course assuming clean structured data is too much but a team might be able to clean a small data in 2 weeks.

Another important part of a successful POC is having clear requirements. Clear requirements require a clear evaluation framework of the requirements. In future blogs I will explore evaluation frameworks required to ensure success of a agentic RAG system.