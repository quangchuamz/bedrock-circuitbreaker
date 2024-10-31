import boto3
from fastapi import HTTPException
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.circuit_handler import circuit_handler, check_failure_simulation
from app.services.load_balancer import LoadBalancer
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

class BedrockService:
    def __init__(self):
        self.load_balancer = LoadBalancer(strategy=settings.LOAD_BALANCER_STRATEGY)
        
        # Log configuration
        logger.info(f"Initializing BedrockService with config: {settings.AWS_REGIONS_CONFIG}")
        
        # Add endpoints from configuration
        for config in settings.AWS_REGIONS_CONFIG:
            region = config['region']
            weight = config['weight']
            logger.info(f"Adding endpoint for {region} with weight {weight}")
            self.load_balancer.add_endpoint(
                BedrockEndpoint(region),
                weight=weight
            )
        
        self._setup_circuit_breaker()

    def _setup_circuit_breaker(self):
        @circuit_handler.decorate
        async def wrapped(*args, **kwargs):
            return await self._generate_conversation_impl(*args, **kwargs)
        self.generate_conversation = wrapped

    async def _generate_conversation_impl(self, message_content: str, system_prompt: str | None = None):
        check_failure_simulation()

        try:
            endpoint = self.load_balancer.get_next_endpoint()
            
            system_prompts = [{"text": system_prompt or "You are a helpful AI assistant."}]
            messages = [{
                "role": "user",
                "content": [{"text": message_content}]
            }]

            try:
                response = endpoint.client.converse(
                    modelId=settings.MODEL_ID,
                    messages=messages,
                    system=system_prompts,
                    inferenceConfig={"temperature": 0.5},
                    additionalModelRequestFields={"top_k": 200}
                )
                
                # Add region information to response
                response['region'] = endpoint.region
                
                # Mark endpoint as healthy on successful response
                self.load_balancer.mark_endpoint_healthy(endpoint)
                
                self._log_token_usage(response)
                return response

            except ClientError as err:
                # Mark endpoint as unhealthy on failure
                self.load_balancer.mark_endpoint_unhealthy(endpoint)
                logger.error(f"Error in region {endpoint.region}: {str(err)}")
                raise

        except Exception as err:
            message = str(err)
            logger.error("A client error occurred: %s", message)
            raise HTTPException(status_code=500, detail=message)

    def _log_token_usage(self, response):
        token_usage = response['usage']
        logger.info("Input tokens: %s", token_usage['inputTokens'])
        logger.info("Output tokens: %s", token_usage['outputTokens'])
        logger.info("Total tokens: %s", token_usage['totalTokens'])
        logger.info("Stop reason: %s", response['stopReason'])

bedrock_service = BedrockService() 