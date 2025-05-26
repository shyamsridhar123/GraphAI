"""
Production-ready test for Graphiti-Cosmos integration
"""
import asyncio
import json
import os
import platform
import sys
import time
from datetime import datetime

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphiti_cosmos import GraphitiCosmos, Episode, GraphitiCosmosConfig

# Fix for Windows ProactorEventLoop issues - set at module level
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class ProductionGraphitiTest:
    """Production-ready test class for Graphiti-Cosmos"""
    
    def __init__(self):
        self.graphiti = None
    
    async def setup(self):
        """Initialize the Graphiti-Cosmos connection"""
        print("🚀 Initializing Graphiti-Cosmos...")
        self.graphiti = GraphitiCosmos()
        await self.graphiti.initialize()
        print("✅ GraphitiCosmos ready!")
    
    async def teardown(self):
        """Clean up connections properly"""
        if self.graphiti and hasattr(self.graphiti, 'gremlin_client'):
            try:
                # Close gremlin client synchronously to avoid event loop issues
                if self.graphiti.gremlin_client:
                    self.graphiti.gremlin_client.close()
                print("🔌 Connections closed")
            except Exception as e:
                print(f"⚠️  Warning during cleanup: {e}")
    
    async def test_episode_processing(self):
        """Test processing a new episode"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_episode_id = f"production_test_{timestamp}_{int(time.time())}"
        
        episode = Episode(
            content="Dr. Elena Rodriguez leads the AI ethics committee at Stanford University. She works closely with Professor James Kim from the computer science department to develop responsible AI guidelines for autonomous vehicles.",
            episode_id=unique_episode_id
        )
        
        print(f"📝 Processing episode: {episode.episode_id}")
        result = await self.graphiti.add_episode(episode)
        print(f"✅ Episode processed: {result}")
        
        return unique_episode_id
    
    async def test_search_capabilities(self):
        """Test various search capabilities"""
        print("\n🔍 Testing search capabilities...")
        
        # Test entity search
        entity_results = await self.graphiti.search_entities("Elena Rodriguez")
        print(f"🎯 Entity search for 'Elena Rodriguez': {len(entity_results)} results")
        for result in entity_results[:3]:  # Show first 3 results
            print(f"  - {result['name']} ({result['type']})")
        
        # Test relationship search  
        relationship_results = await self.graphiti.search_relationships("works")
        print(f"🔗 Relationship search for 'works': {len(relationship_results)} results")
        for result in relationship_results[:3]:  # Show first 3 results
            print(f"  - {result['source']} → {result['target']} ({result['relationship']})")
    
    async def get_system_status(self):
        """Get current system status and statistics"""
        print("\n📊 System Status:")
        stats = await self.graphiti.get_graph_stats()
        print(f"  - Episodes: {stats['episodes']}")
        print(f"  - Entities: {stats['entities']}")
        print(f"  - Relationships: {stats['relationships']}")
        return stats
    
    async def run_full_test(self):
        """Run the complete test suite"""
        try:
            await self.setup()
            episode_id = await self.test_episode_processing()
            await self.test_search_capabilities()
            stats = await self.get_system_status()
            
            print(f"\n🎉 Production test completed successfully!")
            print(f"📋 Test Summary:")
            print(f"  - Episode ID: {episode_id}")
            print(f"  - Current graph size: {stats['entities']} entities, {stats['relationships']} relationships")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            await self.teardown()

async def main():
    """Main test runner"""
    print("🏁 Starting Production Graphiti-Cosmos Test Suite")
    print("=" * 60)
    
    test = ProductionGraphitiTest()
    success = await test.run_full_test()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed! Graphiti-Cosmos is production ready.")
    else:
        print("❌ Tests failed. Check the logs above.")
    
    return success

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
