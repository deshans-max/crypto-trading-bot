import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import config

class RiskManager:
    """Risk management for the trading bot."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_params = config.get_risk_params()
        
        # Track daily trading activity
        self.daily_trades = 0
        self.daily_loss = 0.0
        self.last_trade_date = None
        self.trade_history = []
        self.active_positions = {}
        
        # Cooldown tracking
        self.last_trade_time = 0
        self.cooldown_period = config.cooldown_period
        
    def reset_daily_counters(self):
        """Reset daily trading counters."""
        current_date = datetime.now().date()
        
        if self.last_trade_date != current_date:
            self.daily_trades = 0
            self.daily_loss = 0.0
            self.last_trade_date = current_date
            self.logger.info("Daily trading counters reset")
    
    def can_place_trade(self, symbol: str, trade_type: str, amount: float) -> Tuple[bool, str]:
        """Check if a trade can be placed based on risk management rules."""
        try:
            self.reset_daily_counters()
            
            # Check daily trade limit
            if self.daily_trades >= self.risk_params['max_daily_trades']:
                return False, f"Daily trade limit reached ({self.daily_trades}/{self.risk_params['max_daily_trades']})"
            
            # Check daily loss limit
            if self.daily_loss >= self.risk_params['max_daily_loss']:
                return False, f"Daily loss limit reached (${self.daily_loss:.2f})"
            
            # Check cooldown period
            current_time = time.time()
            if current_time - self.last_trade_time < self.cooldown_period:
                remaining_cooldown = self.cooldown_period - (current_time - self.last_trade_time)
                return False, f"Cooldown period active ({remaining_cooldown:.0f}s remaining)"
            
            # Check position size limit
            if amount > self.risk_params['max_position_size'] * config.investment_amount:
                return False, f"Position size too large (${amount:.2f} > ${self.risk_params['max_position_size'] * config.investment_amount:.2f})"
            
            # Check if already have active position for this symbol
            if symbol in self.active_positions:
                return False, f"Active position already exists for {symbol}"
            
            return True, "Trade allowed"
            
        except Exception as e:
            self.logger.error(f"Error checking trade permission: {e}")
            return False, f"Error: {e}"
    
    def calculate_position_size(self, available_balance: float, current_price: float, risk_percentage: float = None) -> float:
        """Calculate optimal position size based on risk management rules."""
        try:
            if risk_percentage is None:
                risk_percentage = self.risk_params['max_position_size']
            
            # Calculate position size based on available balance and risk percentage
            max_position_value = available_balance * risk_percentage
            position_size = max_position_value / current_price
            
            # Ensure position size doesn't exceed maximum allowed
            max_allowed = config.investment_amount * self.risk_params['max_position_size'] / current_price
            position_size = min(position_size, max_allowed)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def calculate_stop_loss(self, entry_price: float, trade_type: str) -> float:
        """Calculate stop loss price based on percentage."""
        try:
            stop_loss_percentage = self.risk_params['stop_loss'] / 100.0
            
            if trade_type == 'BUY':
                stop_loss = entry_price * (1 - stop_loss_percentage)
            else:  # SELL (short)
                stop_loss = entry_price * (1 + stop_loss_percentage)
            
            return stop_loss
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {e}")
            return 0.0
    
    def calculate_take_profit(self, entry_price: float, trade_type: str) -> float:
        """Calculate take profit price based on percentage."""
        try:
            take_profit_percentage = self.risk_params['take_profit'] / 100.0
            
            if trade_type == 'BUY':
                take_profit = entry_price * (1 + take_profit_percentage)
            else:  # SELL (short)
                take_profit = entry_price * (1 - take_profit_percentage)
            
            return take_profit
            
        except Exception as e:
            self.logger.error(f"Error calculating take profit: {e}")
            return 0.0
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk/reward ratio for a trade."""
        try:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk > 0:
                return reward / risk
            return 0
            
        except Exception as e:
            self.logger.error(f"Error calculating risk/reward ratio: {e}")
            return 0
    
    def record_trade(self, symbol: str, trade_type: str, amount: float, price: float, 
                    stop_loss: float, take_profit: float, order_id: str):
        """Record a new trade for tracking."""
        try:
            trade_record = {
                'symbol': symbol,
                'type': trade_type,
                'amount': amount,
                'entry_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order_id,
                'timestamp': datetime.now(),
                'status': 'OPEN'
            }
            
            self.trade_history.append(trade_record)
            self.active_positions[symbol] = trade_record
            self.daily_trades += 1
            self.last_trade_time = time.time()
            
            self.logger.info(f"Trade recorded: {symbol} {trade_type} {amount} @ {price}")
            
        except Exception as e:
            self.logger.error(f"Error recording trade: {e}")
    
    def close_position(self, symbol: str, exit_price: float, exit_reason: str = "Manual"):
        """Close an active position and calculate P&L."""
        try:
            if symbol not in self.active_positions:
                self.logger.warning(f"No active position found for {symbol}")
                return
            
            position = self.active_positions[symbol]
            entry_price = position['entry_price']
            amount = position['amount']
            trade_type = position['type']
            
            # Calculate P&L
            if trade_type == 'BUY':
                pnl = (exit_price - entry_price) * amount
            else:  # SELL (short)
                pnl = (entry_price - exit_price) * amount
            
            # Update position record
            position['exit_price'] = exit_price
            position['exit_reason'] = exit_reason
            position['pnl'] = pnl
            position['status'] = 'CLOSED'
            position['exit_timestamp'] = datetime.now()
            
            # Update daily loss if negative
            if pnl < 0:
                self.daily_loss += abs(pnl)
            
            # Remove from active positions
            del self.active_positions[symbol]
            
            self.logger.info(f"Position closed: {symbol} P&L: ${pnl:.2f} ({exit_reason})")
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
    
    def check_stop_losses(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check if any active positions have hit stop loss."""
        triggered_stops = []
        
        try:
            for symbol, position in self.active_positions.items():
                if symbol not in current_prices:
                    continue
                
                current_price = current_prices[symbol]
                stop_loss = position['stop_loss']
                trade_type = position['type']
                
                # Check if stop loss is triggered
                stop_triggered = False
                if trade_type == 'BUY' and current_price <= stop_loss:
                    stop_triggered = True
                elif trade_type == 'SELL' and current_price >= stop_loss:
                    stop_triggered = True
                
                if stop_triggered:
                    triggered_stops.append({
                        'symbol': symbol,
                        'position': position,
                        'current_price': current_price,
                        'stop_loss': stop_loss
                    })
            
            return triggered_stops
            
        except Exception as e:
            self.logger.error(f"Error checking stop losses: {e}")
            return []
    
    def check_take_profits(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check if any active positions have hit take profit."""
        triggered_takes = []
        
        try:
            for symbol, position in self.active_positions.items():
                if symbol not in current_prices:
                    continue
                
                current_price = current_prices[symbol]
                take_profit = position['take_profit']
                trade_type = position['type']
                
                # Check if take profit is triggered
                take_triggered = False
                if trade_type == 'BUY' and current_price >= take_profit:
                    take_triggered = True
                elif trade_type == 'SELL' and current_price <= take_profit:
                    take_triggered = True
                
                if take_triggered:
                    triggered_takes.append({
                        'symbol': symbol,
                        'position': position,
                        'current_price': current_price,
                        'take_profit': take_profit
                    })
            
            return triggered_takes
            
        except Exception as e:
            self.logger.error(f"Error checking take profits: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of current portfolio and trading activity."""
        try:
            total_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history if trade.get('status') == 'CLOSED')
            open_positions = len(self.active_positions)
            total_trades = len(self.trade_history)
            closed_trades = len([t for t in self.trade_history if t.get('status') == 'CLOSED'])
            
            return {
                'total_pnl': total_pnl,
                'open_positions': open_positions,
                'total_trades': total_trades,
                'closed_trades': closed_trades,
                'daily_trades': self.daily_trades,
                'daily_loss': self.daily_loss,
                'active_positions': list(self.active_positions.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def is_risk_acceptable(self, entry_price: float, stop_loss: float, take_profit: float) -> bool:
        """Check if the risk/reward ratio is acceptable."""
        try:
            risk_reward_ratio = self.calculate_risk_reward_ratio(entry_price, stop_loss, take_profit)
            
            # Minimum acceptable risk/reward ratio is 2:1
            return risk_reward_ratio >= 2.0
            
        except Exception as e:
            self.logger.error(f"Error checking risk acceptability: {e}")
            return False
