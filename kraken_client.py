import krakenex
import ccxt
import time
import logging
from typing import Dict, List, Optional, Tuple
from config import config

class KrakenClient:
    """Wrapper for Kraken API operations."""
    
    def __init__(self):
        self.api_key = config.kraken_api_key
        self.secret_key = config.kraken_secret_key
        
        # Initialize Kraken API client
        self.kraken = krakenex.API(key=self.api_key, secret=self.secret_key)
        
        # Initialize CCXT for additional functionality
        self.exchange = ccxt.kraken({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'sandbox': False,  # Set to True for testing
            'enableRateLimit': True
        })
        
        self.logger = logging.getLogger(__name__)
        
    def get_account_balance(self) -> Dict[str, float]:
        """Get account balance."""
        try:
            balance = self.kraken.query_private('Balance')
            if balance['error']:
                self.logger.error(f"Error getting balance: {balance['error']}")
                return {}
            
            return {k: float(v) for k, v in balance['result'].items() if float(v) > 0}
        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return {}
    
    def get_ticker_info(self, symbol: str) -> Optional[Dict]:
        """Get current ticker information for a symbol."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': ticker['symbol'],
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['volume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error getting ticker for {symbol}: {e}")
            return None
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[List]:
        """Get OHLCV data for technical analysis."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            self.logger.error(f"Error getting OHLCV for {symbol}: {e}")
            return None
    
    def place_market_buy_order(self, symbol: str, amount: float) -> Optional[Dict]:
        """Place a market buy order."""
        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            self.logger.info(f"Market buy order placed: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing market buy order: {e}")
            return None
    
    def place_market_sell_order(self, symbol: str, amount: float) -> Optional[Dict]:
        """Place a market sell order."""
        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            self.logger.info(f"Market sell order placed: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing market sell order: {e}")
            return None
    
    def place_limit_buy_order(self, symbol: str, amount: float, price: float) -> Optional[Dict]:
        """Place a limit buy order."""
        try:
            order = self.exchange.create_limit_buy_order(symbol, amount, price)
            self.logger.info(f"Limit buy order placed: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing limit buy order: {e}")
            return None
    
    def place_limit_sell_order(self, symbol: str, amount: float, price: float) -> Optional[Dict]:
        """Place a limit sell order."""
        try:
            order = self.exchange.create_limit_sell_order(symbol, amount, price)
            self.logger.info(f"Limit sell order placed: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing limit sell order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an existing order."""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Order cancelled: {result}")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self) -> List[Dict]:
        """Get all open orders."""
        try:
            orders = self.exchange.fetch_open_orders()
            return orders
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Get status of a specific order."""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return None
    
    def get_trade_history(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get recent trade history."""
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            self.logger.error(f"Error getting trade history: {e}")
            return []
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get information about a trading symbol."""
        try:
            market = self.exchange.load_markets()
            if symbol in market:
                return market[symbol]
            return None
        except Exception as e:
            self.logger.error(f"Error getting symbol info: {e}")
            return None
    
    def calculate_position_size(self, symbol: str, investment_amount: float) -> float:
        """Calculate position size based on current price and investment amount."""
        try:
            ticker = self.get_ticker_info(symbol)
            if ticker and ticker['last'] > 0:
                return investment_amount / ticker['last']
            return 0
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
    
    def get_available_balance(self, currency: str) -> float:
        """Get available balance for a specific currency."""
        try:
            balance = self.get_account_balance()
            return balance.get(currency, 0.0)
        except Exception as e:
            self.logger.error(f"Error getting available balance: {e}")
            return 0.0
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            balance = self.get_account_balance()
            return len(balance) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
