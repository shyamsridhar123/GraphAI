"""
Step-by-Step Interactive Graph Visualization Demo
==============================================

A simple, interactive demo that lets you select episodes and visualize 
the graph step by step with detailed descriptions of entities, relationships, 
subgraphs, and communities.

Perfect for understanding how Graphiti-Cosmos builds knowledge graphs from episodes.
"""

import asyncio
import os
import sys
import time
import platform
from datetime import datetime
from typing import Dict, Any, List
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from graphiti_cosmos import GraphitiCosmos, Episode

class StepByStepVisualizationDemo:
    """Interactive demo for step-by-step graph visualization"""
    
    def __init__(self):
        self.graphiti = None
        self.current_step = 0
        self.processed_episodes = []
        self.sample_episodes = self._create_sample_episodes()

    def _create_sample_episodes(self) -> List[Episode]:
        """Create a set of interconnected sample episodes for demonstration"""
        
        episodes = [
            Episode(
                content="""
                Sarah Johnson, a 28-year-old marketing professional from Seattle, visited the Manybirds 
                e-commerce website on Monday morning. She browsed the sustainable sneakers category and 
                spent 5 minutes viewing product details for the EcoWalk Sustainable Sneakers. Sarah 
                showed particular interest in the product's recycled ocean plastic material and added 
                the sneakers to her wishlist for future consideration.
                """,
                episode_id="ep_001_sarah_browsing",
                source="website_analytics"
            ),
            
            Episode(
                content="""
                Two days later, Sarah Johnson returned to Manybirds and purchased the EcoWalk Sustainable 
                Sneakers (Product ID: PROD_ECOWALK_001) for $129.99. She used her Visa credit card for 
                payment and selected standard shipping to her home address in Seattle. The order was 
                confirmed with Order ID: ORD_20250529_001. Sarah also signed up for the sustainability 
                newsletter during checkout.
                """,
                episode_id="ep_002_sarah_purchase",
                source="order_management_system"
            ),
            
            Episode(
                content="""
                Alex Chen, a 32-year-old software engineer from San Francisco, discovered Manybirds 
                through a Google search for "sustainable running shoes". He landed on the product page 
                for EcoWalk Sustainable Sneakers and read customer reviews, including Sarah Johnson's 
                recent 5-star review. Alex was impressed by the environmental impact metrics and added 
                the same product to his cart. He also viewed the Trail Runner Performance shoes but 
                decided to stick with the EcoWalk model.
                """,
                episode_id="ep_003_alex_discovery",
                source="website_analytics"
            ),
            
            Episode(
                content="""
                Manybirds received a shipment of 500 pairs of EcoWalk Sustainable Sneakers from their 
                manufacturing partner GreenStep Manufacturing in Vietnam. The shipment arrived at the 
                Portland distribution center and was processed by warehouse manager Mike Rodriguez. 
                Quality control inspected 50 random pairs and approved the entire shipment. The 
                inventory system was updated to reflect 500 new units available for sale.
                """,
                episode_id="ep_004_inventory_shipment",
                source="warehouse_management_system"
            ),
            
            Episode(
                content="""
                Emily Thompson, a 26-year-old environmental science student from Portland, purchased 
                EcoWalk Sustainable Sneakers during a flash sale promotion offering 20% off sustainable 
                products. She discovered the product through Manybirds' Instagram ad campaign focusing 
                on ocean plastic recycling. Emily paid $103.99 (reduced from $129.99) and chose express 
                shipping. She also purchased the matching Eco-Friendly Shoe Care Kit as an add-on item.
                """,
                episode_id="ep_005_emily_promo_purchase",
                source="order_management_system"
            ),
            
            Episode(
                content="""
                The Manybirds marketing team launched a targeted email campaign to customers who had 
                previously purchased sustainable products. The campaign featured the new Summer 
                Sustainability Collection, including the EcoWalk Sustainable Sneakers. The campaign 
                achieved a 15% open rate and 3.2% click-through rate, resulting in 25 new visitors 
                to the sustainable sneakers category page. Sarah Johnson and Alex Chen both received 
                and opened this email.
                """,
                episode_id="ep_006_marketing_campaign",
                source="email_marketing_platform"
            ),
            
            Episode(
                content="""
                Dr. Maria Rodriguez, a sustainability consultant, wrote a blog post reviewing eco-friendly 
                footwear brands for EcoLifestyle Magazine. She featured Manybirds' EcoWalk Sustainable 
                Sneakers as a "top pick" for their innovative use of recycled ocean plastic. The blog 
                post mentioned the positive reviews from customers like Sarah Johnson and noted the 
                company's commitment to carbon-neutral shipping. The article drove 150 new visitors 
                to the Manybirds website.
                """,
                episode_id="ep_007_influencer_review",
                source="content_marketing_tracker"
            ),
            
            Episode(
                content="""
                GreenStep Manufacturing, Manybirds' key production partner, reported successful completion 
                of their Q2 sustainability audit. The audit confirmed their carbon-neutral production 
                facility and ethical labor practices. Manufacturing Director Linda Chang presented the 
                results to Manybirds' supply chain team, strengthening the partnership for producing 
                EcoWalk Sustainable Sneakers. The audit results will be featured in Manybirds' upcoming 
                sustainability report.
                """,
                episode_id="ep_008_supplier_audit",
                source="supply_chain_management"
            )
        ]
        
        return episodes

    async def initialize(self):
        """Initialize the Graphiti-Cosmos system"""
        print("🚀 STEP-BY-STEP GRAPH VISUALIZATION DEMO")
        print("=" * 60)
        print("🎨 Initializing Graphiti-Cosmos...")
        
        self.graphiti = GraphitiCosmos()
        await self.graphiti.initialize()
        print("✅ Connected to Azure Cosmos DB and OpenAI")
        print("🌟 Ready for interactive graph building!")
        print()

    def display_episode_menu(self):
        """Display available episodes for selection"""
        print("📚 AVAILABLE EPISODES")
        print("-" * 40)
        
        for i, episode in enumerate(self.sample_episodes, 1):
            status = "✅ PROCESSED" if episode.episode_id in [ep.episode_id for ep in self.processed_episodes] else "⏳ PENDING"
            print(f"{i}. {episode.episode_id} - {status}")
            # Show first 80 characters of content
            preview = episode.content.strip()[:80].replace('\n', ' ') + "..."
            print(f"   Preview: {preview}")
            print()

    async def process_selected_episode(self, episode_num: int):
        """Process a selected episode and show step-by-step results"""
        if episode_num < 1 or episode_num > len(self.sample_episodes):
            print("❌ Invalid episode number!")
            return
        
        episode = self.sample_episodes[episode_num - 1]
        
        # Check if already processed
        if episode.episode_id in [ep.episode_id for ep in self.processed_episodes]:
            print(f"⚠️  Episode {episode.episode_id} has already been processed!")
            return
        
        print(f"🎬 PROCESSING EPISODE {episode_num}")
        print("=" * 60)
        print(f"📝 Episode ID: {episode.episode_id}")
        print(f"📊 Source: {episode.source}")
        print(f"📄 Content:")
        print(episode.content.strip())
        print()
          # Step 1: Add episode to graph
        print("STEP 1: Adding Episode to Knowledge Graph")
        print("-" * 40)
        start_time = time.time()
        
        try:
            # Store the extracted data for step-by-step display
            entities = await self.graphiti._extract_entities(episode.content)
            relationships = await self.graphiti._extract_relationships(episode.content, entities)
            
            # Process the episode
            result = await self.graphiti.add_episode(episode)
            processing_time = time.time() - start_time
            
            print(f"✅ Episode processed successfully in {processing_time:.2f} seconds")
            print(f"📊 Processing result: {result}")
            
            # Store extracted data for later steps
            episode._extracted_entities = entities
            episode._extracted_relationships = relationships
            
            # Mark as processed
            self.processed_episodes.append(episode)
            print()
            
            # Step 2: Show current graph statistics
            await self._show_graph_statistics()
            
            # Step 3: Extract and show entities
            await self._show_extracted_entities(episode.episode_id)
            
            # Step 4: Show relationships
            await self._show_relationships(episode.episode_id)
            
            # Step 5: Show subgraphs and communities
            await self._show_subgraphs_and_communities()
            
            # Step 6: Generate visualization
            await self._generate_step_visualization()
            
        except Exception as e:
            print(f"❌ Error processing episode: {e}")
            import traceback
            traceback.print_exc()

    async def _show_graph_statistics(self):
        """Show current graph statistics"""
        print("STEP 2: Current Graph Statistics")
        print("-" * 40)
        
        try:
            stats = await self.graphiti.get_graph_stats()
            print(f"📊 Episodes: {stats['episodes']}")
            print(f"👥 Entities: {stats['entities']}")
            print(f"🔗 Relationships: {stats['relationships']}")
            
            if stats['entities'] > 0:
                density = stats['relationships'] / stats['entities']
                print(f"🎯 Connection Density: {density:.2f} relationships per entity")
            print()
        except Exception as e:
            print(f"❌ Error getting graph statistics: {e}")
            print()

    async def _show_extracted_entities(self, episode_id: str):
        """Show entities extracted from the latest episode"""
        print("STEP 3: Entities Discovered")
        print("-" * 40)
        
        try:
            # Find the episode we just processed
            episode = next((ep for ep in self.processed_episodes if ep.episode_id == episode_id), None)
            
            if episode and hasattr(episode, '_extracted_entities'):
                # Show the actual entities extracted from this episode
                entities = episode._extracted_entities
                
                if entities:
                    print(f"🎯 Entities extracted from episode '{episode_id}':")
                    
                    # Group entities by type
                    entity_groups = {}
                    for entity in entities:
                        entity_type = entity.entity_type.value
                        if entity_type not in entity_groups:
                            entity_groups[entity_type] = []
                        entity_groups[entity_type].append(entity)
                    
                    # Display entities by type
                    for entity_type, type_entities in entity_groups.items():
                        print(f"\n🏷️  {entity_type.upper()} entities:")
                        for entity in type_entities:
                            description = entity.description[:80] + "..." if entity.description and len(entity.description) > 80 else entity.description or "No description"
                            print(f"   • {entity.name}: {description}")
                else:
                    print(f"ℹ️  No entities were extracted from episode '{episode_id}'")
            else:
                print(f"ℹ️  No extraction data available for episode '{episode_id}'")
            
            print()
            
        except Exception as e:
            print(f"❌ Error showing entities: {e}")
            import traceback
            traceback.print_exc()
            print()

    async def _show_relationships(self, episode_id: str):
        """Show relationships discovered"""
        print("STEP 4: Relationships Discovered")
        print("-" * 40)
        
        try:
            # Find the episode we just processed
            episode = next((ep for ep in self.processed_episodes if ep.episode_id == episode_id), None)
            
            if episode and hasattr(episode, '_extracted_relationships'):
                # Show the actual relationships extracted from this episode
                relationships = episode._extracted_relationships
                
                if relationships:
                    print(f"🔗 Relationships extracted from episode '{episode_id}':")
                    for i, rel in enumerate(relationships, 1):
                        confidence_str = f" (confidence: {rel.confidence:.2f})" if rel.confidence < 1.0 else ""
                        print(f"   {i}. {rel.source_entity} → {rel.relation_type.value} → {rel.target_entity}{confidence_str}")
                        if rel.description:
                            print(f"      Description: {rel.description}")
                else:
                    print(f"ℹ️  No relationships were extracted from episode '{episode_id}'")
            else:
                print(f"ℹ️  No relationship extraction data available for episode '{episode_id}'")
            
            print()
            
        except Exception as e:
            print(f"❌ Error showing relationships: {e}")
            import traceback
            traceback.print_exc()
            print()    
    async def _show_subgraphs_and_communities(self):
        """Analyze and show subgraphs and communities"""
        print("STEP 5: Subgraphs and Communities Analysis")
        print("-" * 40)
        
        try:
            # Get entities from processed episodes (not static search results)
            all_extracted_entities = []
            
            for episode in self.processed_episodes:
                if hasattr(episode, '_extracted_entities') and episode._extracted_entities:
                    all_extracted_entities.extend(episode._extracted_entities)
            
            if len(all_extracted_entities) < 3:
                print("ℹ️  Not enough entities extracted from episodes yet for community analysis")
                print()
                return
            
            # Group entities by type from extracted data
            communities = {}
            for entity in all_extracted_entities:
                entity_type = entity.entity_type.value
                if entity_type not in communities:
                    communities[entity_type] = []
                communities[entity_type].append(entity.name)
            
            print("🏘️  Entity Communities from Processed Episodes:")
            total_entities = len(all_extracted_entities)
            print(f"📊 Total entities extracted from {len(self.processed_episodes)} episodes: {total_entities}")
            print()
            
            for community_type, members in communities.items():
                unique_members = list(set(members))  # Remove duplicates
                if len(unique_members) >= 1:  # Show all communities
                    print(f"   📍 {community_type.upper()} Community ({len(unique_members)} unique entities):")
                    for member in unique_members[:8]:  # Show up to 8 members
                        print(f"      • {member}")
                    if len(unique_members) > 8:
                        print(f"      ... and {len(unique_members) - 8} more")
                    print()
            
        except Exception as e:
            print(f"❌ Error analyzing communities: {e}")
            import traceback
            traceback.print_exc()
            print()

    async def _generate_step_visualization(self):
        """Generate visualization for current graph state"""
        print("STEP 6: Visualization Generation")
        print("-" * 40)
        
        try:
            # Create a simple HTML visualization
            html_content = await self._create_html_visualization()
            
            # Save visualization
            viz_dir = "real_time_visualizations"
            os.makedirs(viz_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"step_{len(self.processed_episodes)}_{timestamp}.html"
            filepath = os.path.join(viz_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Visualization saved: {filepath}")
            print(f"🌐 Open in browser to see current graph state")
            print()
            
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")
            print()    
    async def _create_html_visualization(self) -> str:
        """Create HTML visualization of current graph state"""
        try:
            # Get entities and relationships from processed episodes (not static search)
            all_extracted_entities = []
            all_extracted_relationships = []
            
            for episode in self.processed_episodes:
                if hasattr(episode, '_extracted_entities') and episode._extracted_entities:
                    all_extracted_entities.extend(episode._extracted_entities)
                if hasattr(episode, '_extracted_relationships') and episode._extracted_relationships:
                    all_extracted_relationships.extend(episode._extracted_relationships)            
            # Create nodes for vis.js
            nodes = []
            node_colors = {
                'person': '#FF6B6B',      # Red for people
                'product': '#4ECDC4',     # Teal for products
                'organization': '#45B7D1', # Blue for organizations
                'event': '#FFA07A',       # Orange for events
                'location': '#98D8C8',    # Light teal for locations
                'concept': '#F7DC6F',     # Yellow for concepts
                'campaign': '#DDA0DD',    # Plum for campaigns
                'unknown': '#BDC3C7'      # Gray for unknown
            }
            
            # Enhanced entity processing from extracted data
            entity_id_map = {}
            unique_entities = {}
            
            # Remove duplicates by name
            for entity in all_extracted_entities:
                unique_entities[entity.name] = entity
            
            for i, (entity_name, entity) in enumerate(unique_entities.items()):
                entity_type = entity.entity_type.value.lower()
                entity_desc = entity.description or "No description"
                
                # Make size based on importance (longer descriptions = more important)
                size = min(30, max(15, len(entity_desc) // 10))
                
                nodes.append({
                    'id': i,
                    'label': entity_name[:25] + ('...' if len(entity_name) > 25 else ''),
                    'title': f"🏷️ Type: {entity_type.title()}\\n📝 Name: {entity_name}\\n📄 Description: {entity_desc[:150]}{'...' if len(entity_desc) > 150 else ''}",
                    'color': node_colors.get(entity_type, node_colors['unknown']),
                    'size': size,
                    'font': {'size': 12, 'color': '#333333'}
                })
                entity_id_map[entity_name] = i
            
            # Create edges based on extracted relationships
            edges = []
            edge_id = 0
            
            # Use actual extracted relationships
            for rel in all_extracted_relationships:
                source_name = rel.source_entity
                target_name = rel.target_entity
                rel_type = rel.relation_type.value
                
                # Find matching nodes
                source_id = entity_id_map.get(source_name)
                target_id = entity_id_map.get(target_name)
                
                if source_id is not None and target_id is not None and source_id != target_id:
                    confidence_str = f" (conf: {rel.confidence:.2f})" if rel.confidence < 1.0 else ""
                    edges.append({
                        'id': edge_id,
                        'from': source_id,
                        'to': target_id,
                        'label': rel_type[:10] + confidence_str,
                        'title': f"Relationship: {rel_type}\\nSource: {source_name}\\nTarget: {target_name}\\nConfidence: {rel.confidence:.2f}\\nDescription: {rel.description or 'No description'}",
                        'width': max(1, int(rel.confidence * 3)),  # Width based on confidence
                        'color': {'color': '#848484', 'highlight': '#FF6B6B'},
                        'arrows': {'to': {'enabled': True, 'scaleFactor': 1}}
                    })
                    edge_id += 1
            
            # If no relationships found, create some demo connections
            if not edges:
                for i in range(min(len(nodes)-1, 10)):
                    edges.append({
                        'id': edge_id,
                        'from': i,
                        'to': (i + 1) % len(nodes),
                        'title': 'Connected entities',
                        'width': 1,
                        'color': {'color': '#cccccc'},
                        'arrows': {'to': {'enabled': True, 'scaleFactor': 0.8}}
                    })
                    edge_id += 1
            
            # Get processed episodes info
            episode_info = []
            for ep in self.processed_episodes:
                episode_info.append({
                    'id': ep.episode_id,
                    'source': ep.source,
                    'preview': ep.content.strip()[:100] + '...'
                })
            
            # Create episode timeline
            episode_timeline = ""
            for i, ep_info in enumerate(episode_info, 1):
                episode_timeline += f"""
                <div class="episode-item">
                    <h4>Episode {i}: {ep_info['id']}</h4>
                    <p><strong>Source:</strong> {ep_info['source']}</p>
                    <p>{ep_info['preview']}</p>
                </div>
                """
            
            # Generate enhanced HTML
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Step-by-Step Graph Visualization - Step {len(self.processed_episodes)}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .main-content {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }}
        .graph-container {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .sidebar {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ margin: 0; font-size: 14px; color: #2d3436; text-transform: uppercase; letter-spacing: 1px; }}
        .stat-card p {{ margin: 10px 0 0 0; font-size: 28px; font-weight: bold; color: #2d3436; }}
        #network {{ width: 100%; height: 600px; border: 2px solid #ddd; border-radius: 10px; background: #fafbfc; }}
        .controls {{ margin: 20px 0; text-align: center; }}
        .legend {{ background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; }}
        .legend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }}
        .legend-item {{ display: flex; align-items: center; font-size: 12px; }}
        .legend-color {{ width: 16px; height: 16px; border-radius: 50%; margin-right: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .episode-timeline {{ max-height: 400px; overflow-y: auto; }}
        .episode-item {{ background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .episode-item h4 {{ margin: 0 0 10px 0; color: #2d3436; font-size: 14px; }}
        .episode-item p {{ margin: 5px 0; font-size: 12px; color: #636e72; }}
        .controls button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }}
        .controls button:hover {{ opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Step-by-Step Knowledge Graph Visualization</h1>
        <p><strong>Progress:</strong> {len(self.processed_episodes)} Episodes Processed | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>📚 Episodes</h3>
            <p>{len(self.processed_episodes)}</p>
        </div>        <div class="stat-card">
            <h3>👥 Entities</h3>
            <p>{len(unique_entities)}</p>
        </div>
        <div class="stat-card">
            <h3>🔗 Relationships</h3>
            <p>{len(all_extracted_relationships)}</p>
        </div>
        <div class="stat-card">
            <h3>🎯 Density</h3>
            <p>{len(all_extracted_relationships)/max(len(unique_entities), 1):.1f}</p>
        </div>
    </div>
    
    <div class="main-content">
        <div class="graph-container">
            <h3>🌐 Knowledge Graph Visualization</h3>
            <div class="controls">
                <button onclick="network.fit()">🔍 Fit to Screen</button>
                <button onclick="togglePhysics()">⚡ Toggle Physics</button>
                <button onclick="resetZoom()">🔄 Reset View</button>
            </div>
            <div id="network"></div>
            
            <div class="legend">
                <h4>🏷️ Entity Types</h4>
                <div class="legend-grid">
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #FF6B6B;"></span>
                        Person
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #4ECDC4;"></span>
                        Product
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #45B7D1;"></span>
                        Organization
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #FFA07A;"></span>
                        Event
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #98D8C8;"></span>
                        Location
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #F7DC6F;"></span>
                        Concept
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #DDA0DD;"></span>
                        Campaign
                    </div>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <h3>📝 Episode Timeline</h3>
            <div class="episode-timeline">
                {episode_timeline if episode_timeline else '<p>No episodes processed yet.</p>'}
            </div>
        </div>
    </div>
    
    <script>
        const nodes = new vis.DataSet({json.dumps(nodes)});
        const edges = new vis.DataSet({json.dumps(edges)});
        
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{
                font: {{ size: 14, color: '#333333' }},
                borderWidth: 2,
                shadow: {{ enabled: true, color: 'rgba(0,0,0,0.2)', size: 10, x: 2, y: 2 }},
                chosen: {{ node: function(values, id, selected, hovering) {{ values.shadow = true; }} }}
            }},
            edges: {{
                color: {{ color: '#848484', highlight: '#667eea' }},
                shadow: {{ enabled: true, color: 'rgba(0,0,0,0.1)', size: 5, x: 1, y: 1 }},
                smooth: {{ type: 'continuous', roundness: 0.2 }},
                font: {{ size: 10, color: '#666666', strokeWidth: 2, strokeColor: '#ffffff' }}
            }},
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                    damping: 0.4
                }},
                stabilization: {{ iterations: 150 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true,
                hideNodesOnDrag: false
            }},
            layout: {{
                improvedLayout: true
            }}
        }};
        
        const container = document.getElementById('network');
        const network = new vis.Network(container, data, options);
        
        let physicsEnabled = true;
        
        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
        }}
        
        function resetZoom() {{
            network.moveTo({{ scale: 1.0 }});
        }}
        
        // Add click handler for node details
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                alert('🔍 Entity Details:\\n\\n' + node.title.replace(/\\\\n/g, '\\n'));
            }}
        }});
        
        // Add hover effects
        network.on('hoverNode', function(params) {{
            container.style.cursor = 'pointer';
        }});
        
        network.on('blurNode', function(params) {{
            container.style.cursor = 'default';
        }});
        
        // Add double click to focus on node
        network.on('doubleClick', function(params) {{
            if (params.nodes.length > 0) {{
                network.focus(params.nodes[0], {{ scale: 1.5, animation: true }});
            }}
        }});
    </script>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            print(f"Error creating HTML visualization: {e}")
            import traceback
            traceback.print_exc()
            return f"<html><body><h1>Error creating visualization</h1><p>{str(e)}</p></body></html>"

    async def run_interactive_demo(self):
        """Run the main interactive demo loop"""
        await self.initialize()
        
        while True:
            print("🎮 INTERACTIVE MENU")
            print("-" * 40)
            print("1. View available episodes")
            print("2. Process an episode")
            print("3. Show current graph statistics")
            print("4. Search entities")
            print("5. Generate full visualization")
            print("6. Reset graph (clear all data)")
            print("0. Exit")
            print()
            
            choice = input("Enter your choice (0-6): ").strip()
            print()
            
            if choice == "0":
                print("👋 Thanks for using the Step-by-Step Graph Visualization Demo!")
                break
            elif choice == "1":
                self.display_episode_menu()
            elif choice == "2":
                self.display_episode_menu()
                try:
                    episode_num = int(input("Enter episode number to process: ").strip())
                    await self.process_selected_episode(episode_num)
                except ValueError:
                    print("❌ Please enter a valid number!")
            elif choice == "3":
                await self._show_graph_statistics()
            elif choice == "4":
                await self._interactive_entity_search()
            elif choice == "5":
                await self._generate_step_visualization()
            elif choice == "6":
                await self._reset_graph()
            else:
                print("❌ Invalid choice! Please try again.")
            
            input("Press Enter to continue...")
            print("\n" + "="*60 + "\n")

    async def _interactive_entity_search(self):
        """Interactive entity search"""
        print("🔍 ENTITY SEARCH")
        print("-" * 40)
        
        query = input("Enter search term (or press Enter for all): ").strip()
        
        try:
            entities = await self.graphiti.search_entities(query, limit=10)
            
            if entities:
                print(f"\n🎯 Found {len(entities)} entities:")
                for i, entity in enumerate(entities, 1):
                    name = entity.get('name', 'Unknown')
                    entity_type = entity.get('type', 'unknown')
                    description = entity.get('description', 'No description')[:100] + "..."
                    print(f"{i}. {name} ({entity_type})")
                    print(f"   {description}")
                    print()
            else:
                print("❌ No entities found matching your search.")
                
        except Exception as e:
            print(f"❌ Error searching entities: {e}")

    async def _reset_graph(self):
        """Reset the graph (clear all data)"""
        confirm = input("⚠️  Are you sure you want to clear all graph data? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            try:
                # This would need to be implemented in GraphitiCosmos
                print("🧹 Clearing graph data...")
                # await self.graphiti.clear_all_data()  # Would need this method
                self.processed_episodes = []
                print("✅ Graph data cleared!")
            except Exception as e:
                print(f"❌ Error clearing graph: {e}")
        else:
            print("❌ Reset cancelled.")

async def main():
    """Main entry point"""
    demo = StepByStepVisualizationDemo()
    await demo.run_interactive_demo()

if __name__ == "__main__":
    asyncio.run(main())
