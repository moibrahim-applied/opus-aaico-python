# opus-aaico

Official Python SDK for the [OPUS](https://opus.com) workflow automation platform.

Features:
- Full coverage of all OPUS API endpoints (64 endpoints)
- Sync and async clients
- Type-safe with Pydantic models
- Automatic retry with exponential backoff
- High-level `workflows.run()` orchestrator

## Installation

```
pip install opus-aaico
```

## Quick Start

```python
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key")

# Run a workflow end-to-end (initiate -> execute -> poll -> results)
result = client.workflows.run(
    workflow_id="wf-123",
    payload={"query": {"value": "Analyze this", "type": "str"}},
)
print(result.outputs)
```

## Authentication

```python
# Pass directly
client = OpusClient(api_key="sk-...")

# Or set environment variables
# OPUS_API_KEY=sk-...
# OPUS_WORKSPACE_ID=ws-...  (optional)
# OPUS_BASE_URL=https://custom.opus.com  (optional)
client = OpusClient()
```

## Resources

| Resource | Methods | Description |
|----------|---------|-------------|
| `client.workflows` | get, list, list_public, generate, run, share, send_email... | Workflow management + orchestration |
| `client.jobs` | initiate, execute, get_status, get_results, poll, search... | Job lifecycle management |
| `client.files` | upload, download, search, generate, multipart_upload... | File operations |
| `client.reviews` | initiate, list, get, pick, submit_result, submit_output... | Human review management |
| `client.api_keys` | create, list, rotate, revoke, delete... | API key management |
| `client.credits` | get_balance, get_usage, record_usage... | Credit tracking |
| `client.policies` | upload, list, get, get_summary, set_active... | Policy management |
| `client.users` | list, list_projects, get_projects | User & project lookups |

## Async Usage

```python
from opus_aaico import AsyncOpusClient

async with AsyncOpusClient(api_key="sk-...") as client:
    result = await client.workflows.run("wf-123", payload={...})
```

## Error Handling

```python
from opus_aaico import OpusClient, NotFoundError, RateLimitError, OpusError

try:
    result = client.workflows.run("wf-123", payload={...})
except NotFoundError:
    print("Workflow not found")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except OpusError as e:
    print(f"API error: {e.message}")
```

## Configuration

```python
client = OpusClient(
    api_key="sk-...",
    workspace_id="ws-...",
    base_url="https://operator.opus.com",
    timeout=30.0,
    max_retries=3,
)
```

## Requirements

- Python 3.9+
- httpx
- pydantic v2

## License

MIT
