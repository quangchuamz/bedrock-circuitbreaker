# Claude Bedrock Service with Circuit Breaker and Load Balancing

A FastAPI service that integrates with AWS Bedrock for Claude 3 Sonnet, featuring circuit breaker pattern and load balancing capabilities.

## Features

- AWS Bedrock integration with Claude 3 Sonnet
- Multi-region load balancing (Round Robin, Weighted, Failover)
- Circuit breaker pattern for fault tolerance
- Testing utilities and failure simulation
- Comprehensive monitoring endpoints

## Prerequisites

- Python 3.8+
- AWS credentials with Bedrock access
- `curl` and `jq` for testing (optional)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with AWS credentials:
```plaintext
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION_1=us-east-1
AWS_REGION_2=us-west-2
LOAD_BALANCER_STRATEGY=round-robin
```

## Usage

Start the server:
```bash
python main.py
```

The server will run on `http://localhost:8000`

### Basic Chat Request

```bash
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "Hello",
    "system_prompt": "You are a helpful assistant"
  }'
```

## Load Balancing

The service supports three load balancing strategies:
- Round Robin (default)
- Weighted
- Failover

### Monitor Load Balancer Status

```bash
curl http://localhost:8000/test/load-balancer-status | jq
```

### Test Load Balancing Distribution

Run the load balancer test script:
```bash
chmod +x test_load_balancer.sh
./test_load_balancer.sh
```

## Circuit Breaker

The service implements a circuit breaker pattern with the following configuration:
- Failure threshold: 3 attempts
- Recovery timeout: 30 seconds
- States: CLOSED, OPEN, HALF-OPEN

### Monitor Circuit Status

```bash
curl http://localhost:8000/test/circuit-status | jq
```

### Test Circuit Breaker

1. Enable failure simulation:
```bash
curl -X POST http://localhost:8000/test/enable-failures | jq
```

2. Make requests to trigger the circuit breaker:
```bash
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"content": "Hello"}'
```

3. Disable failures and reset:
```bash
curl -X POST http://localhost:8000/test/disable-failures | jq
```

## Testing Scripts

### Complete Test Suite
```bash
# Make scripts executable
chmod +x test_circuit.sh
chmod +x test_load_balancer.sh
chmod +x test_recovery.sh

# Run tests
./test_circuit.sh
./test_load_balancer.sh
./test_recovery.sh
```

## API Response Examples

### Successful Response
```json
{
    "response": "Hello! I'm Claude, how can I help you today?",
    "region": "us-east-1",
    "token_usage": {
        "inputTokens": 20,
        "outputTokens": 43,
        "totalTokens": 63
    },
    "stop_reason": "end_turn",
    "status": "success"
}
```

### Circuit Breaker Open Response
```json
{
    "detail": "Circuit breaker is open. Service is unavailable."
}
```

## Project Structure

- `app/`
  - `core/` - Core configuration and settings
  - `services/` - Main service implementations
  - `testing/` - Test utilities and routes
- `tests/` - Test files
- `main.py` - FastAPI application entry point

## Error Handling

The service includes comprehensive error handling for:
- Circuit breaker state changes
- Load balancer failover scenarios
- AWS Bedrock API failures
- General service exceptions

## Contributing

1. Initialize GitFlow:
```bash
git flow init
```

2. Create a new feature branch:
```bash
git flow feature start feature-name
```

3. Make changes and commit
4. Finish feature:
```bash
git flow feature finish feature-name
```

## License

MIT
```

This README is based on the following code references:


````1:202:README.md
# Hello
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


***1:43:main.py***

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from circuitbreaker import CircuitBreakerError
from app.services.bedrock_service import bedrock_service
from app.testing.test_routes import test_router

app = FastAPI()
app.include_router(test_router)

class Message(BaseModel):
    content: str
    system_prompt: str | None = None

@app.post("/chat")
async def chat(message: Message):
    try:
        response = await bedrock_service.generate_conversation(
            message_content=message.content,
            system_prompt=message.system_prompt
        )
        
        return {
            "response": response['output']['message']['content'][0]['text'],
            "region": response['region'],
            "token_usage": response['usage'],
            "stop_reason": response['stopReason'],
            "status": "success"
        }

    except CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Circuit breaker is open. Service is unavailable."
        )
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service temporarily unavailable. Error: {str(e)}"
        )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```



