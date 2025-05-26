#!/usr/bin/env python3
"""
Multi-Dataset Loader for Manybirds Test Data

This script allows you to load any of the generated Manybirds test datasets
into Azure Cosmos DB using the Gremlin API.

Usage examples:
    python load_test_data.py --file manybirds_sample_small.json
    python load_test_data.py --file combined_manybirds_dataset.json --clear
    python load_test_data.py --list  # Show available datasets
"""

import argparse
import os
import json
import sys
from typing import Dict, List, Any

# Import the existing loader functions
from load_manybirds_to_cosmos import get_cosmos_client, clear_graph, verify_data


def list_available_datasets() -> List[str]:
    """List all available dataset files"""
    dataset_files = []
    
    # Common dataset file patterns
    patterns = [
        "manybirds_products.json",
        "expanded_manybirds_products.json", 
        "enhanced_manybirds_test_data.json",
        "combined_manybirds_dataset.json",
        "manybirds_sample_small.json",
        "manybirds_sample_medium.json",
        "manybirds_sample_large.json",
        "generated_products.json"
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            dataset_files.append(pattern)
    
    return dataset_files


def get_dataset_info(file_path: str) -> Dict[str, Any]:
    """Get information about a dataset file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data.get('products', [])
        total_variants = sum(len(p.get('variants', [])) for p in products)
        total_images = sum(len(p.get('images', [])) for p in products)
        
        # Get product types
        product_types = {}
        vendors = {}
        
        for product in products:
            ptype = product.get('product_type', 'Unknown')
            vendor = product.get('vendor', 'Unknown')
            
            product_types[ptype] = product_types.get(ptype, 0) + 1
            vendors[vendor] = vendors.get(vendor, 0) + 1
        
        return {
            'file_size': os.path.getsize(file_path),
            'products': len(products),
            'variants': total_variants,
            'images': total_images,
            'product_types': product_types,
            'vendors': vendors
        }
        
    except Exception as e:
        return {'error': str(e)}


def load_dataset_to_cosmos(gremlin_client, file_path: str) -> bool:
    """Load a specific dataset file to Cosmos DB"""
    
    print(f"📂 Loading dataset from: {file_path}")
    
    try:
        # Load JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data.get('products', [])
        print(f"📊 Found {len(products)} products to load")
        
        if not products:
            print("⚠️  No products found in dataset")
            return False
        
        # Load products using the same logic as the original loader
        return load_products_to_cosmos(gremlin_client, products)
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_products_to_cosmos(gremlin_client, products: List[Dict[str, Any]]) -> bool:
    """Load products into Cosmos DB (adapted from original loader)"""
    
    successful_loads = 0
    
    for idx, product in enumerate(products):
        try:
            # Create product vertex
            query = """
            g.addV('product')
                .property('id', productId)
                .property('partitionKey', pk)
                .property('title', title)
                .property('handle', handle)
                .property('body_html', body_html)
                .property('vendor', vendor)
                .property('product_type', product_type)
                .property('published_at', published_at)
                .property('created_at', created_at)
                .property('updated_at', updated_at)
            """
            
            bindings = {
                'productId': str(product['id']),
                'pk': 'products',
                'title': product['title'],
                'handle': product['handle'],
                'body_html': product.get('body_html', '')[:1000],
                'vendor': product.get('vendor', 'Manybirds'),
                'product_type': product.get('product_type', ''),
                'published_at': product.get('published_at', ''),
                'created_at': product.get('created_at', ''),
                'updated_at': product.get('updated_at', '')
            }
            
            result = gremlin_client.submit(query, bindings)
            result.all().result()
            
            # Add tags
            tags = product.get('tags', [])
            if tags:
                tags_str = ','.join(tags)
                tag_query = "g.V(productId).property('tags', tags)"
                gremlin_client.submit(tag_query, {'productId': str(product['id']), 'tags': tags_str}).all().result()
            
            # Load variants
            variant_count = 0
            for variant in product.get('variants', []):
                if variant.get('id') is None:
                    continue
                    
                variant_query = """
                g.addV('variant')
                    .property('id', variantId)
                    .property('partitionKey', pk)
                    .property('title', title)
                    .property('sku', sku)
                    .property('price', price)
                    .property('grams', grams)
                    .property('available', available)
                    .property('position', position)
                    .property('product_id', productId)
                """
                
                variant_bindings = {
                    'variantId': str(variant['id']),
                    'pk': 'products',
                    'title': variant.get('title', ''),
                    'sku': variant.get('sku', ''),
                    'price': float(variant.get('price', 0)),
                    'grams': int(variant.get('grams', 0)),
                    'available': bool(variant.get('available', False)),
                    'position': int(variant.get('position', 0)),
                    'productId': str(product['id'])
                }
                
                gremlin_client.submit(variant_query, variant_bindings).all().result()
                
                # Create edge from product to variant
                edge_query = "g.V(productId).addE('has_variant').to(g.V(variantId))"
                edge_bindings = {
                    'productId': str(product['id']),
                    'variantId': str(variant['id'])
                }
                gremlin_client.submit(edge_query, edge_bindings).all().result()
                variant_count += 1
            
            # Load images
            image_count = 0
            for img_idx, image in enumerate(product.get('images', [])):
                if image.get('id') is None:
                    image_id = f"{product['id']}_img_{img_idx}"
                else:
                    image_id = str(image['id'])
                    
                image_query = """
                g.addV('image')
                    .property('id', imageId)
                    .property('partitionKey', pk)
                    .property('src', src)
                    .property('width', width)
                    .property('height', height)
                    .property('position', position)
                    .property('product_id', productId)
                """
                
                image_bindings = {
                    'imageId': image_id,
                    'pk': 'products',
                    'src': image.get('src', ''),
                    'width': int(image.get('width', 0)),
                    'height': int(image.get('height', 0)),
                    'position': int(image.get('position', img_idx)),
                    'productId': str(product['id'])
                }
                
                gremlin_client.submit(image_query, image_bindings).all().result()
                
                # Create edge from product to image
                edge_query = "g.V(productId).addE('has_image').to(g.V(imageId))"
                edge_bindings = {
                    'productId': str(product['id']),
                    'imageId': image_id
                }
                gremlin_client.submit(edge_query, edge_bindings).all().result()
                image_count += 1
            
            successful_loads += 1
            print(f"✅ Loaded product {idx + 1}/{len(products)}: {product['title']} (with {variant_count} variants and {image_count} images)")
            
        except Exception as e:
            print(f"❌ Error loading product {product.get('title', 'Unknown')}: {e}")
    
    print(f"\n📊 Loading Summary:")
    print(f"  Products attempted: {len(products)}")
    print(f"  Products loaded successfully: {successful_loads}")
    print(f"  Success rate: {(successful_loads/len(products)*100):.1f}%")
    
    return successful_loads > 0


def main():
    parser = argparse.ArgumentParser(description='Load Manybirds test datasets into Cosmos DB')
    parser.add_argument('--file', '-f', help='JSON file to load')
    parser.add_argument('--list', '-l', action='store_true', help='List available datasets')
    parser.add_argument('--info', '-i', help='Show information about a dataset file')
    parser.add_argument('--clear', '-c', action='store_true', help='Clear existing data before loading')
    parser.add_argument('--verify', '-v', action='store_true', help='Verify data after loading')
    
    args = parser.parse_args()
    
    # List available datasets
    if args.list:
        print("📁 Available Manybirds datasets:")
        datasets = list_available_datasets()
        
        if not datasets:
            print("  No dataset files found in current directory")
            return
        
        for dataset in datasets:
            info = get_dataset_info(dataset)
            if 'error' in info:
                print(f"  ❌ {dataset} - Error: {info['error']}")
            else:
                size_mb = info['file_size'] / (1024 * 1024)
                print(f"  📊 {dataset}")
                print(f"     Size: {size_mb:.1f} MB")
                print(f"     Products: {info['products']}, Variants: {info['variants']}, Images: {info['images']}")
                
                # Show top product types
                top_types = sorted(info['product_types'].items(), key=lambda x: x[1], reverse=True)[:3]
                types_str = ", ".join([f"{ptype} ({count})" for ptype, count in top_types])
                print(f"     Top types: {types_str}")
        return
    
    # Show dataset info
    if args.info:
        if not os.path.exists(args.info):
            print(f"❌ File not found: {args.info}")
            return
        
        print(f"📊 Dataset Information: {args.info}")
        info = get_dataset_info(args.info)
        
        if 'error' in info:
            print(f"❌ Error: {info['error']}")
            return
        
        size_mb = info['file_size'] / (1024 * 1024)
        print(f"📁 File size: {size_mb:.1f} MB")
        print(f"📦 Products: {info['products']}")
        print(f"🔗 Variants: {info['variants']}")
        print(f"🖼️  Images: {info['images']}")
        print(f"📊 Avg variants per product: {info['variants']/info['products']:.1f}")
        print(f"📊 Avg images per product: {info['images']/info['products']:.1f}")
        
        print(f"\n📋 Product Types:")
        for ptype, count in sorted(info['product_types'].items()):
            print(f"  {ptype}: {count}")
        
        print(f"\n🏷️ Vendors:")
        for vendor, count in sorted(info['vendors'].items()):
            print(f"  {vendor}: {count}")
        
        return
    
    # Load dataset
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            print(f"\n💡 Available files:")
            datasets = list_available_datasets()
            for dataset in datasets:
                print(f"  - {dataset}")
            return
        
        try:
            # Create Cosmos DB client
            print("🔌 Connecting to Cosmos DB...")
            gremlin_client = get_cosmos_client()
            
            # Clear existing data if requested
            if args.clear:
                response = input("⚠️  Are you sure you want to clear existing data? (y/n): ")
                if response.lower() == 'y':
                    clear_graph(gremlin_client)
                else:
                    print("❌ Operation cancelled")
                    return
            
            # Load the dataset
            success = load_dataset_to_cosmos(gremlin_client, args.file)
            
            if success:
                print("✅ Dataset loaded successfully!")
                
                # Verify data if requested
                if args.verify:
                    print("\n🔍 Verifying loaded data...")
                    verify_data(gremlin_client)
            else:
                print("❌ Dataset loading failed")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            if 'gremlin_client' in locals():
                gremlin_client.close()
    
    else:
        # No file specified, show help
        print("💡 Usage examples:")
        print("  python load_test_data.py --list")
        print("  python load_test_data.py --info manybirds_sample_small.json")
        print("  python load_test_data.py --file manybirds_sample_small.json")
        print("  python load_test_data.py --file combined_manybirds_dataset.json --clear --verify")


if __name__ == "__main__":
    main()
