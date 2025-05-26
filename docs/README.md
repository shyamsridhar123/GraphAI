# Cosmos DB Graph Data Loader

This project generates and loads Manybirds-style e-commerce product data into Azure Cosmos DB using the Gremlin API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Azure credentials:
```
COSMOS_ENDPOINT=your-cosmos-endpoint.gremlin.cosmos.azure.com
COSMOS_USERNAME=/dbs/your-database/colls/your-collection
COSMOS_PASSWORD=your-primary-key
COSMOS_DATABASE=your-database-name
COSMOS_GRAPH=your-graph-name

AZURE_OPENAI_ENDPOINT_GPT41=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY_GPT41=your-openai-key
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_GPT41=your-deployment-name
```

## Usage

### Load existing Manybirds data:
```bash
python load_data.py
```

### Generate and load new test data:
```bash
python load_data.py --generate --num-products 50
```

### Clear existing data before loading:
```bash
python load_data.py --clear
```

### Load from a specific JSON file:
```bash
python load_data.py --file custom_products.json
```

## Data Structure

The data follows the exact Manybirds product structure with:
- Products with variants, images, and options
- Categories (Shoes, Socks, Mens, Womens, etc.)
- Relationships between products and categories
- Embeddings for product descriptions using Azure OpenAI

## Generated Data Features

- Multiple product types: Runners, Breezers, Couriers, Socks
- Gender variations: Mens, Womens, Unisex, Toddler
- Realistic SKUs, prices, and weights
- Proper timestamp formatting
- Manybirds-style tags with metadata
