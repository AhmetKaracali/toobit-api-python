import json
import urllib.parse
import requests
import time
import hashlib
import hmac


class TooBitAPI:
    def __init__(self, api_key, secret_key):
        self.base_url = "https://api.toobit.com"
        self.api_key = api_key
        self.secret_key = secret_key

    def _generate_signature(self, params):
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        return hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    def _send_request(self, method, endpoint, params=None, signed=False):
        if params is None:
            params = {}
        headers = {}

        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
            headers['X-BB-APIKEY'] = self.api_key

        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, params=params, headers=headers)

        # Check HTTP Status Code
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code} - {response.text}")
            return None

        try:
            return response.json()
        except ValueError as e:
            print(f"JSON parse error: {e}")
            return None

    def get_server_time(self):
        return self._send_request('GET', '/api/v1/time')

    def get_exchange_info(self):
        """Get exchange info."""
        return self._send_request('GET', '/api/v1/exchangeInfo')

    def get_symbol_price_ticker(self, symbol):
        """
        Get data for a spesific market.

        :param symbol: Symbol to get price ticker. (like 'BTCUSDT').
        """
        params = {'symbol': symbol}
        return self._send_request('GET', '/quote/v1/ticker/price', params=params)

    def get_orderbook_depth(self, symbol, limit=None):
        """
        Belirli bir marketin orderbook derinlik verilerini al.

        :param limit: Orderbook Depth Limit
        :param symbol: Symbol to get orderbook. (like 'BTCUSDT').
        """
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._send_request('GET', '/quote/v1/depth', params=params)

    def place_order(self, symbol, side, order_type, quantity, price=None, time_in_force=None, new_client_order_id=None,
                    recv_window=5000):
        """
        Yeni bir emir gönder.

        :param symbol: Market to trade. (örn. 'BTCUSDT').
        :param side: 'BUY' or 'SELL'.
        :param order_type: ('LIMIT', 'MARKET', 'GTC' etc.).
        :param quantity: Order amount.
        :param price: Price (only required except market order types).
        :param time_in_force: Time in Force :) (only required for some order types).
        :param new_client_order_id: Your local order ID if you want to track your orders.
        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window
        }

        if price:
            params['price'] = price
        if time_in_force:
            params['timeInForce'] = time_in_force
        if new_client_order_id:
            params['newClientOrderId'] = new_client_order_id

        return self._send_request('POST', '/api/v1/spot/order', params=params, signed=True)

    def place_batch_orders(self, orders, recv_window=5000, max_orders_at_once=20):
        """
        Place multiple orders at once.

        :param max_orders_at_once: You can send max. 20 orders in one request. This is Toobit's limit.
        :param orders: Order list.
        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        responses = []
        for i in range(0, len(orders), max_orders_at_once):
            batch = orders[i:i + max_orders_at_once]
            responses.append(self._send_batch_order(batch, recv_window))
        return responses

    def _send_batch_order(self, batch, recv_window):
        params = {
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window
        }
        headers = {
            'X-BB-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        data = json.dumps(batch)
        signature = self._generate_signature(params)
        url = f"{self.base_url}/api/v1/spot/batchOrders?{urllib.parse.urlencode(params)}&signature={signature}"

        response = requests.post(url, headers=headers, data=data)
        return response.json()

    def cancel_order(self, symbol, order_id=None, client_order_id=None, recv_window=5000):
        """
        Cancel a spesific order.

        :param symbol: Market (örn. 'BTCUSDT').
        :param order_id: TooBit order ID for the order which should be cancelled.
        :param client_order_id: Local order ID for the order which should be cancelled.
        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        params = {
            'symbol': symbol,
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window
        }
        if order_id:
            params['orderId'] = order_id
        if client_order_id:
            params['clientOrderId'] = client_order_id

        return self._send_request('DELETE', '/api/v1/spot/order', params=params, signed=True)

    def cancel_multiple_orders(self, order_ids, recv_window=5000, max_cancellation_at_once=100):
        """
        Birden fazla emri toplu olarak iptal et.

        :param max_cancellation_at_once: You can CANCEL max. 100 orders in one request. This is Toobit's limit.
        :param order_ids: List of order ids to cancel.
        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        responses = []
        for i in range(0, len(order_ids), max_cancellation_at_once):
            batch_ids = ','.join(map(str, order_ids[i:i + max_cancellation_at_once]))
            responses.append(self._send_batch_cancel(batch_ids, recv_window))
        return responses

    def _send_batch_cancel(self, batch_ids, recv_window):
        params = {
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window,
            'ids': batch_ids
        }
        return self._send_request('DELETE', '/api/v1/spot/cancelOrderByIds', params=params, signed=True)

    def get_open_orders(self, symbol=None, order_id=None, limit=1000, recv_window=5000):
        """
        Get all open orders for a spesific symbol/all symbols.

        :param symbol: Market (örn. 'BTCUSDT'). If not, all markets.
        :param order_id: Orders less than a certain ID will be filtered out.
        :param limit: Limit on the number of rotating orders. Default 500, maximum 1000.
        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        params = {
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window
        }
        if symbol:
            params['symbol'] = symbol
        if order_id:
            params['orderId'] = order_id
        if limit:
            params['limit'] = limit

        return self._send_request('GET', '/api/v1/spot/openOrders', params=params, signed=True)

    def get_balances(self, recv_window=5000):
        """
        Get user account balances.

        :param recv_window: Max timeframe that the request is valid (miliseconds).
        """
        params = {
            'timestamp': int(time.time() * 1000),
            'recvWindow': recv_window
        }
        return self._send_request('GET', '/api/v1/account', params=params, signed=True)