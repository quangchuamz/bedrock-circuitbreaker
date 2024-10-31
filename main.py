from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.bedrock_service import bedrock_service
from app.testing.test_routes import test_router
from app.core.config import settings
from app.core.logger import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting server with load balancer strategy: {settings.LOAD_BALANCER_STRATEGY}")
    yield

app = FastAPI(lifespan=lifespan)
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
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service temporarily unavailable. Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 