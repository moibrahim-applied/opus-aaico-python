# opus-aaico Python SDK -- Complete Reference

> Drop this file into your AI coding assistant's context to provide full knowledge of the opus-aaico SDK. This enables AI-assisted integration code, debugging, and application development on top of OPUS workflows.

---

## What is opus-aaico

`opus-aaico` is a Python SDK for the OPUS workflow automation platform. It wraps the OPUS REST API endpoints into typed Python methods with both synchronous and asynchronous clients.

- **Package:** `pip install opus-aaico`
- **Import:** `import opus_aaico`
- **Python:** 3.9+
- **Dependencies:** httpx, pydantic v2
- **Source:** https://github.com/moibrahim-applied/opus-aaico-python

---

## Quick Start

```python
from opus_aaico import OpusClient

client = OpusClient(api_key="sk-...")

# Run a workflow end-to-end in one call
result = client.workflows.run(
    workflow_id="wf-123",
    payload={"query": {"value": "Analyze this", "type": "str"}},
)
print(result.status)   # "COMPLETED"
print(result.outputs)  # Workflow output variables
```

---

## Client Initialization

```python
from opus_aaico import OpusClient, AsyncOpusClient

# Synchronous client
client = OpusClient(
    api_key="sk-...",              # required (or set OPUS_API_KEY env var)
    workspace_id="ws-...",         # optional (or set OPUS_WORKSPACE_ID)
    base_url="https://operator.opus.com",  # optional (or set OPUS_BASE_URL)
    timeout=30.0,                  # request timeout in seconds
    max_retries=3,                 # retries on 429/5xx
    bearer_token=None,             # optional Bearer auth
)

# Asynchronous client
async_client = AsyncOpusClient(api_key="sk-...")

# Context manager support
with OpusClient(api_key="sk-...") as client:
    result = client.workflows.run(...)

async with AsyncOpusClient(api_key="sk-...") as client:
    result = await client.workflows.run(...)
```

Environment variables (read automatically if constructor params not provided):

| Variable | Purpose |
|----------|---------|
| `OPUS_API_KEY` | API key |
| `OPUS_WORKSPACE_ID` | Default workspace ID |
| `OPUS_BASE_URL` | Override base URL |

---

## Resource Namespaces

```python
client.workflows     # Workflow management + run() orchestrator
client.jobs          # Job lifecycle + polling
client.files         # File upload/download/search
client.reviews       # Human review management
client.api_keys      # API key CRUD
client.credits       # Credit balance and usage
client.policies      # Policy management
client.users         # User and project lookups
```

---

## Workflows Resource

```python
# Get workflow details
workflow = client.workflows.get(workflow_id: str) -> Workflow

# List private workflows
workflows = client.workflows.list(
    query: str = None,
    industry: str = None,
    workspace_ids: list[str] = None,
    active: bool = None,
    has_jobs: bool = None,
    offset: int = 0,
    max_results: int = 25,
) -> PrivateWorkflowsResponse

# List public workflows
public = client.workflows.list_public(
    query: str = None,
    industry: str = None,
    country: str = None,
    source: str = None,        # "WKG" or "USER_GENERATED"
    offset: int = 0,
    max_results: int = 25,
) -> PublicWorkflowsResponse

# Get public workflow details
client.workflows.get_public(generation_id: str) -> Any

# Generate workflow from natural language
client.workflows.generate(
    user_query: str,
    user_id: str = None,
    make_private: bool = False,
    include_policies: bool = False,
    settings: dict = None,
) -> GenerateWorkflowResponse

# Feed an existing workflow
client.workflows.feed(workflow_id: str, private: bool = False) -> Any

# Feed external generation
client.workflows.feed_external(workflow_object, user_query: str, blueprint) -> Any

# Share workflow
client.workflows.share(workflow_id: str) -> Any

# Get shared workflow
client.workflows.get_shared(workflow_id: str) -> Any

# Send email on behalf of workflow
client.workflows.send_email(
    workflow_id: str,
    recipients: list[str],
    subject: str,
    body: str,
    attachments: list[dict] = None,
) -> None

# List available industries
client.workflows.list_industries() -> Any

# HIGH-LEVEL: Run workflow end-to-end
result = client.workflows.run(
    workflow_id: str,
    payload: dict,               # {var_name: {value: ..., type: "str"|"float"|...}}
    title: str = "SDK Job",
    description: str = "",
    poll_interval: float = 2.0,  # seconds between status checks
    timeout: float = 300.0,      # max wait in seconds
    on_status_change: callable = None,  # called on each status transition
) -> WorkflowRunResult
```

