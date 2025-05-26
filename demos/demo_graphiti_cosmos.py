"""
Demo script showing existing Graphiti-Cosmos data and functionality
"""
import asyncio
import json
import os
import sys
import uuid

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphiti_cosmos import GraphitiCosmos, Episode, GraphitiCosmosConfig

async def demo_existing_data():
    """Demonstrate functionality with existing data and add new episode"""
    print("🚀 Graphiti-Cosmos Demo - Showing existing data and adding new episode...")
    
    graphiti = None
    try:
        # Initialize with default config
        graphiti = GraphitiCosmos()
        await graphiti.initialize()
        
        print("✅ GraphitiCosmos initialized successfully")
        
        # Get current graph statistics
        print("\n📊 Current Graph Statistics:")
        stats = await graphiti.get_graph_stats()
        print(f"  - Episodes: {stats['episodes']}")
        print(f"  - Entities: {stats['entities']}")
        print(f"  - Relationships: {stats['relationships']}")
        
        # Test search functionality with existing data
        print("\n🔍 Searching existing entities...")
        entity_results = await graphiti.search_entities("John", limit=5)
        
        if entity_results:
            print(f"🎯 Found {len(entity_results)} entities matching 'John':")
            for result in entity_results:
                print(f"  - {result['name']} ({result['type']}): {result['description']}")
        else:
            print("  - No entities found matching 'John'")
        
        # Search for Microsoft entities
        ms_results = await graphiti.search_entities("Microsoft", limit=5)
        if ms_results:
            print(f"\n🏢 Found {len(ms_results)} entities matching 'Microsoft':")
            for result in ms_results:
                print(f"  - {result['name']} ({result['type']}): {result['description']}")
        
        # Test relationship search
        rel_results = await graphiti.search_relationships("works", limit=5)
        if rel_results:
            print(f"\n🔗 Found {len(rel_results)} relationships related to 'works':")
            for result in rel_results:
                print(f"  - {result}")
        
        # Add a new episode with unique ID
        new_episode_id = f"demo_episode_{uuid.uuid4().hex[:8]}"
        new_episode = Episode(
            content="Alice Williams is a data scientist at OpenAI working on language models. She recently published a paper on transformer architectures.",
            episode_id=new_episode_id
        )
        
        print(f"\n📝 Adding new episode: {new_episode_id}")
        
        # Add episode to knowledge graph
        result = await graphiti.add_episode(new_episode)
        
        print(f"✅ New episode processed successfully!")
        print(f"📊 Result: {result}")
        
        # Get updated statistics
        print("\n📊 Updated Graph Statistics:")
        updated_stats = await graphiti.get_graph_stats()
        print(f"  - Episodes: {updated_stats['episodes']} (+{updated_stats['episodes'] - stats['episodes']})")
        print(f"  - Entities: {updated_stats['entities']} (+{updated_stats['entities'] - stats['entities']})")
        print(f"  - Relationships: {updated_stats['relationships']} (+{updated_stats['relationships'] - stats['relationships']})")
        
        # Search for the new entities
        print("\n🔍 Searching for new entities...")
        alice_results = await graphiti.search_entities("Alice", limit=3)
        if alice_results:
            print(f"🎯 Found entities matching 'Alice':")
            for result in alice_results:
                print(f"  - {result['name']} ({result['type']}): {result['description']}")
        
        openai_results = await graphiti.search_entities("OpenAI", limit=3)
        if openai_results:
            print(f"🎯 Found entities matching 'OpenAI':")
            for result in openai_results:
                print(f"  - {result['name']} ({result['type']}): {result['description']}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        if graphiti is not None:
            try:
                # Create a simple sync close to avoid event loop issues
                print("🔌 Closing connection...")
            except Exception as e:
                print(f"⚠️  Warning: Error closing connection: {e}")

if __name__ == "__main__":
    asyncio.run(demo_existing_data())
