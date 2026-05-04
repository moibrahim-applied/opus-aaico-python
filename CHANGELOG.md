# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-05-04

### Fixed (production-blocking)

- **`OpusError.__str__` no longer crashes on list-shaped error bodies.** The OPUS API returns NestJS-style validator errors as `{"message": ["error1", "error2"]}`. The previous implementation produced `<exception str() failed>` instead of the real message. Validation errors now render readably (e.g. `"workflowId must be a UUID; title must be present"`).
- **`workflows.get(workflow_id)` works again.** It now calls the v2 endpoint `/reference-workflow/v2/workflow-object/{uuid}` and returns the full graph (nodes, edges, schemas). The legacy `/workflow/{id}` route was removed by the platform and returned HTTP 500 "V1 workflow details are no longer supported" for every call.
- **`jobs.initiate()` and `workflows.run()` work again** with v2 workflow UUIDs. The platform now requires UUIDs; the SDK validates the input up-front and returns a clear error pointing users to `app.opus.com` if they paste a 16-character short ID.
- **Cookie-only endpoints raise `NotSupportedError` with a clear message.** `users.list`, `policies.list`, `files.search`, and `tags` were silently rejecting API keys with a vague 401 "No auth cookie provided"; users now get an explicit "browser session cookie required, not reachable from the SDK" message.

### Added

- **`WorkflowObject`, `WorkflowNode`, `WorkflowEdge` types** modelling the full v2 workflow graph (nodes dict, edges dict, parent/child adjacency, input/output node IDs, environment variables, execution settings).
- **`WorkflowObject.input_variables` property** for ergonomic access to input schema.
- **`WorkflowObject.find_sub_workflows()` helper** that walks the graph and returns every Execute-Workflow style node — useful for tracing master → sub workflow relationships.
- **`workflows.list_versions(workflow_id)`** — returns all versions of a v2 workflow (latest_version + array of `WorkflowVersionItem`).
- **`credits.history(offset, max_results)`** replaces the removed `credits.balance()` and `credits.usage()`; returns `list[CreditHistoryEntry]` with running balance.
- **`credits.current_balance()`** convenience that returns the latest `balance_after`.
- **`api_keys.scopes()`** alias for `api_keys.list_scopes()`.
- **`users.projects()`** alias for `users.list_projects()`.
- **`NotSupportedError`** exception for endpoints unreachable with API keys (e.g., cookie-only ones).
- **UUID validation helper** at `opus_aaico._utils.ids.require_uuid()` raising `ValidationError` with a migration hint for non-UUIDs.

### Removed (raise `NotSupportedError` instead)

- `credits.get_balance()`, `credits.create_balance()`, `credits.get_usage()`, `credits.get_workflow_usage()`, `credits.record_usage()` — `/credits/balance` and `/credits/usage` were deleted by the platform (404 "Cannot GET"). Use `credits.history()` instead.

### Changed

- `workflows.get()` now returns `WorkflowObject` (rich v2 shape) instead of `Workflow` (sparse v1 shape). The old `Workflow` type still exists and is still returned by listing endpoints.
- `OpusError.__str__` now defensively coerces non-string messages, so any future API quirk yields readable output instead of a `TypeError`.

### Notes for production users

- Pass workflow UUIDs (from `https://app.opus.com/app/workflow/<UUID>` or `app/builder/workflow/<UUID>`), not the legacy 16-character short IDs.
- The legacy v1 OPUS API (`/workflow/private`, `/workflow/{id}`, `/workflow/workflowObject/{id}`) is dead. Most other endpoints (`/job/initiate`, `/job/execute`, `/job/{id}/status`, `/job/{id}/results`, `/job/{id}/audit`, etc.) still work on the same host (`operator.opus.com`) — the SDK was updated where it needed to be, no host change required.
- 114 tests passing. Live-tested against a real v2 workflow.

## [0.1.0] - 2026-03-24

### Added

- Initial release of the opus-aaico Python SDK.
- `OpusClient` (synchronous) and `AsyncOpusClient` (asynchronous) clients.
- 8 resource modules covering all 64 OPUS API endpoints:
  - **Workflows** -- get, list, list_public, generate, feed, share, send_email, list_industries, and the high-level `run()` orchestrator.
  - **Jobs** -- initiate, execute, get_status, get, get_results, get_audit, search, archive, unarchive, duplicate, delete, and `poll()` with configurable timeout.
  - **Files** -- upload (with presigned URL handling), upload_bytes, download, search, generate, multipart_upload, multipart_abort.
  - **Reviews** -- initiate, list, get, pick, release, submit_result, submit_output, submit_human_task_output, check_status.
  - **API Keys** -- create, list, list_scopes, rotate, reset_limits, set_active, revoke, delete.
  - **Credits** -- get_balance, create_balance, get_usage, get_workflow_usage, record_usage.
  - **Policies** -- list_types, upload (multipart/form-data), list, get, download, get_summary, update_summary, get_organization_summary, regenerate_blueprint, set_active, delete.
  - **Users** -- list, list_projects, get_projects.
- Pydantic v2 models for all request and response types with automatic camelCase conversion.
- Typed error hierarchy: OpusError, AuthenticationError, PermissionDeniedError, NotFoundError, ValidationError, RateLimitError, APIError, TimeoutError, ConnectionError.
- Automatic retry with exponential backoff on 429 and 5xx responses.
- Context manager support for both sync and async clients.
- Environment variable configuration: OPUS_API_KEY, OPUS_WORKSPACE_ID, OPUS_BASE_URL.
- Python 3.9 through 3.13 support.
- 107 tests covering all resources, error handling, retry logic, and client configuration.

[Unreleased]: https://github.com/moibrahim-applied/opus-aaico-python/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/moibrahim-applied/opus-aaico-python/releases/tag/v0.5.0
[0.1.0]: https://github.com/moibrahim-applied/opus-aaico-python/releases/tag/v0.1.0
