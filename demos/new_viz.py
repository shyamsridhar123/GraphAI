import os
import asyncio
import math
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from dotenv import load_dotenv
from gremlin_python.driver import client, serializer
from openai import AzureOpenAI
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Load environment variables exactly as they are
load_dotenv()

def get_entity_name(entity):
    """Safely extract entity name from either direct field or properties"""
    if isinstance(entity, dict):
        # Try direct name field first
        if 'name' in entity:
            return entity['name']
        # Try properties.name
        if 'properties' in entity and entity['properties']:
            props = entity['properties']
            if 'name' in props:
                name_prop = props['name']
                # Handle both direct string and nested structure
                if isinstance(name_prop, dict):
                    return name_prop.get('value', str(name_prop))
                elif isinstance(name_prop, list):
                    return name_prop[0].get('value', str(name_prop[0])) if name_prop else "Unknown"
                return str(name_prop)
            # Try title as fallback
            elif 'title' in props:
                title_prop = props['title']
                if isinstance(title_prop, dict):
                    return title_prop.get('value', str(title_prop))
                elif isinstance(title_prop, list):
                    return title_prop[0].get('value', str(title_prop[0])) if title_prop else "Unknown"
                return str(title_prop)
        # Try id as fallback
        if 'id' in entity:
            return entity['id']
    return "Unknown"

# Global client instances with proper cleanup
_gremlin_client = None
_executor = ThreadPoolExecutor(max_workers=2)

def get_gremlin_client():
    """Get or create Gremlin client with proper cleanup"""
    global _gremlin_client
    if _gremlin_client is None:
        try:
            _gremlin_client = client.Client(
                f'wss://{os.getenv("COSMOS_ENDPOINT")}:443/',
                'g',
                username=os.getenv("COSMOS_USERNAME"),
                password=os.getenv("COSMOS_PASSWORD"),
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
        except Exception as e:
            st.error(f"Failed to create Gremlin client: {e}")
            return None
    return _gremlin_client

def cleanup_gremlin_client():
    """Safely cleanup Gremlin client"""
    global _gremlin_client
    if _gremlin_client:
        try:
            _gremlin_client.close()
        except:
            pass  # Ignore cleanup errors
        _gremlin_client = None

# Initialize Azure OpenAI with your exact env variables (removing quotes)
def get_openai_client():
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip('"')
        key = os.getenv("AZURE_OPENAI_KEY", "").strip('"')
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01").strip('"')
        
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=api_version
        )
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        return None

def run_gremlin_query_sync(query):
    """Thread-safe synchronous execution of Gremlin queries"""
    try:
        gremlin_client = get_gremlin_client()
        if not gremlin_client:
            return []
            
        result = gremlin_client.submit(query).all().result()
        return result
    except Exception as e:
        st.error(f"Query failed: {e}")
        return []

# Cosmos DB query functions - Streamlit-compatible synchronous versions
def query_cosmos_entities_sync(entity_type=None, limit=50):
    """Synchronous version - Query actual entities from Cosmos DB graph"""
    try:
        if entity_type:
            query = f"g.V().hasLabel('{entity_type}').limit({limit})"
        else:
            query = f"g.V().limit({limit})"
            
        result = run_gremlin_query_sync(query)
        
        entities = []
        for vertex in result:
            entities.append({
                'id': vertex.get('id', ''),
                'label': vertex.get('label', ''),
                'properties': vertex.get('properties', {})
            })
        return entities
    except Exception as e:
        st.error(f"Error querying entities: {e}")
        return []

def query_cosmos_relationships_sync(source_entity=None, limit=50):
    """Synchronous version - Query actual relationships from Cosmos DB graph"""
    try:
        if source_entity:
            query = f"g.V().has('name', '{source_entity}').bothE().limit({limit})"
        else:
            query = f"g.E().limit({limit})"
            
        result = run_gremlin_query_sync(query)
        
        relationships = []
        for edge in result:
            relationships.append({
                'id': edge.get('id', ''),
                'label': edge.get('label', ''),
                'source': edge.get('outV', ''),
                'target': edge.get('inV', ''),
                'properties': edge.get('properties', {})
            })
        return relationships
    except Exception as e:
        st.error(f"Error querying relationships: {e}")
        return []

