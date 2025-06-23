#!/usr/bin/env python3
"""
Semantic Git Blame Tool with LanceDB
A searchable git data lake for better code understanding
"""

import os
import subprocess
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import click
import lancedb
import pyarrow as pa
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.syntax import Syntax
import git
from pathlib import Path

console = Console()

class GitBlameIndexer:
    """Indexes git repository data into LanceDB for semantic search"""
    
    def __init__(self, db_path: str = "./git_blame_lake"):
        self.db = lancedb.connect(db_path)
        self.embedder = SentenceTransformer('microsoft/codebert-base')
        self.setup_tables()
        
    def setup_tables(self):
        """Create LanceDB tables with optimized schema"""
        # Schema for commits
        commit_schema = pa.schema([
            pa.field("commit_hash", pa.string()),
            pa.field("author_name", pa.string()),
            pa.field("author_email", pa.string()),
            pa.field("timestamp", pa.timestamp('s')),
            pa.field("message", pa.string()),
            pa.field("files_changed", pa.list_(pa.string())),
            pa.field("additions", pa.int32()),
            pa.field("deletions", pa.int32()),
            pa.field("message_vector", pa.list_(pa.float32(), 768))
        ])
        
        # Schema for blame entries
        blame_schema = pa.schema([
            pa.field("file_path", pa.string()),
            pa.field("line_number", pa.int32()),
            pa.field("commit_hash", pa.string()),
            pa.field("author_name", pa.string()),
            pa.field("timestamp", pa.timestamp('s')),
            pa.field("code_content", pa.string()),
            pa.field("code_vector", pa.list_(pa.float32(), 768))
        ])
        
        # Schema for diff chunks
        diff_schema = pa.schema([
            pa.field("commit_hash", pa.string()),
            pa.field("file_path", pa.string()),
            pa.field("change_type", pa.string()),
            pa.field("old_content", pa.string()),
            pa.field("new_content", pa.string()),
            pa.field("chunk_vector", pa.list_(pa.float32(), 768))
        ])
        
        # Create tables if they don't exist
        if "commits" not in self.db.table_names():
            self.db.create_table("commits", schema=commit_schema)
        if "blame" not in self.db.table_names():
            self.db.create_table("blame", schema=blame_schema)
        if "diffs" not in self.db.table_names():
            self.db.create_table("diffs", schema=diff_schema)
    
    def index_repository(self, repo_path: str, max_commits: Optional[int] = None):
        """Index entire repository into LanceDB"""
        repo = git.Repo(repo_path)
        commits_table = self.db.open_table("commits")
        diffs_table = self.db.open_table("diffs")
        
        console.print(f"[bold blue]Indexing repository: {repo_path}[/bold blue]")
        
        commits_data = []
        diffs_data = []
        
        # Get all commits
        all_commits = list(repo.iter_commits())
        if max_commits:
            all_commits = all_commits[:max_commits]
        
        for commit in track(all_commits, description="Processing commits..."):
            # Extract commit data
            commit_data = {
                "commit_hash": commit.hexsha,
                "author_name": commit.author.name,
                "author_email": commit.author.email,
                "timestamp": datetime.fromtimestamp(commit.authored_date),
                "message": commit.message.strip(),
                "files_changed": [],
                "additions": 0,
                "deletions": 0
            }
            
            # Generate embedding for commit message
            message_embedding = self.embedder.encode(commit.message)
            commit_data["message_vector"] = message_embedding.tolist()
            
            # Process diffs
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit)
                
                for diff in diffs:
                    if diff.a_path:
                        commit_data["files_changed"].append(diff.a_path)
                    
                    # Extract diff content
                    if diff.a_blob and diff.b_blob:
                        try:
                            old_content = diff.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                            new_content = diff.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                            
                            # Create diff chunk
                            diff_text = f"Changed {diff.a_path}:\n{new_content[:500]}"
                            diff_embedding = self.embedder.encode(diff_text)
                            
                            diff_data = {
                                "commit_hash": commit.hexsha,
                                "file_path": diff.a_path,
                                "change_type": diff.change_type,
                                "old_content": old_content[:1000],  # Limit size
                                "new_content": new_content[:1000],
                                "chunk_vector": diff_embedding.tolist()
                            }
                            diffs_data.append(diff_data)
                            
                        except Exception as e:
                            console.print(f"[yellow]Warning: Could not process diff for {diff.a_path}: {e}[/yellow]")
            
            commits_data.append(commit_data)
            
            # Batch insert every 100 commits
            if len(commits_data) >= 100:
                commits_table.add(commits_data)
                if diffs_data:
                    diffs_table.add(diffs_data)
                commits_data = []
                diffs_data = []
        
        # Insert remaining data
        if commits_data:
            commits_table.add(commits_data)
        if diffs_data:
            diffs_table.add(diffs_data)
        
        console.print(f"[green]✓ Indexed {len(all_commits)} commits[/green]")
    
    def index_file_blame(self, repo_path: str, file_path: str):
        """Index blame data for a specific file"""
        repo = git.Repo(repo_path)
        blame_table = self.db.open_table("blame")
        
        console.print(f"[bold blue]Indexing blame for: {file_path}[/bold blue]")
        
        try:
            # Get blame data
            blame_data = []
            for commit, lines in repo.blame('HEAD', file_path):
                for line_num, line in lines:
                    # Create blame entry
                    code_text = f"{file_path}:{line_num} {line}"
                    code_embedding = self.embedder.encode(code_text)
                    
                    blame_entry = {
                        "file_path": file_path,
                        "line_number": line_num,
                        "commit_hash": commit.hexsha,
                        "author_name": commit.author.name,
                        "timestamp": datetime.fromtimestamp(commit.authored_date),
                        "code_content": line,
                        "code_vector": code_embedding.tolist()
                    }
                    blame_data.append(blame_entry)
            
            # Insert blame data
            if blame_data:
                blame_table.add(blame_data)
                console.print(f"[green]✓ Indexed {len(blame_data)} lines of blame data[/green]")
            
        except Exception as e:
            console.print(f"[red]Error indexing blame for {file_path}: {e}[/red]")
    
    def search_commits(self, query: str, limit: int = 10) -> List[Dict]:
        """Search commits by natural language query"""
        commits_table = self.db.open_table("commits")
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Vector search
        results = commits_table.search(query_embedding).limit(limit).to_pandas()
        
        return results.to_dict('records')
    
    def search_code_changes(self, query: str, limit: int = 10) -> List[Dict]:
        """Search code changes by natural language query"""
        diffs_table = self.db.open_table("diffs")
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Vector search
        results = diffs_table.search(query_embedding).limit(limit).to_pandas()
        
        return results.to_dict('records')
    
    def search_blame(self, query: str, file_path: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search blame data by natural language query"""
        blame_table = self.db.open_table("blame")
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Vector search with optional file filter
        if file_path:
            results = blame_table.search(query_embedding)\
                .where(f"file_path = '{file_path}'")\
                .limit(limit)\
                .to_pandas()
        else:
            results = blame_table.search(query_embedding).limit(limit).to_pandas()
        
        return results.to_dict('records')
    
    def who_wrote(self, query: str, limit: int = 5) -> List[Dict]:
        """Find who wrote code matching the query"""
        # Search both commits and blame data
        commit_results = self.search_commits(query, limit)
        blame_results = self.search_blame(query, limit=limit)
        
        # Aggregate by author
        author_stats = {}
        
        for commit in commit_results:
            author = commit['author_name']
            if author not in author_stats:
                author_stats[author] = {
                    'name': author,
                    'commits': 0,
                    'lines': 0,
                    'relevance': 0
                }
            author_stats[author]['commits'] += 1
            author_stats[author]['relevance'] += commit.get('_distance', 0)
        
        for blame in blame_results:
            author = blame['author_name']
            if author not in author_stats:
                author_stats[author] = {
                    'name': author,
                    'commits': 0,
                    'lines': 0,
                    'relevance': 0
                }
            author_stats[author]['lines'] += 1
            author_stats[author]['relevance'] += blame.get('_distance', 0)
        
        # Sort by relevance
        sorted_authors = sorted(
            author_stats.values(), 
            key=lambda x: x['relevance'], 
            reverse=True
        )[:limit]
        
        return sorted_authors

class GitBlameCLI:
    """Command-line interface for semantic git blame"""
    
    def __init__(self):
        self.indexer = GitBlameIndexer()
    
    def display_commit_results(self, results: List[Dict]):
        """Display commit search results in a table"""
        table = Table(title="Commit Search Results")
        table.add_column("Hash", style="cyan", width=12)
        table.add_column("Author", style="green")
        table.add_column("Date", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Score", style="magenta")
        
        for result in results:
            table.add_row(
                result['commit_hash'][:12],
                result['author_name'],
                result['timestamp'].strftime("%Y-%m-%d"),
                result['message'][:60] + "..." if len(result['message']) > 60 else result['message'],
                f"{result.get('_distance', 0):.3f}"
            )
        
        console.print(table)
    
    def display_blame_results(self, results: List[Dict]):
        """Display blame search results"""
        for result in results:
            console.print(f"\n[bold cyan]{result['file_path']}:{result['line_number']}[/bold cyan]")
            console.print(f"[green]{result['author_name']}[/green] on {result['timestamp'].strftime('%Y-%m-%d')}")
            console.print(f"[yellow]{result['commit_hash'][:12]}[/yellow]")
            
            # Syntax highlight the code
            syntax = Syntax(result['code_content'], "python", theme="monokai", line_numbers=False)
            console.print(syntax)
    
    def display_author_results(self, results: List[Dict]):
        """Display author analysis results"""
        table = Table(title="Who Wrote This?")
        table.add_column("Author", style="green")
        table.add_column("Commits", style="cyan")
        table.add_column("Lines", style="yellow")
        table.add_column("Relevance", style="magenta")
        
        for result in results:
            table.add_row(
                result['name'],
                str(result['commits']),
                str(result['lines']),
                f"{result['relevance']:.3f}"
            )
        
        console.print(table)

@click.group()
def cli():
    """Semantic Git Blame Tool - Search your git history with natural language"""
    pass

@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
@click.option('--max-commits', '-m', type=int, help='Maximum commits to index')
def index(repo, max_commits):
    """Index a git repository into LanceDB"""
    indexer = GitBlameIndexer()
    indexer.index_repository(repo, max_commits)

@cli.command()
@click.option('--repo', '-r', default='.', help='Repository path')
@click.argument('file_path')
def index_file(repo, file_path):
    """Index blame data for a specific file"""
    indexer = GitBlameIndexer()
    indexer.index_file_blame(repo, file_path)

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Number of results')
def search(query, limit):
    """Search commits by natural language query"""
    cli_tool = GitBlameCLI()
    results = cli_tool.indexer.search_commits(query, limit)
    cli_tool.display_commit_results(results)

@cli.command()
@click.argument('query')
@click.option('--file', '-f', help='Filter by file path')
@click.option('--limit', '-l', default=5, help='Number of results')
def blame(query, file, limit):
    """Search blame data by natural language query"""
    cli_tool = GitBlameCLI()
    results = cli_tool.indexer.search_blame(query, file, limit)
    cli_tool.display_blame_results(results)

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Number of results')
def who(query, limit):
    """Find who wrote code matching the query"""
    cli_tool = GitBlameCLI()
    results = cli_tool.indexer.who_wrote(query, limit)
    cli_tool.display_author_results(results)

@cli.command()
def serve():
    """Start HTTP server for Continue integration"""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    indexer = GitBlameIndexer()
    
    @app.route('/retrieve', methods=['POST'])
    def retrieve():
        """Continue HTTP context provider endpoint"""
        data = request.json
        query = data.get('query', '')
        
        # Search all sources
        commits = indexer.search_commits(query, limit=5)
        blame = indexer.search_blame(query, limit=5)
        
        # Format for Continue
        results = []
        for commit in commits:
            results.append({
                'title': f"Commit: {commit['message'][:50]}",
                'content': f"Author: {commit['author_name']}\nDate: {commit['timestamp']}\n\n{commit['message']}",
                'metadata': {
                    'type': 'commit',
                    'hash': commit['commit_hash']
                }
            })
        
        for b in blame:
            results.append({
                'title': f"{b['file_path']}:{b['line_number']}",
                'content': b['code_content'],
                'metadata': {
                    'type': 'blame',
                    'author': b['author_name'],
                    'commit': b['commit_hash']
                }
            })
        
        return jsonify({'results': results})
    
    console.print("[bold green]Starting Continue integration server on http://localhost:5000[/bold green]")
    app.run(port=5000)

if __name__ == '__main__':
    cli()