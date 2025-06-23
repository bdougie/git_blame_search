# Publishing to PyPI

## Prerequisites

1. Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. Install publishing tools:
   ```bash
   uv sync  # Installs build and twine
   ```

## Publishing Steps

### 1. Update Version
Edit `pyproject.toml` and bump the version:
```toml
version = "0.1.1"  # or whatever the next version should be
```

### 2. Update Metadata
Edit `pyproject.toml` and update:
- `authors` - your name and email
- `homepage` and `repository` URLs
- Any other metadata

### 3. Build the Package
```bash
uv run python -m build
```

### 4. Test on TestPyPI (Optional but Recommended)
```bash
# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ git_blame_search
```

### 5. Publish to PyPI
```bash
# Upload to PyPI
uv run twine upload dist/*

# Clean up build artifacts
rm -rf dist/ build/ *.egg-info/
```

### 6. Create Git Tag
```bash
git tag v0.1.0
git push origin v0.1.0
```

## Authentication

### Option 1: API Tokens (Recommended)
1. Go to PyPI → Account Settings → API Tokens
2. Create a token for your project
3. Use it when prompted:
   - Username: `__token__`
   - Password: your API token

### Option 2: Username/Password
Use your PyPI username and password when prompted.

## Automation with GitHub Actions

You can automate publishing with GitHub Actions by creating `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install uv
      uses: astral-sh/setup-uv@v1
    - name: Build package
      run: uv run python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

Then add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.