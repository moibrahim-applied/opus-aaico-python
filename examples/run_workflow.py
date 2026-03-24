"""Run a workflow end-to-end with the high-level run() method."""
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key-here")

# The run() method handles: initiate -> execute -> poll -> results
result = client.workflows.run(
    workflow_id="your-workflow-id",
    payload={
        "query": {"value": "Analyze this document", "type": "str"},
    },
    title="My Analysis Job",
    poll_interval=2.0,  # Check every 2 seconds
    timeout=300,  # Wait up to 5 minutes
)

print(f"Status: {result.status}")
print(f"Job ID: {result.job_id}")
print(f"Execution time: {result.execution_time:.1f}s")
if result.outputs:
    print(f"Outputs: {result.outputs}")
