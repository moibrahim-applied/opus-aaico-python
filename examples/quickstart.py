"""Quickstart -- get workflow details in 4 lines."""
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key-here")

# Get workflow details
workflow = client.workflows.get("your-workflow-id")
print(f"Workflow: {workflow.name}")
print(f"Active: {workflow.active}")
if workflow.job_payload_schema:
    print(f"Expected inputs: {list(workflow.job_payload_schema.keys())}")
