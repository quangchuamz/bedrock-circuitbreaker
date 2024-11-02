#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Region Recovery Scenario${NC}"
echo "============================="

# Function to check circuit status
check_status() {
    echo -e "\n${GREEN}Circuit Status:${NC}"
    curl -s http://localhost:8000/test/circuit-breaker-status | jq
}

# Function to make a chat request
make_request() {
    curl -s -X POST \
        http://localhost:8000/chat \
        -H 'Content-Type: application/json' \
        -d '{"content": "hello"}' | jq
}

# 1. Initial Status
echo -e "\n${GREEN}1. Initial Status${NC}"
check_status

# 2. Trigger failures for ap-southeast-1
echo -e "\n${GREEN}2. Triggering failures for ap-southeast-1${NC}"
for i in {1..5}; do
    echo -e "\n${BLUE}Request $i:${NC}"
    make_request
    sleep 1
done

# 3. Check status after failures
echo -e "\n${GREEN}3. Status after failures${NC}"
check_status

# 4. Wait for recovery timeout
echo -e "\n${GREEN}4. Waiting for recovery timeout (30 seconds)...${NC}"
sleep 30

# 5. Set region mapping before recovery
echo -e "\n${GREEN}5. Setting region mapping (ap-southeast-1 -> us-west-2)${NC}"
curl -s -X POST \
    "http://localhost:8000/test/set-region-mapping?source_region=ap-southeast-1&target_region=us-west-2"

# 6. Test recovery with mapped region
echo -e "\n${GREEN}6. Testing recovery with mapped region${NC}"
for i in {1..2}; do
    echo -e "\n${BLUE}Recovery request $i:${NC}"
    make_request
    sleep 1
done

# 7. Check half-open status
echo -e "\n${GREEN}7. Half-open status${NC}"
check_status

# 8. Continue making requests to reach recovery threshold (successful requests)
echo -e "\n${GREEN}8. Continuing to make requests to reach recovery threshold (successful requests)${NC}"
for i in {1..3}; do
    echo -e "\n${BLUE}Recovery request $i:${NC}"
    make_request
    sleep 1
done

# 9. Check final status
echo -e "\n${GREEN}7. Final Status${NC}"
check_status

# 8. Clear region mapping
echo -e "\n${GREEN}8. Clearing region mapping${NC}"
curl -s -X DELETE http://localhost:8000/test/clear-region-mapping

# 9. Verify original region is working
echo -e "\n${GREEN}9. Verifying original region${NC}"
make_request
check_status 