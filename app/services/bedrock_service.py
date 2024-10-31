import boto3
from fastapi import HTTPException
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.load_balancer import LoadBalancer
from app.services.circuit_breaker import circuit_protected
import logging

logger = logging.getLogger(__name__)

class BedrockEndpoint:
    def __init__(self, region: str):
        self.region = region
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    @circuit_protected
    async def generate_response(self, messages: list, system_prompts: list):
        return self.client.converse(
            modelId=settings.MODEL_ID,
            messages=messages,
            system=system_prompts,
            inferenceConfig={"temperature": 0.5},
            additionalModelRequestFields={"top_k": 200}
        )

class BedrockService:
    def __init__(self):
        self.load_balancer = LoadBalancer(strategy=settings.LOAD_BALANCER_STRATEGY)
        
        # Add endpoints from configuration
        for config in settings.AWS_REGIONS_CONFIG:
            region = config['region']
            weight = config['weight']
            logger.info(f"Adding endpoint for {region} with weight {weight}")
            self.load_balancer.add_endpoint(
                BedrockEndpoint(region),
                weight=weight
            )

    def _log_token_usage(self, response: dict) -> None:
        """Log token usage metrics from the response"""
        try:
            token_usage = response.get('usage', {})
            logger.info(
                f"Token usage - Input: {token_usage.get('inputTokens', 0)}, "
                f"Output: {token_usage.get('outputTokens', 0)}, "
                f"Total: {token_usage.get('totalTokens', 0)}"
            )
            logger.info(f"Stop reason: {response.get('stopReason', 'unknown')}")
        except Exception as e:
            logger.warning(f"Failed to log token usage: {str(e)}")

    async def generate_conversation(self, message_content: str, system_prompt: str | None = None):
        try:
            endpoint = self.load_balancer.get_next_endpoint()
            
            system_prompts = [{"text": system_prompt or "You are a helpful AI assistant."}]
            messages = [{
                "role": "user",
                "content": [{"text": message_content}]
            }]

            try:
                response = await endpoint.generate_response(messages, system_prompts)
                
                # Add region information to response
                response['region'] = endpoint.region
                
                # Mark endpoint as healthy on successful response
                self.load_balancer.mark_endpoint_healthy(endpoint)
                
                self._log_token_usage(response)
                return response

            except Exception as err:
                # Mark endpoint as unhealthy on failure
                self.load_balancer.mark_endpoint_unhealthy(endpoint)
                logger.error(f"Error in region {endpoint.region}: {str(err)}")
                raise

        except Exception as err:
            message = str(err)
            logger.error("A client error occurred: %s", message)
            raise HTTPException(status_code=503, detail=message)

bedrock_service = BedrockService() 