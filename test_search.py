#!/usr/bin/env python3
"""
Quick test script to verify search functionality
"""

import asyncio
import os
import sys
import platform

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graphiti_cosmos import GraphitiCosmos

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_search():
    """Test the search functionality"""
    print("🧪 Testing Graphiti-Cosmos Search Functionality")
    print("=" * 50)
    
    # Initialize
    graphiti = GraphitiCosmos()
    
    try:
        await graphiti.initialize()
        print("✅ Connected successfully!")
        
        # Test entity search
        print("\n🔍 Testing entity search...")
        entity_results = await graphiti.search_entities("sarah", limit=5)
        print(f"Entity search results: {len(entity_results)} found")
        for i, entity in enumerate(entity_results, 1):
            print(f"  {i}. {entity['name']} ({entity['type']}) - {entity['description'][:50]}...")
        
        # Test relationship search
        print("\n🔗 Testing relationship search...")
        rel_results = await graphiti.search_relationships("works", limit=5)
        print(f"Relationship search results: {len(rel_results)} found")
        for i, rel in enumerate(rel_results, 1):
            print(f"  {i}. {rel['source']} → {rel['target']} ({rel['relationship']})")
        
        # Test entity neighbors
        if entity_results:
            print("\n🕸️ Testing entity neighbors...")
            test_entity = entity_results[0]['name']
            neighbors = await graphiti.get_entity_neighbors(test_entity)
            print(f"Neighbors for '{test_entity}': {len(neighbors['entities'])} entities, {len(neighbors['relationships'])} relationships")
            
            if neighbors['entities']:
                print("  Connected entities:")
                for i, entity in enumerate(neighbors['entities'][:5], 1):
                    print(f"    {i}. {entity}")
        
        print("\n✅ Search tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(test_search())
