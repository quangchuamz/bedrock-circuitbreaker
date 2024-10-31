from enum import Enum
from typing import Dict, Any
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def record_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker closed after successful recovery")
    
    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
                return True
            return False
            
        # HALF_OPEN state
        return True

class RegionalCircuitBreaker:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, region: str) -> CircuitBreaker:
        if region not in self.breakers:
            self.breakers[region] = CircuitBreaker()
        return self.breakers[region]
    
    def get_status(self) -> Dict[str, Any]:
        return {
            region: {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "last_failure_time": breaker.last_failure_time
            }
            for region, breaker in self.breakers.items()
        }

regional_circuit_breaker = RegionalCircuitBreaker()

def circuit_protected(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        endpoint = args[0]  # First arg is self (BedrockEndpoint instance)
        breaker = regional_circuit_breaker.get_breaker(endpoint.region)
        
        if not breaker.can_execute():
            raise Exception(f"Circuit breaker is open for region {endpoint.region}")
        
        try:
            result = await func(*args, **kwargs)
            breaker.record_success()
            return result
        except Exception as e:
            breaker.record_failure()
            logger.error(f"Circuit breaker recorded failure for region {endpoint.region}: {str(e)}")
            raise
    
    return wrapper 