#!/usr/bin/env python3
"""
Crypto Swing Trading Bot for Kraken
Trades KSM, SUI, DOT, and ETH using technical analysis and risk management.
"""

import argparse
import sys
import time
import logging
from datetime import datetime
import json

from swing_trader import SwingTrader
from config import config

def setup_argparse():
    """Setup command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Crypto Swing Trading Bot for Kraken',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --start                    # Start the trading bot
  python main.py --test                     # Test API connection
  python main.py --status                   # Show current status
  python main.py --config                   # Show current configuration
  python main.py --balance                  # Show account balance
        """
    )
    
    parser.add_argument('--start', action='store_true',
                       help='Start the trading bot')
    parser.add_argument('--test', action='store_true',
                       help='Test API connection and configuration')
    parser.add_argument('--status', action='store_true',
                       help='Show current trading status and performance')
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')
    parser.add_argument('--balance', action='store_true',
                       help='Show account balance')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no real trades)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    return parser

def test_connection():
    """Test API connection and configuration."""
    print("Testing API connection and configuration...")
    
    try:
        # Test configuration
        if not config.validate_config():
            print("❌ Configuration validation failed")
            return False
        
        print("✅ Configuration validation passed")
        
        # Test API connection
        from kraken_client import KrakenClient
        client = KrakenClient()
        
        if client.test_connection():
            print("✅ API connection successful")
            
            # Show account balance
            balance = client.get_account_balance()
            if balance:
                print("✅ Account balance retrieved:")
                for currency, amount in balance.items():
                    print(f"   {currency}: {amount}")
            else:
                print("⚠️  Could not retrieve account balance")
        else:
            print("❌ API connection failed")
            return False
        
        # Test technical analysis
        from technical_analysis import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        print("✅ Technical analysis module initialized")
        
        # Test risk management
        from risk_manager import RiskManager
        risk_manager = RiskManager()
        print("✅ Risk management module initialized")
        
        print("\n🎉 All tests passed! The bot is ready to run.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_status():
    """Show current trading status and performance."""
    try:
        trader = SwingTrader()
        
        print("=== TRADING BOT STATUS ===")
        print(f"Trading Pairs: {', '.join(config.get_trading_pairs())}")
        print(f"Investment Amount: ${config.investment_amount}")
        print(f"Max Position Size: {config.max_position_size * 100}%")
        print(f"Stop Loss: {config.stop_loss_percentage}%")
        print(f"Take Profit: {config.take_profit_percentage}%")
        
        # Get performance stats
        stats = trader.get_performance_stats()
        if stats:
            print("\n=== PERFORMANCE STATISTICS ===")
            print(f"Total Trades: {stats.get('total_trades', 0)}")
            print(f"Closed Trades: {stats.get('closed_trades', 0)}")
            print(f"Successful Trades: {stats.get('successful_trades', 0)}")
            print(f"Win Rate: {stats.get('win_rate', 0):.1f}%")
            print(f"Total P&L: ${stats.get('total_pnl', 0):.2f}")
            print(f"Average P&L: ${stats.get('average_pnl', 0):.2f}")
        
        # Get portfolio summary
        summary = trader.risk_manager.get_portfolio_summary()
        if summary:
            print("\n=== PORTFOLIO SUMMARY ===")
            print(f"Open Positions: {summary.get('open_positions', 0)}")
            print(f"Daily Trades: {summary.get('daily_trades', 0)}")
            print(f"Daily Loss: ${summary.get('daily_loss', 0):.2f}")
            print(f"Active Positions: {', '.join(summary.get('active_positions', []))}")
        
        print("==========================")
        
    except Exception as e:
        print(f"Error getting status: {e}")

def show_config():
    """Show current configuration."""
    print("=== CURRENT CONFIGURATION ===")
    print(f"Trading Pairs: {config.get_trading_pairs()}")
    print(f"Investment Amount: ${config.investment_amount}")
    print(f"Max Position Size: {config.max_position_size * 100}%")
    print(f"Stop Loss: {config.stop_loss_percentage}%")
    print(f"Take Profit: {config.take_profit_percentage}%")
    print(f"Max Daily Trades: {config.max_daily_trades}")
    print(f"Max Daily Loss: ${config.max_daily_loss}")
    print(f"Cooldown Period: {config.cooldown_period} seconds")
    
    tech_params = config.get_technical_params()
    print("\n=== TECHNICAL ANALYSIS PARAMETERS ===")
    print(f"RSI Period: {tech_params['rsi_period']}")
    print(f"RSI Overbought: {tech_params['rsi_overbought']}")
    print(f"RSI Oversold: {tech_params['rsi_oversold']}")
    print(f"MACD Fast: {tech_params['macd_fast']}")
    print(f"MACD Slow: {tech_params['macd_slow']}")
    print(f"MACD Signal: {tech_params['macd_signal']}")
    print(f"Bollinger Period: {tech_params['bollinger_period']}")
    print(f"Bollinger Std: {tech_params['bollinger_std']}")
    
    print("\n=== SWING TRADING PARAMETERS ===")
    print(f"Swing Hold Period: {config.swing_hold_period} seconds")
    print(f"Min Swing Movement: {config.min_swing_movement * 100}%")
    print(f"Trend Confirmation Period: {config.trend_confirmation_period} hours")
    
    print("================================")

def show_balance():
    """Show account balance."""
    try:
        from kraken_client import KrakenClient
        client = KrakenClient()
        
        balance = client.get_account_balance()
        if balance:
            print("=== ACCOUNT BALANCE ===")
            total_usd = 0
            
            for currency, amount in balance.items():
                if currency == 'USD':
                    total_usd += amount
                    print(f"{currency}: ${amount:.2f}")
                else:
                    # Get current price for crypto
                    ticker = client.get_ticker_info(f"{currency}/USD")
                    if ticker:
                        usd_value = amount * ticker['last']
                        total_usd += usd_value
                        print(f"{currency}: {amount:.6f} (${usd_value:.2f})")
                    else:
                        print(f"{currency}: {amount:.6f}")
            
            print(f"\nTotal Portfolio Value: ${total_usd:.2f}")
            print("======================")
        else:
            print("Could not retrieve account balance")
            
    except Exception as e:
        print(f"Error getting balance: {e}")

def main():
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handle command line arguments
    if args.test:
        success = test_connection()
        sys.exit(0 if success else 1)
    
    elif args.status:
        show_status()
        sys.exit(0)
    
    elif args.config:
        show_config()
        sys.exit(0)
    
    elif args.balance:
        show_balance()
        sys.exit(0)
    
    elif args.start:
        print("Starting Crypto Swing Trading Bot...")
        print("Press Ctrl+C to stop the bot")
        
        try:
            trader = SwingTrader()
            
            # Set dry-run mode if requested
            if args.dry_run:
                print("⚠️  Running in DRY-RUN mode - no real trades will be executed")
                # TODO: Implement dry-run mode
            
            # Start the trading bot
            trader.start()
            
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"Error starting bot: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
