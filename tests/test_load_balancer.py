import asyncio
import aiohttp
import json
from collections import Counter
import time

async def make_request(session, url, message):
    async with session.post(url, json={"content": message}) as response:
        return await response.json()

async def test_round_robin():
    url = "http://localhost:8000/chat"
    message = "Hello"
    requests_per_batch = 10
    num_batches = 3
    
    print("\nTesting Round Robin Load Balancing")
    print("==================================")
    
    async with aiohttp.ClientSession() as session:
        for batch in range(num_batches):
            print(f"\nBatch {batch + 1}:")
            
            # Create tasks for concurrent requests
            tasks = [
                make_request(session, url, message)
                for _ in range(requests_per_batch)
            ]
            
            # Execute requests concurrently
            responses = await asyncio.gather(*tasks)
            
            # Analyze region distribution
            regions = [resp['region'] for resp in responses]
            distribution = Counter(regions)
            
            print("\nRegion Distribution:")
            for region, count in distribution.items():
                print(f"{region}: {count} requests ({count/len(regions)*100:.1f}%)")
            
            # Small delay between batches
            time.sleep(1)

async def test_failover():
    print("\nTesting Failover Scenario")
    print("========================")
    
    # First, check initial status
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/test/load-balancer-status") as response:
            initial_status = await response.json()
            print("\nInitial Status:", json.dumps(initial_status, indent=2))
        
        # Simulate primary region failure
        print("\nSimulating primary region failure...")
        url = "http://localhost:8000/chat"
        
        # Make requests and observe failover
        for i in range(5):
            response = await make_request(session, url, "Hello")
            print(f"\nRequest {i+1} handled by region: {response['region']}")
            time.sleep(1)

def main():
    print("Load Balancer Testing")
    print("====================")
    
    # Run tests
    asyncio.run(test_round_robin())
    asyncio.run(test_failover())

if __name__ == "__main__":
    main() 