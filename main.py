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