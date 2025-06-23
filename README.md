# Semantic Git Blame Tool

A powerful semantic search tool for git repositories using LanceDB. Search your git history, find code authors, and understand code evolution using natural language queries.

## Features

- 🔍 **Semantic Search**: Search commits, code changes, and blame data using natural language
- 👤 **Author Attribution**: Find who implemented specific features or functionality
- 📈 **Code Evolution**: Track how code has changed over time
- ⚡ **Fast Indexing**: Efficient vector indexing with LanceDB
- 🔌 **IDE Integration**: Works with Continue for in-editor code intelligence
- 🌐 **HTTP API**: REST endpoint for integration with other tools

## Quick Start

### Prerequisites

- Python 3.9+
- Git
- uv (recommended) or pip

### Installation

#### Option 1: Global Installation (Recommended)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/git_blame_search.git
cd git_blame_search

# Install globally from local directory
uv tool install .
```

#### Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/git_blame_search.git
cd git_blame_search

# Install dependencies
uv sync
```

#### Option 3: Using pip (after publishing to PyPI)
```bash
pip install git_blame_search
```

## Usage

### 1. Index Your Repository

```bash
# Index current repository (recent 100 commits)
git_blame_search index --max-commits 100

# Index a specific repository
git_blame_search index --repo /path/to/repo --max-commits 500

# For testing with minimal commits (e.g., new repos)
git_blame_search index --max-commits 1
```

### 2. Index Specific Files for Blame Analysis

```bash
# Index blame data for important files
git_blame_search index-file main.py
git_blame_search index-file src/core/auth.py
```

### 3. Search Commits

```bash
# For testing in a new (this) repository
git_blame_search search "init"

# Search by natural language
git_blame_search search "authentication implementation"
git_blame_search search "bug fix for memory leak"
git_blame_search search "refactoring database layer" --limit 20
```

### 4. Semantic Blame Search

```bash
# Find who wrote specific functionality
git_blame_search blame "error handling logic"
git_blame_search blame "database connection" --file src/db.py
```

### 5. Author Attribution

```bash
# Find who implemented features
git_blame_search who "authentication system"
git_blame_search who "caching implementation"
```

## Continue Integration

### 1. Index Your Repository First

```bash
# Index your repository before using MCP
git_blame_search index --max-commits 100

# Optionally index specific files for blame analysis
git_blame_search index-file src/main.py
```

### 2. Configure Continue

Add to your `~/.continue/config.yml`:

```yml
mcpServers:
  git_blame_search:
    command: git_blame_search
    args: ["mcp"]
    cwd: "/path/to/your-project-repo"
```

### 3. Use in VSCode

- Use `@git_blame_search` in Continue chat
- Ask questions like "who implemented the auth system?"

## Example Queries

### Finding Code Authors
```bash
uv run python git_blame_tool.py who "security vulnerability fix"
uv run python git_blame_tool.py who "REST API implementation"
```

### Understanding Code Evolution
```bash
uv run python git_blame_tool.py search "added try-catch blocks"
uv run python git_blame_tool.py search "refactored to use async/await"
```

### Blame Analysis
```bash
uv run python git_blame_tool.py blame "validate.*email"
uv run python git_blame_tool.py blame "test_.*authentication" --file tests/
```

## Architecture

The tool uses:
- **LanceDB**: Vector database for storing and searching embeddings
- **Sentence Transformers**: Microsoft's CodeBERT for code-aware embeddings
- **GitPython**: For parsing git repository data
- **Rich**: For beautiful CLI output

### Data Schema

**Commits Table**
- Commit metadata (hash, author, timestamp, message)
- Files changed, additions, deletions
- Message vector embeddings

**Blame Table**
- File path, line number, commit hash
- Author information and timestamps
- Code content and vector embeddings

**Diffs Table**
- Change type, file paths
- Old and new content
- Diff chunk vector embeddings

## Performance Tips

### Large Repositories

For repositories with 10k+ commits:
```python
# Process in batches
uv run python git_blame_tool.py index --max-commits 1000 --skip 0
uv run python git_blame_tool.py index --max-commits 1000 --skip 1000
```

### Memory Optimization
```bash
# Use smaller batches
uv run python git_blame_tool.py index --max-commits 50

# Increase PyTorch memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Faster Embeddings

Modify the embedder for speed:
```python
# In git_blame_tool.py, change:
self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Faster
```

## API Reference

### CLI Commands

- `index` - Index a git repository
  - `--repo, -r` - Repository path (default: current directory)
  - `--max-commits, -m` - Maximum commits to index

- `index-file` - Index blame data for a specific file
  - `FILE_PATH` - Path to file to index

- `search` - Search commits
  - `QUERY` - Natural language search query
  - `--limit, -l` - Number of results (default: 10)

- `blame` - Search blame data
  - `QUERY` - Natural language search query
  - `--file, -f` - Filter by file path
  - `--limit, -l` - Number of results (default: 5)

- `who` - Find code authors
  - `QUERY` - Natural language search query
  - `--limit, -l` - Number of results (default: 5)

- `serve` - Start HTTP server for IDE integration

### HTTP API

`POST /retrieve`
```json
{
  "query": "authentication implementation"
}
```

Response:
```json
{
  "results": [
    {
      "title": "Commit: Add JWT authentication",
      "content": "Author: Jane Smith\nDate: 2024-01-15\n\nAdd JWT authentication middleware",
      "metadata": {
        "type": "commit",
        "hash": "a1b2c3d4e5f6"
      }
    }
  ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [LanceDB](https://lancedb.com) - The multimodal vector database
- Uses [Microsoft CodeBERT](https://github.com/microsoft/CodeBERT) for code-aware embeddings
- Integrated with [Continue](https://continue.dev) for IDE support