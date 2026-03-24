# Contributing to opus-aaico

Thank you for your interest in contributing to the OPUS Python SDK. This document covers the development setup, workflow, and guidelines for contributors.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Adding a New Resource](#adding-a-new-resource)
- [Adding a New Endpoint](#adding-a-new-endpoint)
- [Type Definitions](#type-definitions)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Development Setup

**Prerequisites:** Python 3.9 or later, git.

```bash
# Clone the repository
git clone https://github.com/moibrahim-applied/opus-aaico-python.git
cd opus-aaico-python

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify the installation
python -c "import opus_aaico; print(opus_aaico.__version__)"
```

## Project Structure

```
src/opus_aaico/
├── __init__.py          # Public exports
├── _client.py           # BaseClient, SyncHTTPClient, AsyncHTTPClient
├── _sync.py             # OpusClient (wires all sync resources)
├── _async.py            # AsyncOpusClient (wires all async resources)
├── _exceptions.py       # Error hierarchy + raise_for_status()
├── _constants.py        # BASE_URL, SDK_VERSION, defaults
├── _compat.py           # Python 3.9 compatibility
├── resources/
│   ├── _base.py         # SyncResource / AsyncResource base classes
│   ├── workflows.py     # SyncWorkflows / AsyncWorkflows
│   ├── jobs.py          # SyncJobs / AsyncJobs
│   └── ...              # One file per resource
├── types/
│   ├── enums.py         # All enumerations
│   ├── shared.py        # _BaseModel and shared types
│   ├── workflows.py     # Workflow-specific Pydantic models
│   └── ...              # One file per resource
└── _utils/
    ├── polling.py       # poll_sync / poll_async
    └── files.py         # Presigned URL upload helpers
```

Key conventions:

- Files prefixed with `_` are internal (not part of the public API).
- Every resource module contains both a `Sync*` and `Async*` class.
- All Pydantic models inherit from `_BaseModel` in `types/shared.py`.
- API field names use `Field(alias="camelCase")` for automatic conversion.

## Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first.** All new functionality must have tests before implementation.

3. **Implement the feature.**

4. **Run the full check suite:**
   ```bash
   # Tests
   pytest tests/ -v

   # Linting
   ruff check src/ tests/

   # Formatting
   ruff format src/ tests/

   # Type checking
   mypy src/opus_aaico/ --ignore-missing-imports
   ```

5. **Commit and push.** Write clear commit messages:
   - `feat: add webhook support to jobs resource`
   - `fix: handle empty response body in get_results`
   - `test: add coverage for multipart upload abort`
   - `docs: update README with pagination examples`

6. **Open a pull request** against `main`.

## Code Standards

- **Python 3.9 compatibility.** Use `from __future__ import annotations` in every file. Use `Optional[X]` instead of `X | None` in runtime code (type hints are fine with union syntax due to the future import).
- **Formatting.** Enforced by `ruff format`. Line length limit is 100 characters.
- **Linting.** Enforced by `ruff check` with rules: E, F, I, UP, B.
- **Type annotations.** All public methods must have complete type annotations. Run `mypy` to verify.
- **No print statements.** Use `logging.getLogger("opus_aaico")` for debug output.
- **Docstrings.** Required for all public classes and methods. Use imperative mood ("Return the workflow" not "Returns the workflow").

## Testing

The test suite uses `pytest` with `pytest-httpx` for HTTP mocking.

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_jobs.py -v

# Run a specific test
pytest tests/test_jobs.py::TestInitiate::test_initiate -v

# Run with coverage (if pytest-cov is installed)
pytest tests/ --cov=opus_aaico --cov-report=term-missing
```

### Test conventions

- Each resource has its own test file: `tests/test_{resource}.py`.
- Tests use `pytest-httpx` (`HTTPXMock`) to mock HTTP responses. No real API calls.
- Fixtures for `api_key` and `base_url` are in `tests/conftest.py`.
- Each test file creates its own `client` and resource fixtures:

```python
@pytest.fixture
def client(api_key, base_url):
    return SyncHTTPClient(api_key=api_key, base_url=base_url)

@pytest.fixture
def jobs(client):
    return SyncJobs(client)
```

### What to test

- Each endpoint method sends the correct HTTP method, path, and body.
- Response data is correctly parsed into the expected Pydantic model.
- Query parameters are passed correctly (and None values are excluded).
- Error cases raise the appropriate exception.

## Adding a New Resource

1. **Create the type definitions** in `src/opus_aaico/types/{resource}.py`:
   - All models inherit from `_BaseModel`
   - Use `Field(alias="camelCase")` for API field mapping
   - Export from `types/__init__.py`

2. **Create the resource module** in `src/opus_aaico/resources/{resource}.py`:
   - Define both `Sync{Resource}(SyncResource)` and `Async{Resource}(AsyncResource)`
   - Each method calls `self._client.request(method, path, ...)`
   - Export from `resources/__init__.py`

3. **Wire into the clients:**
   - Add `self.{resource} = Sync{Resource}(self._http)` in `_sync.py`
   - Add `self.{resource} = Async{Resource}(self._http)` in `_async.py`

4. **Write tests** in `tests/test_{resource}.py`.

5. **Update the README** resource table.

## Adding a New Endpoint

1. Add any new Pydantic models to the relevant `types/{resource}.py`.
2. Add the method to both the `Sync*` and `Async*` classes in `resources/{resource}.py`.
3. Write a test that mocks the HTTP call and verifies the request and response.
4. Export any new types from `types/__init__.py`.

## Type Definitions

All API response types are Pydantic v2 models defined in `src/opus_aaico/types/`.

Guidelines:

- Inherit from `_BaseModel` (defined in `types/shared.py`), which configures `populate_by_name=True` and a clean `__repr__`.
- Use `Field(alias="camelCase")` for fields where the API uses camelCase.
- All fields should be `Optional` with a default of `None` unless the API guarantees the field is always present.
- Enums go in `types/enums.py` and extend `str, Enum` for JSON serialization.
- Shared types (used by multiple resources) go in `types/shared.py`.

Example:

```python
from __future__ import annotations
from typing import Optional
from pydantic import Field
from opus_aaico.types.shared import _BaseModel

class MyResponse(_BaseModel):
    my_field: Optional[str] = Field(None, alias="myField")
    count: int = 0
```

## Pull Request Process

1. Ensure all tests pass and linting is clean.
2. Update the README if you added new public API surface.
3. Add an entry to CHANGELOG.md under "Unreleased".
4. Request review from a maintainer.
5. Squash merge into `main` once approved.

## Release Process

1. Update the version in `src/opus_aaico/_constants.py` and `src/opus_aaico/__init__.py` and `pyproject.toml`.
2. Move the "Unreleased" section in CHANGELOG.md to a versioned heading.
3. Commit: `chore: bump version to X.Y.Z`
4. Tag: `git tag vX.Y.Z`
5. Build: `python -m build`
6. Publish: `twine upload dist/*`

## Questions

If you have questions about contributing, open a GitHub issue or reach out to the maintainers.
