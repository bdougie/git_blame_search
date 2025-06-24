#!/usr/bin/env python3
"""
Tests for git_blame_tool to ensure basic commands work
"""

import subprocess
import tempfile
import os
import shutil
import git
from pathlib import Path


def run_command(cmd):
    """Run a command and return the result"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def create_test_repo():
    """Create a test git repository with some commits"""
    tmpdir = tempfile.mkdtemp()
    repo_path = Path(tmpdir) / "test_repo"
    repo = git.Repo.init(repo_path)
    
    # Configure git user for the test repo
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    
    # Create test files and commits
    test_file = repo_path / "test.py"
    
    # First commit
    test_file.write_text("def hello():\n    print('Hello')\n")
    repo.index.add(["test.py"])
    repo.index.commit("Initial commit")
    
    # Second commit
    test_file.write_text("def hello():\n    print('Hello World')\n\ndef goodbye():\n    print('Goodbye')\n")
    repo.index.add(["test.py"])
    repo.index.commit("Add goodbye function")
    
    # Third commit
    test_file.write_text("def hello():\n    print('Hello World!')\n\ndef goodbye():\n    print('Goodbye!')\n")
    repo.index.add(["test.py"])
    repo.index.commit("Fix bug in output")
    
    return repo_path


def test_index_command():
    """Test the index command"""
    print("Testing index command...")
    repo_path = create_test_repo()
    
    # Test indexing
    cmd = f"uv run git_blame_search index --repo {repo_path} --max-commits 10"
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"Index command failed: {stderr}"
    assert "Indexed" in stdout, "Index command didn't report success"
    print("✓ Index command works")
    
    # Cleanup
    shutil.rmtree(repo_path.parent)


def test_search_command():
    """Test the search command"""
    print("Testing search command...")
    repo_path = create_test_repo()
    
    # First index the repo
    run_command(f"uv run git_blame_search index --repo {repo_path} --max-commits 10")
    
    # Test searching
    cmd = f"uv run git_blame_search search 'bug fix' --limit 5"
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"Search command failed: {stderr}"
    print("✓ Search command works")
    
    # Cleanup
    shutil.rmtree(repo_path.parent)


def test_who_command():
    """Test the who command"""
    print("Testing who command...")
    repo_path = create_test_repo()
    
    # First index the repo
    run_command(f"uv run git_blame_search index --repo {repo_path} --max-commits 10")
    
    # Test who command
    cmd = f"uv run git_blame_search who 'function' --limit 3"
    returncode, stdout, stderr = run_command(cmd)
    
    assert returncode == 0, f"Who command failed: {stderr}"
    print("✓ Who command works")
    
    # Cleanup
    shutil.rmtree(repo_path.parent)


def test_blame_command():
    """Test the blame command (expected to fail without indexed files)"""
    print("Testing blame command...")
    repo_path = create_test_repo()
    
    # First index the repo
    run_command(f"uv run git_blame_search index --repo {repo_path} --max-commits 10")
    
    # Test blame command
    cmd = f"uv run git_blame_search blame 'print' --limit 3"
    returncode, stdout, stderr = run_command(cmd)
    
    # Blame might not return results without indexed files, but shouldn't crash
    assert returncode == 0, f"Blame command crashed: {stderr}"
    print("✓ Blame command works (no crash)")
    
    # Cleanup
    shutil.rmtree(repo_path.parent)


def test_mcp_server():
    """Test that the MCP server can start"""
    print("Testing MCP server initialization...")
    
    # Test that we can import and create the server
    try:
        import sys
        sys.path.append('.')
        from src.server import mcp
        print("✓ MCP server imports successfully")
    except Exception as e:
        assert False, f"Failed to import MCP server: {e}"


def main():
    """Run all tests"""
    print("Running git_blame_tool tests...\n")
    
    # Set environment variable to suppress tokenizer warnings
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    try:
        test_index_command()
        test_search_command()
        test_who_command()
        test_blame_command()
        test_mcp_server()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())