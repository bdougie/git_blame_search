# Semantic Git Blame Tool - 10 Minute Quick Start

## Installation with uv (1 minute!)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project and install dependencies
uv init git-blame-search
cd git-blame-search

# Add dependencies to pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "git-blame-search"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "lancedb>=0.5.0",
    "sentence-transformers>=2.2.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "gitpython>=3.1.0",
    "flask>=3.0.0",
    "pyarrow>=14.0.0",
]

[tool.uv]
dev-dependencies = [
    "ipython>=8.0.0",
]
EOF

# Install everything with uv
uv sync

# Save the script as git_blame_tool.py
# Make it executable
chmod +x git_blame_tool.py
```

### Alternative: Quick one-liner setup
```bash
# Clone and setup in one command
uv init git-blame-search && cd git-blame-search && uv add lancedb sentence-transformers click rich gitpython flask pyarrow && uv sync
```

## Basic Usage (3 minutes)

### 1. Index your repository
```bash
# Index current repository (limit to recent 100 commits for demo)
uv run python git_blame_tool.py index --max-commits 100

# Or index a specific repository
uv run python git_blame_tool.py index --repo /path/to/repo --max-commits 500
```

### 2. Index specific files for blame analysis
```bash
# Index blame data for important files
uv run python git_blame_tool.py index-file main.py
uv run python git_blame_tool.py index-file src/core/auth.py
```

### 3. Search your git history
```bash
# Search commits by natural language
uv run python git_blame_tool.py search "authentication implementation"
uv run python git_blame_tool.py search "bug fix for memory leak"
uv run python git_blame_tool.py search "added error handling"

# Search with more results
uv run python git_blame_tool.py search "refactoring database layer" --limit 20
```

### 4. Semantic blame search
```bash
# Find who wrote specific functionality
uv run python git_blame_tool.py blame "error handling logic"
uv run python git_blame_tool.py blame "database connection" --file src/db.py
uv run python git_blame_tool.py blame "JWT validation"
```

### 5. Author attribution
```bash
# Find who implemented specific features
uv run python git_blame_tool.py who "authentication system"
uv run python git_blame_tool.py who "caching implementation"
uv run python git_blame_tool.py who "REST API endpoints"
```

## Continue Integration (2 minutes)

### 1. Start the HTTP server
```bash
uv run python git_blame_tool.py serve
# Server starts on http://localhost:5000
```

### 2. Configure Continue
Add to your `~/.continue/config.json`:

```json
{
  "contextProviders": [
    {
      "name": "http",
      "params": {
        "url": "http://localhost:5000/retrieve",
        "title": "Git Blame Search",
        "description": "Search git history and blame data"
      }
    }
  ]
}
```

### 3. Use in Continue
In VSCode with Continue:
- Type `@Git Blame Search` in the chat
- Ask questions like "who implemented the auth system?"
- Continue will search your indexed git data

## Example Queries (3 minutes)

### Finding Code Authors
```bash
# Who added security features?
uv run python git_blame_tool.py who "security vulnerability fix"

# Who worked on the API?
uv run python git_blame_tool.py who "REST API implementation"

# Who fixed performance issues?
uv run python git_blame_tool.py who "performance optimization"
```

### Understanding Code Evolution
```bash
# When was error handling added?
uv run python git_blame_tool.py search "added try-catch blocks"

# Find refactoring commits
uv run python git_blame_tool.py search "refactored to use async/await"

# Track feature development
uv run python git_blame_tool.py search "implemented user authentication"
```

### Blame Analysis
```bash
# Find who wrote specific error handling
uv run python git_blame_tool.py blame "catch (Exception e)"

# Track down validation logic authors
uv run python git_blame_tool.py blame "validate.*email" 

# Understand test coverage evolution
uv run python git_blame_tool.py blame "test_.*authentication" --file tests/
```

## Advanced Features

### Batch Processing Large Repos
```python
# For repositories with 10k+ commits, process in batches
import subprocess

# Get total commit count
total = int(subprocess.check_output(['git', 'rev-list', '--count', 'HEAD']).strip())

# Index in chunks
batch_size = 1000
for i in range(0, total, batch_size):
    subprocess.run(['uv', 'run', 'python', 'git_blame_tool.py', 'index', 
                    '--max-commits', str(batch_size), 
                    '--skip', str(i)])
```

### Custom Embeddings
Create a new script or modify the tool to use different embedding models:

```bash
# Add new embedding models with uv
uv add transformers torch

# Then modify the embedder initialization
```

```python
# For better code understanding
self.embedder = SentenceTransformer('microsoft/unixcoder-base')

# For faster processing
self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

# For multilingual repositories  
self.embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
```

### Performance Tuning
```python
# Create vector index for faster search (for 100k+ entries)
table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=96
)
```

## Example Output

### Commit Search
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Hash         ┃ Author     ┃ Date       ┃ Message                           ┃ Score  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ a1b2c3d4e5f6 │ John Doe   │ 2024-01-15 │ Add JWT authentication middleware │ 0.892  │
│ f6e5d4c3b2a1 │ Jane Smith │ 2024-01-10 │ Implement OAuth2 flow             │ 0.875  │
│ 1a2b3c4d5e6f │ Bob Wilson │ 2023-12-20 │ Add user authentication tests     │ 0.823  │
└──────────────┴────────────┴────────────┴───────────────────────────────────┴────────┘
```

