from fastapi import APIRouter
from app.services.bedrock_service import bedrock_service, region_mapper
from app.services.circuit_breaker import regional_circuit_breaker

test_router = APIRouter(prefix="/test", tags=["testing"])

@test_router.get("/load-balancer-status")
async def get_load_balancer_status():
    try:
        endpoints_status = [
            {
                "region": ep["endpoint"].region,
                "healthy": ep["healthy"],
                "weight": ep["weight"]
            }
            for ep in bedrock_service.load_balancer.endpoints
        ]
        
        return {
            "strategy": bedrock_service.load_balancer.strategy.value,
            "endpoints": endpoints_status
        }
    except Exception as e:
        return {"error": str(e)}

@test_router.get("/circuit-breaker-status")
async def get_circuit_breaker_status():
    return regional_circuit_breaker.get_status()

@test_router.post("/set-region-mapping")
async def set_region_mapping(source_region: str, target_region: str):
    """Set a region mapping for testing purposes"""
    region_mapper.set_mapping(source_region, target_region)
    return {"message": f"Mapped {source_region} to {target_region}"}

@test_router.delete("/clear-region-mapping")
async def clear_region_mapping():
    """Clear all region mappings"""
    region_mapper.clear_mappings()
    return {"message": "Cleared all region mappings"}