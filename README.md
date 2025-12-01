# Question Generator API

AI-powered question generation system with automated validation and regeneration.

<img width="579" height="708" alt="Question Generator Workflow" src="https://github.com/user-attachments/assets/99fee51f-0bba-4b9a-91c3-2ae0af556da3" />

## Tech Stack

- **FastAPI** - Web framework
- **MongoDB** - Database
- **ChromaDB** - Vector database
- **LangChain** - LLM orchestration
- **LangGraph** - Workflow management
- **Langfuse** - LLM monitoring

## Setup

### Environment Variables

Create `.env` file:

```bash
MONGO_URI=your_mongodb_connection_string
MONGO_DB=question_generator
OPENAI_API_KEY=your_openrouter_api_key
CHROMA_API_KEY=your_chroma_key
CHROMA_TENANT=your_chroma_tenant
CHROMA_DATABASE=your_chroma_database
```

### Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# Stop
docker-compose down
```

### Local Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run server
./run.sh
```

API available at http://localhost:8000/docs
