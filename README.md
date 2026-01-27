## NU-Faculty-Expertise-RAG
An intelligent academic search system based on RAG (Retrieval-Augmented Generation) architecture, designed to retrieve and analyze the research backgrounds of professors at Northwestern University's McCormick School of Engineering.

## 🌟 Key Highlights
Heterogeneous Data Acquisition: Developed a custom Scrapy crawler to navigate Northwestern’s faculty directories, extracting structured data from complex HTML structures.

Multi-Dimensional Vector Search: Built on Qdrant, utilizing a Metadata-Injected Embedding strategy to link unstructured research descriptions with structured faculty profiles (Name, Dept, Contact, Lab).

Precision Optimization via Multi-Query: Implemented a Multi-Query Retrieval mechanism. It uses an LLM to expand user queries into multiple semantic variations, overcoming the "cold start" problem for technical acronyms (e.g., RAG, HCI) in standard vector similarity searches.

## 🛠️ Tech Stack
LLM Framework: LangChain

Models: OpenAI GPT-3.5-Turbo

Vector Database: Qdrant

Crawler: Scrapy

## 📂 Project Structure

```text
.
├── crawl_NU/              # Scrapy project for data collection
│   ├── spiders/           # Parsing logic for faculty pages
│   └── items.py           # Data models for scraped content
├── notebooks/
│   └── rag_pipeline.ipynb # Core RAG logic & Multi-Query implementation
├── .env.example           # Template for environment variables (copy to .env)
├── .gitignore             # Git ignore file (excludes .env, .venv, etc.)
├── scrapy.cfg             # Scrapy configuration file
└── requirements.txt       # Project dependencies

🚀 Quick Start
1. Clone the Repository
Bash
git clone https://github.com/JohnHuo-coder/NU-Faculty-Expertise-RAG.git
cd NU-Faculty-Expertise-RAG
2. Setup Environment
Create and activate a virtual environment:

Bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

3. Configure Credentials
Create a .env file in the root directory:

Plaintext
OPENAI_API_KEY=your_openai_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true

4. Run the Pipeline
Crawl Data: cd crawl_NU && scrapy crawl nu_professors

Start RAG: Open notebooks/rag_pipeline.ipynb and run all cells to start the interactive search.