The `run()` method handles the full lifecycle: initiate job, execute with payload, poll until complete, fetch results and audit data.

### Compound: Workflow Health Check

```python
# Instant health report -- combines workflow details + job search by status + audit sampling
health = client.workflows.health(
    workflow_id: str,
    days: int = 7,              # how many days to analyze
    sample_audits: int = 20,    # how many jobs to sample for node-level stats
) -> WorkflowHealthReport
```

Returns a `WorkflowHealthReport` with:
- `workflow_name` -- name of the workflow
- `days_analyzed` -- period covered
- `total_runs`, `completed`, `failed`, `cancelled`, `in_progress` -- job counts
- `success_rate` -- percentage (e.g. 94.3)
- `avg_execution_time_seconds` -- average across sampled jobs
- `slowest_node` -- node name with highest avg execution time
- `slowest_node_avg_ms` -- its avg time in milliseconds
- `most_failing_node` -- node name with most failures
- `most_failing_node_count` -- number of failures
- `node_stats` -- list of `NodeHealthStats` per node (name, total_executions, failures, failure_rate, avg_execution_time_ms, max_execution_time_ms)
- `stuck_jobs` -- list of job IDs that have been IN_PROGRESS for over 1 hour

Under the hood: 5 API calls (workflow details + 4 job searches by status) + up to 40 audit calls for node-level stats.

```python
health = client.workflows.health("wf-123", days=30)
print(health.success_rate)        # 94.3
print(health.slowest_node)        # "Document Extraction"
print(health.most_failing_node)   # "Compliance Check"
print(health.model_dump())        # full dict of all fields
```

### Compound: Retry Failed Jobs

```python
# Find all failed jobs and re-run each with its original input payload
report = client.workflows.retry_failed(
    workflow_id: str,
    since_days: int = 7,        # how far back to look
    max_retries: int = 50,      # max number of jobs to retry
) -> RetryReport
```

Returns a `RetryReport` with:
- `workflow_id` -- the workflow
- `total_failed` -- how many failed jobs were found
- `retried` -- how many were successfully re-submitted
- `skipped` -- how many were skipped (no input payload found or error)
- `results` -- list of `RetryResult` (original_job_id, new_job_id, status, error)

Under the hood: searches failed jobs, fetches each job's detail to extract the original input payload, then initiates + executes a new job with that same payload.

```python
report = client.workflows.retry_failed("wf-123", since_days=7)
print(f"Retried {report.retried} of {report.total_failed} failed jobs")
for r in report.results:
    print(f"  {r.original_job_id} -> {r.new_job_id} ({r.status})")
```

---

## Jobs Resource

```python
# Initiate a job (creates shell, no execution)
job = client.jobs.initiate(
    workflow_id: str,
    title: str,                  # required
    description: str,            # required
    ref_user_id: str = None,
) -> JobInitiateResponse         # .job_execution_id

# Execute a job
client.jobs.execute(
    job_execution_id: str,
    payload: dict,               # {var_name: {value: ..., type: ...}}
    callback_url: str = None,    # webhook URL for status updates
) -> JobExecuteResponse

# Get job status
client.jobs.get_status(job_id: str) -> JobStatusResponse  # .status (JobStatus enum)

# Get job details
client.jobs.get(job_id: str) -> Any

# Get job results (only when COMPLETED)
client.jobs.get_results(job_id: str) -> JobResultsResponse

# Get job audit (per-node execution data)
client.jobs.get_audit(job_id: str) -> JobAudit

# Search jobs
client.jobs.search(
    workflow_id: str = None,
    workspace_ids: list[str] = None,
    status: list[str] = None,     # ["COMPLETED", "FAILED"]
    query: str = None,
    archive_status: str = None,   # "all", "archivedOnly", "nonArchivedOnly"
    start_date: str = None,       # ISO date
    end_date: str = None,
    offset: int = 0,
    max_results: int = 25,
) -> JobSearchResponse

# Archive / unarchive / duplicate / delete
client.jobs.archive(job_id: str) -> None
client.jobs.unarchive(job_id: str) -> None
client.jobs.duplicate(job_id: str) -> Any
client.jobs.delete(job_id: str) -> None

# Poll until terminal status
client.jobs.poll(
    job_execution_id: str,
    poll_interval: float = 2.0,
    timeout: float = 300.0,
    terminal_statuses: list[str] = ["COMPLETED", "FAILED", "CANCELLED"],
    on_status_change: callable = None,
) -> JobStatusResponse
```

