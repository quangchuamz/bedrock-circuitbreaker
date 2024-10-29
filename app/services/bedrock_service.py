import boto3
from fastapi import HTTPException
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.circuit_handler import circuit_handler, check_failure_simulation
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self._setup_circuit_breaker()

    def _setup_circuit_breaker(self):
        @circuit_handler.decorate
        @wraps(self._generate_conversation_impl)
        async def wrapped(*args, **kwargs):
            return await self._generate_conversation_impl(*args, **kwargs)
        self.generate_conversation = wrapped

    async def _generate_conversation_impl(self, message_content: str, system_prompt: str | None = None):
        # Check for simulated failures
        check_failure_simulation()

        try:
            system_prompts = [{"text": system_prompt or "You are a helpful AI assistant."}]
            messages = [{
                "role": "user",
                "content": [{"text": message_content}]
            }]

            response = self.client.converse(
                modelId=settings.MODEL_ID,
                messages=messages,
                system=system_prompts,
                inferenceConfig={"temperature": 0.5},
                additionalModelRequestFields={"top_k": 200}
            )

            self._log_token_usage(response)
            return response

        except ClientError as err:
            message = err.response['Error']['Message']
            logger.error("A client error occurred: %s", message)
            raise HTTPException(status_code=500, detail=message)

    def _log_token_usage(self, response):
        token_usage = response['usage']
        logger.info("Input tokens: %s", token_usage['inputTokens'])
        logger.info("Output tokens: %s", token_usage['outputTokens'])
        logger.info("Total tokens: %s", token_usage['totalTokens'])
        logger.info("Stop reason: %s", response['stopReason'])

    @property
    def circuit_state(self):
        return circuit_handler.state

bedrock_service = BedrockService() 