
# Circuit Breaker Testing Guide

## Prerequisites
- Server running on `http://localhost:8000`
- `curl` and `jq` installed
- Python environment with required packages

## Test Commands

### 1. Basic Status Check
```bash
# Check current circuit breaker status
curl http://localhost:8000/test/circuit-status | jq

# Expected Response:
{
  "circuit_state": "closed",
  "failure_count": 0,
  "current_failures": 0,
  "failures_enabled": false
}
```

### 2. Failure Simulation Controls
```bash
# Enable failures
curl -X POST http://localhost:8000/test/enable-failures | jq

# Disable failures and reset circuit
curl -X POST http://localhost:8000/test/disable-failures | jq
```

### 3. Chat Endpoint Tests
```bash
# Basic chat request
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"content": "Hello"}' | jq

# Chat with system prompt
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "Hello",
    "system_prompt": "You are a helpful assistant"
  }' | jq
```

### 4. Complete Test Script
```bash
#!/bin/bash

# Test script for circuit breaker functionality
echo "1. Checking initial circuit status..."
curl http://localhost:8000/test/circuit-status | jq

echo -e "\n2. Enabling failures..."
curl -X POST http://localhost:8000/test/enable-failures | jq

echo -e "\n3. Making requests to trigger circuit breaker..."
for i in {1..4}; do 
    echo -e "\nRequest $i:"
    curl -X POST \
        http://localhost:8000/chat \
        -H 'Content-Type: application/json' \
        -d '{"content": "Hello"}' | jq
    echo -e "\nCircuit status after request $i:"
    curl http://localhost:8000/test/circuit-status | jq
    sleep 1
done

echo -e "\n4. Disabling failures and resetting circuit..."
curl -X POST http://localhost:8000/test/disable-failures | jq

echo -e "\n5. Final circuit status check..."
curl http://localhost:8000/test/circuit-status | jq
```

### 5. Recovery Test Script
```bash
#!/bin/bash

# Test circuit breaker recovery
echo "1. Enable failures"
curl -X POST http://localhost:8000/test/enable-failures | jq

echo -e "\n2. Trigger circuit breaker..."
for i in {1..3}; do 
    curl -X POST \
        http://localhost:8000/chat \
        -H 'Content-Type: application/json' \
        -d '{"content": "Hello"}' | jq
    sleep 1
done

echo -e "\n3. Wait for recovery timeout (30 seconds)..."
sleep 30

echo -e "\n4. Test recovery with new request..."
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"content": "Hello"}' | jq
```

### 6. Status Monitoring Script
```bash
#!/bin/bash

# Monitor circuit status every second
echo "Monitoring circuit status (Ctrl+C to stop)..."
while true; do 
    clear
    date
    curl -s http://localhost:8000/test/circuit-status | jq
    sleep 1
done
```

## Expected Responses

### Success Response
```json
{
    "response": "Hello! I'm Claude, how can I help you today?",
    "token_usage": {
        "inputTokens": 20,
        "outputTokens": 43,
        "totalTokens": 63
    },
    "stop_reason": "end_turn",
    "status": "success"
}
```

### Circuit Open Response
```json
{
    "detail": "Circuit breaker is open. Service is unavailable."
}
```

### Circuit Status States
```json
# Closed State (Normal)
{
    "circuit_state": "closed",
    "failure_count": 0,
    "current_failures": 0,
    "failures_enabled": false
}

# Open State (After Failures)
{
    "circuit_state": "open",
    "failure_count": 3,
    "current_failures": 3,
    "failures_enabled": true
}
```

## Running Test Scripts

```bash
# Make scripts executable
chmod +x test_circuit.sh
chmod +x test_recovery.sh
chmod +x monitor_status.sh

# Run complete test
./test_circuit.sh

# Run recovery test
./test_recovery.sh

# Run status monitor
./monitor_status.sh
```

## Troubleshooting

If you encounter errors, check:
1. Server is running (`python main.py`)
2. Correct port (8000)
3. `jq` is installed (`apt-get install jq` or `brew install jq`)
4. Proper JSON formatting in requests
5. Network connectivity to localhost

## PowerShell Variants (Windows)

```powershell
# Basic request in PowerShell
curl -X POST `
  http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"content\": \"Hello\"}" | ConvertFrom-Json | ConvertTo-Json
```
```
