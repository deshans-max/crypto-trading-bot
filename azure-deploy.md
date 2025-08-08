# Azure Web App Deployment Guide

This guide will help you deploy the Crypto Swing Trading Bot to Azure Web App.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure CLI**: Install Azure CLI for deployment
3. **Git**: For source control and deployment
4. **Kraken API Keys**: Your trading bot API credentials

## Deployment Steps

### 1. Prepare Your Environment Variables

Before deploying, you need to set up your environment variables in Azure:

```bash
# Set your Kraken API credentials
az webapp config appsettings set --name YOUR-APP-NAME --resource-group YOUR-RESOURCE-GROUP --settings KRAKEN_API_KEY="your_api_key_here"
az webapp config appsettings set --name YOUR-APP-NAME --resource-group YOUR-RESOURCE-GROUP --settings KRAKEN_SECRET_KEY="your_secret_key_here"

# Set other configuration
az webapp config appsettings set --name YOUR-APP-NAME --resource-group YOUR-RESOURCE-GROUP --settings SECRET_KEY="your_secret_key_for_flask"
az webapp config appsettings set --name YOUR-APP-NAME --resource-group YOUR-RESOURCE-GROUP --settings LOG_LEVEL="INFO"
```

### 2. Create Azure Web App

```bash
# Create a resource group (if you don't have one)
az group create --name crypto-trading-bot-rg --location "East US"

# Create an App Service plan
az appservice plan create --name crypto-trading-plan --resource-group crypto-trading-bot-rg --sku B1 --is-linux

# Create the web app
az webapp create --resource-group crypto-trading-bot-rg --plan crypto-trading-plan --name YOUR-APP-NAME --runtime "PYTHON:3.11"
```

### 3. Configure the Web App

```bash
# Set Python version
az webapp config set --resource-group crypto-trading-bot-rg --name YOUR-APP-NAME --linux-fx-version "PYTHON|3.11"

# Enable logging
az webapp log config --resource-group crypto-trading-bot-rg --name YOUR-APP-NAME --web-server-logging filesystem

# Set startup command
az webapp config set --resource-group crypto-trading-bot-rg --name YOUR-APP-NAME --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

### 4. Deploy Your Code

#### Option A: Deploy from Local Git

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Add Azure remote
az webapp deployment source config-local-git --name YOUR-APP-NAME --resource-group crypto-trading-bot-rg

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

### 5. Configure Application Settings

In the Azure Portal:

1. Go to your Web App
2. Navigate to "Configuration" → "Application settings"
3. Add the following settings:

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

### 6. Test Your Deployment

1. Visit your web app URL: `https://YOUR-APP-NAME.azurewebsites.net`
2. Test the connection using the "Test Connection" button
3. Start the bot using the web interface

## Security Considerations

### 1. Environment Variables
- Never commit API keys to source control
- Use Azure Key Vault for sensitive data
- Rotate API keys regularly

### 2. Network Security
- Enable HTTPS only
- Configure IP restrictions if needed
- Monitor access logs

### 3. Application Security
- Use strong Flask secret key
- Enable authentication if needed
- Monitor application logs

## Monitoring and Logging

### 1. Application Logs
```bash
# View application logs
az webapp log tail --name YOUR-APP-NAME --resource-group crypto-trading-bot-rg
```

### 2. Performance Monitoring
- Enable Application Insights
- Monitor CPU and memory usage
- Set up alerts for high resource usage

### 3. Trading Bot Monitoring
- Use the web dashboard to monitor bot status
- Check logs for trading activity
- Monitor portfolio performance

## Troubleshooting

### Common Issues

1. **App won't start**
   - Check startup command in Azure
   - Verify Python version compatibility
   - Check application logs

2. **API connection fails**
   - Verify API credentials in Azure settings
   - Check network connectivity
   - Test API keys manually

3. **Bot not trading**
   - Check account balance
   - Verify trading permissions
   - Review risk management settings

### Debug Commands

```bash
# Check app status
az webapp show --name YOUR-APP-NAME --resource-group crypto-trading-bot-rg

# View logs
az webapp log download --name YOUR-APP-NAME --resource-group crypto-trading-bot-rg

# Restart app
az webapp restart --name YOUR-APP-NAME --resource-group crypto-trading-bot-rg
```

## Cost Optimization

1. **App Service Plan**: Start with B1 (Basic) plan
2. **Scaling**: Use consumption plan for low traffic
3. **Monitoring**: Enable only necessary monitoring features
4. **Logs**: Configure log retention periods

## Best Practices

1. **Development**: Test locally before deploying
2. **Staging**: Use staging slots for testing
3. **Backup**: Regular backups of configuration
4. **Updates**: Keep dependencies updated
5. **Security**: Regular security reviews

## Support

- Azure Documentation: https://docs.microsoft.com/azure/app-service/
- Flask Documentation: https://flask.palletsprojects.com/
- Kraken API Documentation: https://www.kraken.com/features/api
