# TooBit API Python Client

This library is designed to interact with the TooBit API using Python. Please test before you use it on your production codebase.

## Installation

You can install the package using pip:

```bash
pip install toobit-api-python
```

## Usage
Here is a simple example of how to use the library:

```python
from toobit_api.toobit_api import TooBitAPI

# Define your API key and secret key
api_key = "your_api_key"
secret_key = "your_secret_key"

# Create a TooBit API object
toobit_api = TooBitAPI(api_key, secret_key)

# Example: Get server time
print(toobit_api.get_server_time())

# Example: Get exchange information
print(toobit_api.get_exchange_info())

# More examples and information can be found in the documentation.
```

For more examples and detailed usage, please refer to the [official documentation](https://toobit-docs.github.io/apidocs/spot/v1/en/#change-log).


## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


