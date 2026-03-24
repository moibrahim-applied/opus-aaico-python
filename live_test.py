"""Live test of the opus-aaico SDK against a real OPUS workflow."""
from opus_aaico import OpusClient

API_KEY = "_f68791cc9ed4ac10f134af8efbb66d939e14a1acdeb4d687b3912f2b12ea385e8e1e182b047037126d6e346276347132"
WORKFLOW_ID = "ysgyFQl8iW7vs8FA"

client = OpusClient(api_key=API_KEY)

print("=" * 60)
print("opus-aaico SDK -- Live Test")
print("=" * 60)

# 1. Get workflow details
print("\n[1] Fetching workflow details...")
workflow = client.workflows.get(WORKFLOW_ID)
print(f"    Name: {workflow.name}")
print(f"    Active: {workflow.active}")
for var_name, var in (workflow.job_payload_schema or {}).items():
    print(f"    Input: {var_name} ({var.type})")

# 2. Run the workflow end-to-end
print("\n[2] Running workflow with workflows.run()...")
result = client.workflows.run(
    workflow_id=WORKFLOW_ID,
    payload={
        "workflow_input_9m8mw83yb": {
            "value": "Hello from the opus-aaico Python SDK! This is a live test.",
            "type": "str",
        },
    },
    title="SDK Live Test",
    description="Testing the opus-aaico Python SDK",
    poll_interval=2.0,
    timeout=120,
    on_status_change=lambda s: print(f"    Status: {s}"),
)

print(f"\n[3] Results:")
print(f"    Status: {result.status}")
print(f"    Job ID: {result.job_id}")
print(f"    Execution Time: {result.execution_time:.1f}s")
if result.outputs:
    print(f"    Outputs: {result.outputs}")
if result.audit:
    print(f"    Nodes executed: {result.audit.executed_nodes}")
    print(f"    Nodes failed: {result.audit.failed_nodes}")

print("\n" + "=" * 60)
print("Test complete.")
print("=" * 60)
