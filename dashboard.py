#!/usr/bin/env python3
"""
Simple Dashboard for Crypto Swing Trading Bot
Provides real-time monitoring of bot performance and portfolio status.
"""

import time
import os
import sys
from datetime import datetime, timedelta
import json

from swing_trader import SwingTrader
from config import config

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_currency(amount):
    """Format currency amount with proper sign and color."""
    if amount >= 0:
        return f"${amount:.2f}"
    else:
        return f"-${abs(amount):.2f}"

def format_percentage(value):
    """Format percentage with proper sign."""
    if value >= 0:
        return f"+{value:.1f}%"
    else:
        return f"{value:.1f}%"

def get_colored_text(text, color_code):
    """Return colored text for terminal output."""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color_code, '')}{text}{colors['reset']}"

def display_header():
    """Display dashboard header."""
    print("=" * 80)
    print(get_colored_text("🚀 CRYPTO SWING TRADING BOT DASHBOARD", 'bold'))
    print("=" * 80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def display_configuration():
    """Display current configuration."""
    print("\n" + get_colored_text("📋 CONFIGURATION", 'cyan'))
    print("-" * 40)
    print(f"Trading Pairs: {', '.join(config.get_trading_pairs())}")
    print(f"Investment Amount: {format_currency(config.investment_amount)}")
    print(f"Max Position Size: {config.max_position_size * 100}%")
    print(f"Stop Loss: {config.stop_loss_percentage}%")
    print(f"Take Profit: {config.take_profit_percentage}%")
    print(f"Max Daily Trades: {config.max_daily_trades}")
    print(f"Max Daily Loss: {format_currency(config.max_daily_loss)}")

def display_portfolio_summary(trader):
    """Display portfolio summary."""
    try:
        summary = trader.risk_manager.get_portfolio_summary()
        
        print("\n" + get_colored_text("💰 PORTFOLIO SUMMARY", 'cyan'))
        print("-" * 40)
        
        total_pnl = summary.get('total_pnl', 0)
        pnl_color = 'green' if total_pnl >= 0 else 'red'
        print(f"Total P&L: {get_colored_text(format_currency(total_pnl), pnl_color)}")
        
        print(f"Open Positions: {summary.get('open_positions', 0)}")
        print(f"Total Trades: {summary.get('total_trades', 0)}")
        print(f"Closed Trades: {summary.get('closed_trades', 0)}")
        print(f"Daily Trades: {summary.get('daily_trades', 0)}")
        
        daily_loss = summary.get('daily_loss', 0)
        if daily_loss > 0:
            print(f"Daily Loss: {get_colored_text(format_currency(daily_loss), 'red')}")
        
        active_positions = summary.get('active_positions', [])
        if active_positions:
            print(f"Active Positions: {', '.join(active_positions)}")
        
    except Exception as e:
        print(f"Error getting portfolio summary: {e}")

def display_performance_stats(trader):
    """Display performance statistics."""
    try:
        stats = trader.get_performance_stats()
        
        print("\n" + get_colored_text("📊 PERFORMANCE STATISTICS", 'cyan'))
        print("-" * 40)
        
        if stats:
            total_trades = stats.get('total_trades', 0)
            closed_trades = stats.get('closed_trades', 0)
            successful_trades = stats.get('successful_trades', 0)
            win_rate = stats.get('win_rate', 0)
            total_pnl = stats.get('total_pnl', 0)
            avg_pnl = stats.get('average_pnl', 0)
            
            print(f"Total Trades: {total_trades}")
            print(f"Closed Trades: {closed_trades}")
            print(f"Successful Trades: {successful_trades}")
            
            win_rate_color = 'green' if win_rate >= 50 else 'red'
            print(f"Win Rate: {get_colored_text(f'{win_rate:.1f}%', win_rate_color)}")
            
            pnl_color = 'green' if total_pnl >= 0 else 'red'
            print(f"Total P&L: {get_colored_text(format_currency(total_pnl), pnl_color)}")
            
            avg_color = 'green' if avg_pnl >= 0 else 'red'
            print(f"Average P&L: {get_colored_text(format_currency(avg_pnl), avg_color)}")
            
            if closed_trades > 0:
                profit_factor = successful_trades / closed_trades if closed_trades > 0 else 0
                print(f"Profit Factor: {profit_factor:.2f}")
        
    except Exception as e:
        print(f"Error getting performance stats: {e}")

def display_active_positions(trader):
    """Display active positions."""
    try:
        active_positions = trader.risk_manager.active_positions
        
        if not active_positions:
            print("\n" + get_colored_text("📈 ACTIVE POSITIONS", 'cyan'))
            print("-" * 40)
            print("No active positions")
            return
        
        print("\n" + get_colored_text("📈 ACTIVE POSITIONS", 'cyan'))
        print("-" * 40)
        
        for symbol, position in active_positions.items():
            print(f"\nSymbol: {get_colored_text(symbol, 'bold')}")
            print(f"Type: {position['type']}")
            print(f"Amount: {position['amount']:.6f}")
            print(f"Entry Price: {format_currency(position['entry_price'])}")
            print(f"Stop Loss: {format_currency(position['stop_loss'])}")
            print(f"Take Profit: {format_currency(position['take_profit'])}")
            print(f"Entry Time: {position['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Calculate current P&L if we have current price
            try:
                from kraken_client import KrakenClient
                client = KrakenClient()
                ticker = client.get_ticker_info(symbol)
                if ticker:
                    current_price = ticker['last']
                    if position['type'] == 'BUY':
                        pnl = (current_price - position['entry_price']) * position['amount']
                    else:
                        pnl = (position['entry_price'] - current_price) * position['amount']
                    
                    pnl_color = 'green' if pnl >= 0 else 'red'
                    pnl_percent = (pnl / (position['entry_price'] * position['amount'])) * 100
                    
                    print(f"Current Price: {format_currency(current_price)}")
                    print(f"Current P&L: {get_colored_text(format_currency(pnl), pnl_color)}")
                    print(f"P&L %: {get_colored_text(format_percentage(pnl_percent), pnl_color)}")
            except Exception as e:
                print(f"Could not calculate current P&L: {e}")
        
    except Exception as e:
        print(f"Error displaying active positions: {e}")

def display_recent_trades(trader, limit=5):
    """Display recent trades."""
    try:
        trade_history = trader.risk_manager.trade_history
        
        if not trade_history:
            print("\n" + get_colored_text("📝 RECENT TRADES", 'cyan'))
            print("-" * 40)
            print("No trades yet")
            return
        
        print("\n" + get_colored_text("📝 RECENT TRADES", 'cyan'))
        print("-" * 40)
        
        recent_trades = sorted(trade_history, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        for trade in recent_trades:
            status_color = 'green' if trade.get('status') == 'CLOSED' else 'yellow'
            print(f"\nSymbol: {get_colored_text(trade['symbol'], 'bold')}")
            print(f"Type: {trade['type']}")
            print(f"Amount: {trade['amount']:.6f}")
            print(f"Entry Price: {format_currency(trade['entry_price'])}")
            print(f"Status: {get_colored_text(trade.get('status', 'OPEN'), status_color)}")
            print(f"Time: {trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            if trade.get('status') == 'CLOSED' and 'pnl' in trade:
                pnl = trade['pnl']
                pnl_color = 'green' if pnl >= 0 else 'red'
                print(f"P&L: {get_colored_text(format_currency(pnl), pnl_color)}")
                print(f"Exit Reason: {trade.get('exit_reason', 'Unknown')}")
        
    except Exception as e:
        print(f"Error displaying recent trades: {e}")

def display_system_status():
    """Display system status."""
    print("\n" + get_colored_text("⚙️ SYSTEM STATUS", 'cyan'))
    print("-" * 40)
    
    # Check if bot is running (simplified check)
    try:
        trader = SwingTrader()
        print("Bot Status: " + get_colored_text("Ready", 'green'))
    except Exception as e:
        print("Bot Status: " + get_colored_text("Error", 'red'))
        print(f"Error: {e}")
    
    # Check log file
    log_file = config.log_file
    if os.path.exists(log_file):
        file_size = os.path.getsize(log_file)
        print(f"Log File: {log_file} ({file_size} bytes)")
    else:
        print(f"Log File: {log_file} (not found)")

def main():
    """Main dashboard function."""
    try:
        while True:
            clear_screen()
            display_header()
            
            # Initialize trader
            trader = SwingTrader()
            
            # Display all sections
            display_configuration()
            display_portfolio_summary(trader)
            display_performance_stats(trader)
            display_active_positions(trader)
            display_recent_trades(trader)
            display_system_status()
            
            # Footer
            print("\n" + "=" * 80)
            print("Press Ctrl+C to exit | Auto-refresh every 30 seconds")
            print("=" * 80)
            
            # Wait for 30 seconds before refreshing
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Dashboard error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