### Payload Format

The OPUS API expects job payloads in this format:

```python
payload = {
    "variable_name": {"value": "actual value", "type": "str"},
    "amount": {"value": 1500, "type": "float"},
    "flag": {"value": True, "type": "bool"},
    "document": {"value": "https://files.opus.com/...", "type": "file"},
}
```

Valid types: `str`, `float`, `bool`, `date`, `file`, `array`, `array_files`, `object`.

#### Multiple files (`File (Multiple)` / `array<file>`)

A bare list of file URLs is forwarded to the agent as plain text, so it never
receives readable files. The array item type must be declared as `file` via a
`typeDefinition`. Use the `file_input` / `file_array_input` helpers instead of
hand-writing this:

```python
from opus_aaico import file_input, file_array_input

payload = {
    "documents": file_array_input([url1, url2]),   # File (Multiple)
    "cover": file_input(url1),                      # single File
}

# file_array_input([...]) expands to:
# {
#     "value": [url1, url2],
#     "type": "array",
#     "typeDefinition": {
#         "id": "file",
#         "variable_name": "file",
#         "allowed_types": [{"type": "file"}],
#     },
# }
```

Single-file inputs are unaffected (`{"value": url, "type": "file"}`). Some docs
mention `type: "array_files"`; the shape that works is `type: "array"` plus the
`typeDefinition` above. When in doubt, derive the exact shape from a live
`workflows.get(workflow_id)`.

---

## Files Resource

```python
# Upload a local file (handles presigned URL automatically).
# Requires a scope: pass workflow_id= OR workspace_id= (or set a default
# workspace on the client / OPUS_WORKSPACE_ID). Raises ValidationError if none.
file_url = client.files.upload(
    file_path: str,
    access_scope: str = "organization",
    workflow_id: str = None,     # one of workflow_id / workspace_id required
    workspace_id: str = None,
) -> str  # returns permanent file URL

# Upload from bytes
file_url = client.files.upload_bytes(
    data: bytes,
    file_extension: str,         # e.g. ".pdf"
    access_scope: str = "organization",
    workflow_id: str = None,     # one of workflow_id / workspace_id required
    workspace_id: str = None,
) -> str

# Get download URL
client.files.download(
    file_url: str,
    custom_expiry: int = None,   # seconds
) -> JobFileDownloadResponse     # .presigned_url, .content_type, .content_length

# Search files
client.files.search(
    query: str,                  # required
    media_type: str = None,      # "document" or "image"
    country: str = None,
    language: str = None,
    max_results: int = 25,
) -> FileSearchResponse

# Generate a file
client.files.generate(
    user_query: str,
    mime_type: str,
    file_extension: str,
    country: str = None,
) -> FileGenerateResponse

# Multipart upload for large files
file_url = client.files.multipart_upload(
    file_path: str,
    content_type: str,
    job_id: str = None,
    use_public_bucket: bool = False,
) -> str  # handles initiate + complete; aborts on failure

# Abort a multipart upload
client.files.multipart_abort(file_key: str, upload_id: str) -> AbortUploadResponse
```

---

## Reviews Resource

```python
# Initiate a review
client.reviews.initiate(
    job_execution_id: str,
    type: str,                      # "AGENT", "HUMAN", "HUMAN_TASK"
    node_id: str,
    node_name: str,
    workflow_id: str,
    review_payload: dict,           # data for reviewer
    input_definition_schema: dict,
    output_definition_schema: dict,
    webhook_callback: str,          # webhook URL
    assignee_id: str = None,
    max_duration: int = 24,         # hours
) -> ReviewInitiateResponse

# List reviews
client.reviews.list(type=None, status=None, offset=0, max_results=25) -> Any

# Get review details
client.reviews.get(review_id: str, type: str = None) -> Any

# Pick/release a review
client.reviews.pick(review_id: str) -> Any
client.reviews.release(review_id: str) -> Any

# Submit review result
client.reviews.submit_result(
    review_id: str,
    status: str,
    review_result: dict,            # {variable_name: ..., value: ...}
) -> ReviewSubmitResponse

# Submit review output
client.reviews.submit_output(
    review_id: str,
    accept: bool,
    updated: dict,
    comment: str = None,
) -> Any

# Submit human task output
client.reviews.submit_human_task_output(review_id: str, updated: dict) -> Any

# Check review status
client.reviews.check_status(job_id: str) -> Any
```

