#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Circuit Breaker Status Monitor${NC}"
echo "============================"

while true; do
    clear
    echo -e "${GREEN}$(date)${NC}"
    echo "Circuit Breaker Status:"
    curl -s http://localhost:8000/test/circuit-breaker-status | jq
    sleep 1
done 