#!/bin/bash
# Simple test runner for git_blame_search

echo "🧪 Running git_blame_search tests..."
echo "=================================="

# Set environment variable
export TOKENIZERS_PARALLELISM=false

# Run the test suite
uv run python test_git_blame_tool.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi