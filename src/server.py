#!/usr/bin/env python3
"""
FastMCP Server for Git Blame Search Tool
Provides semantic search capabilities over git repositories
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from git_blame_tool import GitBlameIndexer
from typing import Optional


# Initialize the indexer
indexer = GitBlameIndexer()

# Create FastMCP app
mcp = FastMCP("Git Blame Search")

@mcp.tool()
def search_commits(query: str, limit: int = 10) -> str:
    """Search git commits using natural language.
    
    Args:
        query: Natural language search query
        limit: Number of results to return (default: 10)
    
    Returns:
        Formatted search results
    """
    try:
        results = indexer.search_commits(query, limit)
        if not results:
            return f"No commits found matching: {query}"
        
        formatted_results = []
        for r in results:
            formatted_results.append(
                f"**{r['commit_hash'][:8]}** by {r['author_name']} on {r['timestamp']}\n"
                f"{r['message']}\n"
            )
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching commits: {str(e)}"


@mcp.tool()
def search_blame(query: str, file_path: Optional[str] = None, limit: int = 10) -> str:
    """Search code blame data using natural language.
    
    Args:
        query: Natural language search query
        file_path: Optional file path to filter results
        limit: Number of results to return (default: 10)
    
    Returns:
        Formatted blame search results
    """
    try:
        results = indexer.search_blame(query, file_path, limit)
        if not results:
            return f"No blame data found matching: {query}"
        
        formatted_results = []
        for r in results:
            formatted_results.append(
                f"**{r['file_path']}:{r['line_number']}** by {r['author_name']}\n"
                f"Commit: {r['commit_hash'][:8]}\n"
                f"Code: {r['code_content']}\n"
            )
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching blame data: {str(e)}"


@mcp.tool()
def who_wrote(query: str, limit: int = 5) -> str:
    """Find who wrote code matching a query.
    
    Args:
        query: Natural language search query
        limit: Number of authors to return (default: 5)
    
    Returns:
        Author analysis results
    """
    try:
        results = indexer.who_wrote(query, limit)
        if not results:
            return f"No authors found for: {query}"
        
        formatted_results = []
        for r in results:
            formatted_results.append(
                f"**{r['name']}**: {r['commits']} commits, {r['lines']} lines modified"
            )
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error analyzing authors: {str(e)}"


@mcp.tool()
def search_code_changes(query: str, limit: int = 10) -> str:
    """Search code changes/diffs using natural language.
    
    Args:
        query: Natural language search query
        limit: Number of results to return (default: 10)
    
    Returns:
        Formatted diff search results
    """
    try:
        results = indexer.search_code_changes(query, limit)
        if not results:
            return f"No code changes found matching: {query}"
        
        formatted_results = []
        for r in results:
            formatted_results.append(
                f"**{r['file_path']}** in commit {r['commit_hash'][:8]}\n"
                f"Change type: {r['change_type']}\n"
                f"New content: {r['new_content'][:200]}...\n"
            )
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching code changes: {str(e)}"


def run_server():
    """Run the FastMCP server"""
    print("Starting Git Blame Search MCP server on stdio")
    mcp.run()


if __name__ == "__main__":
    run_server()