---

## API Keys Resource

```python
client.api_keys.create(
    name: str,
    scopes: list[str],
    expires_at: str = None,
    key_prefix: str = None,
) -> ApiKey                         # .key only returned on creation

client.api_keys.list() -> list
client.api_keys.list_scopes() -> ScopesResponse
client.api_keys.rotate(key_id: str) -> Any
client.api_keys.reset_limits(key_id: str) -> Any
client.api_keys.set_active(key_id: str, active: bool) -> Any
client.api_keys.revoke(key_id: str) -> None
client.api_keys.delete(key_id: str) -> None
```

---

## Credits Resource

```python
client.credits.get_balance() -> CreditBalance  # .credits, .credits_left
client.credits.create_balance(user_id: str, organization_id: str) -> CreditBalance
client.credits.get_usage() -> Any
client.credits.get_workflow_usage(workflow_id: str) -> Any
client.credits.record_usage(
    usage_type: str,               # "workflowGeneration" or "nodeExecution"
    workflow_id: str = None,
    node_id: str = None,
    node_type: str = None,
    node_name: str = None,
    credits_used: float = 0,
    description: str = None,
    generation_id: str = None,
) -> Any
```

---

## Policies Resource

```python
client.policies.list_types() -> Any
client.policies.upload(file_path: str, policy_type: str) -> Policy  # multipart/form-data
client.policies.list(
    page=1, limit=25, sort="DESC",
    policy_type=None, title=None, keyword=None,
) -> PolicyListResponse
client.policies.get(policy_id: str) -> Policy
client.policies.download(policy_id: str) -> Any
client.policies.get_summary(policy_id: str) -> PolicySummary
client.policies.update_summary(policy_id: str, summary: str = None) -> Any
client.policies.get_organization_summary() -> Any
client.policies.regenerate_blueprint() -> Any
client.policies.set_active(policy_id: str, active: bool) -> Any
client.policies.delete(policy_id: str) -> None
```

---

## Users Resource

```python
client.users.list(workspace_id: str = None) -> Any
client.users.list_projects(workspace_id: str = None) -> Any
client.users.get_projects(workspace_id: str = None) -> Any
```

---

## Error Handling

All errors inherit from `OpusError`:

```
OpusError (base)
    .message: str
    .status_code: int | None
    .body: Any | None
    .request_id: str | None

AuthenticationError          401 -- invalid API key
PermissionDeniedError        403 -- insufficient permissions
NotFoundError                404 -- resource not found
ValidationError              400 -- bad request parameters
RateLimitError               429 -- too many requests (.retry_after: float)
APIError                     5xx -- server error
TimeoutError                 request or polling timeout
ConnectionError              network failure
```

Usage:

```python
from opus_aaico import OpusClient, NotFoundError, RateLimitError, OpusError

try:
    result = client.workflows.run("wf-123", payload={...})
except NotFoundError:
    print("Workflow not found")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except OpusError as e:
    print(f"API error: {e.message} (status={e.status_code})")
```

The SDK automatically retries on 429 and 5xx with exponential backoff (1s, 2s, 4s, up to 30s). It does not retry on 400, 401, 403, 404.

---

## Enums

```python
from opus_aaico.types import JobStatus, ReviewType, ReviewStatus, MediaType

# Job statuses
JobStatus.PENDING | IN_PROGRESS | COMPLETED | FAILED | WAITING | CANCELLED | UNKNOWN

# Review types
ReviewType.AGENT | HUMAN | HUMAN_TASK

# Review statuses
ReviewStatus.PENDING | COMPLETED | FAILED | OVERDUE | DISPATCHED | NODE_DISPATCHED | NODE_DISPATCH_FAILED

# Media types
MediaType.IMAGE | DOCUMENT

# Credit usage types
CreditUsageType.WORKFLOW_GENERATION | NODE_EXECUTION

# Archive status
ArchiveStatus.ALL | ARCHIVED_ONLY | NON_ARCHIVED_ONLY

# Workflow source
WorkflowSource.WKG | USER_GENERATED

# Review setting type
ReviewSettingType.HUMAN_REVIEW | AGENTIC_REVIEW
```

---

## Key Pydantic Models

All models auto-convert between camelCase (API) and snake_case (Python).

### Workflow

