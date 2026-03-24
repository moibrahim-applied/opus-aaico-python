"""Poll multiple jobs concurrently with async client."""
import asyncio

from opus_aaico import AsyncOpusClient


async def main():
    async with AsyncOpusClient(api_key="your-api-key-here") as client:
        # Run multiple workflows concurrently
        tasks = [
            client.workflows.run(
                workflow_id="your-workflow-id",
                payload={"query": {"value": f"Task {i}", "type": "str"}},
                title=f"Concurrent Job {i}",
            )
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            print(f"Job {i}: {result.status} in {result.execution_time:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
