#!/usr/bin/env python3
"""
Quick Demo of Enhanced Graph Explorer
Shows the LLM-powered features in action
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from demos.graph_explorer import GraphExplorer

async def demo_enhanced_features():
    """Demonstrate the enhanced LLM features"""
    print("🚀 ENHANCED GRAPH EXPLORER DEMO")
    print("=" * 50)
    
    explorer = GraphExplorer()
    await explorer.initialize()
    
    # Demo queries showcasing LLM enhancement
    demo_queries = [
        "Find technology companies in our graph",
        "Show me people who work for sustainable organizations", 
        "What products are related to environmental impact?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Demo Query {i}: '{query}'")
        print("-" * 50)
        
        # Show LLM interpretation
        interpretation = await explorer._interpret_natural_language_query(query)
        print(f"🧠 LLM Analysis:")
        print(f"   Intent: {interpretation['intent']}")
        print(f"   Strategy: {interpretation['strategy']}")
        print(f"   Terms: {', '.join(interpretation['search_terms'])}")
        print(f"   Confidence: {interpretation['confidence']:.2f}")
        print(f"   Explanation: {interpretation['explanation']}")
        
        # Show search results
        search_terms = interpretation['search_terms'][:2]
        entities = []
        
        for term in search_terms:
            results = await explorer.graphiti.search_entities(term, limit=3)
            entities.extend(results)
        
        # Remove duplicates
        unique_entities = {}
        for entity in entities:
            entity_id = entity.get('id') or entity.get('name')
            if entity_id not in unique_entities:
                unique_entities[entity_id] = entity
        
        entities = list(unique_entities.values())
        
        print(f"\n📊 Results: {len(entities)} entities found")
        for j, entity in enumerate(entities[:3], 1):
            name = entity.get('name', 'Unknown')
            entity_type = entity.get('type', entity.get('entity_type', 'Unknown'))
            description = entity.get('description', 'No description')
            print(f"   {j}. {name} ({entity_type})")
            print(f"      {description[:60]}{'...' if len(description) > 60 else ''}")
        
        # Show LLM enhancement
        if entities:
            enhanced = await explorer._enhance_search_results_with_llm(query, entities, interpretation)
            if hasattr(explorer, '_last_enhancement'):
                enhancement = explorer._last_enhancement
                print(f"\n💡 LLM Insights: {enhancement.get('insights', 'No insights')}")
                
                follow_ups = enhancement.get('follow_up_queries', [])
                if follow_ups:
                    print(f"🔄 Suggested follow-ups:")
                    for k, suggestion in enumerate(follow_ups[:2], 1):
                        print(f"   {k}. {suggestion}")
        
        print()
    
    print("✅ Demo completed! The graph explorer is now fully LLM-powered.")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_features())
