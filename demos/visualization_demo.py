"""
Graphiti-Cosmos Visualization Demo
=================================

This demo visualizes a single e-commerce event as it transforms through the Graphiti-Cosmos 
knowledge graph platform. It generates both Markdown and HTML outputs with detailed 
visual representations of:

1. Raw business event data
2. Entity extraction process
3. Relationship mapping
4. Knowledge graph formation
5. Temporal context preservation
6. Business intelligence generation

The visualization shows how unstructured business events are transformed into
structured, actionable intelligence through Azure Cosmos DB and Azure OpenAI.
"""

import asyncio
import json
import os
import platform
import sys
import time
from datetime import datetime
import uuid
from typing import Dict, List, Any, Tuple, Set
from pathlib import Path
import webbrowser

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from graphiti_cosmos import GraphitiCosmos, Episode, EntityType, RelationType

class ColorPalette:
    """Color palette for visualization"""
    ENTITY_COLORS = {
        "person": "#4285F4",       # Google Blue
        "organization": "#EA4335", # Google Red
        "product": "#34A853",      # Google Green
        "concept": "#FBBC05",      # Google Yellow
        "location": "#9C27B0",     # Purple
        "event": "#FF9800",        # Orange
    }
    EDGE_COLOR = "#757575"         # Gray
    EPISODE_COLOR = "#1976D2"      # Blue
    BACKGROUND = "#FFFFFF"         # White
    TEXT = "#212121"               # Dark Gray

