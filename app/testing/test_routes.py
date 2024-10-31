from fastapi import APIRouter
from app.services.bedrock_service import bedrock_service

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