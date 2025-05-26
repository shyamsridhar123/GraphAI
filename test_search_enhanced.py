#!/usr/bin/env python3
"""
Enhanced test script for validating search functionality fixes in Graphiti-Cosmos
"""

import asyncio
import sys
import os
import platform

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graphiti_cosmos import GraphitiCosmos, Episode

async def test_search_functionality():
    """Test the search functionality after fixes"""
    print("🧪 Testing Graphiti-Cosmos Search Functionality (Enhanced)")
    print("=" * 60)
    
    # Initialize the system
    graphiti = GraphitiCosmos()
    
    try:
        await graphiti.initialize()
        print("✅ Successfully initialized Graphiti-Cosmos")
        
        # Test 1: Add some test episodes first
        print("\n📝 Adding test episodes...")
        episodes = [
            Episode(
                content="Microsoft is a technology company based in Redmond, Washington. It develops software and cloud services.",
                episode_id="test_001",
                source="test"
            ),
            Episode(
                content="Alice Johnson works as a software engineer at Microsoft. She specializes in artificial intelligence.",
                episode_id="test_002", 
                source="test"
            ),
            Episode(
                content="The Azure cloud platform is Microsoft's primary cloud computing service offering.",
                episode_id="test_003",
                source="test"
            )
        ]
        
        for episode in episodes:
            try:
                await graphiti.add_episode(episode)
                print(f"  ✅ Added episode: {episode.episode_id}")
            except Exception as e:
                print(f"  ❌ Failed to add episode {episode.episode_id}: {e}")
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Test 2: Entity Search
        print("\n🔍 Testing Entity Search...")
        try:
            entities = await graphiti.search_entities("Microsoft", limit=5)
            print(f"  Found {len(entities)} entities for 'Microsoft':")
            for entity in entities:
                print(f"    - {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
        except Exception as e:
            print(f"  ❌ Entity search failed: {e}")
        
        # Test 3: Relationship Search
        print("\n🔗 Testing Relationship Search...")
        try:
            relationships = await graphiti.search_relationships("works", limit=5)
            print(f"  Found {len(relationships)} relationships for 'works':")
            for rel in relationships:
                print(f"    - {rel.get('source', 'N/A')} → {rel.get('relationship', 'N/A')} → {rel.get('target', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Relationship search failed: {e}")
        
        # Test 4: Entity Neighbors
        print("\n👥 Testing Entity Neighbors...")
        try:
            neighbors = await graphiti.get_entity_neighbors("Microsoft", max_hops=1)
            print(f"  Found neighbors for 'Microsoft':")
            print(f"    - Center: {neighbors.get('center_entity', 'N/A')}")
            print(f"    - Connected entities: {len(neighbors.get('entities', []))}")
            print(f"    - Relationships: {len(neighbors.get('relationships', []))}")
            
            for entity in neighbors.get('entities', [])[:3]:  # Show first 3
                print(f"      • {entity}")
        except Exception as e:
            print(f"  ❌ Entity neighbors search failed: {e}")
        
        # Test 5: General Search
        print("\n🔍 Testing General Search...")
        try:
            search_results = await graphiti.search("Alice", limit=5)
            print(f"  Found {len(search_results)} results for 'Alice':")
            for result in search_results:
                print(f"    - {result.get('type', 'N/A')}: {result.get('name', 'N/A')}")
        except Exception as e:
            print(f"  ❌ General search failed: {e}")
        
        # Test 6: Graph Statistics
        print("\n📊 Testing Graph Statistics...")
        try:
            stats = await graphiti.get_graph_stats()
            print("  Graph Statistics:")
            for key, value in stats.items():
                print(f"    - {key.title()}: {value}")
        except Exception as e:
            print(f"  ❌ Graph stats failed: {e}")
        
        print("\n✅ Search functionality testing completed!")
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            await graphiti.close()
            print("🔌 Successfully closed Graphiti-Cosmos client")
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {e}")


async def main():
    """Main test function"""
    try:
        await test_search_functionality()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting Enhanced Graphiti-Cosmos Search Tests")
    asyncio.run(main())
