import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Tuple
import logging
from config import config

class TechnicalAnalyzer:
    """Technical analysis for swing trading strategies."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tech_params = config.get_technical_params()
        
    def prepare_dataframe(self, ohlcv_data: List) -> pd.DataFrame:
        """Convert OHLCV data to pandas DataFrame."""
        try:
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error preparing dataframe: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        """Calculate RSI indicator."""
        try:
            rsi = ta.momentum.RSIIndicator(df['close'], window=self.tech_params['rsi_period'])
            return rsi.rsi()
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return pd.Series()
    
    def calculate_macd(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator."""
        try:
            macd = ta.trend.MACD(
                df['close'],
                window_fast=self.tech_params['macd_fast'],
                window_slow=self.tech_params['macd_slow'],
                window_sign=self.tech_params['macd_signal']
            )
            return macd.macd(), macd.macd_signal(), macd.macd_diff()
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands."""
        try:
            bb = ta.volatility.BollingerBands(
                df['close'],
                window=self.tech_params['bollinger_period'],
                window_dev=self.tech_params['bollinger_std']
            )
            return bb.bollinger_hband(), bb.bollinger_lband(), bb.bollinger_mavg()
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        try:
            return ta.trend.SMAIndicator(df['close'], window=period).sma_indicator()
        except Exception as e:
            self.logger.error(f"Error calculating SMA: {e}")
            return pd.Series()
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        try:
            return ta.trend.EMAIndicator(df['close'], window=period).ema_indicator()
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {e}")
            return pd.Series()
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator."""
        try:
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=k_period, smooth_window=d_period)
            return stoch.stoch(), stoch.stoch_signal()
        except Exception as e:
            self.logger.error(f"Error calculating Stochastic: {e}")
            return pd.Series(), pd.Series()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        try:
            atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=period)
            return atr.average_true_range()
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {e}")
            return pd.Series()
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe."""
        try:
            # RSI
            df['rsi'] = self.calculate_rsi(df)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_diff'] = self.calculate_macd(df)
            
            # Bollinger Bands
            df['bb_upper'], df['bb_lower'], df['bb_middle'] = self.calculate_bollinger_bands(df)
            
            # Moving Averages
            df['sma_20'] = self.calculate_sma(df, 20)
            df['sma_50'] = self.calculate_sma(df, 50)
            df['ema_12'] = self.calculate_ema(df, 12)
            df['ema_26'] = self.calculate_ema(df, 26)
            
            # Stochastic
            df['stoch_k'], df['stoch_d'] = self.calculate_stochastic(df)
            
            # ATR
            df['atr'] = self.calculate_atr(df)
            
            # Price position relative to Bollinger Bands
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
        except Exception as e:
            self.logger.error(f"Error adding indicators: {e}")
            return df
    
    def generate_swing_signals(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate swing trading signals based on multiple indicators."""
        try:
            if df.empty or len(df) < 50:
                return {'signal': 'HOLD', 'strength': 'WEAK', 'reason': 'Insufficient data'}
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            signals = []
            reasons = []
            
            # RSI signals
            if latest['rsi'] < self.tech_params['rsi_oversold']:
                signals.append('BUY')
                reasons.append(f"RSI oversold ({latest['rsi']:.2f})")
            elif latest['rsi'] > self.tech_params['rsi_overbought']:
                signals.append('SELL')
                reasons.append(f"RSI overbought ({latest['rsi']:.2f})")
            
            # MACD signals
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                signals.append('BUY')
                reasons.append("MACD bullish crossover")
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                signals.append('SELL')
                reasons.append("MACD bearish crossover")
            
            # Bollinger Bands signals
            if latest['close'] < latest['bb_lower']:
                signals.append('BUY')
                reasons.append("Price below lower Bollinger Band")
            elif latest['close'] > latest['bb_upper']:
                signals.append('SELL')
                reasons.append("Price above upper Bollinger Band")
            
            # Moving Average signals
            if latest['close'] > latest['sma_20'] > latest['sma_50']:
                signals.append('BUY')
                reasons.append("Price above moving averages (bullish trend)")
            elif latest['close'] < latest['sma_20'] < latest['sma_50']:
                signals.append('SELL')
                reasons.append("Price below moving averages (bearish trend)")
            
            # Stochastic signals
            if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:
                signals.append('BUY')
                reasons.append("Stochastic oversold")
            elif latest['stoch_k'] > 80 and latest['stoch_d'] > 80:
                signals.append('SELL')
                reasons.append("Stochastic overbought")
            
            # Volume confirmation
            volume_confirmed = latest['volume_ratio'] > 1.5
            
            # Determine final signal
            buy_signals = signals.count('BUY')
            sell_signals = signals.count('SELL')
            
            if buy_signals > sell_signals and buy_signals >= 2:
                strength = 'STRONG' if volume_confirmed else 'MODERATE'
                return {
                    'signal': 'BUY',
                    'strength': strength,
                    'reason': '; '.join(reasons),
                    'indicators': signals
                }
            elif sell_signals > buy_signals and sell_signals >= 2:
                strength = 'STRONG' if volume_confirmed else 'MODERATE'
                return {
                    'signal': 'SELL',
                    'strength': strength,
                    'reason': '; '.join(reasons),
                    'indicators': signals
                }
            else:
                return {
                    'signal': 'HOLD',
                    'strength': 'WEAK',
                    'reason': 'Mixed or weak signals',
                    'indicators': signals
                }
                
        except Exception as e:
            self.logger.error(f"Error generating swing signals: {e}")
            return {'signal': 'HOLD', 'strength': 'WEAK', 'reason': f'Error: {e}'}
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels."""
        try:
            recent_highs = df['high'].rolling(window=window).max()
            recent_lows = df['low'].rolling(window=window).min()
            
            resistance = recent_highs.iloc[-1]
            support = recent_lows.iloc[-1]
            
            return support, resistance
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {e}")
            return 0.0, 0.0
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk/reward ratio."""
        try:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk > 0:
                return reward / risk
            return 0
        except Exception as e:
            self.logger.error(f"Error calculating risk/reward ratio: {e}")
            return 0
    
    def is_trend_strong(self, df: pd.DataFrame, period: int = 20) -> bool:
        """Check if the trend is strong enough for swing trading."""
        try:
            if len(df) < period:
                return False
            
            # Calculate trend strength using linear regression
            x = np.arange(period)
            y = df['close'].tail(period).values
            
            slope = np.polyfit(x, y, 1)[0]
            r_squared = np.corrcoef(x, y)[0, 1] ** 2
            
            # Trend is strong if slope is significant and R-squared is high
            return abs(slope) > 0.001 and r_squared > 0.7
        except Exception as e:
            self.logger.error(f"Error checking trend strength: {e}")
            return False
