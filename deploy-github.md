# GitHub-Based Azure Deployment Guide

This guide will help you deploy the Crypto Trading Bot using GitHub integration, which avoids authentication issues.

## Step 1: Push Code to GitHub

1. **Create a new GitHub repository**:
   - Go to https://github.com/new
   - Name it `crypto-trading-bot`
   - Make it public or private (your choice)

2. **Push your code to GitHub**:
   ```bash
   # Add GitHub as remote
   git remote add origin https://github.com/YOUR_USERNAME/crypto-trading-bot.git
   
   # Push to GitHub
   git push -u origin main
   ```

## Step 2: Deploy via Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com

2. **Navigate to your Web App**:
   - Search for "crypto-trading-bot-1754687445"
   - Click on the web app

3. **Configure Deployment**:
   - Go to "Deployment Center"
   - Choose "GitHub" as source
   - Connect your GitHub account
   - Select your repository
   - Choose the main branch
   - Click "Save"

4. **Monitor Deployment**:
   - Go to "Deployment Center" → "Logs"
   - Watch the deployment progress

## Step 3: Configure Application Settings

1. **Go to Configuration**:
   - In your web app, go to "Configuration" → "Application settings"

2. **Add these settings**:
   ```
   KRAKEN_API_KEY = your_kraken_api_key
   KRAKEN_SECRET_KEY = your_kraken_secret_key
   SECRET_KEY = your_flask_secret_key
   LOG_LEVEL = INFO
   LOG_FILE = trading_bot.log
   TRADING_PAIRS = KSM/USD,SUI/USD,DOT/USD,ETH/USD
   INVESTMENT_AMOUNT = 100
   MAX_POSITION_SIZE = 0.1
   STOP_LOSS_PERCENTAGE = 5
   TAKE_PROFIT_PERCENTAGE = 15
   MAX_DAILY_TRADES = 10
   MAX_DAILY_LOSS = 50
   COOLDOWN_PERIOD = 3600
   ```

3. **Save the settings**

## Step 4: Test Your Deployment

1. **Visit your web app**: https://crypto-trading-bot-1754687445.azurewebsites.net

2. **Test the connection** using the "Test Connection" button

3. **Start the bot** using the web interface

## Alternative: Manual File Upload

If GitHub deployment doesn't work, you can manually upload files:

1. **Go to Azure Portal** → Your Web App → "Development Tools" → "Advanced Tools"

2. **Click "Go"** to open Kudu

3. **Navigate to site/wwwroot**

4. **Upload your files**:
   - app.py
   - requirements.txt
   - All other Python files
   - templates/ folder
   - static/ folder

5. **Install dependencies**:
   - Go to "Debug console" → "CMD"
   - Run: `pip install -r requirements.txt`

## Troubleshooting

### Common Issues

1. **Deployment Fails**:
   - Check the deployment logs in Azure Portal
   - Verify all files are committed to GitHub
   - Check Python version compatibility

2. **App Won't Start**:
   - Check the startup command in Configuration
   - Verify all dependencies are installed
   - Check the application logs

3. **API Connection Fails**:
   - Verify API credentials in Application Settings
   - Check if the API keys have proper permissions
   - Test API connection manually

### Useful Commands

```bash
# Check web app status
az webapp show --name crypto-trading-bot-1754687445 --resource-group crypto-trading-bot-uk-rg

# View logs
az webapp log tail --name crypto-trading-bot-1754687445 --resource-group crypto-trading-bot-uk-rg

# Restart web app
az webapp restart --name crypto-trading-bot-1754687445 --resource-group crypto-trading-bot-uk-rg
```

## Next Steps

Once deployed successfully:

1. **Configure your Kraken API credentials**
2. **Test the connection**
3. **Start the bot**
4. **Monitor performance** using the web dashboard

Your web app URL: https://crypto-trading-bot-1754687445.azurewebsites.net
