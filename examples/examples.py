from toobit_api.toobit_api import TooBitAPI

# Define your API keys.
api_key = "your-api-key"
secret_key = "your-api-secret"

# Create an API Instance
toobit_api = TooBitAPI(api_key, secret_key)

# Test Server Time
print(toobit_api.get_server_time())

# Get Exchange Info
print(toobit_api.get_exchange_info())

# Get Balances
print(toobit_api.get_balances())

# TBA..