***1:91:app/services/bedrock_service.py***
```python
import boto3
from fastapi import HTTPException
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.circuit_handler import circuit_handler, check_failure_simulation
from app.services.load_balancer import LoadBalancer
import logging

logger = logging.getLogger(__name__)

class BedrockEndpoint:
    def __init__(self, region: str):
        self.region = region
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
class BedrockService:
    def __init__(self):
        self.load_balancer = LoadBalancer(strategy=settings.LOAD_BALANCER_STRATEGY)
        
        # Add endpoints with weights (higher weight = more traffic)
        self.load_balancer.add_endpoint(
            BedrockEndpoint(settings.AWS_REGION_1), 
            weight=2  # Primary region gets more traffic
        )
        self.load_balancer.add_endpoint(
            BedrockEndpoint(settings.AWS_REGION_2), 
            weight=1  # Secondary region gets less traffic
        )
        
        self._setup_circuit_breaker()

    def _setup_circuit_breaker(self):
        @circuit_handler.decorate
        async def wrapped(*args, **kwargs):
            return await self._generate_conversation_impl(*args, **kwargs)
        self.generate_conversation = wrapped
    async def _generate_conversation_impl(self, message_content: str, system_prompt: str | None = None):
        check_failure_simulation()

        try:
            endpoint = self.load_balancer.get_next_endpoint()
            
            system_prompts = [{"text": system_prompt or "You are a helpful AI assistant."}]
            messages = [{
                "role": "user",
                "content": [{"text": message_content}]
            }]

            try:
                response = endpoint.client.converse(
                    modelId=settings.MODEL_ID,
                    messages=messages,
                    system=system_prompts,
                    inferenceConfig={"temperature": 0.5},
                    additionalModelRequestFields={"top_k": 200}
                )
                
                # Add region information to response
                response['region'] = endpoint.region
                
                # Mark endpoint as healthy on successful response
                self.load_balancer.mark_endpoint_healthy(endpoint)
                
                self._log_token_usage(response)
                return response

            except ClientError as err:
                # Mark endpoint as unhealthy on failure
                self.load_balancer.mark_endpoint_unhealthy(endpoint)
                logger.error(f"Error in region {endpoint.region}: {str(err)}")
                raise

        except Exception as err:
            message = str(err)
            logger.error("A client error occurred: %s", message)
            raise HTTPException(status_code=500, detail=message)
    def _log_token_usage(self, response):
        token_usage = response['usage']
        logger.info("Input tokens: %s", token_usage['inputTokens'])
        logger.info("Output tokens: %s", token_usage['outputTokens'])
        logger.info("Total tokens: %s", token_usage['totalTokens'])
        logger.info("Stop reason: %s", response['stopReason'])
bedrock_service = BedrockService()
```



***1:70:app/services/load_balancer.py***
```python
from enum import Enum
from typing import List, Any
import random
import logging

logger = logging.getLogger(__name__)

class LoadBalancerStrategy(Enum):
    ROUND_ROBIN = "round-robin"
    WEIGHTED = "weighted"
    FAILOVER = "failover"
class LoadBalancer:
    def __init__(self, strategy: str = LoadBalancerStrategy.ROUND_ROBIN.value):
        self.strategy = LoadBalancerStrategy(strategy)
        self.current_index = 0
        self.endpoints: List[Any] = []
        
    def add_endpoint(self, endpoint: Any, weight: int = 1):
        self.endpoints.append({"endpoint": endpoint, "weight": weight, "healthy": True})
        
    def get_next_endpoint(self) -> Any:
        if not self.endpoints:
            raise Exception("No endpoints available")
            
        if self.strategy == LoadBalancerStrategy.ROUND_ROBIN:
            return self._round_robin()
        elif self.strategy == LoadBalancerStrategy.WEIGHTED:
            return self._weighted()
        elif self.strategy == LoadBalancerStrategy.FAILOVER:
            return self._failover()
            
    def _round_robin(self) -> Any:
        healthy_endpoints = [ep for ep in self.endpoints if ep["healthy"]]
        if not healthy_endpoints:
            raise Exception("No healthy endpoints available")
            
        endpoint = healthy_endpoints[self.current_index % len(healthy_endpoints)]
        self.current_index += 1
        logger.info(f"Selected endpoint in region: {endpoint['endpoint'].region}")
        return endpoint["endpoint"]
    def _weighted(self) -> Any:
        healthy_endpoints = [ep for ep in self.endpoints if ep["healthy"]]
        if not healthy_endpoints:
            raise Exception("No healthy endpoints available")
            
        weights = [ep["weight"] for ep in healthy_endpoints]
        endpoint = random.choices(healthy_endpoints, weights=weights, k=1)[0]
        logger.info(f"Selected endpoint in region: {endpoint['endpoint'].region}")
        return endpoint["endpoint"]
        
    def _failover(self) -> Any:
        for endpoint in self.endpoints:
            if endpoint["healthy"]:
                logger.info(f"Selected endpoint in region: {endpoint['endpoint'].region}")
                return endpoint["endpoint"]
        raise Exception("No healthy endpoints available")

    def mark_endpoint_unhealthy(self, endpoint: Any):
        for ep in self.endpoints:
            if ep["endpoint"] == endpoint:
                ep["healthy"] = False
                logger.warning(f"Marked endpoint in region {endpoint.region} as unhealthy")
                
    def mark_endpoint_healthy(self, endpoint: Any):
        for ep in self.endpoints:
            if ep["endpoint"] == endpoint:
                ep["healthy"] = True
                logger.info(f"Marked endpoint in region {endpoint.region} as healthy")
```

