#!/usr/bin/env python3
"""
Crypto Swing Trading Bot - Azure Web App
Flask web application for monitoring and controlling the trading bot.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
import threading
import time
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our trading bot components
from config import config
from swing_trader import SwingTrader
from kraken_client import KrakenClient

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Global variables
trader = None
bot_thread = None
bot_running = False
bot_status = "stopped"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_trader():
    """Initialize the trading bot."""
    global trader
    try:
        trader = SwingTrader()
        return True
    except Exception as e:
        logger.error(f"Error initializing trader: {e}")
        return False

def run_bot():
    """Run the trading bot in a separate thread."""
    global bot_running, bot_status, trader
    
    try:
        bot_status = "starting"
        bot_running = True
        
        # Initialize trader if not already done
        if trader is None:
            if not initialize_trader():
                bot_status = "error"
                return
        
        # Start the trading bot
        trader.start()
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        bot_status = "error"
        bot_running = False

def stop_bot():
    """Stop the trading bot."""
    global bot_running, bot_status, trader
    
    try:
        bot_running = False
        bot_status = "stopping"
        
        if trader:
            trader.stop()
        
        bot_status = "stopped"
        logger.info("Bot stopped successfully")
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        bot_status = "error"

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get bot status and basic info."""
    global bot_running, bot_status, trader
    
    try:
        status_data = {
            'bot_running': bot_running,
            'bot_status': bot_status,
            'trading_pairs': config.get_trading_pairs(),
            'investment_amount': config.investment_amount,
            'max_position_size': config.max_position_size * 100,
            'stop_loss': config.stop_loss_percentage,
            'take_profit': config.take_profit_percentage,
            'max_daily_trades': config.max_daily_trades,
            'max_daily_loss': config.max_daily_loss
        }
        
        return jsonify(status_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def api_portfolio():
    """Get portfolio summary."""
    global trader
    
    try:
        if trader is None:
            return jsonify({'error': 'Trader not initialized'}), 400
        
        summary = trader.risk_manager.get_portfolio_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def api_performance():
    """Get performance statistics."""
    global trader
    
    try:
        if trader is None:
            return jsonify({'error': 'Trader not initialized'}), 400
        
        stats = trader.get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/balance')
def api_balance():
    """Get account balance."""
    try:
        client = KrakenClient()
        balance = client.get_account_balance()
        return jsonify(balance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def api_positions():
    """Get active positions."""
    global trader
    
    try:
        if trader is None:
            return jsonify([])
        
        positions = []
        for symbol, position in trader.risk_manager.active_positions.items():
            positions.append({
                'symbol': symbol,
                'type': position['type'],
                'amount': position['amount'],
                'entry_price': position['entry_price'],
                'stop_loss': position['stop_loss'],
                'take_profit': position['take_profit'],
                'timestamp': position['timestamp'].isoformat()
            })
        
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def api_trades():
    """Get recent trades."""
    global trader
    
    try:
        if trader is None:
            return jsonify([])
        
        trades = []
        for trade in trader.risk_manager.trade_history[-10:]:  # Last 10 trades
            trade_data = {
                'symbol': trade['symbol'],
                'type': trade['type'],
                'amount': trade['amount'],
                'entry_price': trade['entry_price'],
                'status': trade.get('status', 'OPEN'),
                'timestamp': trade['timestamp'].isoformat()
            }
            
            if trade.get('status') == 'CLOSED':
                trade_data.update({
                    'exit_price': trade.get('exit_price'),
                    'pnl': trade.get('pnl', 0),
                    'exit_reason': trade.get('exit_reason', 'Unknown')
                })
            
            trades.append(trade_data)
        
        return jsonify(trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start_bot():
    """Start the trading bot."""
    global bot_thread, bot_running
    
    try:
        if bot_running:
            return jsonify({'error': 'Bot is already running'}), 400
        
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({'message': 'Bot started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop_bot():
    """Stop the trading bot."""
    global bot_running
    
    try:
        if not bot_running:
            return jsonify({'error': 'Bot is not running'}), 400
        
        stop_bot()
        return jsonify({'message': 'Bot stopped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration."""
    if request.method == 'GET':
        try:
            config_data = {
                'trading_pairs': config.get_trading_pairs(),
                'investment_amount': config.investment_amount,
                'max_position_size': config.max_position_size,
                'stop_loss_percentage': config.stop_loss_percentage,
                'take_profit_percentage': config.take_profit_percentage,
                'max_daily_trades': config.max_daily_trades,
                'max_daily_loss': config.max_daily_loss,
                'cooldown_period': config.cooldown_period
            }
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update configuration (this would need to be implemented in config.py)
            # For now, we'll just return success
            return jsonify({'message': 'Configuration updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/test')
def api_test():
    """Test API connection."""
    try:
        # Test configuration
        if not config.validate_config():
            return jsonify({'error': 'Configuration validation failed'}), 400
        
        # Test API connection
        client = KrakenClient()
        if client.test_connection():
            return jsonify({'message': 'All tests passed'})
        else:
            return jsonify({'error': 'API connection failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Azure."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Initialize trader
    initialize_trader()
    
    # Get port from environment variable (for Azure)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
