"""
Interactive Demo Script for Graphiti-Cosmos Integration
=====================================================

This script provides an interactive menu to test various Graphiti-Cosmos features:
- Add episodes with custom content
- Search entities and relationships
- Explore graph connections
- View graph statistics
- Import data from files
"""

import asyncio
import json
import os
import platform
import sys
import time
from datetime import datetime
from typing import Optional

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphiti_cosmos import GraphitiCosmos, Episode, GraphitiCosmosConfig

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class GraphitiInteractiveDemo:
    """Interactive demo for Graphiti-Cosmos features"""
    
    def __init__(self):
        self.graphiti: Optional[GraphitiCosmos] = None
        self.is_connected = False
        
    async def initialize(self):
        """Initialize Graphiti-Cosmos connection"""
        try:
            print("🔌 Connecting to Graphiti-Cosmos...")
            self.graphiti = GraphitiCosmos()
            await self.graphiti.initialize()
            self.is_connected = True
            print("✅ Connected successfully!")
            
            # Show initial stats
            stats = await self.graphiti.get_graph_stats()
            print(f"📊 Current graph: {stats['entities']} entities, {stats['relationships']} relationships, {stats['episodes']} episodes")
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            if self.graphiti:
                try:
                    await self.graphiti.close()
                except:
                    pass  # Ignore cleanup errors during failed initialization
                self.graphiti = None
            return False
        return True
    
    async def cleanup(self):
        """Clean up connections properly"""
        if self.graphiti:
            try:
                await self.graphiti.close()
                print("🔌 Disconnected from Graphiti-Cosmos")
            except Exception as e:
                print(f"⚠️  Warning during cleanup: {e}")
        self.is_connected = False
    
    def display_menu(self):
        """Display the interactive menu"""
        print("\n" + "="*60)
        print("🧠 GRAPHITI-COSMOS INTERACTIVE DEMO")
        print("="*60)
        print("1️⃣  Add New Episode")
        print("2️⃣  Search Entities")  
        print("3️⃣  Search Relationships")
        print("4️⃣  Explore Entity Connections")
        print("5️⃣  View Graph Statistics")
        print("6️⃣  Load Sample Data")
        print("7️⃣  Quick Test Scenarios")
        print("8️⃣  Clear Screen")
        print("9️⃣  Show Recent Episodes")
        print("0️⃣  Exit")
        print("="*60)
    
    async def add_episode(self):
        """Interactive episode addition"""
        print("\n📝 ADD NEW EPISODE")
        print("-" * 40)
        
        content = input("Enter episode content (or 'sample' for pre-made): ").strip()
        
        if content.lower() == 'sample':
            samples = [
                "Tesla announced a new autonomous driving feature. Elon Musk collaborated with the engineering team to enhance safety protocols.",
                "Dr. Sarah Chen published research on quantum computing at MIT. She worked with Professor David Kim on quantum error correction.",
                "OpenAI released GPT-5 with improved reasoning capabilities. The research team focused on alignment and safety features.",
                "Microsoft acquired GitHub for developer collaboration. Satya Nadella emphasized the importance of open source development.",
                "Apple introduced the M4 chip with enhanced AI processing. The silicon team optimized it for machine learning workloads."
            ]
            content = samples[len(samples) % 5]  # Cycle through samples
            print(f"Using sample: {content}")
        
        if not content:
            print("❌ Content cannot be empty")
            return
        
        # Generate unique episode ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        episode_id = f"demo_{timestamp}_{int(time.time() % 10000)}"
        
        try:
            episode = Episode(content=content, episode_id=episode_id)
            print(f"🔄 Processing episode: {episode_id}")
            
            result = await self.graphiti.add_episode(episode)
            print(f"✅ Episode processed successfully!")
            print(f"📊 Result: {result}")
            
        except Exception as e:
            print(f"❌ Error adding episode: {e}")
    
    async def search_entities(self):
        """Interactive entity search"""
        print("\n🔍 SEARCH ENTITIES")
        print("-" * 40)
        
        query = input("Enter search term (or 'examples' to see suggestions): ").strip()
        
        if query.lower() == 'examples':
            print("💡 Try searching for:")
            print("  - Person names: Elon Musk, Sarah Chen, David Kim")
            print("  - Companies: Tesla, Microsoft, OpenAI, Apple")
            print("  - Technologies: GPT, quantum computing, autonomous driving")
            return
        
        if not query:
            print("❌ Search term cannot be empty")
            return
        
        try:
            results = await self.graphiti.search_entities(query)
            print(f"🎯 Found {len(results)} entities matching '{query}':")
            
            for i, result in enumerate(results[:10]):  # Show first 10 results
                print(f"  {i+1}. {result['name']} ({result['type']})")
                print(f"     Description: {result['description']}")
                print()
            
            if len(results) > 10:
                print(f"... and {len(results) - 10} more results")
                
        except Exception as e:
            print(f"❌ Error searching entities: {e}")
    
    async def search_relationships(self):
        """Interactive relationship search"""
        print("\n🔗 SEARCH RELATIONSHIPS")
        print("-" * 40)
        
        query = input("Enter relationship term (or 'examples' for suggestions): ").strip()
        
        if query.lower() == 'examples':
            print("💡 Try searching for:")
            print("  - Actions: works, collaborates, develops, published")
            print("  - Connections: at, with, for, on")
            print("  - Types: CEO, researcher, engineer, scientist")
            return
        
        if not query:
            print("❌ Search term cannot be empty")
            return
        
        try:
            results = await self.graphiti.search_relationships(query)
            print(f"🔗 Found {len(results)} relationships matching '{query}':")
            
            for i, result in enumerate(results[:10]):
                print(f"  {i+1}. {result['source']} → {result['target']}")
                print(f"     Relationship: {result['relationship']}")
                if 'description' in result['properties']:
                    print(f"     Description: {result['properties']['description']}")
                print()
            
            if len(results) > 10:
                print(f"... and {len(results) - 10} more results")
                
        except Exception as e:
            print(f"❌ Error searching relationships: {e}")    
    async def explore_connections(self):
        """Interactive connection exploration"""
        print("\n🕸️  EXPLORE ENTITY CONNECTIONS")
        print("-" * 40)
        
        entity_name = input("Enter entity name to explore: ").strip()
        
        if not entity_name:
            print("❌ Entity name cannot be empty")
            return
        
        try:
            neighbors = await self.graphiti.get_entity_neighbors(entity_name)
            print(f"🌐 Connections for '{entity_name}':")
            
            if neighbors and isinstance(neighbors, dict):
                paths = neighbors.get('paths', [])
                entities = neighbors.get('entities', [])
                relationships = neighbors.get('relationships', [])
                
                if paths:
                    print(f"  Found {len(paths)} connection paths:")
                    
                    # Safely handle path display
                    for i, path in enumerate(paths[:5], 1):  # Show first 5 paths
                        try:
                            # Create a simplified representation
                            if isinstance(path, dict):
                                path_repr = f"Path data: {str(path)[:100]}..."
                            elif isinstance(path, list):
                                path_repr = f"Path with {len(path)} steps"
                            else:
                                path_repr = str(path)[:100]
                            print(f"    {i}. {path_repr}")
                        except Exception:
                            print(f"    {i}. [Complex path structure]")
                            
                elif entities:
                    print(f"  Found {len(entities)} connected entities:")
                    for i, entity in enumerate(entities[:10], 1):  # Show first 10 entities
                        print(f"    {i}. {entity}")
                elif relationships:
                    print(f"  Found {len(relationships)} relationships:")
                    for i, rel in enumerate(relationships[:10], 1):  # Show first 10 relationships
                        print(f"    {i}. {rel}")
                else:
                    print("  No connections found")
                    print("  💡 Try searching for an entity first to find valid names")
                    print("  💡 Example entities to try: Tesla, OpenAI, Microsoft, Sarah, David")
            else:
                print("  No connections found")
                print("  💡 Try searching for an entity first to find valid names")
                
        except Exception as e:
            print(f"❌ Error exploring connections: {e}")
    
    async def view_statistics(self):
        """View comprehensive graph statistics"""
        print("\n📈 GRAPH STATISTICS")
        print("-" * 40)
        
        try:
            stats = await self.graphiti.get_graph_stats()
            print(f"📊 Graph Overview:")
            print(f"   Episodes: {stats['episodes']}")
            print(f"   Entities: {stats['entities']}")
            print(f"   Relationships: {stats['relationships']}")
            
            # Calculate some derived metrics
            if stats['episodes'] > 0:
                entities_per_episode = stats['entities'] / stats['episodes']
                relationships_per_episode = stats['relationships'] / stats['episodes']
                print(f"\n📋 Derived Metrics:")
                print(f"   Avg entities per episode: {entities_per_episode:.1f}")
                print(f"   Avg relationships per episode: {relationships_per_episode:.1f}")
                
                if stats['entities'] > 0:
                    connectivity = stats['relationships'] / stats['entities']
                    print(f"   Graph connectivity ratio: {connectivity:.2f}")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    async def load_sample_data(self):
        """Load sample data from files"""
        print("\n📁 LOAD SAMPLE DATA")
        print("-" * 40)
        print("Available options:")
        print("1. Load Manybirds product data")
        print("2. Load predefined test scenarios")
        print("3. Generate synthetic episodes")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            await self._load_manybirds_data()
        elif choice == "2":
            await self._load_test_scenarios()
        elif choice == "3":
            await self._generate_synthetic_episodes()
        else:
            print("❌ Invalid choice")
    
    async def _load_manybirds_data(self):
        """Load Manybirds product data"""
        try:
            import json
            with open("manybirds_products.json", "r") as f:
                products = json.load(f)
            
            print(f"📦 Found {len(products)} products. Loading first 3...")
            
            for i, product in enumerate(products[:3]):
                content = f"Manybirds offers {product['name']} in the {product['category']} category. {product['description']} It's priced at ${product['price']}."
                episode_id = f"manybirds_product_{product['id']}_{int(time.time())}"
                
                episode = Episode(content=content, episode_id=episode_id)
                await self.graphiti.add_episode(episode)
                print(f"  ✅ Loaded: {product['name']}")
            
            print("✅ Sample Manybirds data loaded successfully!")
            
        except FileNotFoundError:
            print("❌ manybirds_products.json not found")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    async def _load_test_scenarios(self):
        """Load predefined test scenarios"""
        scenarios = [
            "Amazon launched a new cloud service called AWS Lambda. Jeff Bezos worked with the cloud team to revolutionize serverless computing.",
            "Netflix developed an AI recommendation system. Reed Hastings collaborated with data scientists to improve user engagement.",
            "Google introduced Bard AI assistant. Sundar Pichai emphasized responsible AI development with the research team."
        ]
        
        print(f"🎭 Loading {len(scenarios)} test scenarios...")
        
        for i, content in enumerate(scenarios):
            episode_id = f"test_scenario_{i+1}_{int(time.time())}"
            episode = Episode(content=content, episode_id=episode_id)
            await self.graphiti.add_episode(episode)
            print(f"  ✅ Scenario {i+1} loaded")
        
        print("✅ Test scenarios loaded successfully!")
    
    async def _generate_synthetic_episodes(self):
        """Generate synthetic episodes"""
        print("🤖 Generating synthetic episodes...")
        
        people = ["Alice Johnson", "Bob Smith", "Carol Wilson", "David Brown"]
        companies = ["TechCorp", "InnovateLabs", "FutureSoft", "DataDyne"]
        actions = ["developed", "launched", "researched", "collaborated on"]
        projects = ["AI platform", "mobile app", "data analytics tool", "blockchain solution"]
        
        import random
        
        for i in range(3):
            person = random.choice(people)
            company = random.choice(companies)
            action = random.choice(actions)
            project = random.choice(projects)
            
            content = f"{person} at {company} {action} a new {project}. The team focused on innovation and user experience."
            episode_id = f"synthetic_{i+1}_{int(time.time())}"
            
            episode = Episode(content=content, episode_id=episode_id)
            await self.graphiti.add_episode(episode)
            print(f"  ✅ Generated: {person} - {project}")
        
        print("✅ Synthetic episodes generated successfully!")
    
    async def quick_test_scenarios(self):
        """Run quick test scenarios"""
        print("\n⚡ QUICK TEST SCENARIOS")
        print("-" * 40)
        print("1. Add sample episode + search entities")
        print("2. Test relationship discovery")
        print("3. Full workflow demo")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            await self._quick_test_entities()
        elif choice == "2":
            await self._quick_test_relationships()
        elif choice == "3":
            await self._full_workflow_demo()
        else:
            print("❌ Invalid choice")
    
    async def _quick_test_entities(self):
        """Quick entity test"""
        print("🧪 Quick Entity Test")
        content = "Dr. Marie Curie conducted groundbreaking research on radioactivity at the University of Paris. She collaborated with Pierre Curie on Nobel Prize-winning experiments."
        episode_id = f"quick_test_entities_{int(time.time())}"
        
        episode = Episode(content=content, episode_id=episode_id)
        await self.graphiti.add_episode(episode)
        print("✅ Episode added")
        
        # Search for entities
        results = await self.graphiti.search_entities("Marie Curie")
        print(f"🔍 Found {len(results)} entities for 'Marie Curie'")
        for result in results[:3]:
            print(f"  • {result['name']} ({result['type']})")
    
    async def _quick_test_relationships(self):
        """Quick relationship test"""
        print("🧪 Quick Relationship Test")
        
        results = await self.graphiti.search_relationships("collabor")
        print(f"🔗 Found {len(results)} relationships with 'collabor'")
        for result in results[:3]:
            print(f"  • {result['source']} → {result['target']} ({result['relationship']})")
    
    async def _full_workflow_demo(self):
        """Full workflow demonstration"""
        print("🧪 Full Workflow Demo")
        
        # Add episode
        content = "SpaceX successfully launched Starship with Elon Musk overseeing the mission. The engineering team achieved a breakthrough in reusable rocket technology."
        episode_id = f"workflow_demo_{int(time.time())}"
        
        episode = Episode(content=content, episode_id=episode_id)
        await self.graphiti.add_episode(episode)
        print("✅ Episode added")
        
        # Search entities
        results = await self.graphiti.search_entities("SpaceX")
        print(f"🔍 Entity search: {len(results)} results")
        
        # Search relationships
        results = await self.graphiti.search_relationships("launch")
        print(f"🔗 Relationship search: {len(results)} results")
        
        # Get stats
        stats = await self.graphiti.get_graph_stats()
        print(f"📊 Updated stats: {stats['entities']} entities, {stats['relationships']} relationships")
    
    async def show_recent_episodes(self):
        """Show recent episodes (simplified version)"""
        print("\n📚 RECENT EPISODES")
        print("-" * 40)
        print("ℹ️  This is a simplified view. Recent episodes are tracked in the graph statistics.")
        await self.view_statistics()
    
    def clear_screen(self):
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    async def run(self):
        """Main interactive loop"""
        self.clear_screen()
        print("🚀 Starting Graphiti-Cosmos Interactive Demo...")
        
        if not await self.initialize():
            return
        
        try:
            while True:
                self.display_menu()
                choice = input("\n👉 Enter your choice: ").strip()
                
                if choice == "1":
                    await self.add_episode()
                elif choice == "2":
                    await self.search_entities()
                elif choice == "3":
                    await self.search_relationships()
                elif choice == "4":
                    await self.explore_connections()
                elif choice == "5":
                    await self.view_statistics()
                elif choice == "6":
                    await self.load_sample_data()
                elif choice == "7":
                    await self.quick_test_scenarios()
                elif choice == "8":
                    self.clear_screen()
                elif choice == "9":
                    await self.show_recent_episodes()
                elif choice == "0":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\n📝 Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    demo = GraphitiInteractiveDemo()
    asyncio.run(demo.run())
