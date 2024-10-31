#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Circuit Breaker${NC}"
echo "====================="

# Get initial circuit status
echo -e "\n${GREEN}1. Initial circuit status:${NC}"
curl -s http://localhost:8000/test/circuit-breaker-status | jq

# Trigger circuit breaker
echo -e "\n${GREEN}2. Triggering circuit breaker...${NC}"
for i in {1..4}; do
    echo -e "\n${BLUE}Request $i:${NC}"
    curl -s -X POST \
        http://localhost:8000/chat \
        -H 'Content-Type: application/json' \
        -d '{"content": "trigger error"}' | jq
    sleep 1
done

# Check circuit status after failures
echo -e "\n${GREEN}3. Circuit status after failures:${NC}"
curl -s http://localhost:8000/test/circuit-breaker-status | jq

# Wait for recovery
echo -e "\n${GREEN}4. Waiting for recovery timeout (30 seconds)...${NC}"
sleep 30

# Check circuit status after timeout
echo -e "\n${GREEN}5. Circuit status after timeout:${NC}"
curl -s http://localhost:8000/test/circuit-breaker-status | jq

# Test recovery
echo -e "\n${GREEN}6. Testing recovery...${NC}"
curl -s -X POST \
    http://localhost:8000/chat \
    -H 'Content-Type: application/json' \
    -d '{"content": "Hello"}' | jq 