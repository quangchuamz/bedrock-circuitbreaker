from fastapi import APIRouter
from app.testing.failure_simulator import failure_simulator
from app.services.bedrock_service import bedrock_service
from app.services.circuit_handler import circuit_handler

test_router = APIRouter(prefix="/test", tags=["testing"])

@test_router.post("/enable-failures")
async def enable_failures():
    return failure_simulator.enable_failures()

@test_router.post("/disable-failures")
async def disable_failures():
    circuit_handler.reset()  # Reset circuit breaker state
    return failure_simulator.disable_failures()

@test_router.get("/circuit-status")
async def get_circuit_status():
    try:
        return {
            "circuit_state": circuit_handler.state,
            "failure_count": circuit_handler.failure_count,
            "current_failures": failure_simulator.failure_count,
            "failures_enabled": failure_simulator.fail_next_requests
        }
    except Exception as e:
        return {"error": str(e)}

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