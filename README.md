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

Using uv (recommended):
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/git-blame-search.git
cd git-blame-search

# Install dependencies
uv sync
```

Using pip:
```bash
pip install lancedb sentence-transformers click rich gitpython flask pyarrow
```

## Usage

### 1. Index Your Repository

```bash
# Index current repository (recent 100 commits)
uv run python git_blame_tool.py index --max-commits 100

# Index a specific repository
uv run python git_blame_tool.py index --repo /path/to/repo --max-commits 500

# For testing with minimal commits (e.g., new repos)
uv run python git_blame_tool.py index --max-commits 1
```

### 2. Index Specific Files for Blame Analysis

```bash
# Index blame data for important files
uv run python git_blame_tool.py index-file main.py
uv run python git_blame_tool.py index-file src/core/auth.py
```

### 3. Search Commits

```bash
# For testing in a new (this) repository
uv run python git_blame_tool.py search "init"

# Search by natural language
uv run python git_blame_tool.py search "authentication implementation"
uv run python git_blame_tool.py search "bug fix for memory leak"
uv run python git_blame_tool.py search "refactoring database layer" --limit 20
```

### 4. Semantic Blame Search

```bash
# Find who wrote specific functionality
uv run python git_blame_tool.py blame "error handling logic"
uv run python git_blame_tool.py blame "database connection" --file src/db.py
```

### 5. Author Attribution

```bash
# Find who implemented features
uv run python git_blame_tool.py who "authentication system"
uv run python git_blame_tool.py who "caching implementation"
```

## Continue Integration

### 1. Start the HTTP Server

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

### 3. Use in VSCode

- Type `@Git Blame Search` in Continue chat
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