### Blame Search
```
src/auth/jwt.py:45
Jane Smith on 2024-01-15
a1b2c3d4e5f6

def validate_token(token: str) -> dict:
    """Validate JWT token and return claims"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
```

### Author Attribution
```
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ Author     ┃ Commits ┃ Lines ┃ Relevance ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ Jane Smith │ 5       │ 127   │ 4.521     │
│ John Doe   │ 3       │ 89    │ 3.892     │
│ Bob Wilson │ 2       │ 45    │ 2.156     │
└────────────┴─────────┴───────┴───────────┘
```

## Troubleshooting

### Memory Issues
For large repositories, use streaming:
```bash
# Process in smaller batches
uv run python git_blame_tool.py index --max-commits 50

# Or increase memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Slow Indexing
- Use a faster embedding model: `all-MiniLM-L6-v2`
- Index only recent commits: `--max-commits 1000`
- Skip large binary files in `.gitignore`

### Search Quality
- Re-index with better embeddings: `microsoft/codebert-base`
- Add more context to queries
- Use file filters for targeted search

### uv-specific Tips
```bash
# Update dependencies
uv sync --upgrade

# Add development tools
uv add --dev ipython jupyter

# Run in isolated environment
uv run --isolated python git_blame_tool.py search "bug fix"

# Use specific Python version
uv python install 3.11
uv run --python 3.11 python git_blame_tool.py index
```

## Continue Agent Mode Prompts

Use these prompts in Continue to enhance the tool:

1. **"Add incremental indexing to only process new commits since last run"**
2. **"Implement fuzzy file path matching for the blame command"**
3. **"Add export functionality to save search results as markdown reports"**
4. **"Create a web UI using Flask and HTMX for the search interface"**
5. **"Add support for indexing pull request descriptions and linking them to commits"**
6. **"Implement semantic diff search to find similar code changes across the repository"**

This tool provides a powerful semantic search layer over your git history, making it easy to understand code evolution, track down implementations, and attribute code ownership using natural language queries.

## 🚀 Explore LanceDB's Multimodal Lakehouse

You've just scratched the surface of what's possible with LanceDB! This git blame tool showcases vector search, but LanceDB's new **Multimodal Lakehouse** platform offers so much more:

### Discover Advanced Features

**🔍 Unified Search**
- Search across code, documentation, images, and logs in a single query
- Combine vector similarity with SQL filters for precise results
- Scale to billions of embeddings with sub-millisecond latency

**🧠 AI-Native Training**
- Train models directly on your LanceDB data
- Zero-copy data loading for ML frameworks
- Automatic versioning and lineage tracking

**📊 Exploratory Data Analysis**
- Analyze patterns across your entire codebase
- Visualize code evolution and team contributions
- Generate insights from multimodal data

**⚡ Feature Engineering with Geneva**
- Transform git data into ML-ready features
- Declarative Python UDFs for complex computations
- Distributed processing with automatic checkpointing

### Next Steps

1. **Extend Your Git Blame Tool**
   ```python
   # Add image diff search for UI changes
   # Index PR comments and code reviews
   # Create knowledge graphs of code dependencies
   ```

2. **Try LanceDB Cloud**
   - Managed infrastructure with automatic scaling
   - Built-in integrations with Continue, LangChain, and more
   - Enterprise features for team collaboration

3. **Join the Community**
   - [LanceDB Documentation](https://lancedb.github.io/lancedb/)
   - [GitHub Discussions](https://github.com/lancedb/lancedb/discussions)
   - [Discord Community](https://discord.gg/lancedb)

### Learn More

📚 **Resources**
- [Building Multimodal RAG Applications](https://blog.lancedb.com/multimodal-rag)
- [Vector Database Performance Guide](https://lancedb.github.io/lancedb/performance/)
- [Geneva Feature Engineering](https://lancedb.github.io/geneva/features/)

🎯 **Use Cases**
- **Code Intelligence**: Semantic code search, dependency analysis, security scanning
- **Documentation Q&A**: Natural language queries over technical docs
- **Log Analysis**: Anomaly detection and pattern recognition
- **Multi-Modal Search**: Find similar UI designs, architecture diagrams, or flowcharts

### Ready to Build More?

Transform your development workflow with LanceDB's Multimodal Lakehouse. Whether you're building AI-powered developer tools, creating intelligent documentation systems, or analyzing large-scale codebases, LanceDB provides the infrastructure you need.

**[Get Started with LanceDB](https://lancedb.com) | [View Examples](https://github.com/lancedb/lancedb/tree/main/examples) | [Read the Docs](https://lancedb.github.io/lancedb/)**

---

*Built something cool with LanceDB? Share it with the community and get featured in our showcase!*