import os
import json
from dotenv import load_dotenv
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
import sys

# Load environment variables
load_dotenv()

def get_cosmos_client():
    """Create and return a Cosmos DB Gremlin client"""
    endpoint = f"wss://{os.getenv('COSMOS_ENDPOINT')}:443/"
    username = os.getenv('COSMOS_USERNAME')
    password = os.getenv('COSMOS_PASSWORD')
    
    # Use GraphSON v2 serializer for Azure Cosmos DB
    return client.Client(
        endpoint, 
        'g',
        username=username,
        password=password,
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

def clear_graph(gremlin_client):
    """Clear all existing data from the graph"""
    print("Clearing existing graph data...")
    try:
        # Drop all vertices (this will also drop all edges)
        result = gremlin_client.submit("g.V().drop()")
        result.all().result()
        print("Graph cleared successfully")
    except Exception as e:
        print(f"Error clearing graph: {e}")

def load_manybirds_data(gremlin_client, json_file='manybirds_products.json'):
    """Load Manybirds product data into Cosmos DB"""
    
    # Load JSON data
    print(f"Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"Found {len(products)} products to load")
    
    # Create vertices for products
    for idx, product in enumerate(products):
        try:
            # Create product vertex - using 'partitionKey' property name
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
                'pk': 'products',  # Use a fixed partition key for all products
                'title': product['title'],
                'handle': product['handle'],
                'body_html': product.get('body_html', '')[:1000],  # Limit to 1000 chars
                'vendor': product.get('vendor', 'Manybirds'),
                'product_type': product.get('product_type', ''),
                'published_at': product.get('published_at', ''),
                'created_at': product.get('created_at', ''),
                'updated_at': product.get('updated_at', '')
            }
            
            result = gremlin_client.submit(query, bindings)
            result.all().result()
            
            # Add tags as a single property (comma-separated)
            tags = product.get('tags', [])
            if tags:
                tags_str = ','.join(tags)
                tag_query = "g.V(productId).property('tags', tags)"
                gremlin_client.submit(tag_query, {'productId': str(product['id']), 'tags': tags_str}).all().result()
            
            # Create variant vertices and edges
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
                    'pk': 'products',  # Same partition key as parent product
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
            
            # Create image vertices and edges  
            image_count = 0
            for img_idx, image in enumerate(product.get('images', [])):
                if image.get('id') is None:
                    # Generate ID if missing
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
                    'pk': 'products',  # Same partition key as parent product
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
            
            print(f"Loaded product {idx + 1}/{len(products)}: {product['title']} (with {variant_count} variants and {image_count} images)")
            
        except Exception as e:
            print(f"Error loading product {product.get('title', 'Unknown')}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nData loading completed!")

def verify_data(gremlin_client):
    """Verify the loaded data"""
    try:
        # Count products
        product_count_query = "g.V().hasLabel('product').count()"
        result = gremlin_client.submit(product_count_query)
        product_count = result.all().result()[0]
        
        # Count variants
        variant_count_query = "g.V().hasLabel('variant').count()"
        result = gremlin_client.submit(variant_count_query)
        variant_count = result.all().result()[0]
        
        # Count images
        image_count_query = "g.V().hasLabel('image').count()"
        result = gremlin_client.submit(image_count_query)
        image_count = result.all().result()[0]
        
        # Count edges
        edge_count_query = "g.E().count()"
        result = gremlin_client.submit(edge_count_query)
        edge_count = result.all().result()[0]
        
        print(f"\nVerification Results:")
        print(f"- Products loaded: {product_count}")
        print(f"- Variants loaded: {variant_count}")
        print(f"- Images loaded: {image_count}")
        print(f"- Edges created: {edge_count}")
        
        # Sample query to show a product with its relationships
        if product_count > 0:
            sample_query = "g.V().hasLabel('product').limit(1).values('title')"
            result = gremlin_client.submit(sample_query)
            sample_title = result.all().result()[0]
            print(f"\nSample product loaded: {sample_title}")
        
    except Exception as e:
        print(f"Error during verification: {e}")

def main():
    """Main function to load Manybirds data into Cosmos DB"""
    try:
        # Create Cosmos DB client
        gremlin_client = get_cosmos_client()
        
        # Optional: Clear existing data
        response = input("Do you want to clear existing data before loading? (y/n): ")
        if response.lower() == 'y':
            clear_graph(gremlin_client)
        
        # Load the data
        load_manybirds_data(gremlin_client)
        
        # Verify the data was loaded
        verify_data(gremlin_client)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'gremlin_client' in locals():
            gremlin_client.close()

if __name__ == "__main__":
    main()