import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION_1 = os.getenv('AWS_REGION_1', 'us-east-1')
    AWS_REGION_2 = os.getenv('AWS_REGION_2', 'us-west-2')
    MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
    LOAD_BALANCER_STRATEGY = os.getenv('LOAD_BALANCER_STRATEGY', 'round-robin')

settings = Settings() 