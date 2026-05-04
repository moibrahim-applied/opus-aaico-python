# Migrating to opus-aaico v0.5

**Audience:** Anyone running `opus-aaico` v0.4.x or earlier in production.

**Bottom line:** Upgrading should not take working software down. The "breaking" changes in v0.5 fix calls that were already broken on the platform side — `workflows.get()`, `workflows.run()`, `jobs.initiate()`, `credits.get_balance()` and friends were returning errors regardless of SDK version, because OPUS deprecated their underlying endpoints. v0.5 makes those calls work again (where the platform allows) or fail clearly (where it doesn't). Code paths that worked in v0.4 still work in v0.5.

This document is the canonical reference for the v0.4 → v0.5 migration.

---

## TL;DR — will my code break?

| Code pattern | v0.4 behavior | v0.5 behavior | Action needed |
|---|---|---|---|
| `client.workflows.list_industries()`, `list_public()` | Worked | Works | None |
| `client.api_keys.list()`, `list_scopes()` | Worked | Works | None |
| `client.reviews.list()` | Worked | Works | None |
| `client.jobs.search()`, `get_status()`, `get_audit()`, `get_results()` | Worked | Works | None |
| `client.workflows.get(uuid)` | **500 error** every call | Returns full v2 graph | If you parse the result, **read the new fields** (see below) |
| `client.workflows.run(uuid, …)` | **400 error** every call | Works | Pass a UUID, not a 16-char short ID |
| `client.jobs.initiate(uuid, …)` | **400 error** every call | Works | Same — pass a UUID |
| `client.credits.get_balance()` / `get_usage()` / `record_usage()` | **404 error** every call | Raises `NotSupportedError` | Switch to `credits.history()` / `credits.current_balance()` |
| `client.users.list()` / `policies.list()` / `files.search()` | 401 "No auth cookie" | `NotSupportedError` (clear message) | These can't be reached with API keys at all — remove the calls or use the OPUS web UI |
| `str(error)` after a validation failure | `<exception str() failed>` (TypeError) | Renders real message | Pure fix, no action |

**If a row says "Worked / Works": your code is unaffected. Move on.**

---

## Why this happened

OPUS shipped v2 of the platform earlier in 2026. They upgraded `operator.opus.com` in place rather than putting v2 on a new host. As part of that upgrade:

1. **Workflow IDs moved from short slugs to UUIDs.** The 16-character ID you see in the v1 URL bar (`4k4bJCXrUJE1XWzF`) is no longer a valid identifier. Workflows now have UUIDs (`3f69dcbf-713a-493d-8d08-3fdb754825ab`).
2. **The `/workflow/{id}` endpoint was deprecated.** Replaced by `/reference-workflow/v2/workflow-object/{uuid}`, which returns a much richer object (full graph: nodes, edges, schemas, version info).
3. **Credits endpoints were rewritten.** `/credits/balance`, `/credits/usage`, `/credits/usage/workflow/{id}` were deleted. Everything is now in `/credits/history` (a single transaction log with running balance).
4. **Several read endpoints became browser-cookie-only.** `/users`, `/policies`, `/files/search`, `/tags` no longer accept API keys; they require an authenticated browser session.

The opus-aaico v0.4 SDK still pointed at the v1 endpoints. v0.5 catches up.

---

## Will my software be down?

**Almost certainly no.** Here's the reasoning:

- **If your software was working last week**, it's working through endpoints that v0.5 hasn't touched. Same calls, same responses.
- **If your software was failing last week** with `<exception str() failed>` or 500 errors, v0.5 either fixes the call (UUID validation + v2 endpoint) or surfaces a clear, actionable error message. You weren't running the broken paths in production anyway.
- **The one real schema change** is `workflows.get()` returning `WorkflowObject` instead of `Workflow`. But since v0.4 was returning HTTP 500 for every `workflows.get()` call, no production code is currently consuming the old `Workflow` shape — it never received one to consume.

**The only failure mode** that could surprise you is code that swallows exceptions silently — e.g., `try: client.workflows.get(...) except: pass`. That code was previously hiding a permanent 500. v0.5 still raises an exception (caught by `except: pass`), so behavior doesn't change.

**Recommendation before upgrading prod:**
1. Install in a venv and run the [smoke test snippet](#smoke-test-after-upgrading) below.
2. Skim your codebase for the changed methods (use the [find-and-replace cheatsheet](#find-and-replace-cheatsheet) below).
3. Roll out to staging for an hour, then prod.

---

## Migration recipes

### 1. `workflows.get()` returns a new shape

**v0.4** (broken — was returning HTTP 500, but if it had returned the spec'd shape):
```python
wf = client.workflows.get(workflow_id)
print(wf.name, wf.active, wf.industry)
print(wf.job_payload_schema)  # input variables
```

**v0.5**:
```python
wf = client.workflows.get(workflow_uuid)  # must be a UUID now
print(wf.name, wf.active_status == "active")
print(wf.input_variables)                 # convenience property
# new: full graph access
print(f"{len(wf.nodes)} nodes, {len(wf.edges)} edges")
for node in wf.nodes.values():
    print(node.id, node.type, node.name)
```

Field mapping:

| v0.4 `Workflow` | v0.5 `WorkflowObject` |
|---|---|
| `wf.workflow_id` | `wf.workflow_id` (same) |
| `wf.name` | `wf.name` |
| `wf.description` | `wf.description` |
| `wf.active` (bool) | `wf.active_status == "active"` |
| `wf.job_payload_schema` | `wf.input_variables` (property) |
| `wf.industry`, `wf.workflow_image` | gone — not in v2 |
| `wf.execution_estimation` | use `client.workflows.estimate(id)` |
| (didn't exist) | `wf.nodes`, `wf.edges`, `wf.version`, `wf.workspace_id` |

### 2. Pass UUIDs, not short IDs

**v0.4** (already broken in practice — API rejected non-UUIDs):
```python
client.workflows.run("4k4bJCXrUJE1XWzF", payload)   # 400 error
```

**v0.5**:
```python
# Find the UUID at https://app.opus.com — it's in the URL after /builder/workflow/
client.workflows.run("3f69dcbf-713a-493d-8d08-3fdb754825ab", payload)
```

If you pass a non-UUID, v0.5 raises `ValidationError` with a clear message before the API call:
```
'workflow_id' must be a UUID. OPUS v2 uses UUIDs for workflow IDs.
The legacy 16-char short IDs from the URL bar are no longer accepted.
Open your workflow at https://app.opus.com to copy its UUID.
```

### 3. Credits methods consolidated into `history()`

**v0.4** (broken — endpoints were 404):
```python
balance = client.credits.get_balance().credits_left
usages = client.credits.get_usage()
client.credits.record_usage(usage_type="nodeExecution", credits_used=5.0)
```

**v0.5**:
```python
balance = client.credits.current_balance()
history = client.credits.history(max_results=100)
for entry in history:
    print(entry.date, entry.credits_used, entry.balance_after)
# record_usage / create_balance / get_workflow_usage no longer supported
```

Calling the removed methods raises `NotSupportedError` with the migration hint baked in.

### 4. Cookie-only endpoints raise `NotSupportedError`

**v0.4**:
```python
try:
    users = client.users.list()
except AuthenticationError:
    print("Auth failed?")  # misleading — it wasn't an auth issue
```

**v0.5**:
```python
from opus_aaico import NotSupportedError
try:
    users = client.users.list()
except NotSupportedError as e:
    # Clear message: "This endpoint requires a browser session cookie..."
    print(str(e))
```

`NotSupportedError` inherits from `OpusError`. If your code does `except OpusError:` (the recommended pattern), nothing changes.

### 5. New: walk the workflow graph for sub-workflow tracing

```python
wf = client.workflows.get(workflow_uuid)
subs = wf.find_sub_workflows()
for s in subs:
    print(f"{s['node_name']} -> handler {s['handler_id']}")
```

Use `client.workflows.list_versions(uuid)` to enumerate versions:
```python
versions = client.workflows.list_versions(workflow_uuid)
print(f"latest: v{versions.latest_version}, total: {len(versions.versions)}")
```

---

## Find-and-replace cheatsheet

Run these greps against your codebase to find anything that needs touching:

```bash
# Calls that may need a UUID
grep -rn "workflows\.get\|workflows\.run\|jobs\.initiate" your_code/

# Removed credits methods
grep -rn "credits\.get_balance\|credits\.get_usage\|credits\.record_usage\|credits\.create_balance" your_code/

# Cookie-only endpoints (will now raise NotSupportedError)
grep -rn "users\.list\|policies\.list\|files\.search\b" your_code/

# Catching only AuthenticationError on cookie-only calls (rare but possible)
grep -rn -A2 "except AuthenticationError" your_code/
```

Anything not flagged by those greps doesn't need migration work.

---

## Smoke test after upgrading

```python
from opus_aaico import OpusClient

client = OpusClient(api_key="YOUR_KEY")

# Should still work (untouched in v0.5)
print(client.api_keys.list())
print(client.workflows.list_industries())
print(client.jobs.search(max_results=1).total_count)

# New v0.5 capability
print(client.credits.current_balance())

# Should raise NotSupportedError with a clear message
from opus_aaico import NotSupportedError
try: client.credits.get_balance()
except NotSupportedError as e: print("OK:", str(e)[:80])
```

If all five lines run without surprise, you're good.

---

## Rollback

If v0.5 surfaces something unexpected and you need to roll back:

```bash
pip install opus-aaico==0.4.0
```

Note: rolling back returns you to the broken state — `workflows.get()` and friends will resume returning HTTP 500. Use only as a temporary measure while reporting the issue.

---

## Reporting issues

File at: https://github.com/moibrahim-applied/opus-aaico-python/issues

Include:
- SDK version (`python -c "import opus_aaico; print(opus_aaico.__version__)"`)
- The exact call you're making
- The full exception traceback (now readable, since v0.5 fixed `__str__`)
