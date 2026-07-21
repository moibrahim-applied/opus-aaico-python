"""Upload a file and use it in a workflow."""
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key-here")

# Upload a file (handles presigned URL flow automatically).
# /job/file/upload now requires a scope: pass workflow_id= or workspace_id=
# (or configure a default workspace on the client / OPUS_WORKSPACE_ID).
file_url = client.files.upload("./report.pdf", workflow_id="your-workflow-id")
print(f"Uploaded: {file_url}")

# Use the uploaded file in a workflow
result = client.workflows.run(
    workflow_id="your-workflow-id",
    payload={
        "document": {"value": file_url, "type": "file"},
        "query": {"value": "Summarize this report", "type": "str"},
    },
)
print(f"Result: {result.outputs}")
