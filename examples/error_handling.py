"""Demonstrate error handling patterns."""
from opus_aaico import (
    AuthenticationError,
    NotFoundError,
    OpusClient,
    OpusError,
    RateLimitError,
)

# Bad API key
try:
    client = OpusClient(api_key="invalid-key")
    client.workflows.get("wf-123")
except AuthenticationError:
    print("Invalid API key")

# Workflow not found
try:
    client = OpusClient(api_key="your-api-key-here")
    client.workflows.get("nonexistent-workflow")
except NotFoundError:
    print("Workflow not found")

# Rate limiting
try:
    client = OpusClient(api_key="your-api-key-here")
    # SDK automatically retries on 429, but if retries exhausted:
    client.jobs.search()
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")

# Catch-all for any OPUS error
try:
    client = OpusClient(api_key="your-api-key-here")
    client.workflows.run("wf-123", payload={})
except OpusError as e:
    print(f"OPUS error: {e.message} (status={e.status_code})")
