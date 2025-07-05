# 🔬 Multi-Domain Research Agent

## 🚀 **100% Free & Open-Source Research Agent**

A sophisticated, production-ready research agent that can perform comprehensive research across multiple domains using **100% free and open-source tools**. Built with modern Python frameworks and advanced AI orchestration.

### ✨ **Key Features**

- 🧠 **Hybrid AI Architecture**: Local Ollama models (primary) + optional Gemini API (secondary)
- 🔍 **Multi-Domain Research**: Academic papers, web search, social media, government data, and more
- 🏗️ **Professional Architecture**: FastAPI, PostgreSQL, Redis, LangChain, and LangGraph
- 🎯 **Advanced Workflows**: Parallel processing, source validation, and confidence scoring
- 🖥️ **Multiple Interfaces**: CLI, Web UI (Streamlit), and REST API
- 📊 **Comprehensive Analytics**: Research history, source tracking, and performance metrics
- 🔒 **Security First**: Rate limiting, authentication, and secure API handling
- 🚀 **Production Ready**: Docker deployment, monitoring, and scalability

### 🌟 **What Makes This Special**

- **Completely Free**: No paid subscriptions required for core functionality
- **Local-First**: Primary processing using Ollama (works offline)
- **Professional Grade**: Enterprise-level architecture and code quality
- **Extensible**: Easy to add new research sources and capabilities
- **Well-Documented**: Comprehensive guides and API documentation

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Streamlit   │ │ FastAPI     │ │ CLI Client  │          │
│  │ Web UI      │ │ REST API    │ │ Interface   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Research Orchestration                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ LangChain   │ │ LangGraph   │ │ Query       │          │
│  │ Agents      │ │ Workflows   │ │ Planner     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Tool Integration                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Academic    │ │ Web Search  │ │ Social      │          │
│  │ Sources     │ │ Tools       │ │ Media       │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ **Tech Stack**

### **Core Framework**
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Advanced ORM with async support
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **ChromaDB**: Vector database for embeddings

### **AI & ML**
- **Ollama**: Local LLM processing (primary)
- **LangChain**: AI orchestration framework
- **LangGraph**: Advanced AI workflows
- **Google Gemini**: Cloud LLM (optional enhancement)

### **User Interfaces**
- **Streamlit**: Modern web interface
- **Typer**: Rich CLI framework
- **Rich**: Beautiful terminal output

### **Development**
- **Poetry**: Dependency management
- **pytest**: Testing framework
- **Black & Ruff**: Code formatting and linting
- **pre-commit**: Git hooks for code quality

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Poetry
- Ollama
- PostgreSQL
- Redis

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd multi-domain-research-agent
cp .env.example .env
```

### **2. Install Dependencies**
```bash
poetry install
poetry shell
```

### **3. Setup Database**
```bash
# Start PostgreSQL and Redis (adjust commands for your system)
# PostgreSQL: brew services start postgresql
# Redis: brew services start redis

# Run database migrations
alembic upgrade head
```

### **4. Start Ollama and Download Models**
```bash
# Start Ollama service
ollama serve

# Download recommended models (in another terminal)
ollama pull llama3:8b
ollama pull mistral:7b
ollama pull deepseek-r1:1.5b
```

### **5. Run the Application**

#### **Start the API Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### **Start the Web UI**
```bash
streamlit run web_ui/streamlit_app.py
```

#### **Use the CLI**
```bash
research-agent --help
research-agent research "Your research query here"
```

## 🔧 **Configuration**

### **Environment Variables**
Copy `.env.example` to `.env` and configure:

- **Database**: PostgreSQL connection string
- **Redis**: Redis connection URL
- **Ollama**: Base URL and model settings
- **APIs**: Free tier API keys (optional)
- **Logging**: Log level and file settings

### **LLM Configuration**
- **Budget Mode**: Set `LLM_BUDGET_MODE=true` for 100% local processing
- **Hybrid Mode**: Set `LLM_BUDGET_MODE=false` to use cloud LLM for complex queries
- **Model Selection**: Configure primary and fallback models

## 📖 **Usage Examples**

### **CLI Usage**
```bash
# Simple research query
research-agent research "What are the latest developments in quantum computing?"

# Complex multi-domain query
research-agent research "Research vertical farming, compare costs with traditional farming, and identify top companies with recent funding"

# Export results
research-agent research "Climate change impact on agriculture" --export json --output results.json
```

### **API Usage**
```bash
# Start a research session
curl -X POST "http://localhost:8000/research/start" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your research query here"}'

# Get research results
curl "http://localhost:8000/research/results/{session_id}"
```

### **Web UI Usage**
1. Navigate to `http://localhost:8501`
2. Enter your research query
3. Watch real-time progress
4. Explore sources and results
5. Export or share findings

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only
```

## 🚀 **Deployment**

### **Docker Deployment**
```bash
# Build the image
docker build -t research-agent .

# Run with docker-compose
docker-compose up -d
```

### **Production Deployment**
- Use PostgreSQL with proper backups
- Configure Redis for session persistence
- Set up reverse proxy (nginx)
- Enable SSL/TLS certificates
- Configure monitoring and logging

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### **Development Setup**
```bash
# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
ruff check . --fix

# Run type checking
mypy app/
```

## 📊 **Performance**

### **Local Processing (Ollama)**
- **Query Analysis**: ~2-5 seconds
- **Source Search**: ~10-30 seconds (parallel)
- **Synthesis**: ~5-15 seconds
- **Total**: ~20-50 seconds per query

### **Hybrid Processing**
- **Complex Queries**: Route to Gemini for better results
- **Simple Queries**: Keep local for speed and privacy
- **Fallback**: Always available to local processing

## 🔒 **Security**

- **API Rate Limiting**: Prevents abuse
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Configurable origins
- **Environment Variables**: Secure configuration management

## 📚 **Documentation**

- **API Documentation**: Auto-generated with FastAPI
- **Architecture Guide**: Detailed system design
- **Development Guide**: Setup and contribution instructions
- **User Guide**: How to use all features

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check OLLAMA_BASE_URL in .env file

2. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Run migrations: `alembic upgrade head`

3. **Redis Connection Error**
   - Ensure Redis is running
   - Check REDIS_URL in .env file

4. **API Rate Limits**
   - Check free tier limits for external APIs
   - Configure rate limiting in .env file

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Ollama**: For providing excellent local LLM capabilities
- **LangChain**: For the powerful AI orchestration framework
- **FastAPI**: For the modern web framework
- **Streamlit**: For the beautiful web interface
- **All contributors**: Thank you for making this project better!

---

**Built with ❤️ for the open-source community**

[![GitHub stars](https://img.shields.io/github/stars/username/multi-domain-research-agent?style=social)](https://github.com/username/multi-domain-research-agent)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 