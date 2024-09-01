import os
from dotenv import load_dotenv

load_dotenv()

OPENSEA_API_KEY = os.getenv('OPENSEA_API_KEY')
OPENSEA_API_URL = 'https://api.opensea.io/v2'

# Production
LOOTEX_API_URL = 'https://v3-api.lootex.io/api/v3'

# Preview
# LOOTEX_API_URL = 'https://dex-v3-api-aws.lootex.dev/api/v3'