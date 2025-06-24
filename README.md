# Git Blame Search

Semantic search for git repositories using natural language. Find who wrote code, when changes happened, and why.

## Features

- 🔍 **Natural Language Search** - Search commits and code using plain English
- 👤 **Author Attribution** - Find who wrote specific code or features
- 🔌 **IDE Integration** - MCP server for Continue/Claude
- ⚡ **Fast** - Vector search powered by LanceDB

## Installation

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/git_blame_search.git
cd git_blame_search
uv sync
```

## Quick Start

### 1. Index Your Repository

```bash
# Index current directory (last 100 commits)
uv run git_blame_search index --max-commits 100

# Index another repository
uv run git_blame_search index --repo /path/to/repo --max-commits 500
```

### 2. Search

```bash
# Search commits
uv run git_blame_search search "authentication"
uv run git_blame_search search "bug fix" --limit 20

# Find who wrote code
uv run git_blame_search who "database connection"
uv run git_blame_search who "error handling"

# Search with blame context (requires indexing files first)
uv run git_blame_search blame "validation logic"
```

## Continue Integration

Add to your Continue config:

```yaml
mcpServers:
  git_blame_search:
    command: uv
    args:
      - run
      - python
      - src/server.py
    cwd: /path/to/git_blame_search
    env:
      TOKENIZERS_PARALLELISM: "false"
```

Then ask questions like:
- "Who wrote the authentication code?"
- "Find commits about database changes"
- "Show me bug fixes from last month"

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `index` | Index a repository | `uv run git_blame_search index --max-commits 100` |
| `search` | Search commits | `uv run git_blame_search search "bug fix"` |
| `who` | Find code authors | `uv run git_blame_search who "authentication"` |
| `blame` | Search blame data | `uv run git_blame_search blame "error handling"` |

### Command Options

- `--repo PATH` - Repository to index/search (default: current directory)
- `--max-commits N` - Number of commits to index
- `--limit N` - Number of results to return
- `--file PATH` - Filter blame search by file

## Testing

```bash
# Run tests
./run_tests.sh

# Or directly
uv run python test_git_blame_tool.py
```

## License

MIT
