"""Upload a file and use it in a workflow."""
from opus_aaico import OpusClient

client = OpusClient(api_key="your-api-key-here")

# Upload a file (handles presigned URL flow automatically)
file_url = client.files.upload("./report.pdf")
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