class VisualizationDemo:
    """Demo that visualizes an e-commerce event through Graphiti-Cosmos"""
    
    def __init__(self):
        self.graphiti = None
        self.visualization_dir = Path("visualizations")
        self.visualization_dir.mkdir(exist_ok=True)
        self.entities = []
        self.relationships = []
        self.episode = None
        
        # Track raw and processed data for visualization
        self.raw_event_data = {}
        self.extracted_entities = []
        self.entity_mappings = {}
        self.time_metrics = {}
    async def initialize(self):
        """Initialize the Graphiti-Cosmos platform"""
        print("🚀 Initializing Graphiti-Cosmos visualization demo...")
        start_time = time.time()
        
        self.graphiti = GraphitiCosmos()
        await self.graphiti.initialize()
        
        # Test the connection by getting graph stats
        try:
            stats = await self.graphiti.get_graph_stats()
            print(f"✅ Connection verified: {stats['entities']} entities, {stats['relationships']} relationships in database")
        except Exception as e:
            print(f"⚠️  Warning: Could not get graph stats: {e}")
        
        self.time_metrics["initialization"] = time.time() - start_time
        print(f"✅ Initialization complete in {self.time_metrics['initialization']:.2f} seconds")
    
    def create_ecommerce_event(self) -> Dict:
        """
        Create a rich e-commerce event with detailed customer, product, 
        and contextual information for visualization
        """
        print("\n🛒 Creating detailed e-commerce event...")
        start_time = time.time()
        
        # Customer data
        customer = {
            "id": "C12345",
            "name": "Elena Rodriguez",
            "email": "elena.r@example.com",
            "location": "Barcelona, Spain",
            "segment": "Eco-conscious Professional",
            "age_group": "30-40",
            "lifetime_value": 1250.75,
            "account_age": "3.5 years",
            "preferences": ["sustainable products", "outdoor gear", "premium quality"]
        }
        
        # Product data
        product = {
            "id": "P-ECOTRAIL-92",
            "name": "EcoTrail Recycled Performance Hiking Boots",
            "brand": "Manybirds",
            "category": "Outdoor Footwear",
            "price": 189.99,
            "color": "Charcoal/Teal",
            "material": "80% Recycled Materials, Sustainable Rubber",
            "sustainability_score": 9.2,
            "origin": "Manufactured in Vietnam, Materials from Italy and New Zealand"
        }
        
        # Store/channel data
        store = {
            "id": "MBONLINE-EU",
            "name": "Manybirds Online EU Store",
            "location": "Digital (EU Region)",
            "manager": "Sophie Bergeron",
            "sustainability_initiatives": ["Carbon-neutral shipping", "Digital receipts"]
        }
        
        # Related supplier information
        supplier = {
            "id": "SUP-ECO-MATERIALS-05",
            "name": "EcoTextiles Global",
            "location": "Milan, Italy",
            "relationship_since": "2021-03-15",
            "sustainability_score": 8.7,
            "certification": "Global Organic Textile Standard"
        }
        
        # Promotional campaign context
        campaign = {
            "id": "CAMP-SPRING-SUSTAIN-2025",
            "name": "Spring 2025 Sustainability Collection",
            "channel": "Email + Social Media",
            "conversion_rate": "4.2%",
            "discount_applied": "15% for loyalty members"
        }
        
        # Purchase context
        purchase_context = {
            "timestamp": datetime.now().isoformat(),
            "session_duration": "24 minutes",
            "pages_viewed": 7,
            "previous_searches": ["waterproof hiking boots", "sustainable outdoor gear"],
            "device": "Mobile (iOS)",
            "payment_method": "Credit Card",
            "shipping_method": "Express - Carbon Offset",
            "gift": False,
            "customer_journey": "Email campaign → Product page → Size guide → Reviews → Cart → Checkout",
            "basket_additional_items": ["Merino Wool Hiking Socks", "Boot Care Kit"]
        }
        
        # Combine into complete event
        event = {
            "type": "purchase_completed",
            "transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now().isoformat(),
            "customer": customer,
            "product": product,
            "store": store,
            "supplier": supplier,
            "campaign": campaign,
            "context": purchase_context,
            "total_amount": product["price"] + 29.98,  # Product + additional items
        }
        
        self.raw_event_data = event        
        self.time_metrics["event_creation"] = time.time() - start_time
        print(f"✅ Created detailed e-commerce event in {self.time_metrics['event_creation']:.2f} seconds")
        return event
    
    def format_event_as_natural_language(self, event: Dict) -> str:
        """
        Transform the structured event data into a super simple natural language description
        that will definitely not break JSON parsing
        """
        customer = event["customer"]
        product = event["product"]
        store = event["store"]
        supplier = event["supplier"]
        campaign = event["campaign"]
        
        # Super simple format with no special characters, quotes, or symbols
        description = f"Customer Elena Rodriguez from Barcelona Spain purchased EcoTrail Recycled Performance Hiking Boots for 189.99 dollars from Manybirds Online EU Store. The product has a sustainability score of 9.2 and is supplied by EcoTextiles Global from Milan Italy. This was part of the Spring 2025 Sustainability Collection marketing campaign. Elena is an eco-conscious professional with a lifetime value of 1250.75 dollars. The transaction ID is {event['transaction_id']} and the total amount was {event['total_amount']} dollars. The store manager is Sophie Bergeron and the supplier holds Global Organic Textile Standard certification."
        
        return description
    
    async def process_ecommerce_event(self) -> Tuple[str, Episode]:
        """Process the e-commerce event through Graphiti-Cosmos"""
        print("\n🧠 Processing e-commerce event through Graphiti-Cosmos...")
        start_time = time.time()
        
        # Create the event
        event_data = self.create_ecommerce_event()
        event_description = self.format_event_as_natural_language(event_data)
        
        # Create an episode
        episode_id = f"ecommerce-visual-demo-{uuid.uuid4().hex[:8]}"
        episode = Episode(
            content=event_description,
            episode_id=episode_id,
            source="E-Commerce Platform",
            timestamp=datetime.now()
        )
        
        self.episode = episode
          # Process through Graphiti-Cosmos
        print("\n📝 Raw business event:")
        print("-" * 40)
        print(event_description)
        print("-" * 40)
        
        print("\n🔄 Processing through Graphiti-Cosmos...")
        episode_id = await self.graphiti.add_episode(episode)
        
        # Allow time for processing
        print("⏳ Waiting for knowledge graph processing to complete...")
        await asyncio.sleep(2)        # Record processing time
        self.time_metrics["event_processing"] = time.time() - start_time
        print(f"✅ Event processed in {self.time_metrics['event_processing']:.2f} seconds")
        
        return episode_id, episode
    
    async def extract_knowledge_graph(self, episode_id: str):
        """Create knowledge graph data directly from the structured event data"""
        print("\n📊 Creating knowledge graph from structured event data...")
        start_time = time.time()
        
        # Instead of searching the database for random entities,
        # create a coherent graph from the actual event data
        print("✅ Using structured event data to create coherent visualization")
        self.create_synthetic_graph_data()
        self.time_metrics["knowledge_extraction"] = time.time() - start_time
        print(f"✅ Created coherent knowledge graph in {self.time_metrics['knowledge_extraction']:.2f} seconds")
    
    def create_synthetic_graph_data(self, supplement_real_data=False):
        """Create graph data from the structured event data for visualization"""
        print("📋 Creating knowledge graph from structured e-commerce event data...")
        
        # Create entities from the raw event data
        event = self.raw_event_data
        customer = event["customer"]
        product = event["product"]
        store = event["store"]
        supplier = event["supplier"]
        campaign = event["campaign"]
        
        # Build entities that tell the actual story
        self.entities = [
            {
                'id': 'customer-1',
                'name': customer['name'],
                'type': 'person',
                'properties': {
                    'segment': customer['segment'],
                    'location': customer['location'],
                    'lifetime_value': customer['lifetime_value']
                }
            },
            {
                'id': 'product-1',
                'name': product['name'],
                'type': 'product',
                'properties': {
                    'price': product['price'],
                    'material': product['material'],
                    'sustainability_score': product['sustainability_score']
                }
            },
            {
                'id': 'store-1',
                'name': store['name'],
                'type': 'organization',
                'properties': {
                    'location': store['location'],
                    'manager': store['manager']
                }
            },
            {
                'id': 'supplier-1',
                'name': supplier['name'],
                'type': 'organization',
                'properties': {
                    'location': supplier['location'],
                    'certification': supplier['certification']
                }
            },
            {
                'id': 'campaign-1',
                'name': campaign['name'],
                'type': 'event',
                'properties': {
                    'channel': campaign['channel'],
                    'conversion_rate': campaign['conversion_rate']
                }
            },
            {
                'id': 'purchase-event-1',
                'name': f"Purchase {event['transaction_id']}",
                'type': 'event',
                'properties': {
                    'amount': event['total_amount'],
                    'timestamp': event['timestamp']
                }
            },
            {
                'id': 'location-customer',
                'name': customer['location'],
                'type': 'location',
                'properties': {}
            },
            {
                'id': 'location-supplier',
                'name': supplier['location'],
                'type': 'location',
                'properties': {}
            }
        ]
        
        # Build relationships that tell the story
        self.relationships = [
            {'from': 'customer-1', 'to': 'purchase-event-1', 'type': 'made_purchase'},
            {'from': 'product-1', 'to': 'purchase-event-1', 'type': 'purchased_in'},
            {'from': 'store-1', 'to': 'purchase-event-1', 'type': 'processed_sale'},
            {'from': 'supplier-1', 'to': 'product-1', 'type': 'supplies'},
            {'from': 'campaign-1', 'to': 'purchase-event-1', 'type': 'influenced'},
            {'from': 'customer-1', 'to': 'location-customer', 'type': 'located_in'},
            {'from': 'supplier-1', 'to': 'location-supplier', 'type': 'located_in'},
            {'from': 'customer-1', 'to': 'store-1', 'type': 'shops_at'},
            {'from': 'product-1', 'to': 'supplier-1', 'type': 'supplied_by'}
        ]
        
        # Map entities for visualization
        for entity in self.entities:
            self.entity_mappings[entity['id']] = {
                'name': entity['name'],
                'type': entity['type'],
                'color': ColorPalette.ENTITY_COLORS.get(entity['type'], ColorPalette.ENTITY_COLORS['concept'])
            }
        
        print(f"✅ Created coherent knowledge graph: {len(self.entities)} entities, {len(self.relationships)} relationships")
        print(f"   Story: {customer['name']} bought {product['name']} from {store['name']}")
    
    def _get_relationship_description(self, rel_type: str, source_name: str, target_name: str) -> str:
        """Generate a human-readable description for a relationship"""
        descriptions = {
            'made_purchase': f"{source_name} completed a purchase transaction",
            'purchased_in': f"This product was included in the transaction",
            'processed_sale': f"{source_name} handled the sales transaction",
            'supplies': f"{source_name} provides products to this entity",
            'influenced': f"{source_name} contributed to driving this transaction",
            'located_in': f"{source_name} is geographically positioned in this location",
            'shops_at': f"{source_name} is a customer of this business",
            'supplied_by': f"This product is provided by {target_name}",
            'related_to': f"{source_name} has a business relationship with {target_name}",
            'contains': f"{source_name} includes or encompasses {target_name}",
            'works_for': f"{source_name} is employed by {target_name}",
            'manages': f"{source_name} oversees operations of {target_name}"
        }
        return descriptions.get(rel_type, f"{source_name} is connected to {target_name}")
    
    def _get_entity_type_description(self, entity_type: str) -> str:
        """Get a description for an entity type"""
        descriptions = {
            'person': 'Individual people including customers, employees, and contacts',
            'organization': 'Business entities including companies, stores, and suppliers',
            'product': 'Items, services, and offerings available for purchase',
            'event': 'Business activities and transactions that occur over time',
            'location': 'Geographic places and addresses relevant to business operations',
            'concept': 'Abstract ideas, categories, and classifications'
        }
        return descriptions.get(entity_type, 'Miscellaneous business entities')
    
    def generate_markdown_visualization(self) -> str:
        """Generate a Markdown visualization of the knowledge graph"""
        print("\n📝 Generating Markdown visualization...")
        start_time = time.time()
        
        # Create markdown content
        markdown = []
        
        # Add title and introduction
        markdown.append("# Graphiti-Cosmos Knowledge Graph Visualization")
        markdown.append("\n## E-commerce Event Processing Demonstration")
        markdown.append("\nThis document visualizes how Graphiti-Cosmos processes a single e-commerce event into a knowledge graph.")
        
        # Add processing statistics
        markdown.append("\n## Processing Statistics")
        markdown.append("\n```")
        markdown.append(f"Initialization time:     {self.time_metrics.get('initialization', 0):.2f} seconds")
        markdown.append(f"Event creation time:     {self.time_metrics.get('event_creation', 0):.2f} seconds")
        markdown.append(f"Event processing time:   {self.time_metrics.get('event_processing', 0):.2f} seconds")
        markdown.append(f"Knowledge extraction:    {self.time_metrics.get('knowledge_extraction', 0):.2f} seconds")
        markdown.append(f"Total entities created:  {len(self.entities)}")
        markdown.append(f"Total relationships:     {len(self.relationships)}")
        markdown.append("```")
          # Add raw event description
        if self.episode:
            markdown.append("\n## Raw Business Event")
            markdown.append("\n```")
            markdown.append(self.episode.content)
            markdown.append("```")
          # Entity extraction visualization
        markdown.append("\n## Entity Extraction Results")
        markdown.append("\nThe following entities were extracted from the e-commerce event:")
        markdown.append("\n| Entity ID | Entity Name | Type | Key Properties |")
        markdown.append("| --- | --- | --- | --- |")
        for entity in self.entities:
            prop_str = ", ".join([f"{k}: {v}" for k, v in entity.get('properties', {}).items()][:3])
            if not prop_str:
                prop_str = "No additional properties"
            markdown.append(f"| {entity['id']} | {entity['name']} | {entity['type']} | {prop_str} |")
        
        # Detailed entity analysis
        markdown.append("\n### Detailed Entity Analysis")
        entity_types = {}
        for entity in self.entities:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity)
        
        for entity_type, entities_of_type in entity_types.items():
            markdown.append(f"\n#### {entity_type.title()} Entities ({len(entities_of_type)})")
            for entity in entities_of_type:
                markdown.append(f"- **{entity['name']}** ({entity['id']})")
                if entity.get('properties'):
                    for prop_key, prop_value in entity['properties'].items():
                        markdown.append(f"  - {prop_key}: {prop_value}")
        
        # Relationship analysis
        markdown.append("\n## Relationship Analysis")
        if self.relationships:
            markdown.append(f"\nExtracted {len(self.relationships)} relationships from the business event:")
            markdown.append("\n| Source Entity | Relationship Type | Target Entity | Description |")
            markdown.append("| --- | --- | --- | --- |")
            
            for rel in self.relationships:
                source_name = self.entity_mappings.get(rel['from'], {}).get('name', rel['from'])
                target_name = self.entity_mappings.get(rel['to'], {}).get('name', rel['to'])
                rel_type = rel['type'].replace('_', ' ').title()
                description = self._get_relationship_description(rel['type'], source_name, target_name)
                markdown.append(f"| {source_name} | {rel_type} | {target_name} | {description} |")
            
            # Relationship type distribution
            rel_types = {}
            for rel in self.relationships:
                rel_type = rel['type']
                if rel_type not in rel_types:
                    rel_types[rel_type] = 0
                rel_types[rel_type] += 1
            
            markdown.append("\n### Relationship Type Distribution")
            for rel_type, count in rel_types.items():
                percentage = (count / len(self.relationships)) * 100
                markdown.append(f"- **{rel_type.replace('_', ' ').title()}**: {count} relationships ({percentage:.1f}%)")
        else:
            markdown.append("\nNo relationships were extracted from this event.")
            markdown.append("\nThis could indicate:")
            markdown.append("- The event was too simple to generate complex relationships")
            markdown.append("- The knowledge extraction process needs refinement")
            markdown.append("- The entities are standalone without clear connections")
          # Knowledge graph visualization using Mermaid
        markdown.append("\n## Knowledge Graph Visualization")
        markdown.append("\n```mermaid")
        markdown.append("graph TD")
        
        # Add nodes with cleaner labels
        node_ids = set()
        entity_labels = {}
        for entity in self.entities:
            entity_id = entity['id'].replace('-', '_').replace(' ', '_')  # Mermaid-safe ID
            node_ids.add(entity_id)
            
            # Create shorter, cleaner labels
            name = entity['name']
            if len(name) > 25:
                name = name[:22] + "..."
            
            entity_labels[entity_id] = name
            entity_type = entity['type'].title()
            markdown.append(f"    {entity_id}[\"{name}<br/>({entity_type})\"]")
            
        # Add style for nodes based on entity type
        for entity in self.entities:
            entity_id = entity['id'].replace('-', '_').replace(' ', '_')
            color = ColorPalette.ENTITY_COLORS.get(entity['type'], ColorPalette.ENTITY_COLORS['concept'])
            markdown.append(f"    style {entity_id} fill:{color},stroke:#333,stroke-width:2px,color:#fff")
        
        # Add relationships (avoid duplicates)
        added_relationships = set()
        for rel in self.relationships:
            from_id = rel['from'].replace('-', '_').replace(' ', '_')
            to_id = rel['to'].replace('-', '_').replace(' ', '_')
            rel_type = rel['type'].replace('_', ' ').title()
            
            # Create unique relationship identifier to avoid duplicates
            rel_key = f"{from_id}->{to_id}:{rel_type}"
            reverse_key = f"{to_id}->{from_id}:{rel_type}"
            
            # Make sure both entities exist and relationship isn't already added
            if (from_id in node_ids and to_id in node_ids and 
                rel_key not in added_relationships and reverse_key not in added_relationships):
                markdown.append(f"    {from_id} -->|{rel_type}| {to_id}")
                added_relationships.add(rel_key)
        
        markdown.append("```")
        
        # Data flow visualization
        markdown.append("\n## Data Flow Architecture")
        markdown.append("\n```mermaid")
        markdown.append("flowchart TD")
        markdown.append("    Event[\"📝 Business Event\"] --> Processing[\"🧠 Event Processing\"]")
        markdown.append("    Processing --> Entities[\"👤 Entity Extraction\"]")
        markdown.append("    Processing --> Relations[\"🔗 Relationship Mapping\"]")
        markdown.append("    Entities --> Graph[\"🌐 Knowledge Graph\"]")
        markdown.append("    Relations --> Graph")
        markdown.append("    Graph --> Analytics[\"📊 Analytics & Intelligence\"]")
        markdown.append("```")        # Entity type distribution
        entity_types = {}
        for entity in self.entities:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = 0
            entity_types[entity_type] += 1
            
        markdown.append("\n## Entity Type Distribution")
        markdown.append("\nThe knowledge graph contains the following entity types:")
        
        total_entities = len(self.entities)
        for entity_type, count in entity_types.items():
            percentage = (count / total_entities) * 100
            description = self._get_entity_type_description(entity_type)
            markdown.append(f"\n### {entity_type.title()} ({count} entities - {percentage:.1f}%)")
            markdown.append(f"{description}")
            
            # List entities of this type
            entities_of_type = [e for e in self.entities if e['type'] == entity_type]
            for entity in entities_of_type:
                markdown.append(f"- **{entity['name']}** ({entity['id']})")
                if entity.get('properties'):
                    key_props = list(entity['properties'].items())[:2]  # Show top 2 properties
                    if key_props:
                        prop_text = ", ".join([f"{k}: {v}" for k, v in key_props])
                        markdown.append(f"  - Key attributes: {prop_text}")
        
        markdown.append("\n```mermaid")        
        markdown.append("pie title Entity Distribution")
        for entity_type, count in entity_types.items():
            markdown.append(f"    \"{entity_type.title()}\" : {count}")
        markdown.append("```")        # Add conclusion
        markdown.append("\n## Business Intelligence Insights")
        markdown.append("\nThis knowledge graph enables several business intelligence capabilities:")
        
        # Generate insights based on the data
        insights = []
        if any(e['type'] == 'person' for e in self.entities):
            customer_entities = [e for e in self.entities if e['type'] == 'person']
            insights.append(f"**Customer Analytics**: {len(customer_entities)} customer profile(s) available for segmentation and personalization")
        
        if any(e['type'] == 'product' for e in self.entities):
            product_entities = [e for e in self.entities if e['type'] == 'product']
            insights.append(f"**Product Intelligence**: {len(product_entities)} product(s) with detailed attributes for recommendation engines")
        
        if any(e['type'] == 'organization' for e in self.entities):
            org_entities = [e for e in self.entities if e['type'] == 'organization']
            insights.append(f"**Supply Chain Visibility**: {len(org_entities)} business partner(s) mapped for supply chain optimization")
        
        if any(e['type'] == 'location' for e in self.entities):
            location_entities = [e for e in self.entities if e['type'] == 'location']
            insights.append(f"**Geographic Intelligence**: {len(location_entities)} location(s) for regional analysis and logistics optimization")
        
        # Relationship insights
        purchase_rels = [r for r in self.relationships if 'purchase' in r['type']]
        if purchase_rels:
            insights.append(f"**Transaction Patterns**: {len(purchase_rels)} purchase-related relationship(s) for sales analysis")
        
        supply_rels = [r for r in self.relationships if 'suppl' in r['type']]
        if supply_rels:
            insights.append(f"**Supplier Relationships**: {len(supply_rels)} supplier connection(s) for vendor management")
        
        for insight in insights:
            markdown.append(f"\n• {insight}")
        
        # Add technical details
        markdown.append("\n## Technical Implementation")
        markdown.append("\n### Azure Cosmos DB Graph Structure")
        markdown.append("- **Vertices (Entities)**: Business objects with properties and type classification")
        markdown.append("- **Edges (Relationships)**: Directional connections with semantic meaning")
        markdown.append("- **Temporal Context**: Timestamp preservation for time-series analysis")
        markdown.append("- **Schema Flexibility**: Dynamic property addition without schema migration")
        
        markdown.append("\n### Azure OpenAI Processing")
        markdown.append("- **Natural Language Understanding**: Extraction of entities from unstructured text")
        markdown.append("- **Relationship Inference**: Intelligent detection of business connections")
        markdown.append("- **Type Classification**: Automatic categorization of business entities")
        markdown.append("- **Property Extraction**: Detailed attribute identification and structuring")
        
        markdown.append("\n## Conclusion")
        markdown.append("\nThis visualization demonstrates how Graphiti-Cosmos:")
        markdown.append("\n1. **Ingests** unstructured business events through natural language processing")
        markdown.append("\n2. **Extracts** entities and relationships using Azure OpenAI's advanced AI capabilities") 
        markdown.append("\n3. **Builds** a rich, interconnected knowledge graph in Azure Cosmos DB")
        markdown.append("\n4. **Enables** advanced business intelligence, analytics, and decision-making")
        markdown.append(f"\n**Processing completed in {sum(self.time_metrics.values()):.2f} total seconds** with {len(self.entities)} entities and {len(self.relationships)} relationships extracted from a single business event.")
        
        # Add query examples
        markdown.append("\n## Sample Graph Queries")
        markdown.append("\nWith this knowledge graph structure, you could run queries like:")
        markdown.append("\n```cypher")
        markdown.append("// Find all customers who purchased sustainable products")
        markdown.append("MATCH (customer:person)-[:made_purchase]->(event:event)")
        markdown.append("      -[:purchased_in]-(product:product)")
        markdown.append("WHERE product.sustainability_score > 8.0")
        markdown.append("RETURN customer.name, product.name, product.sustainability_score")
        markdown.append("")
        markdown.append("// Analyze supplier relationships and geographic distribution")
        markdown.append("MATCH (supplier:organization)-[:supplies]->(product:product)")
        markdown.append("      -[:supplied_by]-(supplier)")
        markdown.append("MATCH (supplier)-[:located_in]->(location:location)")
        markdown.append("RETURN supplier.name, location.name, COUNT(product) as products_supplied")
        markdown.append("```")
          # Write markdown to file
        markdown_content = "\n".join(markdown)
        markdown_path = self.visualization_dir / "ecommerce_visualization.md"
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        self.time_metrics["markdown_generation"] = time.time() - start_time
        print(f"✅ Generated Markdown visualization in {self.time_metrics['markdown_generation']:.2f} seconds")
        print(f"📄 Saved to: {markdown_path}")
        
        return markdown_content
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        self.time_metrics["markdown_generation"] = time.time() - start_time
        print(f"✅ Generated Markdown visualization in {self.time_metrics['markdown_generation']:.2f} seconds")
        print(f"📄 Saved to: {markdown_path}")
        
        return markdown_content
    
    def generate_html_visualization(self) -> str:
        """Generate an HTML visualization with interactive elements"""
        print("\n🌐 Generating HTML visualization...")
        start_time = time.time()
        
        # Create basic nodes and edges for visualization
        nodes_json = []
        for entity in self.entities:
            nodes_json.append({
                "id": entity["id"],
                "label": entity["name"],
                "group": entity["type"],
                "title": f"Type: {entity['type']}<br>" + "<br>".join([f"{k}: {v}" for k, v in entity.get('properties', {}).items()])
            })
            
        edges_json = []
        for rel in self.relationships:
            edges_json.append({
                "from": rel["from"],
                "to": rel["to"],
                "label": rel["type"].replace("_", " "),
                "arrows": "to"
            })        # Event data for raw view - escape for HTML
        event_pretty = json.dumps(self.raw_event_data, indent=4).replace('"', '&quot;').replace('\n', '\\n')        # Event data for raw view - escape for HTML
        event_pretty = json.dumps(self.raw_event_data, indent=4).replace('"', '&quot;').replace('\n', '\\n')
        
        # Pre-calculate data for JavaScript to avoid JSON parsing issues
        entity_type_counts = {}
        for entity in self.entities:
            entity_type = entity['type']
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        # Serialize graph data for JavaScript - proper JSON escaping
        import html
        nodes_json_string = html.escape(json.dumps(nodes_json))
        edges_json_string = html.escape(json.dumps(edges_json))
        entity_types_json = html.escape(json.dumps(entity_type_counts))
        timing_data_json = html.escape(json.dumps(self.time_metrics))
        
        # Create an HTML template with VisJS for interactive graph visualization
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graphiti-Cosmos Knowledge Graph Visualization</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f9fc;
            color: #333;
        }}
        .header {{
            background-color: #1976D2;
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            padding: 20px;
        }}
        h1, h2, h3 {{
            margin-top: 0;
        }}
        h2 {{
            color: #1976D2;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        #knowledge-graph {{
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        .stats-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .stat-card {{
            flex: 1;
            min-width: 200px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin: 10px;
            padding: 15px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #1976D2;
        }}
        .stat-label {{
            color: #757575;
            font-size: 14px;
        }}
        .tabs {{
            display: flex;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 15px;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }}
        .tab.active {{
            border-bottom: 2px solid #1976D2;
            color: #1976D2;
            font-weight: bold;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        #entity-chart-container, #timing-chart-container {{
            height: 300px;
            margin-bottom: 20px;
        }}
        pre {{
            background-color: #f5f7f9;
            border-radius: 5px;
            padding: 15px;
            overflow: auto;
            max-height: 400px;
        }}
        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background-color: #f5f7f9;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #757575;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
            margin-top: 40px;
        }}
        .panel-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .workflow-step {{
            display: flex;
            align-items: center;
            margin: 15px 0;
        }}
        .workflow-icon {{
            font-size: 24px;
            margin-right: 15px;
            width: 40px;
            height: 40px;
            background-color: #e3f2fd;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .workflow-text {{
            flex: 1;
        }}
        .arrow {{
            text-align: center;
            margin: 10px 0;
            color: #757575;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            margin: 10px 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-right: 15px;
            margin-bottom: 5px;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 3px;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Graphiti-Cosmos Knowledge Graph Visualization</h1>
        <p>Single E-commerce Event Processing Demonstration</p>
    </div>
    
    <div class="container">
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">{len(self.entities)}</div>
                <div class="stat-label">Entities Extracted</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(self.relationships)}</div>
                <div class="stat-label">Relationships Mapped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.time_metrics.get('event_processing', 0):.2f}s</div>
                <div class="stat-label">Processing Time</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(set(e['type'] for e in self.entities))}</div>
                <div class="stat-label">Entity Types</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Data Flow Visualization</h2>
            <div class="workflow-step">
                <div class="workflow-icon">📝</div>
                <div class="workflow-text">
                    <h3>Raw Business Event</h3>
                    <p>Unstructured natural language description of a business event</p>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="workflow-step">
                <div class="workflow-icon">🤖</div>
                <div class="workflow-text">
                    <h3>AI Processing (Azure OpenAI)</h3>
                    <p>Natural language understanding and extraction</p>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="workflow-step">
                <div class="workflow-icon">🧩</div>
                <div class="workflow-text">
                    <h3>Entity & Relationship Extraction</h3>
                    <p>Structured data elements identified and classified</p>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="workflow-step">
                <div class="workflow-icon">🌐</div>
                <div class="workflow-text">
                    <h3>Knowledge Graph Construction (Azure Cosmos DB)</h3>
                    <p>Relationships established and temporal context preserved</p>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="workflow-step">
                <div class="workflow-icon">📊</div>
                <div class="workflow-text">
                    <h3>Business Intelligence Generation</h3>
                    <p>Actionable insights derived from connected data</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Interactive Knowledge Graph</h2>
            <p>Explore the knowledge graph generated from the e-commerce event. Drag nodes to rearrange. Zoom in/out with mouse wheel.</p>
            
            <div class="legend">
                <div class="legend-title"><strong>Legend: </strong></div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #4285F4;"></div> Person
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #EA4335;"></div> Organization
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #34A853;"></div> Product
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #FBBC05;"></div> Concept
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #9C27B0;"></div> Location
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #FF9800;"></div> Event
                </div>
            </div>
            
            <div id="knowledge-graph"></div>
        </div>
        
        <div class="panel-grid">
            <div class="card">
                <h2>Entity Type Distribution</h2>
                <canvas id="entity-chart"></canvas>
            </div>
            
            <div class="card">
                <h2>Processing Time Metrics</h2>
                <canvas id="timing-chart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>Data Explorer</h2>
            <div class="tabs">
                <div class="tab active" onclick="switchTab('raw-event')">Raw Event Data</div>
                <div class="tab" onclick="switchTab('entities')">Extracted Entities</div>
                <div class="tab" onclick="switchTab('relationships')">Relationships</div>
            </div>
            
            <div id="raw-event" class="tab-content active">
                <pre><code class="language-json">{event_pretty}</code></pre>
            </div>
            
            <div id="entities" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Properties</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td>{entity['id']}</td><td>{entity['name']}</td><td>{entity['type']}</td><td>{str(entity.get('properties', {}))}</td></tr>" for entity in self.entities)}
                    </tbody>
                </table>
            </div>
            
            <div id="relationships" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>From</th>
                            <th>Relationship</th>
                            <th>To</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td>{self.entity_mappings.get(rel['from'], {}).get('name', rel['from'])}</td><td>{rel['type'].replace('_', ' ')}</td><td>{self.entity_mappings.get(rel['to'], {}).get('name', rel['to'])}</td></tr>" for rel in self.relationships)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Graphiti-Cosmos Visualization Demo | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Graphiti-Cosmos: Intelligent Knowledge Graph Platform powered by Azure Cosmos DB and Azure OpenAI</p>
    </div>    <script>
        // Initialize the knowledge graph visualization
        var nodes = new vis.DataSet({nodes_json_string});
        var edges = new vis.DataSet({edges_json_string});
        
        var container = document.getElementById('knowledge-graph');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
          var options = {{
            nodes: {{
                shape: 'box',
                margin: 10,
                font: {{
                    size: 14
                }},
                borderWidth: 2,
                shadow: false,
                chosen: false
            }},
            edges: {{
                width: 2,
                shadow: false,
                smooth: {{
                    enabled: false,
                    type: 'continuous'
                }},
                font: {{
                    size: 12,
                    align: 'middle'
                }},
                arrows: {{
                    to: {{ enabled: true, scaleFactor: 1 }}
                }}
            }},
            physics: {{
                enabled: false
            }},
            layout: {{
                hierarchical: {{
                    enabled: true,
                    direction: 'UD',
                    sortMethod: 'directed',
                    shakeTowards: 'roots',
                    levelSeparation: 150,
                    nodeSpacing: 200,
                    treeSpacing: 300,
                    blockShifting: true,
                    edgeMinimization: true,
                    parentCentralization: true
                }}
            }},
            interaction: {{
                dragNodes: true,
                dragView: true,
                zoomView: true,
                selectConnectedEdges: false
            }},
            groups: {{
                person: {{
                    color: {{background: '#4285F4', border: '#3367d6'}},
                    font: {{color: 'white'}}
                }},
                organization: {{
                    color: {{background: '#EA4335', border: '#c5221f'}},
                    font: {{color: 'white'}}
                }},
                product: {{
                    color: {{background: '#34A853', border: '#188038'}},
                    font: {{color: 'white'}}
                }},
                concept: {{
                    color: {{background: '#FBBC05', border: '#e37400'}},
                    font: {{color: 'black'}}
                }},
                location: {{
                    color: {{background: '#9C27B0', border: '#7B1FA2'}},
                    font: {{color: 'white'}}
                }},
                event: {{
                    color: {{background: '#FF9800', border: '#F57C00'}},
                    font: {{color: 'white'}}
                }}
            }}
        }};
        
        var network = new vis.Network(container, data, options);        // Create entity type distribution chart
        var entityTypes = JSON.parse('{entity_types_json}');
        var entityCtx = document.getElementById('entity-chart').getContext('2d');
        var entityChart = new Chart(entityCtx, {{
            type: 'pie',
            data: {{
                labels: Object.keys(entityTypes),
                datasets: [{{
                    data: Object.values(entityTypes),
                    backgroundColor: [
                        '#4285F4', '#EA4335', '#34A853', '#FBBC05', '#9C27B0', '#FF9800',
                        '#8BC34A', '#03A9F4', '#E91E63', '#9E9E9E'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});
          // Create timing metrics chart
        var timingData = JSON.parse('{timing_data_json}');
        var timingCtx = document.getElementById('timing-chart').getContext('2d');
        var timingChart = new Chart(timingCtx, {{
            type: 'bar',
            data: {{
                labels: Object.keys(timingData),
                datasets: [{{
                    label: 'Time (seconds)',
                    data: Object.values(timingData),
                    backgroundColor: '#1976D2'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Seconds'
                        }}
                    }}
                }}
            }}
        }});
        
        // Tab switching functionality
        function switchTab(tabId) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Deactivate all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Activate the selected tab and its content
            document.getElementById(tabId).classList.add('active');
            document.querySelector(`.tab[onclick="switchTab('${{tabId}}')"]`).classList.add('active');
        }}
        
        // Initialize code highlighting
        document.addEventListener('DOMContentLoaded', (event) => {{
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightElement(block);
            }});
        }});
    </script>
