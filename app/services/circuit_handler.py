from circuitbreaker import CircuitBreaker, STATE_CLOSED, STATE_OPEN, STATE_HALF_OPEN
from app.testing.failure_simulator import failure_simulator
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerHandler:
    def __init__(self):
        self.breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            name='bedrock_circuit'
        )
        self._state = STATE_CLOSED
        self._failure_count = 0

    def decorate(self, func):
        original_func = self.breaker(func)
        
        async def wrapper(*args, **kwargs):
            try:
                result = await original_func(*args, **kwargs)
                self._state = STATE_CLOSED
                return result
            except Exception as e:
                self._failure_count += 1
                if self._failure_count >= 3:  # failure_threshold
                    self._state = STATE_OPEN
                raise e
        
        return wrapper

    @property
    def state(self):
        return self._state

    @property
    def failure_count(self):
        return self._failure_count

    def reset(self):
        self._state = STATE_CLOSED
        self._failure_count = 0

circuit_handler = CircuitBreakerHandler()

def check_failure_simulation():
    if failure_simulator.should_fail():
        logger.error(f"Simulated failure #{failure_simulator.failure_count}")
        raise Exception("Simulated failure")