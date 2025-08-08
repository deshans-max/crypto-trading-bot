import time
import logging
import schedule
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from config import config
from kraken_client import KrakenClient
from technical_analysis import TechnicalAnalyzer
from risk_manager import RiskManager

class SwingTrader:
    """Main swing trading bot implementation."""
    
    def __init__(self):
        # Initialize components
        self.kraken_client = KrakenClient()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager()
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Trading state
        self.is_running = False
        self.trading_pairs = config.get_trading_pairs()
        self.last_analysis = {}
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.total_pnl = 0.0
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.log_file),
                logging.StreamHandler()
            ]
        )
    
    def start(self):
        """Start the trading bot."""
        try:
            self.logger.info("Starting Swing Trading Bot...")
            
            # Validate configuration
            if not config.validate_config():
                self.logger.error("Configuration validation failed")
                return False
            
            # Test API connection
            if not self.kraken_client.test_connection():
                self.logger.error("Failed to connect to Kraken API")
                return False
            
            self.logger.info("API connection successful")
            
            # Get initial account balance
            balance = self.kraken_client.get_account_balance()
            self.logger.info(f"Account balance: {balance}")
            
            # Start the trading loop
            self.is_running = True
            self.logger.info("Trading bot started successfully")
            
            # Schedule regular trading checks
            schedule.every(1).hours.do(self.trading_cycle)
            schedule.every(5).minutes.do(self.check_positions)
            
            # Run initial trading cycle
            self.trading_cycle()
            
            # Start the scheduler
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Trading bot stopped by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Error in trading bot: {e}")
            self.stop()
    
    def stop(self):
        """Stop the trading bot."""
        self.is_running = False
        self.logger.info("Trading bot stopped")
    
    def trading_cycle(self):
        """Main trading cycle - analyze markets and execute trades."""
        try:
            self.logger.info("Starting trading cycle...")
            
            # Get current prices for all trading pairs
            current_prices = {}
            for pair in self.trading_pairs:
                ticker = self.kraken_client.get_ticker_info(pair)
                if ticker:
                    current_prices[pair] = ticker['last']
            
            # Check existing positions for stop loss/take profit
            self.check_positions()
            
            # Analyze each trading pair
            for pair in self.trading_pairs:
                try:
                    self.analyze_and_trade(pair, current_prices.get(pair))
                except Exception as e:
                    self.logger.error(f"Error analyzing {pair}: {e}")
            
            # Log portfolio summary
            self.log_portfolio_summary()
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
    
    def analyze_and_trade(self, symbol: str, current_price: float):
        """Analyze a symbol and execute trades if conditions are met."""
        try:
            if not current_price:
                self.logger.warning(f"No current price available for {symbol}")
                return
            
            # Get historical data for technical analysis
            ohlcv_data = self.kraken_client.get_ohlcv(symbol, '1h', 100)
            if not ohlcv_data:
                self.logger.warning(f"No historical data available for {symbol}")
                return
            
            # Prepare dataframe and add indicators
            df = self.technical_analyzer.prepare_dataframe(ohlcv_data)
            df = self.technical_analyzer.add_all_indicators(df)
            
            if df.empty:
                self.logger.warning(f"Empty dataframe for {symbol}")
                return
            
            # Generate trading signals
            signals = self.technical_analyzer.generate_swing_signals(df)
            
            # Check if trend is strong enough for swing trading
            if not self.technical_analyzer.is_trend_strong(df):
                self.logger.info(f"Trend not strong enough for {symbol}, skipping")
                return
            
            # Log analysis results
            self.logger.info(f"{symbol} Analysis: {signals}")
            
            # Execute trades based on signals
            if signals['signal'] == 'BUY' and signals['strength'] in ['STRONG', 'MODERATE']:
                self.execute_buy_order(symbol, current_price, signals)
            elif signals['signal'] == 'SELL' and signals['strength'] in ['STRONG', 'MODERATE']:
                self.execute_sell_order(symbol, current_price, signals)
            
            # Store analysis results
            self.last_analysis[symbol] = {
                'timestamp': datetime.now(),
                'signals': signals,
                'current_price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
    
    def execute_buy_order(self, symbol: str, current_price: float, signals: Dict):
        """Execute a buy order based on swing trading signals."""
        try:
            # Check if we can place a trade
            can_trade, reason = self.risk_manager.can_place_trade(symbol, 'BUY', config.investment_amount)
            if not can_trade:
                self.logger.info(f"Cannot place BUY order for {symbol}: {reason}")
                return
            
            # Calculate position size
            available_balance = self.kraken_client.get_available_balance('USD')
            position_size = self.risk_manager.calculate_position_size(available_balance, current_price)
            
            if position_size <= 0:
                self.logger.warning(f"Insufficient balance for {symbol} trade")
                return
            
            # Calculate stop loss and take profit
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, 'BUY')
            take_profit = self.risk_manager.calculate_take_profit(current_price, 'BUY')
            
            # Check if risk/reward ratio is acceptable
            if not self.risk_manager.is_risk_acceptable(current_price, stop_loss, take_profit):
                self.logger.info(f"Risk/reward ratio not acceptable for {symbol}")
                return
            
            # Place the order
            order = self.kraken_client.place_market_buy_order(symbol, position_size)
            
            if order:
                # Record the trade
                self.risk_manager.record_trade(
                    symbol, 'BUY', position_size, current_price,
                    stop_loss, take_profit, order['id']
                )
                
                self.total_trades += 1
                self.logger.info(f"BUY order executed for {symbol}: {position_size} @ {current_price}")
                self.logger.info(f"Stop Loss: {stop_loss}, Take Profit: {take_profit}")
                
            else:
                self.logger.error(f"Failed to place BUY order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing BUY order for {symbol}: {e}")
    
    def execute_sell_order(self, symbol: str, current_price: float, signals: Dict):
        """Execute a sell order based on swing trading signals."""
        try:
            # Check if we can place a trade
            can_trade, reason = self.risk_manager.can_place_trade(symbol, 'SELL', config.investment_amount)
            if not can_trade:
                self.logger.info(f"Cannot place SELL order for {symbol}: {reason}")
                return
            
            # Calculate position size
            available_balance = self.kraken_client.get_available_balance('USD')
            position_size = self.risk_manager.calculate_position_size(available_balance, current_price)
            
            if position_size <= 0:
                self.logger.warning(f"Insufficient balance for {symbol} trade")
                return
            
            # Calculate stop loss and take profit
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, 'SELL')
            take_profit = self.risk_manager.calculate_take_profit(current_price, 'SELL')
            
            # Check if risk/reward ratio is acceptable
            if not self.risk_manager.is_risk_acceptable(current_price, stop_loss, take_profit):
                self.logger.info(f"Risk/reward ratio not acceptable for {symbol}")
                return
            
            # Place the order
            order = self.kraken_client.place_market_sell_order(symbol, position_size)
            
            if order:
                # Record the trade
                self.risk_manager.record_trade(
                    symbol, 'SELL', position_size, current_price,
                    stop_loss, take_profit, order['id']
                )
                
                self.total_trades += 1
                self.logger.info(f"SELL order executed for {symbol}: {position_size} @ {current_price}")
                self.logger.info(f"Stop Loss: {stop_loss}, Take Profit: {take_profit}")
                
            else:
                self.logger.error(f"Failed to place SELL order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing SELL order for {symbol}: {e}")
    
    def check_positions(self):
        """Check active positions for stop loss and take profit triggers."""
        try:
            # Get current prices for active positions
            active_positions = self.risk_manager.active_positions
            if not active_positions:
                return
            
            current_prices = {}
            for symbol in active_positions.keys():
                ticker = self.kraken_client.get_ticker_info(symbol)
                if ticker:
                    current_prices[symbol] = ticker['last']
            
            # Check stop losses
            triggered_stops = self.risk_manager.check_stop_losses(current_prices)
            for stop in triggered_stops:
                self.close_position(stop['symbol'], stop['current_price'], "Stop Loss")
            
            # Check take profits
            triggered_takes = self.risk_manager.check_take_profits(current_prices)
            for take in triggered_takes:
                self.close_position(take['symbol'], take['current_price'], "Take Profit")
                
        except Exception as e:
            self.logger.error(f"Error checking positions: {e}")
    
    def close_position(self, symbol: str, exit_price: float, exit_reason: str):
        """Close a position and record the trade."""
        try:
            # Place market order to close position
            position = self.risk_manager.active_positions.get(symbol)
            if not position:
                return
            
            amount = position['amount']
            trade_type = position['type']
            
            if trade_type == 'BUY':
                # Sell to close long position
                order = self.kraken_client.place_market_sell_order(symbol, amount)
            else:
                # Buy to close short position
                order = self.kraken_client.place_market_buy_order(symbol, amount)
            
            if order:
                # Update risk manager
                self.risk_manager.close_position(symbol, exit_price, exit_reason)
                
                # Update performance tracking
                pnl = position.get('pnl', 0)
                self.total_pnl += pnl
                if pnl > 0:
                    self.successful_trades += 1
                
                self.logger.info(f"Position closed: {symbol} {exit_reason} P&L: ${pnl:.2f}")
            else:
                self.logger.error(f"Failed to close position for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
    
    def log_portfolio_summary(self):
        """Log current portfolio summary."""
        try:
            summary = self.risk_manager.get_portfolio_summary()
            balance = self.kraken_client.get_account_balance()
            
            self.logger.info("=== PORTFOLIO SUMMARY ===")
            self.logger.info(f"Total P&L: ${summary.get('total_pnl', 0):.2f}")
            self.logger.info(f"Open Positions: {summary.get('open_positions', 0)}")
            self.logger.info(f"Total Trades: {summary.get('total_trades', 0)}")
            self.logger.info(f"Daily Trades: {summary.get('daily_trades', 0)}")
            self.logger.info(f"Daily Loss: ${summary.get('daily_loss', 0):.2f}")
            self.logger.info(f"Account Balance: {balance}")
            self.logger.info("========================")
            
        except Exception as e:
            self.logger.error(f"Error logging portfolio summary: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        try:
            summary = self.risk_manager.get_portfolio_summary()
            total_trades = summary.get('total_trades', 0)
            closed_trades = summary.get('closed_trades', 0)
            
            win_rate = (self.successful_trades / closed_trades * 100) if closed_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'closed_trades': closed_trades,
                'successful_trades': self.successful_trades,
                'win_rate': win_rate,
                'total_pnl': self.total_pnl,
                'average_pnl': self.total_pnl / closed_trades if closed_trades > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {}
