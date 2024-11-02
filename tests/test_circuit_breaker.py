import asyncio
import aiohttp
import json
from datetime import datetime
import time

async def get_circuit_status(session):
    """Get current circuit breaker status"""
    url = "http://localhost:8000/test/circuit-breaker-status"
    async with session.get(url) as response:
        return await response.json()

async def make_chat_request(session, content="Hello"):
    """Make a chat request"""
    url = "http://localhost:8000/chat"
    try:
        async with session.post(
            url,
            json={"content": content}
        ) as response:
            return await response.json(), response.status
    except Exception as e:
        return {"error": str(e)}, 500

async def test_circuit_breaker():
    print("\nCircuit Breaker Test Suite")
    print("=========================")
    
    async with aiohttp.ClientSession() as session:
        # 1. Check initial state
        print("\n1. Initial Circuit Status:")
        status = await get_circuit_status(session)
        print(json.dumps(status, indent=2))

        # 2. Trigger failures
        print("\n2. Triggering failures...")
        for i in range(4):
            print(f"\nRequest {i+1}:")
            response, status_code = await make_chat_request(
                session, 
                content="trigger error"
            )
            print(f"Status Code: {status_code}")
            print(json.dumps(response, indent=2))
            
            status = await get_circuit_status(session)
            print("\nCircuit Status:")
            print(json.dumps(status, indent=2))
            await asyncio.sleep(1)

        # 3. Wait for recovery timeout
        print("\n3. Waiting for recovery timeout (30 seconds)...")
        await asyncio.sleep(30)

        # 4. Check status after timeout
        print("\n4. Circuit Status after timeout:")
        status = await get_circuit_status(session)
        print(json.dumps(status, indent=2))

        # 5. Test recovery
        print("\n5. Testing recovery...")
        response, status_code = await make_chat_request(session)
        print(f"Status Code: {status_code}")
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(test_circuit_breaker()) 