# Manybirds Test Data Generator

This repository contains comprehensive test data generators and loaders for Manybirds product data, designed to work with Azure Cosmos DB using the Gremlin API.

## 📁 Generated Test Datasets

### Available Dataset Files

| File | Products | Variants | Images | Description |
|------|----------|----------|--------|-------------|
| `manybirds_products.json` | 5 | 37 | 26 | Original Manybirds sample data |
| `expanded_manybirds_products.json` | 15 | 113 | 67 | Basic generated test data |
| `enhanced_manybirds_test_data.json` | 25 | 73 | 77 | Enhanced test data with diverse categories |
| `combined_manybirds_dataset.json` | 45 | 223 | 170 | **Complete combined dataset** |
| `manybirds_sample_small.json` | 5 | 37 | 26 | Small sample for quick testing |
| `manybirds_sample_medium.json` | 15 | 111 | 66 | Medium sample for development |
| `manybirds_sample_large.json` | 30 | 186 | 128 | Large sample for performance testing |

### Product Categories Included

The enhanced test data includes diverse product categories:

- **Shoes** (12 products) - Runners, loafers, boots, sandals, etc.
- **Accessories** (7 products) - Various accessories and add-ons
- **Socks** (6 products) - Different styles and materials
- **Gift Cards** (5 products) - Digital gift card products
- **Underwear** (4 products) - Sustainable undergarments
- **Care Products** (4 products) - Shoe care and maintenance
- **Insoles** (3 products) - Comfort and support insoles
- **Apparel** (2 products) - Clothing items
- **Bags** (1 product) - Eco-friendly bags
- **Laces** (1 product) - Replacement laces

### Brands Represented

- **Manybirds** (23 products) - Primary brand
- **EcoBirds** (10 products) - Eco-focused line
- **UrbanBirds** (5 products) - Urban lifestyle products
- **TinyBirds** (4 products) - Kids and toddler line
- **SkyBirds** (3 products) - Premium line

## 🛠️ Scripts and Tools

### Data Generation Scripts

1. **`generate_test_data.py`** - Basic test data generator
   - Generates realistic product names, descriptions, and metadata
   - Creates appropriate variants and images for each product
   - Follows Manybirds tagging conventions

2. **`generate_enhanced_test_data.py`** - Enhanced test data generator
   - Supports multiple product categories (shoes, socks, apparel, accessories, etc.)
   - More realistic pricing, sizing, and material combinations
   - Enhanced tagging system with category-specific tags
   - Multiple brand support

3. **`combine_datasets.py`** - Dataset combination utility
   - Combines multiple JSON datasets into a single file
   - Removes duplicate products
   - Creates sample datasets of different sizes
   - Validates dataset structure and completeness

### Data Loading Scripts

1. **`load_manybirds_to_cosmos.py`** - Original Cosmos DB loader
   - Loads Manybirds product data into Azure Cosmos DB
   - Creates graph structure with products, variants, and images
   - Includes data verification functionality

2. **`load_test_data.py`** - Enhanced multi-dataset loader
   - Load any of the generated test datasets
   - Command-line interface with multiple options
   - Dataset information and validation features

## 🚀 Usage Examples

### Generate New Test Data

```powershell
# Generate 15 basic products
python generate_test_data.py

# Generate 25 enhanced products with diverse categories
python generate_enhanced_test_data.py
```

### Combine Datasets

```powershell
# Combine all datasets and create samples
python combine_datasets.py
```

### Load Data into Cosmos DB

```powershell
# List available datasets
python load_test_data.py --list

# Show dataset information
python load_test_data.py --info combined_manybirds_dataset.json

# Load small sample (recommended for testing)
python load_test_data.py --file manybirds_sample_small.json

# Load complete dataset with verification
python load_test_data.py --file combined_manybirds_dataset.json --clear --verify

# Load specific dataset without clearing existing data
python load_test_data.py --file enhanced_manybirds_test_data.json --verify
```

## 📊 Data Structure

Each product follows the Shopify/Manybirds JSON structure:

```json
{
  "id": 12345678901234,
  "title": "Product Name",
  "handle": "product-handle",
  "body_html": "Product description...",
  "vendor": "Manybirds",
  "product_type": "Shoes",
  "tags": ["Manybirds::material = wool", "sustainable", ...],
  "variants": [
    {
      "id": 98765432109876,
      "title": "Size 9",
      "price": "125.00",
      "sku": "PRODUCT-SKU-001",
      "available": true,
      "grams": 320,
      ...
    }
  ],
  "images": [
    {
      "id": 11111111111111,
      "src": "https://cdn.shopify.com/...",
      "position": 1,
      "width": 1600,
      "height": 1600,
      ...
    }
  ]
}
```

## 🏷️ Tagging System

The generated data includes comprehensive Manybirds-style tags:

- `Manybirds::material = wool` - Material type
- `Manybirds::gender = women` - Target gender
- `Manybirds::silhouette = runner` - Product silhouette
- `Manybirds::price-tier = tier-2` - Pricing tier
- `Manybirds::edition = classic` - Product edition
- `Manybirds::carbon-score = 3.2` - Environmental impact
- `sustainable` - Sustainability marker
- `machine-washable` - Care instructions
- `loop::returnable = true` - Return policy

## 🔧 Configuration

### Environment Variables Required

Create a `.env` file with your Cosmos DB credentials:

```env
COSMOS_ENDPOINT=your-cosmos-account-name.gremlin.cosmosdb.azure.com
COSMOS_USERNAME=/dbs/your-database/colls/your-container
COSMOS_PASSWORD=your-primary-key
```

### Prerequisites

```powershell
pip install -r requirements.txt
```

Required packages:
- `gremlin-python` - Cosmos DB Gremlin client
- `python-dotenv` - Environment variable management
- `argparse` - Command-line argument parsing

## 📈 Performance Considerations

### Dataset Size Recommendations

- **Development**: Use `manybirds_sample_small.json` (5 products)
- **Testing**: Use `manybirds_sample_medium.json` (15 products)  
- **Performance Testing**: Use `manybirds_sample_large.json` (30 products)
- **Full Dataset**: Use `combined_manybirds_dataset.json` (45 products)

### Loading Performance

- Small datasets (5-15 products): ~30-60 seconds
- Medium datasets (15-30 products): ~1-3 minutes
- Large datasets (30+ products): ~3-6 minutes

## 🎯 Use Cases

1. **Development Testing** - Quick dataset loading for feature development
2. **Performance Testing** - Large datasets to test query performance
3. **Demo Scenarios** - Realistic product data for demonstrations
4. **Data Structure Validation** - Ensure proper graph relationships
5. **Cosmos DB Capacity Planning** - Estimate storage and throughput needs

## 🔍 Data Validation

The `load_test_data.py` script includes comprehensive validation:

- Required field presence
- Data type validation
- Relationship integrity (product→variant, product→image edges)
- Duplicate detection
- Structure completeness

## 📚 Additional Resources

- [Azure Cosmos DB Gremlin API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin/)
- [Shopify Product API Reference](https://shopify.dev/api/admin-rest/2023-04/resources/product)
- [Graph Database Best Practices](https://docs.microsoft.com/en-us/azure/cosmos-db/graph/modeling)

---

*Generated test data follows realistic e-commerce patterns while maintaining compliance with Manybirds' sustainable product philosophy and tagging conventions.*
