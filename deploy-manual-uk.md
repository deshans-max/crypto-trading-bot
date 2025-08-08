# Manual Azure Deployment Guide - UK West Region

This guide will help you manually deploy the Crypto Trading Bot to Azure Web App in the UK West region.

## Prerequisites

1. **Azure CLI installed** ✅ (Already done)
2. **Logged into Azure** ✅ (Already done)
3. **Git repository ready** ✅ (Already done)

## Step-by-Step Manual Deployment

### Step 1: Create Resource Group

```bash
az group create --name crypto-trading-bot-uk-rg --location "UK West"
```

### Step 2: Create App Service Plan (Free Tier)

```bash
az appservice plan create \
    --name crypto-trading-plan-uk \
    --resource-group crypto-trading-bot-uk-rg \
    --sku F1 \
    --is-linux
```

### Step 3: Create Web App

```bash
az webapp create \
    --resource-group crypto-trading-bot-uk-rg \
    --plan crypto-trading-plan-uk \
    --name crypto-trading-bot-$(date +%s) \
    --runtime "PYTHON:3.11"
```

### Step 4: Configure the Web App

```bash
# Set Python version
az webapp config set \
    --resource-group crypto-trading-bot-uk-rg \
    --name YOUR_APP_NAME \
    --linux-fx-version "PYTHON|3.11"

# Enable logging
az webapp log config \
    --resource-group crypto-trading-bot-uk-rg \
    --name YOUR_APP_NAME \
    --web-server-logging filesystem

# Set startup command
az webapp config set \
    --resource-group crypto-trading-bot-uk-rg \
    --name YOUR_APP_NAME \
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

### Step 5: Deploy Your Code

#### Option A: Deploy from Local Git

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial deployment"

# Configure deployment
az webapp deployment source config-local-git \
    --name YOUR_APP_NAME \
    --resource-group crypto-trading-bot-uk-rg

# Deploy
git remote add azure <GIT_URL_FROM_PREVIOUS_COMMAND>
git push azure main
```

#### Option B: Deploy from GitHub

1. Push your code to GitHub
2. In Azure Portal, go to your Web App
3. Navigate to "Deployment Center"
4. Choose "GitHub" as source
5. Connect your GitHub account and select your repository

### Step 6: Configure Application Settings

In Azure Portal:

1. Go to your Web App
2. Navigate to "Configuration" → "Application settings"
3. Add these settings:

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

### Step 7: Test Your Deployment

1. Visit your web app URL: `https://YOUR_APP_NAME.azurewebsites.net`
2. Test the connection using the "Test Connection" button
3. Start the bot using the web interface

## Troubleshooting

### Common Issues

1. **Quota Exceeded**: Use Free tier (F1) instead of Basic
2. **Region Not Available**: Try different regions like "UK South" or "West Europe"
3. **Python Version Issues**: Make sure to use Python 3.11
4. **Deployment Failures**: Check the deployment logs in Azure Portal

### Alternative Regions

If UK West doesn't work, try these regions:

```bash
# UK South
az group create --name crypto-trading-bot-uk-south-rg --location "UK South"

# West Europe
az group create --name crypto-trading-bot-we-rg --location "West Europe"

# North Europe
az group create --name crypto-trading-bot-ne-rg --location "North Europe"
```

### Check Available Regions

```bash
az account list-locations --output table
```

## Cost Optimization

- **Free Tier**: Use F1 plan for development/testing
- **Basic Tier**: Use B1 plan for production (if needed)
- **Monitoring**: Enable only necessary monitoring features
- **Logs**: Configure log retention periods

## Security Best Practices

1. **Environment Variables**: Never commit API keys to source control
2. **HTTPS Only**: Enable HTTPS only in Azure
3. **IP Restrictions**: Configure IP restrictions if needed
4. **Regular Updates**: Keep dependencies updated

## Support

- Azure Documentation: https://docs.microsoft.com/azure/app-service/
- Flask Documentation: https://flask.palletsprojects.com/
- Kraken API Documentation: https://www.kraken.com/features/api
