import json
import os
from typing import List, Dict, Any

def combine_manybirds_datasets(file_paths: List[str], output_file: str = "combined_manybirds_dataset.json") -> None:
    """
    Combine multiple Manybirds JSON datasets into a single file
    """
    combined_products = []
    total_files_processed = 0
    
    print("🔄 Combining Manybirds datasets...")
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"⚠️  Warning: File '{file_path}' not found, skipping...")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            products = data.get('products', [])
            combined_products.extend(products)
            total_files_processed += 1
            
            print(f"✅ Loaded {len(products)} products from '{file_path}'")
            
        except Exception as e:
            print(f"❌ Error loading '{file_path}': {e}")
            continue
    
    # Remove duplicates based on product ID
    seen_ids = set()
    unique_products = []
    
    for product in combined_products:
        product_id = product.get('id')
        if product_id not in seen_ids:
            seen_ids.add(product_id)
            unique_products.append(product)
        else:
            print(f"🔍 Removing duplicate product ID: {product_id}")
    
    # Create combined dataset
    combined_dataset = {
        "products": unique_products
    }
    
    # Save combined dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Combined dataset saved to '{output_file}'")
    print(f"📊 Dataset Summary:")
    print(f"  Files processed: {total_files_processed}")
    print(f"  Total products: {len(unique_products)}")
    print(f"  Total variants: {sum(len(p.get('variants', [])) for p in unique_products)}")
    print(f"  Total images: {sum(len(p.get('images', [])) for p in unique_products)}")
    
    # Show product type breakdown
    product_types = {}
    vendors = {}
    
    for product in unique_products:
        ptype = product.get('product_type', 'Unknown')
        vendor = product.get('vendor', 'Unknown')
        
        product_types[ptype] = product_types.get(ptype, 0) + 1
        vendors[vendor] = vendors.get(vendor, 0) + 1
    
    print(f"\n📋 Product Types:")
    for ptype, count in sorted(product_types.items()):
        print(f"  {ptype}: {count}")
    
    print(f"\n🏷️ Vendors:")
    for vendor, count in sorted(vendors.items()):
        print(f"  {vendor}: {count}")

def create_sample_datasets():
    """Create smaller sample datasets for testing"""
    
    # Load the combined dataset
    if os.path.exists("combined_manybirds_dataset.json"):
        with open("combined_manybirds_dataset.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data.get('products', [])
        
        # Create small sample (5 products)
        small_sample = {"products": products[:5]}
        with open("manybirds_sample_small.json", 'w', encoding='utf-8') as f:
            json.dump(small_sample, f, indent=2, ensure_ascii=False)
        print(f"✅ Created small sample: 5 products")
        
        # Create medium sample (15 products)
        medium_sample = {"products": products[:15]}
        with open("manybirds_sample_medium.json", 'w', encoding='utf-8') as f:
            json.dump(medium_sample, f, indent=2, ensure_ascii=False)
        print(f"✅ Created medium sample: 15 products")
        
        # Create large sample (30 products)
        large_sample = {"products": products[:30]}
        with open("manybirds_sample_large.json", 'w', encoding='utf-8') as f:
            json.dump(large_sample, f, indent=2, ensure_ascii=False)
        print(f"✅ Created large sample: 30 products")

def validate_dataset(file_path: str) -> None:
    """Validate a Manybirds dataset for completeness and structure"""
    
    print(f"\n🔍 Validating dataset: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    products = data.get('products', [])
    issues = []
    
    for i, product in enumerate(products):
        product_num = i + 1
        
        # Check required fields
        required_fields = ['id', 'title', 'handle', 'vendor', 'product_type']
        for field in required_fields:
            if not product.get(field):
                issues.append(f"Product {product_num}: Missing '{field}'")
        
        # Check variants
        variants = product.get('variants', [])
        if not variants:
            issues.append(f"Product {product_num}: No variants found")
        else:
            for j, variant in enumerate(variants):
                if not variant.get('id'):
                    issues.append(f"Product {product_num}, Variant {j+1}: Missing 'id'")
                if not variant.get('price'):
                    issues.append(f"Product {product_num}, Variant {j+1}: Missing 'price'")
        
        # Check images
        images = product.get('images', [])
        if not images:
            issues.append(f"Product {product_num}: No images found")
    
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    else:
        print("✅ Dataset validation passed - no issues found!")
    
    print(f"📊 Validation Summary:")
    print(f"  Products validated: {len(products)}")
    print(f"  Issues found: {len(issues)}")

def main():
    """Main function to combine datasets and create samples"""
    
    # List of dataset files to combine
    dataset_files = [
        "manybirds_products.json",           # Original data
        "expanded_manybirds_products.json",  # First generated data
        "enhanced_manybirds_test_data.json" # Enhanced generated data
    ]
    
    # Combine all datasets
    combine_manybirds_datasets(dataset_files, "combined_manybirds_dataset.json")
    
    # Create sample datasets
    print(f"\n🎯 Creating sample datasets...")
    create_sample_datasets()
    
    # Validate the combined dataset
    validate_dataset("combined_manybirds_dataset.json")
    
    print(f"\n🎉 Dataset combination and validation complete!")
    print(f"\n📁 Generated files:")
    print(f"  - combined_manybirds_dataset.json (complete dataset)")
    print(f"  - manybirds_sample_small.json (5 products)")
    print(f"  - manybirds_sample_medium.json (15 products)")
    print(f"  - manybirds_sample_large.json (30 products)")

if __name__ == "__main__":
    main()
