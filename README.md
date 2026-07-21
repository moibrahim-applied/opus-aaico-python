# opus-aaico

Unofficial Python SDK for the [OPUS](https://opus.com) workflow automation platform by [AAICO](https://aaico.com).

[![PyPI version](https://img.shields.io/pypi/v/opus-aaico.svg)](https://pypi.org/project/opus-aaico/)
[![Python versions](https://img.shields.io/pypi/pyversions/opus-aaico.svg)](https://pypi.org/project/opus-aaico/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## Overview

`opus-aaico` provides a type-safe, production-ready interface to the OPUS REST API. It covers all 64 API endpoints across 8 resource modules, with both synchronous and asynchronous clients.

Key capabilities:

- **Full API coverage** -- all OPUS endpoints wrapped in typed Python methods
- **Sync and async** -- `OpusClient` for scripts, `AsyncOpusClient` for high-throughput services
- **High-level orchestration** -- `workflows.run()` handles the entire job lifecycle in one call
- **Type safety** -- Pydantic v2 models for all requests and responses
- **Resilient** -- automatic retry with exponential backoff on transient failures
- **Minimal footprint** -- only two runtime dependencies (`httpx`, `pydantic`)

## Installation

```bash
pip install opus-aaico
```

Requires Python 3.9 or later.

## Quick Start

```python
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key")

# Run a workflow end-to-end: initiate, execute, poll, and return results
result = client.workflows.run(
    workflow_id="wf-123",
    payload={"query": {"value": "Analyze this document", "type": "str"}},
)

print(result.status)       # "COMPLETED"
print(result.outputs)      # Workflow output variables
print(result.execution_time)  # Seconds elapsed
```

## Authentication

```python
from opus_aaico import OpusClient

# Option 1: Pass directly
client = OpusClient(api_key="sk-...")

# Option 2: With workspace context
client = OpusClient(
    api_key="sk-...",
    workspace_id="ws-...",
)

# Option 3: From environment variables
# Set OPUS_API_KEY, OPUS_WORKSPACE_ID (optional), OPUS_BASE_URL (optional)
client = OpusClient()
```

| Environment Variable | Purpose |
|---------------------|---------|
| `OPUS_API_KEY` | API key (required if not passed to constructor) |
| `OPUS_WORKSPACE_ID` | Default workspace ID |
| `OPUS_BASE_URL` | Override base URL for staging or self-hosted instances |

## Resources

The client organizes the API into resource namespaces:

| Resource | Description | Key Methods |
|----------|-------------|-------------|
| `client.workflows` | Workflow management and orchestration | `get`, `list`, `generate`, `run`, `share`, `send_email` |
| `client.jobs` | Job lifecycle | `initiate`, `execute`, `get_status`, `get_results`, `poll`, `search` |
| `client.files` | File upload, download, and search | `upload`, `download`, `search`, `generate`, `multipart_upload` |
| `client.reviews` | Human review and task management | `initiate`, `list`, `get`, `pick`, `submit_result`, `submit_output` |
| `client.api_keys` | API key management | `create`, `list`, `rotate`, `revoke`, `delete` |
| `client.credits` | Credit balance and usage tracking | `get_balance`, `get_usage`, `record_usage` |
| `client.policies` | Organizational policy management | `upload`, `list`, `get`, `get_summary`, `set_active` |
| `client.users` | User and project lookups | `list`, `list_projects`, `get_projects` |

## Usage Examples

### Run a Workflow

```python
from opus_aaico import OpusClient

client = OpusClient(api_key="sk-...")

# High-level: one call handles initiate -> execute -> poll -> results
result = client.workflows.run(
    workflow_id="wf-123",
    payload={
        "query": {"value": "Summarize this report", "type": "str"},
        "document": {"value": "https://files.opus.com/doc.pdf", "type": "file"},
    },
    title="Q1 Report Analysis",
    poll_interval=2.0,   # seconds between status checks
    timeout=300,         # max wait time in seconds
)

print(result.status)
print(result.job_id)
print(result.outputs)
print(result.execution_time)
```

### Upload a File

```python
# Upload a local file (handles presigned URL flow automatically).
# The upload endpoint requires a scope -- pass workflow_id or workspace_id
# (or configure a default workspace via OpusClient(workspace_id=...) / OPUS_WORKSPACE_ID).
file_url = client.files.upload("./report.pdf", workflow_id="wf-123")

# Use it in a workflow
result = client.workflows.run(
    workflow_id="wf-123",
    payload={
        "document": {"value": file_url, "type": "file"},
    },
)
```

### Pass Multiple Files to a Workflow

For a `File (Multiple)` / `array<file>` input, a bare list of URLs is forwarded to
the agent as plain text -- so a vision/extraction agent receives links instead of
readable files. Use `file_array_input()` to build the value with the required
`typeDefinition`, which tells OPUS to resolve each URL into an attached file:

```python
from opus_aaico import OpusClient, file_input, file_array_input

client = OpusClient(api_key="sk-...", workspace_id="ws-...")

urls = [
    client.files.upload("./doc1.pdf", workflow_id="wf-123"),
    client.files.upload("./doc2.pdf", workflow_id="wf-123"),
]

result = client.workflows.run(
    workflow_id="wf-123",
    payload={
        "documents": file_array_input(urls),        # File (Multiple) input
        "cover_letter": file_input(urls[0]),        # single File input
        "instructions": {"value": "Compare these", "type": "str"},
    },
)
```

### Low-Level Job Control

```python
# Step-by-step control when you need it
job = client.jobs.initiate(
    workflow_id="wf-123",
    title="My Job",
    description="Processing data",
)

client.jobs.execute(
    job_execution_id=job.job_execution_id,
    payload={"query": {"value": "Analyze", "type": "str"}},
)

# Poll until complete
status = client.jobs.poll(job.job_execution_id, timeout=120)

if status.status.value == "COMPLETED":
    results = client.jobs.get_results(job.job_execution_id)
    audit = client.jobs.get_audit(job.job_execution_id)
```

### Search and List

```python
# Search jobs
jobs = client.jobs.search(
    workflow_id="wf-123",
    status=["COMPLETED", "FAILED"],
    start_date="2026-01-01",
    max_results=50,
)

# List workflows
workflows = client.workflows.list(
    query="onboarding",
    active=True,
)
```

### Async Usage

```python
import asyncio
from opus_aaico import AsyncOpusClient

async def main():
    async with AsyncOpusClient(api_key="sk-...") as client:
        # Run multiple workflows concurrently
        tasks = [
            client.workflows.run(
                workflow_id="wf-123",
                payload={"query": {"value": f"Task {i}", "type": "str"}},
            )
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(f"{r.job_id}: {r.status}")

asyncio.run(main())
```

## Error Handling

All errors inherit from `OpusError`. Catch specific exceptions or the base class:

```python
from opus_aaico import (
    OpusClient,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    PermissionDeniedError,
    OpusError,
)

try:
    result = client.workflows.run("wf-123", payload={...})
except AuthenticationError:
    # 401 -- invalid API key
    pass
except NotFoundError:
    # 404 -- workflow does not exist
    pass
except RateLimitError as e:
    # 429 -- retry after e.retry_after seconds
    pass
except ValidationError:
    # 400 -- invalid request parameters
    pass
except PermissionDeniedError:
    # 403 -- insufficient permissions
    pass
except OpusError as e:
    # Any other API error
    print(f"{e.message} (status={e.status_code})")
```

Error hierarchy:

```
OpusError
├── AuthenticationError       (401)
├── PermissionDeniedError     (403)
├── NotFoundError             (404)
├── ValidationError           (400)
├── RateLimitError            (429)  -- includes retry_after
├── APIError                  (5xx)
├── TimeoutError              (request or polling timeout)
└── ConnectionError           (network failure)
```

The SDK automatically retries on 429 and 5xx errors with exponential backoff (up to 3 retries by default).

## Configuration

```python
client = OpusClient(
    api_key="sk-...",              # required (or set OPUS_API_KEY)
    workspace_id="ws-...",         # optional default workspace
    base_url="https://operator.opus.com",  # override for staging
    timeout=30.0,                  # request timeout in seconds
    max_retries=3,                 # retries on transient failures
)
```

Both `OpusClient` and `AsyncOpusClient` support context managers for proper connection cleanup:

```python
with OpusClient(api_key="sk-...") as client:
    result = client.workflows.run("wf-123", payload={...})
```

## Architecture

```
src/opus_aaico/
├── __init__.py              # Public API: OpusClient, AsyncOpusClient, errors
├── _client.py               # HTTP layer: auth, retry, request handling
├── _sync.py                 # OpusClient (synchronous)
├── _async.py                # AsyncOpusClient (asynchronous)
├── _exceptions.py           # Typed error hierarchy
├── _constants.py            # Base URL, defaults, version
├── _cli.py                  # CLI entry point (opus-aaico command)
├── resources/               # One module per API resource
│   ├── workflows.py         # Workflow CRUD + run() orchestrator
│   ├── jobs.py              # Job lifecycle + polling
│   ├── files.py             # File upload/download + multipart
│   ├── reviews.py           # Human review management
│   ├── api_keys.py          # API key CRUD
│   ├── credits.py           # Credit tracking
│   ├── policies.py          # Policy management
│   └── users.py             # User and project lookups
├── types/                   # Pydantic v2 models for all DTOs
│   ├── enums.py             # JobStatus, ReviewType, etc.
│   ├── shared.py            # Base model, UserDetails, etc.
│   ├── workflows.py         # Workflow, WorkflowRunResult, etc.
│   ├── jobs.py              # JobAudit, JobSearchItem, etc.
│   └── ...                  # One file per resource
└── _utils/
    ├── polling.py           # Exponential backoff polling
    └── files.py             # Presigned URL upload helpers
```

Design principles:

- **Resource-based namespacing** following the OpenAI/Stripe SDK pattern
- **Async-first internals** with sync wrapper using httpx's dual transport
- **camelCase to snake_case** conversion handled automatically by Pydantic aliases
- **Minimal dependencies** -- only `httpx` and `pydantic` at runtime

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and development workflow.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT License. See [LICENSE](LICENSE) for details.
