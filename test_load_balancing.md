# Create a test script:
## Create a python script

```python:tests/test_load_balancer.py
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
```


## Create a shell script for quick testing:

```bash:test_load_balancer.sh
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Load Balancer Distribution${NC}"
echo "================================="

# Function to make a request and extract region
make_request() {
    curl -s -X POST \
        http://localhost:8000/chat \
        -H 'Content-Type: application/json' \
        -d '{"content": "Hello"}' | jq -r .region
}

# Test round-robin distribution
echo -e "\n${GREEN}Testing Round Robin Distribution (10 requests):${NC}"
for i in {1..10}; do
    region=$(make_request)
    echo "Request $i: $region"
    sleep 0.5
done

# Show load balancer status
echo -e "\n${GREEN}Current Load Balancer Status:${NC}"
curl -s http://localhost:8000/test/load-balancer-status | jq

# Test concurrent requests
echo -e "\n${GREEN}Testing Concurrent Requests:${NC}"
for i in {1..5}; do
    make_request & 
done
wait

# Show final status
echo -e "\n${GREEN}Final Load Balancer Status:${NC}"
curl -s http://localhost:8000/test/load-balancer-status | jq
```


To run the tests:

1. Using Python script:
```bash
python tests/test_load_balancer.py
```


2. Using shell script:
```bash
chmod +x test_load_balancer.sh
./test_load_balancer.sh
```


Expected output example:
```
Testing Load Balancer Distribution
=================================

Testing Round Robin Distribution (10 requests):
Request 1: us-east-1
Request 2: us-west-2
Request 3: us-east-1
Request 4: us-west-2
Request 5: us-east-1
...

Current Load Balancer Status:
{
  "strategy": "round-robin",
  "endpoints": [
    {
      "region": "us-east-1",
      "healthy": true,
      "weight": 2
    },
    {
      "region": "us-west-2",
      "healthy": true,
      "weight": 1
    }
  ]
}
```


To test different scenarios:

1. Test Round Robin:
```bash
# Change in .env
LOAD_BALANCER_STRATEGY=round-robin
```


2. Test Weighted:
```bash
# Change in .env
LOAD_BALANCER_STRATEGY=weighted
```


3. Test Failover:
```bash
# Change in .env
LOAD_BALANCER_STRATEGY=failover
```