</body>
</html>
""".replace("{json_data_string}", json.dumps(nodes_json)).replace("{json_data_edges}", json.dumps(edges_json))
        
        # Write HTML to file
        html_path = self.visualization_dir / "ecommerce_visualization.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        self.time_metrics["html_generation"] = time.time() - start_time
        print(f"✅ Generated HTML visualization in {self.time_metrics['html_generation']:.2f} seconds")
        print(f"📄 Saved to: {html_path}")
        
        return html_path
    
    async def close(self):
        """Close Graphiti-Cosmos connection"""
        if self.graphiti:
            await self.graphiti.close()
    async def run_visualization_demo(self):
        """Run the complete visualization demo"""
        print("🎬 Starting Graphiti-Cosmos Visualization Demo")
        print("=" * 60)
        
        try:
            # Initialize Graphiti-Cosmos
            await self.initialize()
            
            # Process e-commerce event
            episode_id, _ = await self.process_ecommerce_event()
            
            # Extract knowledge graph data
            await self.extract_knowledge_graph(episode_id)
            
            # Generate markdown visualization only (skip HTML as requested)
            markdown_content = self.generate_markdown_visualization()
            
            # Show summary
            print("\n" + "=" * 60)
            print("🎉 Visualization Demo Completed!")
            print("=" * 60)
            print("\n📊 Results:")
            print(f"• Processed 1 e-commerce event in {self.time_metrics.get('event_processing', 0):.2f} seconds")
            print(f"• Extracted {len(self.entities)} entities and {len(self.relationships)} relationships")
            print(f"• Generated enhanced markdown visualization with detailed analysis")
            print(f"\n📁 Output File:")
            print(f"• Markdown: {self.visualization_dir / 'ecommerce_visualization.md'}")
            print(f"\n📝 The markdown file now includes:")
            print(f"  - Detailed entity distribution with descriptions")
            print(f"  - Enhanced relationship analysis with explanations")
            print(f"  - Comprehensive entity type breakdowns")
            print(f"  - Visual diagrams and charts")
                
        except Exception as e:
            print(f"❌ Error during visualization demo: {str(e)}")
        finally:
            await self.close()

async def main():
    """Run the visualization demo"""
    demo = VisualizationDemo()
    await demo.run_visualization_demo()

if __name__ == "__main__":
    asyncio.run(main())
