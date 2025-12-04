# CLAUDE.md - pyLDAvis Development Guide

## Project Overview

pyLDAvis is an interactive visualization library for topic models (primarily LDA). It is a Python port of the R LDAvis package, providing D3-based visualizations that help interpret topics in text data.

**Version**: 3.4.1
**Python Support**: 3.9, 3.10, 3.11
**License**: BSD-3-Clause

## Repository Structure

```
pyLDAvis/
├── pyLDAvis/           # Core package
│   ├── __init__.py     # Package exports and version
│   ├── _prepare.py     # Core data transformation logic (prepare function)
│   ├── _display.py     # Visualization display and HTML generation
│   ├── _server.py      # Local web server for viewing visualizations
│   ├── gensim_models.py # Gensim LDA/HDP model integration
│   ├── graphlab.py     # GraphLab model integration (legacy)
│   ├── lda_model.py    # sklearn LDA model integration
│   ├── urls.py         # CDN URLs for JS/CSS assets
│   └── utils.py        # Utility functions (NumPyEncoder, etc.)
├── tests/              # Test suite
│   ├── pyLDAvis/       # Unit tests
│   └── data/           # Test fixtures (JSON files via git-lfs)
├── notebooks/          # Example Jupyter notebooks
├── docs/               # Sphinx documentation
└── js/                 # JavaScript visualization assets (ldavis.js, d3)
```

## Development Environment Setup

### Prerequisites: git-lfs

This project uses **git-lfs** (Git Large File Storage) for test data files. Install it before cloning:

```bash
# macOS
brew install git-lfs

# Ubuntu/Debian
sudo apt-get install git-lfs

# Windows (with chocolatey)
choco install git-lfs
```

Then initialize git-lfs:
```bash
git lfs install
```

If you've already cloned without git-lfs, pull the LFS files:
```bash
git lfs pull
```

### Using pip (recommended)

```bash
# Clone the repository (git-lfs files download automatically if installed)
git clone https://github.com/bmabey/pyLDAvis.git
cd pyLDAvis

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest flake8
```

### Using Pipenv

```bash
pipenv install -e .
pipenv install --dev
pipenv shell
```

### Dependencies

Runtime dependencies (from requirements.txt):
- numpy, scipy, pandas (>=2.0.0)
- joblib (>=1.2.0), jinja2, numexpr
- funcy, scikit-learn (>=1.0.0), gensim

## Running Tests

### Quick Test Run

```bash
# Run all tests
make test
# or directly:
pytest
```

### With Coverage

```bash
make coverage
# Generates htmlcov/index.html
```

### Cross-Python Version Testing

```bash
make test-all  # Uses tox
```

### Test Data

Test fixtures are stored in `tests/data/` using git-lfs. If tests fail with missing data:
```bash
git lfs pull
```

Or download manually:
```bash
cd tests/data
curl -L -O https://github.com/bmabey/pyLDAvis/raw/master/tests/data/movie_reviews_input.json
curl -L -O https://github.com/bmabey/pyLDAvis/raw/master/tests/data/movie_reviews_output.json
```

## Code Quality

### Linting

```bash
make lint
# or directly:
flake8 pyLDAvis tests
```

**Flake8 Configuration** (from .flake8):
- Max line length: 100 characters
- Ignores: W (warnings), E731 (lambda assignments), F403 (star imports)

## Test-Driven Development (TDD)

This project encourages TDD practices:

1. **Write tests first**: Before implementing new features, write tests that define expected behavior
2. **PR requirements**: All pull requests must include tests (see CONTRIBUTING.rst)
3. **End-to-end validation**: Tests compare Python output against reference R LDAvis output (`tests/data/movie_reviews_output.json`)
4. **Model integration tests**: Each supported model type (Gensim LDA, HDP, sklearn) has integration tests

### Test Structure

- `test_prepare.py`: Core algorithm tests comparing against R reference output
- `test_gensim_models.py`: Gensim model integration tests

### Writing Tests

When adding new functionality:
1. Create test file in `tests/pyLDAvis/`
2. Use pytest fixtures for common setup
3. For numerical comparisons, use `numpy.testing.assert_array_equal` or pandas `assert_frame_equal`
4. Test edge cases and error conditions

## Building Documentation

```bash
make docs
# Opens docs/_build/html/index.html
```

## Key APIs

### Main Entry Point

```python
import pyLDAvis

# Prepare visualization data
prepared_data = pyLDAvis.prepare(
    topic_term_dists,  # shape (n_topics, n_terms)
    doc_topic_dists,   # shape (n_docs, n_topics)
    doc_lengths,       # shape (n_docs,)
    vocab,             # shape (n_terms,)
    term_frequency     # shape (n_terms,)
)

# Display in notebook
pyLDAvis.display(prepared_data)

# Save to HTML
pyLDAvis.save_html(prepared_data, 'output.html')
```

### Gensim Integration

```python
import pyLDAvis.gensim_models as gensim_vis

prepared_data = gensim_vis.prepare(lda_model, corpus, dictionary)
```

## Common Makefile Commands

| Command | Description |
|---------|-------------|
| `make test` | Run tests with pytest |
| `make lint` | Check code style with flake8 |
| `make coverage` | Generate test coverage report |
| `make docs` | Build Sphinx documentation |
| `make clean` | Remove build artifacts |
| `make install` | Install package locally |

## CI/CD

Travis CI runs tests on Python 3.9, 3.10, and 3.11. See `.travis.yml` for configuration.

## Contributing

See `CONTRIBUTING.rst` for detailed contribution guidelines. Key points:
- Fork, clone, create feature branch
- Run `flake8` and `pytest` before submitting
- Include tests for new functionality
- Update docs if adding features