## Load Balancer Configuration

### Available Strategies

The load balancer supports three strategies, configurable via the `LOAD_BALANCER_STRATEGY` environment variable:

1. **Round Robin** (`round-robin`)
   - Distributes requests evenly across healthy endpoints
   - Default strategy if none specified
   ```python
   LOAD_BALANCER_STRATEGY=round-robin
   ```

2. **Weighted** (`weighted`)
   - Distributes traffic based on endpoint weights
   - Primary region (REGION_1) has weight=2
   - Secondary region (REGION_2) has weight=1
   ```python
   LOAD_BALANCER_STRATEGY=weighted
   ```

3. **Failover** (`failover`)
   - Uses primary endpoint until it fails
   - Automatically switches to backup endpoint
   ```python
   LOAD_BALANCER_STRATEGY=failover
   ```

### Endpoint Health Monitoring

The load balancer automatically:
- Tracks endpoint health status
- Removes unhealthy endpoints from rotation
- Restores endpoints when they recover
- Logs all health state changes

## Circuit Breaker Configuration

The circuit breaker pattern is implemented using the `circuitbreaker` package with the following settings:

```python
@circuit_breaker(
    failure_threshold=3,           # Number of failures before opening
    recovery_timeout=30,           # Seconds to wait before half-open
    expected_exception=Exception   # Exceptions that trigger the breaker
)
```

### States

1. **Closed** (Normal Operation)
   - All requests proceed normally
   - Failures are counted

2. **Open** (Service Protection)
   - All requests immediately fail
   - Prevents cascade failures
   - Automatic timeout-based recovery

3. **Half-Open** (Recovery Testing)
   - Allows one test request
   - Success returns to closed state
   - Failure returns to open state

## Monitoring and Logging

### Log Levels

```python
logging.basicConfig(level=logging.INFO)
```

The service logs:
- Request regions and routing decisions
- Token usage statistics
- Circuit breaker state changes
- Endpoint health status changes
- Error details and stack traces

### Token Usage Monitoring

Each response includes detailed token usage:
```json
{
    "token_usage": {
        "inputTokens": 20,
        "outputTokens": 43,
        "totalTokens": 63
    }
}
```

## Advanced Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION_1=us-east-1
AWS_REGION_2=us-west-2

# Load Balancer
LOAD_BALANCER_STRATEGY=round-robin

# Model Configuration
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Custom Circuit Breaker Settings

Modify `circuit_handler.py` to adjust circuit breaker behavior:

```python
FAILURE_THRESHOLD = 3
RECOVERY_TIMEOUT = 30
EXPECTED_EXCEPTIONS = (Exception,)
```

## Development

### Running Tests

```bash
# Unit tests
python -m pytest tests/

# Load balancer distribution test
python -m pytest tests/test_load_balancer.py

# Circuit breaker behavior test
python -m pytest tests/test_circuit_breaker.py
```

### Adding New Features

1. Create feature branch:
```bash
git flow feature start feature-name
```

2. Implement changes following the project structure:
```
app/
├── core/
│   └── config.py          # Configuration settings
├── services/
│   ├── bedrock_service.py # AWS Bedrock integration
│   ├── load_balancer.py   # Load balancing logic
│   └── circuit_handler.py # Circuit breaker implementation
└── testing/
    ├── test_routes.py     # Test endpoints
    └── failure_simulator.py# Failure simulation
```

3. Add tests in `tests/` directory
4. Update documentation
5. Complete feature:
```bash
git flow feature finish feature-name
```

## Performance Considerations

- Load balancer adds minimal overhead (~1ms)
- Circuit breaker state checks are in-memory
- Token usage logging is asynchronous
- Health checks are passive (no active polling)

## Security

- AWS credentials are loaded from environment only
- All endpoints use HTTPS
- Circuit breaker prevents cascade failures
- Error messages are sanitized in production

## Troubleshooting

### Common Issues

1. Circuit Breaker Trips Too Often
   - Check failure threshold in circuit_handler.py
   - Monitor endpoint health status
   - Review AWS credentials and permissions

2. Uneven Load Distribution
   - Verify load balancer strategy setting
   - Check endpoint weights
   - Monitor endpoint health status

3. High Latency
   - Check AWS region configuration
   - Monitor token usage
   - Review network connectivity

### Debug Mode

Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues and feature requests:
1. Check existing issues
2. Enable debug logging
3. Provide relevant logs and configuration
4. Create detailed bug report

## Roadmap

- [ ] Add support for additional AWS regions
- [ ] Implement active health checks
- [ ] Add metrics collection and dashboards
- [ ] Support for custom load balancing strategies
- [ ] Enhanced failure simulation scenarios

## License - Quang Chu
