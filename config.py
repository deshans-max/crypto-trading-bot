import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class TradingConfig:
    """Configuration class for the crypto trading bot."""
    
    def __init__(self):
        # API Configuration
        self.kraken_api_key = os.getenv('KRAKEN_API_KEY')
        self.kraken_secret_key = os.getenv('KRAKEN_SECRET_KEY')
        
        # Trading pairs
        self.trading_pairs = os.getenv('TRADING_PAIRS', 'KSM/USD,SUI/USD,DOT/USD,ETH/USD').split(',')
        
        # Investment settings
        self.investment_amount = float(os.getenv('INVESTMENT_AMOUNT', '100'))
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '0.1'))
        
        # Risk management
        self.stop_loss_percentage = float(os.getenv('STOP_LOSS_PERCENTAGE', '5'))
        self.take_profit_percentage = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '15'))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '10'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', '50'))
        self.cooldown_period = int(os.getenv('COOLDOWN_PERIOD', '3600'))
        
        # Technical Analysis parameters
        self.rsi_period = int(os.getenv('RSI_PERIOD', '14'))
        self.rsi_overbought = float(os.getenv('RSI_OVERBOUGHT', '70'))
        self.rsi_oversold = float(os.getenv('RSI_OVERSOLD', '30'))
        
        self.macd_fast = int(os.getenv('MACD_FAST', '12'))
        self.macd_slow = int(os.getenv('MACD_SLOW', '26'))
        self.macd_signal = int(os.getenv('MACD_SIGNAL', '9'))
        
        self.bollinger_period = int(os.getenv('BOLLINGER_PERIOD', '20'))
        self.bollinger_std = float(os.getenv('BOLLINGER_STD', '2'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'trading_bot.log')
        
        # Swing trading specific parameters
        self.swing_hold_period = 24 * 60 * 60  # 24 hours in seconds
        self.min_swing_movement = 0.05  # 5% minimum movement for swing
        self.trend_confirmation_period = 4  # hours
        
    def validate_config(self) -> bool:
        """Validate the configuration settings."""
        if not self.kraken_api_key or not self.kraken_secret_key:
            print("ERROR: Kraken API credentials not found in environment variables")
            return False
            
        if self.investment_amount <= 0:
            print("ERROR: Investment amount must be positive")
            return False
            
        if self.stop_loss_percentage <= 0 or self.take_profit_percentage <= 0:
            print("ERROR: Stop loss and take profit percentages must be positive")
            return False
            
        return True
    
    def get_trading_pairs(self) -> List[str]:
        """Get list of trading pairs."""
        return self.trading_pairs
    
    def get_risk_params(self) -> Dict[str, Any]:
        """Get risk management parameters."""
        return {
            'stop_loss': self.stop_loss_percentage,
            'take_profit': self.take_profit_percentage,
            'max_daily_trades': self.max_daily_trades,
            'max_daily_loss': self.max_daily_loss,
            'max_position_size': self.max_position_size
        }
    
    def get_technical_params(self) -> Dict[str, Any]:
        """Get technical analysis parameters."""
        return {
            'rsi_period': self.rsi_period,
            'rsi_overbought': self.rsi_overbought,
            'rsi_oversold': self.rsi_oversold,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'bollinger_period': self.bollinger_period,
            'bollinger_std': self.bollinger_std
        }

# Global configuration instance
config = TradingConfig()
