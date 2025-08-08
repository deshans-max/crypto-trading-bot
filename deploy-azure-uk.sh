#!/bin/bash

# Azure Web App Deployment Script for Crypto Trading Bot - UK South Region

echo "🚀 Deploying Crypto Trading Bot to Azure Web App (UK South)..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

# Configuration for UK South
RESOURCE_GROUP="crypto-trading-bot-uk-rg"
APP_NAME="crypto-trading-bot-$(date +%s)"
LOCATION="UK South"
PLAN_NAME="crypto-trading-plan-uk"

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Name: $APP_NAME"
echo "   Location: $LOCATION"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output none

# Create App Service plan with Free tier
echo "📋 Creating App Service plan (Free tier)..."
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku F1 \
    --is-linux \
    --output none

# Create web app
echo "🌐 Creating web app..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "PYTHON:3.11" \
    --output none

# Configure Python version
echo "🐍 Configuring Python..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --linux-fx-version "PYTHON|3.11" \
    --output none

# Enable logging
echo "📝 Enabling logging..."
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --web-server-logging filesystem \
    --output none

# Set startup command
echo "⚙️ Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app" \
    --output none

# Initialize git repository
echo "📁 Initializing git repository..."
git init
git add .
git commit -m "Initial deployment" --quiet

# Configure deployment
echo "🔧 Configuring deployment..."
DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query url \
    --output tsv)

# Add Azure remote
git remote add azure $DEPLOYMENT_URL

# Deploy
echo "🚀 Deploying to Azure..."
git push azure main --force

# Get the web app URL
WEBAPP_URL=$(az webapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query defaultHostName \
    --output tsv)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your API credentials in Azure Portal:"
echo "   https://portal.azure.com/#@/resource/subscriptions/*/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME/configuration"
echo ""
echo "2. Add these application settings:"
echo "   KRAKEN_API_KEY = your_kraken_api_key"
echo "   KRAKEN_SECRET_KEY = your_kraken_secret_key"
echo "   SECRET_KEY = your_flask_secret_key"
echo ""
echo "3. Visit your web app:"
echo "   https://$WEBAPP_URL"
echo ""
echo "4. Test the connection and start the bot!"
echo ""
echo "📚 For more information, see azure-deploy.md"
