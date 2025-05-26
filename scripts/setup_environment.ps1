# Setup environment for Azure Cosmos DB Gremlin API with Azure OpenAI
# This script installs the required packages and checks the environment

Write-Host "Setting up environment for Azure Cosmos DB Gremlin API with Azure OpenAI..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} 
catch {
    Write-Host "Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit
}

# Check if pip is installed
try {
    $pipVersion = pip --version
    Write-Host "Found pip: $pipVersion" -ForegroundColor Green
} 
catch {
    Write-Host "pip not found. Please install pip." -ForegroundColor Red
    exit
}

# Create and activate virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies from requirements.txt
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists
if (Test-Path .\.env) {
    Write-Host ".env file found." -ForegroundColor Green
} else {
    Write-Host ".env file not found. Creating template..." -ForegroundColor Yellow
    @"
# Cosmos DB Configuration
COSMOS_ENDPOINT=your-cosmos-db-endpoint.gremlin.cosmosdb.azure.com
COSMOS_USERNAME=/dbs/your-database/colls/your-collection
COSMOS_PASSWORD=your-cosmos-db-password
COSMOS_DATABASE=your-database
COSMOS_GRAPH=your-collection

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT_GPT41="https://your-openai-resource.openai.azure.com/"
AZURE_OPENAI_KEY_GPT41="your-api-key"
AZURE_OPENAI_MODEL_GPT41="your-model-deployment-name"
AZURE_OPENAI_DEPLOYMENT_GPT41="your-model-deployment-name"
AZURE_OPENAI_API_VERSION="2024-03-01-preview"
"@ | Out-File -FilePath .\.env -Encoding utf8
    
    Write-Host "Please update the .env file with your Azure credentials." -ForegroundColor Yellow
}

Write-Host "Environment setup complete. You can now run the Jupyter notebook." -ForegroundColor Green
Write-Host "To start Jupyter, run: jupyter notebook" -ForegroundColor Cyan
