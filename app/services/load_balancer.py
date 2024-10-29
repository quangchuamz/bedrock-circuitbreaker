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