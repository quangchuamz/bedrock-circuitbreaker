import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    @property
    def AWS_REGIONS(self) -> list[str]:
        regions_str = os.getenv('AWS_REGIONS')
        return [region.strip() for region in regions_str.split(',')]
    
    @property
    def AWS_REGION_WEIGHTS(self) -> list[int]:
        weights_str = os.getenv('AWS_REGION_WEIGHTS')
        return [int(weight.strip()) for weight in weights_str.split(',')]
    
    @property
    def AWS_REGIONS_CONFIG(self) -> list[dict]:
        regions = self.AWS_REGIONS
        weights = self.AWS_REGION_WEIGHTS
        
        # If weights list is shorter than regions, pad with 1s
        if len(weights) < len(regions):
            weights.extend([1] * (len(regions) - len(weights)))
        
        return [
            {'region': region, 'weight': weight}
            for region, weight in zip(regions, weights)
        ]
    
    MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
    LOAD_BALANCER_STRATEGY = os.getenv('LOAD_BALANCER_STRATEGY', 'round-robin')

settings = Settings() 