```python
Workflow:
    workflow_id: str
    name: str
    description: str
    industry: str
    active: bool
    workflow_blueprint: WorkflowBlueprint
    execution_estimation: ExecutionEstimation
    job_payload_schema: dict[str, PayloadVariable]   # expected inputs
    job_results_payload_schema: dict
    created_at: str
```

### WorkflowRunResult

```python
WorkflowRunResult:
    status: str              # "COMPLETED", "FAILED", etc.
    job_id: str              # job execution ID
    outputs: dict | None     # workflow output variables
    execution_time: float    # seconds elapsed
    audit: JobAudit | None   # per-node execution data
```

### JobAudit

```python
JobAudit:
    nb_nodes: int
    nb_executed_nodes: int
    nb_failed_nodes: int
    executed_nodes: list[str]
    failed_nodes: list[str]
    remaining_nodes_to_execute: list[str]
    running_node: str | None
    nodes_execution_data: dict[str, NodeExecutionData]

NodeExecutionData:
    execution_status: str
    execution_time: int       # milliseconds
    execution_start_time: int
    execution_index: int
```

### PayloadVariable

```python
PayloadVariable:
    id: str
    variable_name: str
    display_name: str
    type: str                 # "str", "float", "bool", "date", "file", "array", "object"
    is_nullable: bool
```

### Other Key Models

```python
JobSearchItem:        title, description, job_execution_id, workflow_id, status, created_at
JobSearchResponse:    total_count, jobs: list[JobSearchItem]
FileMetadata:         file_id, file_uri, file_name, file_mime_type, file_extension
FileSearchResponse:   total_count, files: list[FileMetadata]
ApiKey:               id, name, key, scopes, is_active, created_at, expires_at
CreditBalance:        user_id, organization_id, credits, credits_left
Policy:               id, file_name, policy_type, summary, summary_status, policy_enabled
ReviewItem:           id, job_execution_id, type, status, node_id, node_name
```

---

## Common Patterns

### Run workflow with file upload

```python
client = OpusClient(api_key="sk-...")
file_url = client.files.upload("./document.pdf", workflow_id="wf-123")
result = client.workflows.run(
    workflow_id="wf-123",
    payload={
        "document": {"value": file_url, "type": "file"},
        "instructions": {"value": "Extract key findings", "type": "str"},
    },
)
```

### Poll with status callback

```python
def on_change(status):
    print(f"Status changed to: {status}")

result = client.workflows.run(
    workflow_id="wf-123",
    payload={...},
    on_status_change=on_change,
    poll_interval=3.0,
    timeout=600,
)
```

### Concurrent async execution

```python
import asyncio
from opus_aaico import AsyncOpusClient

async def run_batch():
    async with AsyncOpusClient(api_key="sk-...") as client:
        tasks = [
            client.workflows.run("wf-123", payload={"query": {"value": item, "type": "str"}})
            for item in ["doc1", "doc2", "doc3"]
        ]
        return await asyncio.gather(*tasks)
```

### Inspect workflow before running

```python
workflow = client.workflows.get("wf-123")
print(f"Name: {workflow.name}")
print(f"Active: {workflow.active}")
for var_name, var in (workflow.job_payload_schema or {}).items():
    print(f"  Input: {var.display_name} ({var.type}, nullable={var.is_nullable})")
```

### Search completed jobs

```python
jobs = client.jobs.search(
    workflow_id="wf-123",
    status=["COMPLETED"],
    start_date="2026-01-01",
    end_date="2026-03-31",
    max_results=100,
)
for job in jobs.jobs:
    print(f"{job.title}: {job.status} at {job.created_at}")
```

---

## Architecture Notes

- **HTTP layer:** `_client.py` contains `SyncHTTPClient` and `AsyncHTTPClient`, both extending `BaseClient`. Handles auth headers (`x-service-key`, `x-workspace-id`), retry logic, and error mapping.
- **Resources:** Each resource in `resources/` has both `Sync*` and `Async*` classes extending `SyncResource`/`AsyncResource`. Methods call `self._client.request(method, path, ...)`.
- **Types:** All in `types/` as Pydantic v2 models. Use `Field(alias="camelCase")` for API field mapping. Import from `opus_aaico.types`.
- **Polling:** `_utils/polling.py` provides `poll_sync`/`poll_async` with configurable interval, timeout, and status change callback.
- **File uploads:** `_utils/files.py` handles the presigned URL upload flow (get URL from API, PUT file to S3).
