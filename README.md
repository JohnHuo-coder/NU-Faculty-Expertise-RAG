## NU-Faculty-Expertise-RAG
An intelligent academic search system based on RAG (Retrieval-Augmented Generation) architecture, designed to retrieve and analyze the research backgrounds of professors at Northwestern University's McCormick School of Engineering.

## Key Highlights
Heterogeneous Data Acquisition: Developed a custom Scrapy crawler to navigate Northwestern’s faculty directories, extracting structured data from complex HTML structures.

Multi-Dimensional Vector Search: Built on Qdrant, utilizing a Metadata-Injected Embedding strategy to link unstructured research descriptions with structured faculty profiles (Name, Dept, Contact, Lab).

Precision Optimization via Multi-Query: Implemented a Multi-Query Retrieval mechanism. It uses an LLM to expand user queries into multiple semantic variations, overcoming the "cold start" problem for technical acronyms (e.g., RAG, HCI) in standard vector similarity searches.

## Tech Stack
LLM Framework: LangChain

Models: OpenAI GPT-3.5-Turbo

Vector Database: Qdrant

Crawler: Scrapy

## Project Structure

```text
.
├── crawl_NU/                      # Scrapy project for data collection
|   ├── crawl_NU/                  # Parsing logic for faculty pages
│       ├── spiders/               # Parsing logic for faculty pages
│       └── items.py               # Data models for scraped content
│   ├── labs_info.json             # 
│   └── professors_info.json       # 
|
├── process_documents/             # Document preprocessing layer
│   ├── prepare_labs_info.py       # Format & clean lab data
│   └── prepare_professors_info.py # Format & clean professor data
│
├── rag_engine/                    # Core RAG engine (modularized)
│   ├── __init__.py                # Package initializer
│   ├── vectorstore.py             # Qdrant vector store setup
│   ├── retriever.py               # Retriever builder (metadata filtering)
│   ├── schemas.py                 # Pydantic structured output models
│   ├── prompts.py                 # Prompt templates & routing prompts
│   ├── chains.py                  # RAG chain assembly
│   └── utils.py                   # Utility functions (formatting, helpers)
│
├── .env                           # Environment variables (excluded from git)
└── pipeline.ipynb                 # Place to input question and see results
```

#### Start RAG: Open pipeline.ipynb and run the cell to start the interactive search.
