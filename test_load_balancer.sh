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