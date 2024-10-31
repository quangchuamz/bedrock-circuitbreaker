from enum import Enum
from typing import List, Any
import random
import logging
from collections import deque

logger = logging.getLogger(__name__)

class LoadBalancerStrategy(Enum):
    ROUND_ROBIN = "round-robin"
    WEIGHTED = "weighted"
    FAILOVER = "failover"

class LoadBalancer:
    def __init__(self, strategy: str = LoadBalancerStrategy.ROUND_ROBIN.value):
        self.strategy = LoadBalancerStrategy(strategy)
        self.endpoints: List[dict] = []
        self._rotation_index = 0
        logger.info(f"Initializing LoadBalancer with strategy: {strategy}")
    
    def _get_weighted_sequence(self) -> List[int]:
        """Generate the complete weighted sequence of endpoint indices"""
        sequence = []
        for idx, endpoint in enumerate(self.endpoints):
            weight = endpoint["weight"]
            sequence.extend([idx] * weight)
        return sequence
    
    def _round_robin(self) -> Any:
        """
        Weighted round-robin implementation using rotation index
        """
        if not self.endpoints:
            raise Exception("No endpoints available")

        healthy_indices = [
            idx for idx, ep in enumerate(self.endpoints) 
            if ep["healthy"]
        ]
        
        if not healthy_indices:
            raise Exception("No healthy endpoints available")

        # Get the complete weighted sequence
        sequence = self._get_weighted_sequence()
        sequence_length = len(sequence)
        
        if sequence_length == 0:
            raise Exception("No weighted sequence available")

        # Try to find next healthy endpoint
        for _ in range(sequence_length):
            # Get current index and move to next position
            current_idx = sequence[self._rotation_index]
            self._rotation_index = (self._rotation_index + 1) % sequence_length
            
            if current_idx in healthy_indices:
                endpoint = self.endpoints[current_idx]
                logger.info(
                    f"Round Robin selection: region={endpoint['endpoint'].region}, "
                    f"weight={endpoint['weight']}, "
                    f"rotation_index={self._rotation_index}, "
                    f"sequence={sequence}"
                )
                return endpoint["endpoint"]

        raise Exception("No healthy endpoints found in rotation")
    
    def add_endpoint(self, endpoint: Any, weight: int = 1):
        """Add endpoint with specified weight"""
        self.endpoints.append({
            "endpoint": endpoint,
            "weight": weight,
            "healthy": True
        })
        logger.info(f"Added endpoint {endpoint.region} with weight {weight}")
    
    def get_next_endpoint(self) -> Any:
        """Get next endpoint based on selected strategy"""
        if not self.endpoints:
            raise Exception("No endpoints available")
            
        if self.strategy == LoadBalancerStrategy.ROUND_ROBIN:
            return self._round_robin()
        elif self.strategy == LoadBalancerStrategy.WEIGHTED:
            return self._weighted()
        elif self.strategy == LoadBalancerStrategy.FAILOVER:
            return self._failover()
    
    def _weighted(self) -> Any:
        """
        Random selection with probability proportional to weights
        Higher weights have higher chance of being selected
        """
        healthy_endpoints = [ep for ep in self.endpoints if ep["healthy"]]
        if not healthy_endpoints:
            raise Exception("No healthy endpoints available")
        
        # Calculate weights for healthy endpoints
        weights = [ep["weight"] for ep in healthy_endpoints]
        total_weight = sum(weights)
        
        if total_weight == 0:
            raise Exception("Total weight is 0")
        
        # Normalize weights to probabilities
        probabilities = [w/total_weight for w in weights]
        
        # Select endpoint based on weights
        endpoint = random.choices(healthy_endpoints, weights=probabilities, k=1)[0]
        logger.info(
            f"Weighted selection chose endpoint in region: {endpoint['endpoint'].region} "
            f"(weight: {endpoint['weight']}, probability: {endpoint['weight']/total_weight:.2%})"
        )
        return endpoint["endpoint"]
    
    def _failover(self) -> Any:
        """
        Failover strategy prioritizing endpoints by weight
        Higher weights are tried first
        """
        # Sort endpoints by weight (highest to lowest)
        sorted_endpoints = sorted(
            self.endpoints,
            key=lambda x: (x["weight"], id(x)),  # Use id as tiebreaker for stable sorting
            reverse=True
        )
        
        # Try endpoints in weight order
        for endpoint in sorted_endpoints:
            if endpoint["healthy"]:
                logger.info(
                    f"Failover selected endpoint in region: {endpoint['endpoint'].region} "
                    f"(weight: {endpoint['weight']})"
                )
                return endpoint["endpoint"]
        
        raise Exception("No healthy endpoints available")
    
    def mark_endpoint_unhealthy(self, endpoint: Any):
        """Mark an endpoint as unhealthy"""
        for ep in self.endpoints:
            if ep["endpoint"] == endpoint:
                ep["healthy"] = False
                logger.warning(f"Marked endpoint in region {endpoint.region} as unhealthy")
                break
    
    def mark_endpoint_healthy(self, endpoint: Any):
        """Mark an endpoint as healthy"""
        for ep in self.endpoints:
            if ep["endpoint"] == endpoint:
                ep["healthy"] = True
                logger.info(f"Marked endpoint in region {endpoint.region} as healthy")
                break