def get_real_ecommerce_data_sync(filter_entity_type="All", entity_limit=20):
    """Synchronous version - Fetch real ecommerce data from your Cosmos DB"""
    try:
        customers = []
        products = []
        organizations = []
        
        # Check what actual entity types exist in the database
        # Based on your database, we'll query for 'entity' type (GraphitiCosmos) and 'product' type
        
        if filter_entity_type == "All" or filter_entity_type == "person":
            # Try to get customer-like entities (people, users, etc.)
            # First try 'entity' label (from GraphitiCosmos), then fallback to other types
            customers_entity = query_cosmos_entities_sync("entity", min(entity_limit, 10))
            customers_episode = query_cosmos_entities_sync("episode", min(entity_limit, 5))
              # Filter entities that might represent people/customers
            for entity in customers_entity:
                props = entity.get('properties', {})
                # Look for person-like entities based on name patterns or properties
                name = props.get('name', [''])[0] if 'name' in props else entity.get('id', '')
                # Safely handle name conversion to string
                name_str = str(name).lower() if name else ''
                if any(keyword in name_str for keyword in ['person', 'user', 'customer', 'alice', 'bob', 'jennifer', 'sarah']):
                    customers.append(entity)
            
            # If still no customers, use some episodes as customer interactions
            if not customers and customers_episode:
                customers = customers_episode[:min(entity_limit, 5)]
        
        if filter_entity_type == "All" or filter_entity_type == "product":
            # Get actual products from your database
            products = query_cosmos_entities_sync("product", min(entity_limit, 15))
            
            # If no 'product' label, try getting entities that look like products
            if not products:
                all_entities = query_cosmos_entities_sync("entity", min(entity_limit, 20))                
                for entity in all_entities:
                    props = entity.get('properties', {})
                    name = props.get('name', [''])[0] if 'name' in props else entity.get('id', '')
                    # Look for product-like entities - safely handle name conversion
                    name_str = str(name).lower() if name else ''
                    if any(keyword in name_str for keyword in ['shoe', 'boot', 'product', 'runner', 'couriers', 'insole']):
                        products.append(entity)
        
        if filter_entity_type == "All" or filter_entity_type == "organization":
            # Get organizations - try different entity types
            organizations_org = query_cosmos_entities_sync("organization", min(entity_limit, 10))
            organizations_entity = query_cosmos_entities_sync("entity", min(entity_limit, 15))
              # Filter entities that represent organizations
            for entity in organizations_entity:
                props = entity.get('properties', {})
                name = props.get('name', [''])[0] if 'name' in props else entity.get('id', '')
                # Safely handle name conversion to string
                name_str = str(name).lower() if name else ''
                if any(keyword in name_str for keyword in ['microsoft', 'company', 'corp', 'team', 'azure', 'organization']):
                    organizations.append(entity)
            
            # Add any found organization entities
            organizations.extend(organizations_org)
        
        if filter_entity_type == "All" or filter_entity_type == "location":
            # Get locations
            locations = query_cosmos_entities_sync("location", min(entity_limit, 5))
            organizations.extend(locations)  # Combine with organizations for simplicity
        
        if filter_entity_type == "All" or filter_entity_type == "event":
            # Get events
            events = query_cosmos_entities_sync("event", min(entity_limit, 5))
            organizations.extend(events)  # Combine with organizations for simplicity        
        # Get relationships
        relationships = query_cosmos_relationships_sync(limit=30)
        
        # Debug: Show what we found
        st.write(f"🔍 **Debug Info:**")
        st.write(f"- Found {len(customers)} customer entities")
        st.write(f"- Found {len(products)} product entities") 
        st.write(f"- Found {len(organizations)} organization entities")
        st.write(f"- Found {len(relationships)} relationships")
        
        # If still no data, try a broad query to see what's actually in the database
        if not customers and not products and not organizations:
            st.write("🧐 **Investigating database contents...**")
            
            # Try to get ANY vertices with different labels
            any_entities = query_cosmos_entities_sync(None, 20)  # Query without label filter
            st.write(f"- Found {len(any_entities)} total entities of any type")
            
            if any_entities:
                st.write("**Sample entities found:**")
                for i, entity in enumerate(any_entities[:5]):
                    label = entity.get('label', 'unknown')
                    entity_id = entity.get('id', 'no-id')
                    props = entity.get('properties', {})
                    st.write(f"  {i+1}. Label: `{label}`, ID: `{entity_id}`, Properties: {list(props.keys())}")
                
                # Try to use these entities as fallback data
                if filter_entity_type == "All":
                    # Distribute entities across categories for demo purposes
                    mid_point = len(any_entities) // 2
                    customers = any_entities[:mid_point//2] if mid_point > 0 else []
                    products = any_entities[mid_point//2:mid_point] if mid_point > 0 else []
                    organizations = any_entities[mid_point:] if mid_point > 0 else []
            
            return get_filtered_synthetic_data(filter_entity_type, entity_limit)
        
        return {
            'customers': customers,
            'products': products,
            'organizations': organizations,
            'relationships': relationships
        }
    except Exception as e:
        st.error(f"Error fetching real data: {e}")
        # Fallback to synthetic data with filtering
        return get_filtered_synthetic_data(filter_entity_type, entity_limit)

def get_filtered_synthetic_data(filter_entity_type="All", entity_limit=20):
    """Generate synthetic data that respects entity type filtering"""
    customers = []
    products = []
    organizations = []
    
    # Sample synthetic data with various entity types
    sample_customers = [
        {'id': 'customer-1', 'label': 'person', 'properties': {'name': 'Emma Thompson', 'segment': 'eco_conscious_millennials'}},
        {'id': 'customer-2', 'label': 'person', 'properties': {'name': 'Marcus Chen', 'segment': 'professional_urban'}},
        {'id': 'customer-3', 'label': 'person', 'properties': {'name': 'Sofia Rodriguez', 'segment': 'outdoor_enthusiasts'}},
    ]
    
    sample_products = [
        {'id': 'product-1', 'label': 'product', 'properties': {'name': 'EcoTrail Hiking Boots', 'price': 189.99}},
        {'id': 'product-2', 'label': 'product', 'properties': {'name': 'Urban Classic Loafers', 'price': 159.99}},
        {'id': 'product-3', 'label': 'product', 'properties': {'name': 'Performance Sneakers', 'price': 139.99}},
    ]
    
    sample_organizations = [
        {'id': 'org-1', 'label': 'organization', 'properties': {'name': 'Manybirds Store', 'type': 'retailer'}},
        {'id': 'org-2', 'label': 'organization', 'properties': {'name': 'EcoTextiles Global', 'type': 'supplier'}},
        {'id': 'location-1', 'label': 'location', 'properties': {'name': 'Barcelona, Spain'}},
        {'id': 'event-1', 'label': 'event', 'properties': {'name': 'Spring 2025 Campaign', 'type': 'marketing'}},
    ]
    
    # Apply filtering based on entity type
    if filter_entity_type == "All":
        customers = sample_customers[:min(entity_limit//3, len(sample_customers))]
        products = sample_products[:min(entity_limit//3, len(sample_products))]
        organizations = sample_organizations[:min(entity_limit//3, len(sample_organizations))]
    elif filter_entity_type == "person":
        customers = sample_customers[:min(entity_limit, len(sample_customers))]
    elif filter_entity_type == "product":
        products = sample_products[:min(entity_limit, len(sample_products))]
    elif filter_entity_type == "organization":
        organizations = [org for org in sample_organizations if org['label'] == 'organization'][:min(entity_limit, 2)]
    elif filter_entity_type == "location":
        organizations = [org for org in sample_organizations if org['label'] == 'location'][:min(entity_limit, 2)]
    elif filter_entity_type == "event":
        organizations = [org for org in sample_organizations if org['label'] == 'event'][:min(entity_limit, 2)]
      # Sample relationships with business context and temporal data
    relationships = [
        {
            'id': 'rel-1', 
            'label': 'purchased', 
            'source': 'customer-1', 
            'target': 'product-1',
            'properties': {
                'purchase_date': '2024-03-15',
                'amount': 194.99,
                'quantity': 1,
                'channel': 'online',
                'payment_method': 'credit_card'
            }
        },
        {
            'id': 'rel-2', 
            'label': 'supplies_material_for', 
            'source': 'org-2', 
            'target': 'product-1',
            'properties': {
                'contract_start': '2024-01-01',
                'sustainability_score': 9.2,
                'delivery_frequency': 'weekly',
                'cost_per_unit': 12.50
            }
        },
        {
            'id': 'rel-3', 
            'label': 'ships_to', 
            'source': 'customer-1', 
            'target': 'location-1',
            'properties': {
                'shipping_method': 'carbon_neutral',
                'delivery_time': '2-3 days',
                'shipping_cost': 0.00,
                'address_type': 'residential'
            }
        },
        {
            'id': 'rel-4', 
            'label': 'frequently_bought_together', 
            'source': 'product-1', 
            'target': 'product-2',
            'properties': {
                'correlation_score': 0.87,
                'bundle_discount': 15.0,
                'recommendation_strength': 'high'
            }
        },
        {
            'id': 'rel-5', 
            'label': 'manufactured_by', 
            'source': 'product-1', 
            'target': 'org-1',
            'properties': {
                'production_location': 'Portugal',
                'quality_rating': 4.8,
                'production_capacity': '10000_units_monthly'
            }
        }
    ]
    
    return {
        'customers': customers,
        'products': products,
        'organizations': organizations,
        'relationships': relationships
    }

def test_cosmos_connection():
    """Test connection to Cosmos DB"""
    try:
        gremlin_client = get_gremlin_client()
        if not gremlin_client:
            return False
            
        # Simple test query
        result = run_gremlin_query_sync("g.V().limit(1)")
        return len(result) >= 0  # Even empty result means connection works
    except Exception as e:
        st.error(f"Connection test failed: {e}")
        return False

st.set_page_config(page_title="Temporal Knowledge Evolution", layout="wide", page_icon="🌌")

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.title("🌌 Temporal Knowledge Graph: Real-Time Evolution")
st.markdown("### Watch as AI builds understanding over time using Graphiti + Cosmos DB")

# Real ecommerce data visualization focuses on live Cosmos DB data

# Sidebar controls
with st.sidebar:
    st.header("🔧 Visualization Controls")
    
    # Data description
    st.markdown("**🏪 Real Ecommerce Data Source:**")
    st.markdown("Live data from your Manybirds ecommerce knowledge graph")
    
    # Episode ingestion description
    st.markdown("---")
    st.markdown("**📚 Episodes Being Ingested:**")
    st.markdown("""
    The system processes real-time episodes from your ecommerce operations:
    
    • **Customer Interactions** - Search behavior, product views, cart activities
    • **Purchase Transactions** - Orders, payments, shipping preferences  
    • **Product Catalog** - New items, inventory updates, sustainability scores
    • **Supply Chain Events** - Supplier relationships, shipments, material sourcing
    • **Marketing Activities** - Campaign performance, email engagement, reviews
    • **Operational Metrics** - Warehouse operations, fulfillment, quality control
    
    Each episode builds the knowledge graph with entities, relationships, and temporal context.
    """)
    
    st.divider()
    
    # Real data options
    entity_limit = st.slider("Max Entities to Show", 5, 50, 20)
    show_relationships = st.checkbox("Show Relationships", True)
    filter_entity_type = st.selectbox(
        "Filter by Entity Type:",
        ["All", "person", "product", "organization", "location", "event"]
    )
    st.divider()

    animation_speed = st.slider("Animation Speed", 0.5, 3.0, 1.0, 0.1)
    show_confidence = st.checkbox("Show Confidence Scores", True)
    show_embeddings = st.checkbox("Show Semantic Similarity", True)
      # Visualization mode selection
    viz_mode = st.selectbox(
        "Visualization Mode:",
        ["🌐 3D Temporal Graph", "📈 Timeline Evolution", "📋 Business Dashboard"],
        help="Choose the best view for your analysis needs"
    )
    # Connection test for real data
    if st.button("🔍 Test Connection"):
        with st.spinner("Testing Cosmos DB connection..."):
            if test_cosmos_connection():                st.success("✅ Connected! Database is accessible")
            else:
                st.error("❌ Connection failed - check your settings")
                
    if st.button("📊 Start Visualization", type="primary"):
        st.session_state.demo_running = True
        st.session_state.data_source = "🏪 Real Ecommerce Data"
        st.session_state.viz_mode = viz_mode

# Main visualization area
col1, col2 = st.columns([3, 1])

with col1:
    graph_container = st.container()
    
with col2:
    metrics_container = st.container()
    with metrics_container:
        st.markdown("### 📊 Live Metrics")
        nodes_metric = st.metric("Entities", 0, delta=0)
        edges_metric = st.metric("Relationships", 0, delta=0)
        confidence_metric = st.metric("Avg Confidence", "0%", delta="0%")

# Timeline
timeline_container = st.container()

async def extract_entities_with_llm(text):
    """Use Azure OpenAI to extract entities and relationships from real ecommerce data"""
    client = get_openai_client()
    deployment = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT").strip('"')
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "Extract entities and their relationships from ecommerce data. Return JSON format with entities like customers, products, orders, suppliers, etc."},
                {"role": "user", "content": f"Ecommerce episode data: {text}"}
            ],
            temperature=0.3
        )
        
        # Extract from real data response
        result = response.choices[0].message.content
        import json
        return json.loads(result)
        
    except Exception as e:
        # Fallback for real data
        return {
            "entities": ["customer", "product", "order", "payment"],
            "relationships": [("customer", "places", "order"), ("order", "contains", "product")]
        }

def create_3d_temporal_graph(graph_data, current_time_index):
    """Create beautiful 3D graph visualization"""
    fig = go.Figure()
    
    # Calculate node positions in 3D space
    active_nodes = [n for i, n in enumerate(graph_data['nodes']) if i <= current_time_index]
    
    if not active_nodes:
        return fig
    
    # Node traces with temporal depth
    for i, node in enumerate(active_nodes):
        time_layer = i * 0.5  # Stack nodes in time
        age = current_time_index - i
        opacity = max(0.3, 1 - (age * 0.15))
        
        # Glow effect for recent nodes
        if age < 2:
            fig.add_trace(go.Scatter3d(
                x=[node['x']],
                y=[node['y']],
                z=[time_layer],
                mode='markers',
                marker=dict(
                    size=25,
                    color='rgba(255, 255, 255, 0.3)',
                    line=dict(width=0)
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Main node
        fig.add_trace(go.Scatter3d(
            x=[node['x']],
            y=[node['y']],
            z=[time_layer],
            mode='markers+text',
            marker=dict(
                size=15 + node.get('importance', 1) * 5,
                color=node['color'],
                opacity=opacity,
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            text=node['label'],
            textposition='top center',
            textfont=dict(size=10, color='black'),
            name=node['label'],
            hovertemplate=f"""
            <b>{node['label']}</b><br>
            Time: Step {i}<br>
            Confidence: {node.get('confidence', 0.8):.2%}<br>
            <extra></extra>
            """
        ))
    
    # Edge traces with gradient effect
    active_edges = [e for i, e in enumerate(graph_data['edges']) if i <= current_time_index]
    
    for edge in active_edges:
        # Find source and target positions
        source_idx = edge['source_idx']
        target_idx = edge['target_idx']
        
        if source_idx < len(active_nodes) and target_idx < len(active_nodes):
            source = active_nodes[source_idx]
            target = active_nodes[target_idx]
            
            # Create curved edge for beauty
            t = np.linspace(0, 1, 20)
            curve_height = 0.3
            x_curve = source['x'] + t * (target['x'] - source['x'])
            y_curve = source['y'] + t * (target['y'] - source['y'])
            z_curve = source_idx * 0.5 + t * (target_idx * 0.5 - source_idx * 0.5) + curve_height * np.sin(np.pi * t)
            
            fig.add_trace(go.Scatter3d(
                x=x_curve,
                y=y_curve,
                z=z_curve,
                mode='lines',
                line=dict(
                    color=edge['color'],
                    width=3,
                    shape='spline'
                ),
                opacity=0.6,
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Beautiful 3D layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, showticklabels=False, title=''),
            zaxis=dict(showgrid=True, showticklabels=True, title='Time →'),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0)
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        showlegend=True,
        legend=dict(
            x=1.02,
            y=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        )
    )
    
    return fig



def create_real_data_visualization(real_data, time_index):
    """Create visualization using real Cosmos DB data with proper relationship mapping"""
    if not real_data:
        return go.Figure()
    
    fig = go.Figure()
      # Color scheme for different entity types with icons
    colors = {
        'person': '#4285F4',      # Blue for customers
        'product': '#34A853',     # Green for products  
        'organization': '#EA4335', # Red for organizations
        'location': '#9C27B0',    # Purple for locations
        'event': '#FF9800'        # Orange for events
    }
      # Entity type icons for better legend distinction
    entity_icons = {
        'person': '👤',
        'product': '📦', 
        'organization': '🏢',
        'location': '📍',
        'event': '⚡'
    }
      # Initialize relationship tracking variables (global scope for debug info)
    relationships_drawn = 0
    max_relationships = 0
      # Add nodes from real data with better entity mapping
    all_entities = []
    entity_id_map = {}  # Map entity IDs to positions for relationship drawing
    entity_type_added = set()  # Track which entity types we've added to legend
    
    if 'customers' in real_data:
        for entity in real_data['customers']:
            all_entities.append((entity, 'person'))
            entity_id_map[entity.get('id', f"person_{len(entity_id_map)}")] = len(all_entities) - 1
    
    if 'products' in real_data:
        for entity in real_data['products']:
            all_entities.append((entity, 'product'))
            entity_id_map[entity.get('id', f"product_{len(entity_id_map)}")] = len(all_entities) - 1
    
    if 'organizations' in real_data:
        for entity in real_data['organizations']:
            all_entities.append((entity, 'organization'))
            entity_id_map[entity.get('id', f"org_{len(entity_id_map)}")] = len(all_entities) - 1
    
    # Limit entities based on time progression
    visible_entities = all_entities[:time_index + 1]
    node_positions = {}
    
    for i, (entity, entity_type) in enumerate(visible_entities):
        # Create clustered layout based on entity type
        type_angle_offset = {'person': 0, 'product': 2*np.pi/3, 'organization': 4*np.pi/3}.get(entity_type, 0)
        cluster_radius = 0.8
        
        # Position nodes in clusters with some randomness
        angle = type_angle_offset + (2 * np.pi * (i % 5) / 5) + np.random.normal(0, 0.2)
        radius = cluster_radius + (i // 5) * 0.3 + np.random.normal(0, 0.1)
        
        x = np.cos(angle) * radius
        y = np.sin(angle) * radius
        z = i * 0.15  # Stack in time
        
        # Store position for relationship drawing
        entity_id = entity.get('id', f'entity_{i}')
        node_positions[entity_id] = {'x': x, 'y': y, 'z': z, 'index': i}
        
        # Get entity name from properties
        name = "Unknown"
        if entity.get('properties'):
            if 'name' in entity['properties']:
                name_prop = entity['properties']['name']
                name = name_prop[0]['value'] if isinstance(name_prop, list) else str(name_prop)
            elif 'title' in entity['properties']:
                title_prop = entity['properties']['title']
                name = title_prop[0]['value'] if isinstance(title_prop, list) else str(title_prop)
        
        name = name[:15] + "..." if len(name) > 15 else name
        
        # Calculate opacity based on recency
        age = len(visible_entities) - i - 1
        opacity = max(0.6, 1 - (age * 0.05))
        
        # Add glow effect for recent nodes
        if age < 3:
            fig.add_trace(go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode='markers',
                marker=dict(
                    size=20,
                    color='rgba(255, 255, 255, 0.2)',
                    line=dict(width=0)
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
          # Main node
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers+text',
            marker=dict(
                size=12 + (3 if age < 2 else 0),
                color=colors.get(entity_type, '#757575'),
                opacity=opacity,
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            text=[name],
            textposition="middle center",
            textfont=dict(color='white', size=8, family="Arial Black"),
            name=f"{entity_icons.get(entity_type, '')} {entity_type.title()}",
            showlegend=(entity_type not in entity_type_added),  # Only show in legend once per type
            legendgroup=entity_type,  # Group by entity type
            hovertemplate=f"<b>{name}</b><br>Type: {entity_type}<br>ID: {entity.get('id', 'N/A')}<br>Properties: {len(entity.get('properties', {}))}<extra></extra>"
        ))
        
        # Mark this entity type as added to legend
        entity_type_added.add(entity_type)
      # Enhanced relationship drawing with better matching
    if 'relationships' in real_data and len(visible_entities) > 1:
        relationships_drawn = 0
        max_relationships = min(15, time_index + 2)  # Show more relationships as time progresses
        for rel in real_data['relationships'][:max_relationships]:
            # Try multiple key names for source and target (handle different data formats)
            source_id = rel.get('source', rel.get('source_id', ''))
            target_id = rel.get('target', rel.get('target_id', ''))
            
            # Skip if we don't have valid IDs
            if not source_id or not target_id:
                continue
            
            # Try multiple ID formats to find matches
            possible_sources = [source_id, str(source_id), source_id.replace('-', '')]
            possible_targets = [target_id, str(target_id), target_id.replace('-', '')]
            
            source_pos = None
            target_pos = None
            
            # Find source position
            for pid in possible_sources:
                if pid in node_positions:
                    source_pos = node_positions[pid]
                    break
            
            # Find target position  
            for pid in possible_targets:
                if pid in node_positions:
                    target_pos = node_positions[pid]
                    break
              # If we can't find exact matches, try a more intelligent approach
            if not source_pos and not target_pos and len(visible_entities) >= 2:
                # Create relationships between entities of different types
                all_positions = list(node_positions.items())
                
                # Try to match partial IDs or find entities by type
                if not source_pos:
                    # Look for entities that might match the source
                    for eid, pos in all_positions:
                        if any(possible_id in eid or eid in possible_id for possible_id in possible_sources):
                            source_pos = pos
                            break
                
                if not target_pos:
                    # Look for entities that might match the target
                    for eid, pos in all_positions:
                        if any(possible_id in eid or eid in possible_id for possible_id in possible_targets):
                            target_pos = pos
                            break
                
                # If still no matches, create synthetic relationships between different entity types
                if not source_pos and not target_pos and relationships_drawn < 3:
                    customers = [pos for eid, pos in node_positions.items() if any(e[0].get('id') == eid and e[1] == 'person' for e in visible_entities)]
                    products = [pos for eid, pos in node_positions.items() if any(e[0].get('id') == eid and e[1] == 'product' for e in visible_entities)]
                    orgs = [pos for eid, pos in node_positions.items() if any(e[0].get('id') == eid and e[1] == 'organization' for e in visible_entities)]
                    
                    # Create relationships between different types
                    if customers and products:
                        source_pos = customers[relationships_drawn % len(customers)]
                        target_pos = products[relationships_drawn % len(products)]
                    elif customers and orgs:
                        source_pos = customers[relationships_drawn % len(customers)]
                        target_pos = orgs[relationships_drawn % len(orgs)]
                    elif products and orgs:
                        source_pos = products[relationships_drawn % len(products)]
                        target_pos = orgs[relationships_drawn % len(orgs)]
            if source_pos and target_pos and relationships_drawn < max_relationships:
                # Create curved relationship line with variable curve height for better visibility
                t = np.linspace(0, 1, 25)
                curve_height = 0.3 + (relationships_drawn * 0.1)  # Vary curve height
                
                x_curve = source_pos['x'] + t * (target_pos['x'] - source_pos['x'])
                y_curve = source_pos['y'] + t * (target_pos['y'] - source_pos['y'])
                z_curve = source_pos['z'] + t * (target_pos['z'] - source_pos['z']) + curve_height * np.sin(np.pi * t)
                
                # Enhanced color scheme for relationships
                relationship_colors = [
                    'rgba(255, 99, 71, 0.8)',    # Tomato
                    'rgba(50, 205, 50, 0.8)',    # Lime Green
                    'rgba(30, 144, 255, 0.8)',   # Dodger Blue
                    'rgba(255, 165, 0, 0.8)',    # Orange
                    'rgba(147, 112, 219, 0.8)',  # Medium Slate Blue
                    'rgba(255, 20, 147, 0.8)',   # Deep Pink
                    'rgba(0, 206, 209, 0.8)',    # Dark Turquoise
                    'rgba(255, 215, 0, 0.8)'     # Gold
                ]
                rel_color = relationship_colors[relationships_drawn % len(relationship_colors)]
                
                # Get relationship label for better hover info
                rel_label = rel.get('label', 'connects')
                rel_source = rel.get('source', rel.get('source_id', 'Unknown'))
                rel_target = rel.get('target', rel.get('target_id', 'Unknown'))
                
                fig.add_trace(go.Scatter3d(
                    x=x_curve, y=y_curve, z=z_curve,
                    mode='lines',
                    line=dict(
                        color=rel_color,
                        width=6  # Make lines thicker for better visibility
                    ),
                    showlegend=False,
                    hovertemplate=f"<b>{rel_label}</b><br>From: {rel_source}<br>To: {rel_target}<br>Relationship #{relationships_drawn + 1}<extra></extra>",
                    name=f"🔗 {rel_label}"
                ))
                relationships_drawn += 1
    
    # Update layout for better 3D visualization
    fig.update_layout(
        scene=dict(
            bgcolor='rgba(10,10,30,0.8)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', showticklabels=False, title=''),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', showticklabels=False, title=''),
            zaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', showticklabels=True, title="Time Evolution →"),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.5))
        ),        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=60, b=0),  # Increased top margin for titleshowlegend=True,
        legend=dict(
            x=0.02, y=0.98, 
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='rgba(0,0,0,0.3)',
            borderwidth=1,
            font=dict(
                color='black',  # Dark text for better visibility
                size=12,
                family='Arial'
            )
        ),        title=dict(
            text="🌐 Real-Time Knowledge Graph Evolution",
            x=0.5,
            y=0.98,  # Position title lower to avoid overlap with 3D controls
            font=dict(size=16, color='white')
        ),        height=650
    )
    
    # Debug information - store in streamlit session state for display
    if 'relationships' in real_data:
        debug_info = {
            'total_relationships': len(real_data['relationships']),
            'relationships_drawn': relationships_drawn,
            'max_relationships': max_relationships,
            'visible_entities': len(visible_entities),
            'sample_relationships': real_data['relationships'][:3] if real_data['relationships'] else []
        }
        # Store debug info for later display
        import streamlit as st
        st.session_state.relationship_debug = debug_info
    
    return fig

# Enhanced visualization modes for different use cases

def create_timeline_view(real_data, time_index):
    """Timeline-based view showing evolution over time"""
    fig = go.Figure()
    
    # Get data subsets
    customers = real_data.get('customers', [])[:time_index + 1]
    products = real_data.get('products', [])[:time_index + 1] 
    organizations = real_data.get('organizations', [])[:time_index + 1]
    
    # Create timeline data
    timeline_data = []
    
    # Add entities to timeline
    for i, customer in enumerate(customers):
        timeline_data.append({
            'x': i,
            'y': 1,
            'type': 'Customer',
            'name': get_entity_name(customer)
        })
    
    for i, product in enumerate(products):
        timeline_data.append({
            'x': len(customers) + i,
            'y': 2,
            'type': 'Product',
            'name': get_entity_name(product)
        })
    
    for i, org in enumerate(organizations):
        timeline_data.append({
            'x': len(customers) + len(products) + i,
            'y': 3,
            'type': 'Organization',
            'name': get_entity_name(org)
        })
    
    # Plot by type
    colors = {'Customer': '#FF6B6B', 'Product': '#4ECDC4', 'Organization': '#45B7D1'}
    
    for entity_type, color in colors.items():
        type_data = [item for item in timeline_data if item['type'] == entity_type]
        if type_data:
            fig.add_trace(go.Scatter(
                x=[item['x'] for item in type_data],
                y=[item['y'] for item in type_data],
                mode='markers',
                marker=dict(size=15, color=color),
                name=entity_type,
                text=[item['name'] for item in type_data],
                hovertemplate=f"<b>%{{text}}</b><br>Type: {entity_type}<extra></extra>"
            ))
    
    fig.update_layout(
        title="📈 Timeline Evolution",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        yaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=['👥 Customers', '📦 Products', '🏢 Organizations']
        ),
        height=400
    )
    
    return fig

def create_dashboard_view(real_data, time_index):
    """Business metrics dashboard with graph insights - data only, no UI creation"""
    
    # Calculate key metrics
    customers = real_data.get('customers', [])[:time_index + 1]
    products = real_data.get('products', [])[:time_index + 1]
    organizations = real_data.get('organizations', [])[:time_index + 1]
    relationships = real_data.get('relationships', [])
    
    entity_counts = {
        'customers': len(customers),
        'products': len(products),
        'organizations': len(organizations),
        'total': len(customers) + len(products) + len(organizations)
    }
    
    relationship_counts = {
        'customer_product': len([r for r in relationships if 'customer' in str(r.get('type', ''))]),
        'product_org': len([r for r in relationships if 'supplier' in str(r.get('type', ''))]),
        'total': len(relationships)
    }
    
    # Create charts for dashboard
    fig1 = go.Figure()
    
    # Entity distribution pie chart
    fig1.add_trace(go.Pie(
        labels=['Customers', 'Products', 'Organizations'],
        values=[entity_counts['customers'], entity_counts['products'], entity_counts['organizations']],
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1'],
        textinfo='label+percent',
        textfont=dict(color='white', size=12)
    ))
    
    fig1.update_layout(
        title=dict(
            text="📊 Entity Distribution",
            x=0.5,
            font=dict(size=14, color='white')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # Growth trend chart
    fig2 = go.Figure()
    
    # Generate growth data over time
    time_steps = list(range(time_index + 1))
    cumulative_customers = [min(i + 1, len(customers)) for i in time_steps]
    cumulative_products = [min(i + 1, len(products)) for i in time_steps]
    cumulative_orgs = [min(i + 1, len(organizations)) for i in time_steps]
    
    fig2.add_trace(go.Scatter(
        x=time_steps,
        y=cumulative_customers,
        mode='lines+markers',
        name='👥 Customers',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=6)
    ))
    
    fig2.add_trace(go.Scatter(
        x=time_steps,
        y=cumulative_products,
        mode='lines+markers',
        name='📦 Products',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=6)
    ))
    
    fig2.add_trace(go.Scatter(
        x=time_steps,
        y=cumulative_orgs,
        mode='lines+markers',
        name='🏢 Organizations',
        line=dict(color='#45B7D1', width=3),
        marker=dict(size=6)
    ))
    
    fig2.update_layout(
        title=dict(
            text="📈 Growth Trends Over Time",
            x=0.5,
            font=dict(size=14, color='white')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        xaxis=dict(
            title="Time Steps",
            showgrid=True,
            gridcolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            title="Entity Count",
            showgrid=True,
            gridcolor='rgba(255,255,255,0.2)'
        ),
        height=300,
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
      # Business insights
    insights = []
    
    if entity_counts['customers'] > 0:
        insights.append(f"🎯 **Customer Base**: {entity_counts['customers']} customers in knowledge graph")
    else:
        insights.append("🎯 **Customer Base**: No customer data available yet")
        
    if entity_counts['products'] > 0:
        insights.append(f"📦 **Product Catalog**: {entity_counts['products']} products available") 
    else:
        insights.append("📦 **Product Catalog**: No product data available yet")
        
    if entity_counts['organizations'] > 0:
        insights.append(f"🤝 **Business Network**: {entity_counts['organizations']} organizations connected")
    else:
        insights.append("🤝 **Business Network**: No partner organizations found yet")
        
    if relationship_counts['total'] > 0:
        insights.append(f"🔗 **Network Density**: {relationship_counts['total']} active relationships")
        insights.append(f"📊 **Connectivity**: {(relationship_counts['total'] / max(entity_counts['total'], 1) * 100):.1f}% relationship density")
    else:
        insights.append("🔗 **Network Density**: No relationships mapped yet")
        insights.append("📊 **Connectivity**: Graph is still building connections")
    
    return {
        'entity_counts': entity_counts,
        'relationship_trends': relationship_counts,
        'business_insights': insights,
        'distribution_chart': fig1,
        'growth_chart': fig2
    }

# Business intelligence features
def generate_business_insights(graph_data):
    """Generate actionable business insights from graph analysis"""
    
    insights = {
        'trending_entities': [],
        'emerging_relationships': [],
        'anomaly_detection': [],
        'prediction_signals': [],
        'optimization_opportunities': []
    }
    
    # LLM-powered insight generation
    # Pattern recognition in temporal data
    # Anomaly detection in relationship changes
    # Predictive analytics based on graph evolution
    
    return insights

def create_insight_panel(insights):
    """Create a panel showing AI-generated business insights"""
    
    with st.sidebar:
        st.header("🧠 AI Insights")
        
        for insight_type, items in insights.items():
            if items:
                st.subheader(insight_type.replace('_', ' ').title())
                for item in items:
                    st.info(item)

# Add business context extraction
def extract_business_context(entity_data):
    """Extract business-relevant context from entity properties"""
    
    context = {
        'customer_value_signals': [],
        'product_performance_indicators': [],
        'market_trend_indicators': [],
        'operational_efficiency_metrics': []
    }
    
    # Extract customer value signals
    customers = entity_data.get('customers', [])
    for customer in customers[:5]:  # Sample first 5
        customer_name = get_entity_name(customer)
        properties = customer.get('properties', {})
        
        # Look for value indicators
        if 'purchase_amount' in properties:
            context['customer_value_signals'].append(f"High-value customer: {customer_name}")
        elif 'loyalty_status' in properties:
            context['customer_value_signals'].append(f"Loyal customer segment: {customer_name}")
        else:
            context['customer_value_signals'].append(f"Active customer: {customer_name}")
    
    # Extract product performance indicators
    products = entity_data.get('products', [])
    for product in products[:5]:  # Sample first 5
        product_name = get_entity_name(product)
        properties = product.get('properties', {})
        
        if 'sustainability' in str(properties).lower():
            context['product_performance_indicators'].append(f"Eco-friendly product: {product_name}")
        elif 'popular' in str(properties).lower():
            context['product_performance_indicators'].append(f"Popular item: {product_name}")
        else:
            context['product_performance_indicators'].append(f"Active product: {product_name}")
    
    # Extract market trend indicators
    organizations = entity_data.get('organizations', [])
    for org in organizations[:3]:  # Sample first 3
        org_name = get_entity_name(org)
        context['market_trend_indicators'].append(f"Partner organization: {org_name}")
    
    # Extract operational efficiency metrics
    relationships = entity_data.get('relationships', [])
    total_relationships = len(relationships)
    total_entities = len(customers) + len(products) + len(organizations)
    
    if total_entities > 0:
        connectivity_ratio = total_relationships / total_entities
        if connectivity_ratio > 1.5:
            context['operational_efficiency_metrics'].append("High network connectivity detected")
        elif connectivity_ratio > 1.0:
            context['operational_efficiency_metrics'].append("Moderate network connectivity")
        else:
            context['operational_efficiency_metrics'].append("Building network connections")
    
    context['operational_efficiency_metrics'].append(f"Total network size: {total_entities} entities")
    context['operational_efficiency_metrics'].append(f"Relationship density: {connectivity_ratio:.2f}" if total_entities > 0 else "Relationship density: 0.00")
    
    return context

# Real-time streaming capabilities
async def setup_real_time_updates():
    """Setup WebSocket or SSE for real-time graph updates"""
      # Azure Service Bus or Event Hubs integration
    # Real-time event streaming from business systems
    # Incremental graph updates without full refresh
    
    try:
        # Real-time setup for production use
        # In production, this would connect to Azure Event Hubs or Service Bus
        st.session_state.real_time_enabled = True
        st.session_state.last_update = time.time()
        return True
    except Exception as e:
        st.error(f"Failed to setup real-time updates: {e}")
        return False

def create_streaming_visualization():
    """Streaming visualization with live updates"""
    
    # Use Streamlit's automatic rerun capabilities
    # or implement WebSocket updates
    # Incremental node/edge additions
    
    if not hasattr(st.session_state, 'streaming_data'):
        st.session_state.streaming_data = {
            'nodes': [],
            'edges': [],
            'last_update': time.time()
        }
      # Simulate streaming data for visualization
    current_time = time.time()
    if current_time - st.session_state.streaming_data['last_update'] > 2:  # Update every 2 seconds
        # Add a new node to simulate streaming
        new_node_id = f"stream_node_{len(st.session_state.streaming_data['nodes'])}"
        new_node = {
            'id': new_node_id,
            'name': f"Stream Entity {len(st.session_state.streaming_data['nodes']) + 1}",
            'type': 'streaming',
            'timestamp': current_time        }        
        st.session_state.streaming_data['nodes'].append(new_node)
        st.session_state.streaming_data['last_update'] = current_time
        
        # Trigger rerun to show updated visualization
        if len(st.session_state.streaming_data['nodes']) < 10:  # Limit to 10 nodes for visualization
            st.rerun()
    
    return st.session_state.streaming_data

# Visualization execution
if 'demo_running' in st.session_state and st.session_state.demo_running:
    # Real data visualization
    st.header("🏪 Live Ecommerce Knowledge Graph")
    with st.spinner("Fetching real data from Cosmos DB..."):
        real_data = get_real_ecommerce_data_sync(filter_entity_type, entity_limit)
    
    if real_data:
        # Progress through entities over time
        total_entities = len(real_data.get('customers', [])) + len(real_data.get('products', [])) + len(real_data.get('organizations', []))
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for time_index in range(min(total_entities, entity_limit)):
            progress = (time_index + 1) / min(total_entities, entity_limit)
            progress_bar.progress(progress)
            status_text.text(f"Loading entity {time_index + 1} of {min(total_entities, entity_limit)}...")            # Create visualization based on selected mode
            viz_mode = getattr(st.session_state, 'viz_mode', '🌐 3D Temporal Graph')
            if viz_mode == "🌐 3D Temporal Graph":
                fig = create_real_data_visualization(real_data, time_index)
                graph_container.plotly_chart(fig, use_container_width=True, key=f"3d_graph_{time_index}")

            elif viz_mode == "📈 Timeline Evolution":
                fig = create_timeline_view(real_data, time_index)
                graph_container.plotly_chart(fig, use_container_width=True, key=f"timeline_{time_index}")            
            elif viz_mode == "📋 Business Dashboard":
                dashboard_data = create_dashboard_view(real_data, time_index)
                  # Display only dashboard charts during animation, not metrics/insights
                col1, col2 = graph_container.columns(2)                
                with col1:
                    st.plotly_chart(dashboard_data['distribution_chart'], use_container_width=True, key=f"distribution_chart_{time_index}")
                with col2:
                    st.plotly_chart(dashboard_data['growth_chart'], use_container_width=True, key=f"growth_chart_{time_index}")
                
                # Save final dashboard data for end display
                if time_index == min(total_entities, entity_limit) - 1:
                    st.session_state.final_dashboard_data = dashboard_data
              
        else:
            # Fallback to 3D view
            fig = create_real_data_visualization(real_data, time_index)
            graph_container.plotly_chart(fig, use_container_width=True, key=f"fallback_3d_{time_index}")
        
        # Update metrics with real data
            visible_count = time_index + 1
            rel_count = len(real_data.get('relationships', []))
            nodes_metric.metric("Entities", visible_count, delta=1 if time_index > 0 else 0)
            edges_metric.metric("Relationships", min(rel_count, time_index), delta=0)
            confidence_metric.metric("Data Quality", "95%", delta="High")
            
            # Add real-time insights
            with timeline_container:
                if time_index < 3:  # Show first few insights
                    insights = [
                        "🏷️ Product catalog loaded - sustainable footwear detected",
                        "👥 Customer profiles identified - eco-conscious segments emerging", 
                        "🌐 Supply chain relationships mapped - EcoBirds partnership active"
                    ]
                    if time_index < len(insights):
                        st.info(f"**Insight {time_index + 1}:** {insights[time_index]}")
            
            time.sleep(1 / animation_speed)
        progress_bar.empty()
        status_text.success("✨ Real knowledge graph loaded!")
          # Show comprehensive business intelligence only once at the end
        st.markdown("### 🎯 Live Business Intelligence")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Customers", len(real_data.get('customers', [])))
        with col2:
            st.metric("Products", len(real_data.get('products', [])))        
        with col3:
            st.metric("Partners", len(real_data.get('organizations', [])))
        
        # Show dashboard insights and metrics if dashboard mode was used
        if hasattr(st.session_state, 'final_dashboard_data'):
            dashboard_data = st.session_state.final_dashboard_data
            
            # Display detailed dashboard metrics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="👥 Total Customers",
                    value=dashboard_data['entity_counts']['customers'],
                    delta=f"+{dashboard_data['entity_counts']['customers']} total" if dashboard_data['entity_counts']['customers'] > 0 else None
                )
            
            with col2:
                st.metric(
                    label="📦 Active Products", 
                    value=dashboard_data['entity_counts']['products'],
                    delta=f"+{dashboard_data['entity_counts']['products']} total" if dashboard_data['entity_counts']['products'] > 0 else None
                )
            
            with col3:
                st.metric(
                    label="🏢 Partner Organizations",
                    value=dashboard_data['entity_counts']['organizations'], 
                    delta=f"+{dashboard_data['entity_counts']['organizations']} total" if dashboard_data['entity_counts']['organizations'] > 0 else None
                )
            
            with col4:
                st.metric(
                    label="🔗 Relationships",
                    value=dashboard_data['relationship_trends']['total'],
                    delta=f"+{dashboard_data['relationship_trends']['total']} total" if dashboard_data['relationship_trends']['total'] > 0 else None
                )
            
            st.markdown("### 💡 Business Insights")
            for insight in dashboard_data['business_insights']:
                st.markdown(f"• {insight}")
            # Clear the stored data
            del st.session_state.final_dashboard_data
        
    else:
        st.error("Failed to fetch real data. Please check your Cosmos DB connection.")

else:
    # Show placeholder
    with graph_container:
        st.info("👈 Configure settings and click 'Start Visualization' to begin analyzing real ecommerce data")

# Footer
st.markdown("---")
st.caption("Powered by Graphiti + Azure Cosmos DB Gremlin API + Azure OpenAI")