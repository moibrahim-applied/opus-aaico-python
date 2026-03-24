# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/moibrahim-applied/opus-aaico-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/moibrahim-applied/opus-aaico-python/releases/tag/v0.1.0
