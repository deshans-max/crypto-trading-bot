# Crypto Swing Trading Bot for Kraken

A sophisticated automated trading bot designed for swing trading cryptocurrencies on Kraken. The bot trades KSM, SUI, DOT, and ETH using advanced technical analysis and comprehensive risk management.

## 🌐 Azure Web App Deployment

This bot can be deployed as an Azure Web App for cloud-based operation with a beautiful web dashboard.

### Quick Deploy to Azure

1. **Install Azure CLI** (if not already installed):
   ```bash
   # macOS
   brew install azure-cli
   
   # Windows
   winget install Microsoft.AzureCLI
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Deploy to Azure**:
   ```bash
   ./deploy-azure.sh
   ```

4. **Configure API Credentials** in Azure Portal:
   - Go to your Web App in Azure Portal
   - Navigate to Configuration → Application settings
   - Add your Kraken API credentials

5. **Access Your Bot**:
   - Visit your web app URL
   - Use the web dashboard to monitor and control the bot

### Web Dashboard Features

- **Real-time Monitoring**: Live portfolio tracking and performance statistics
- **Control Panel**: Start/stop bot with one click
- **Portfolio Summary**: View total P&L, open positions, and trade history
- **Configuration**: Adjust trading parameters through the web interface
- **Mobile Responsive**: Works on desktop and mobile devices

## Features

- **Swing Trading Strategy**: Designed for medium-term trades (hours to days)
- **Multi-Indicator Analysis**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic
- **Risk Management**: Stop-loss, take-profit, position sizing, daily limits
- **Real-time Monitoring**: Live portfolio tracking and performance statistics
- **Automated Trading**: 24/7 operation with scheduled analysis cycles
- **Comprehensive Logging**: Detailed logs for debugging and performance analysis
- **Web Dashboard**: Beautiful web interface for monitoring and control

## Trading Strategy

The bot implements a swing trading strategy that:

1. **Identifies Trends**: Uses multiple technical indicators to identify strong trends
2. **Entry Signals**: Generates buy/sell signals based on oversold/overbought conditions
3. **Risk Management**: Implements strict stop-loss and take-profit levels
4. **Position Sizing**: Calculates optimal position sizes based on available balance
5. **Portfolio Management**: Limits exposure and manages multiple positions

### Technical Indicators Used

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Trend following and momentum
- **Bollinger Bands**: Volatility and price channel analysis
- **Moving Averages**: Trend confirmation (SMA 20, 50 and EMA 12, 26)
- **Stochastic Oscillator**: Momentum and reversal signals
- **Volume Analysis**: Confirms signal strength

## Installation

### Prerequisites

- Python 3.8 or higher
- Kraken API account with trading permissions
- Sufficient funds for trading
- Azure account (for cloud deployment)

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd crypto-trading-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your Kraken API credentials and trading parameters:
   ```env
   KRAKEN_API_KEY=your_kraken_api_key_here
   KRAKEN_SECRET_KEY=your_kraken_secret_key_here
   
   # Trading Configuration
   TRADING_PAIRS=KSM/USD,SUI/USD,DOT/USD,ETH/USD
   INVESTMENT_AMOUNT=100
   MAX_POSITION_SIZE=0.1
   STOP_LOSS_PERCENTAGE=5
   TAKE_PROFIT_PERCENTAGE=15
   ```

## Usage

### Local Development

#### Testing the Setup

Before running the bot, test your configuration:

```bash
python main.py --test
```

This will verify:
- API connection to Kraken
- Configuration validation
- Technical analysis module initialization
- Risk management setup

#### Starting the Bot

```bash
# Start the trading bot
python main.py --start

# Start in dry-run mode (no real trades)
python main.py --start --dry-run

# Enable verbose logging
python main.py --start --verbose
```

#### Web Dashboard (Local)

```bash
# Start the Flask web app
python app.py

# Visit http://localhost:5000 in your browser
```

### Azure Web App

Once deployed to Azure:

1. **Access your web app**: Visit your Azure Web App URL
2. **Test connection**: Use the "Test Connection" button
3. **Start the bot**: Click "Start Bot" in the web interface
4. **Monitor performance**: Use the real-time dashboard

### Monitoring and Control

**Check current status**:
```bash
python main.py --status
```

**View account balance**:
```bash
python main.py --balance
```

**Show configuration**:
```bash
python main.py --config
```

**Stop the bot**: Press `Ctrl+C` in the terminal or use the web interface

## Configuration

### Trading Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INVESTMENT_AMOUNT` | 100 | Base investment amount per trade |
| `MAX_POSITION_SIZE` | 0.1 | Maximum position size as fraction of balance |
| `STOP_LOSS_PERCENTAGE` | 5 | Stop loss percentage |
| `TAKE_PROFIT_PERCENTAGE` | 15 | Take profit percentage |
| `MAX_DAILY_TRADES` | 10 | Maximum trades per day |
| `MAX_DAILY_LOSS` | 50 | Maximum daily loss in USD |
| `COOLDOWN_PERIOD` | 3600 | Seconds between trades |

### Technical Analysis Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RSI_PERIOD` | 14 | RSI calculation period |
| `RSI_OVERBOUGHT` | 70 | RSI overbought threshold |
| `RSI_OVERSOLD` | 30 | RSI oversold threshold |
| `MACD_FAST` | 12 | MACD fast EMA period |
| `MACD_SLOW` | 26 | MACD slow EMA period |
| `MACD_SIGNAL` | 9 | MACD signal line period |
| `BOLLINGER_PERIOD` | 20 | Bollinger Bands period |
| `BOLLINGER_STD` | 2 | Bollinger Bands standard deviation |

## Risk Management

The bot implements several risk management features:

### Position Sizing
- Calculates optimal position size based on available balance
- Limits maximum position size to prevent overexposure
- Considers current market price for accurate sizing

### Stop Loss and Take Profit
- Automatic stop-loss orders to limit losses
- Take-profit orders to secure gains
- Configurable percentages for both

### Daily Limits
- Maximum number of trades per day
- Maximum daily loss limit
- Cooldown periods between trades

### Portfolio Management
- Tracks all active positions
- Monitors portfolio performance
- Prevents overexposure to single assets

## Trading Pairs

The bot is configured to trade:
- **KSM/USD** (Kusama)
- **SUI/USD** (Sui)
- **DOT/USD** (Polkadot)
- **ETH/USD** (Ethereum)

## Performance Tracking

The bot tracks various performance metrics:

- Total number of trades
- Win rate percentage
- Total P&L (Profit & Loss)
- Average P&L per trade
- Daily trading activity
- Active positions

## Logging

The bot provides comprehensive logging:

- **File Logging**: All activities logged to `trading_bot.log`
- **Console Output**: Real-time status updates
- **Error Tracking**: Detailed error messages and stack traces
- **Trade Records**: Complete trade history with timestamps
- **Web Dashboard**: Real-time monitoring interface

## Safety Features

### API Security
- Secure API key storage using environment variables
- Rate limiting to prevent API abuse
- Error handling for network issues

### Trading Safety
- Dry-run mode for testing
- Manual override capabilities
- Emergency stop functionality
- Web-based control interface

### Data Protection
- Local data storage only
- No external data transmission
- Secure credential handling

## Azure Deployment

### Benefits of Azure Web App

1. **24/7 Operation**: Runs continuously in the cloud
2. **Web Dashboard**: Beautiful interface for monitoring
3. **Scalability**: Can handle multiple trading pairs
4. **Security**: Azure-managed security and updates
5. **Monitoring**: Built-in logging and monitoring
6. **Cost Effective**: Pay only for what you use

### Deployment Options

1. **Quick Deploy**: Use the provided script
2. **Manual Deploy**: Follow the detailed guide
3. **GitHub Integration**: Deploy directly from GitHub

See `azure-deploy.md` for detailed deployment instructions.

## Important Notes

### ⚠️ Risk Warning
- Cryptocurrency trading involves significant risk
- Past performance does not guarantee future results
- Only trade with funds you can afford to lose
- The bot is for educational and experimental purposes

### 🔧 Technical Requirements
- Stable internet connection required
- Kraken API access with trading permissions
- Sufficient account balance for trading
- Python environment with required dependencies
- Azure account (for cloud deployment)

### 📊 Monitoring
- Regularly check bot performance
- Monitor account balance and positions
- Review logs for any issues
- Adjust parameters based on market conditions
- Use the web dashboard for real-time monitoring

## Troubleshooting

### Common Issues

**API Connection Failed**:
- Verify API credentials in `.env` file or Azure settings
- Check internet connection
- Ensure API permissions include trading

**No Trades Executed**:
- Check account balance
- Verify trading pair availability
- Review technical analysis parameters
- Check daily trade limits

**Configuration Errors**:
- Validate all environment variables
- Check parameter ranges and types
- Ensure proper file permissions

**Azure Deployment Issues**:
- Check Azure CLI installation
- Verify Azure login status
- Review deployment logs
- Check application settings in Azure Portal

### Getting Help

1. Check the logs in `trading_bot.log`
2. Run `python main.py --test` to diagnose issues
3. Review configuration with `python main.py --config`
4. Check account status with `python main.py --balance`
5. Use the web dashboard for real-time monitoring

## Development

### Project Structure
```
crypto-trading-bot/
├── app.py                 # Flask web application
├── main.py               # Command-line interface
├── config.py             # Configuration management
├── kraken_client.py      # Kraken API wrapper
├── technical_analysis.py # Technical indicators
├── risk_manager.py       # Risk management
├── swing_trader.py       # Main trading logic
├── dashboard.py          # Terminal dashboard
├── templates/            # Web templates
│   └── index.html       # Main dashboard page
├── static/              # Static web assets
│   ├── css/
│   │   └── style.css    # Dashboard styles
│   └── js/
│       └── app.js       # Dashboard JavaScript
├── requirements.txt      # Python dependencies
├── env_example.txt      # Environment variables template
├── deploy-azure.sh      # Azure deployment script
├── azure-deploy.md      # Detailed deployment guide
└── README.md           # This file
```

### Adding New Features

1. **New Trading Pairs**: Add to `TRADING_PAIRS` in `.env`
2. **New Indicators**: Extend `TechnicalAnalyzer` class
3. **Risk Rules**: Modify `RiskManager` class
4. **Trading Logic**: Update `SwingTrader` class
5. **Web Interface**: Modify Flask app and templates

## License

This project is for educational purposes. Use at your own risk.

## Disclaimer

This trading bot is provided as-is without any guarantees. Cryptocurrency trading involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software.
