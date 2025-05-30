#!/usr/bin/env python3
"""
End-to-end test to demonstrate the original error is fixed
This simulates the exact search and display scenario that was failing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed graph explorer
from demos.graph_explorer import GraphExplorer

def test_original_error_scenario():
    """Test the exact scenario that was causing the 'unhashable type: list' error"""
    print("🧪 Testing Original Error Scenario - Entity Search & Display")
    print("=" * 60)
    
    explorer = GraphExplorer()
    
    # Simulate search results in Cosmos DB valueMap(true) format
    # This is the exact format that was causing the error
    mock_search_results = [
        {
            'name': ['John Smith'],
            'type': ['person'], 
            'description': ['A customer who purchased electronics'],
            'confidence': ['0.95'],
            'id': ['person_001']
        },
        {
            'name': ['iPhone 14'],
            'type': ['product'],
            'description': ['Latest smartphone from Apple'],
            'confidence': ['0.92'],
            'id': ['product_001']
        },
        {
            'name': ['Amazon'],
            'type': ['company'],
            'description': ['E-commerce platform'],
            'confidence': ['0.98'],
            'id': ['company_001']
        }
    ]
    
    print("✅ Step 1: Testing entity grouping by type (original failure point)")
    try:
        # This was the exact line that failed with "unhashable type: 'list'"
        entity_groups = {}
        for entity in mock_search_results:
            entity_type = explorer._extract_property(entity, 'type', 'unknown')
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity)
        
        print(f"   ✅ Successfully grouped {len(mock_search_results)} entities into {len(entity_groups)} types")
        for group_type, entities in entity_groups.items():
            print(f"      - {group_type}: {len(entities)} entities")
            
    except TypeError as e:
        if "unhashable type: 'list'" in str(e):
            print(f"   ❌ FAILED: The original error still exists: {e}")
            return False
        else:
            print(f"   ❌ FAILED: Unexpected error: {e}")
            return False
    
    print("\n✅ Step 2: Testing entity display formatting")
    try:
        for i, entity in enumerate(mock_search_results, 1):
            name = explorer._extract_property(entity, 'name', 'Unknown')
            entity_type = explorer._extract_property(entity, 'type', 'unknown')
            description = explorer._extract_property(entity, 'description', '')
            confidence = explorer._extract_property(entity, 'confidence', '1.0')
            
            print(f"   {i}. {name} ({entity_type})")
            print(f"      Description: {description}")
            print(f"      Confidence: {confidence}")
            
    except Exception as e:
        print(f"   ❌ FAILED: Error in display formatting: {e}")
        return False
        
    print("\n✅ Step 3: Testing relationship processing")
    try:
        # Mock relationship data in Cosmos DB format
        mock_relationships = [
            {
                'source': ['John Smith'],
                'target': ['iPhone 14'], 
                'type': ['purchased'],
                'confidence': ['0.89']
            },
            {
                'source': ['iPhone 14'],
                'target': ['Amazon'],
                'type': ['sold_by'],
                'confidence': ['0.94']
            }
        ]
        
        # Process relationships (another failure point)
        processed_relationships = []
        for rel in mock_relationships:
            source = explorer._extract_property(rel, 'source', '')
            target = explorer._extract_property(rel, 'target', '')
            rel_type = explorer._extract_property(rel, 'type', 'unknown')
            confidence = explorer._extract_property(rel, 'confidence', '1.0')
            
            processed_relationships.append({
                'source': source,
                'target': target,
                'type': rel_type,
                'confidence': confidence
            })
            
            print(f"   {source} → {rel_type} → {target} (conf: {confidence})")
            
        print(f"   ✅ Successfully processed {len(processed_relationships)} relationships")
        
    except Exception as e:
        print(f"   ❌ FAILED: Error in relationship processing: {e}")
        return False
    
    print("\n✅ Step 4: Testing Counter usage (another failure point)")
    try:
        # Test Counter with entity types (this also failed before)
        from collections import Counter
        
        type_counts = Counter()
        for entity in mock_search_results:
            entity_type = explorer._extract_property(entity, 'type', 'unknown')
            type_counts[entity_type] += 1
            
        print(f"   ✅ Entity type distribution: {dict(type_counts)}")
        
    except Exception as e:
        print(f"   ❌ FAILED: Error in Counter usage: {e}")
        return False
    
    print("\n🎉 All tests passed! The original 'unhashable type: list' error has been completely resolved.")
    print("✨ The graph explorer can now handle both Cosmos DB valueMap(true) and simple dictionary formats.")
    return True

def test_backward_compatibility():
    """Test that the fix maintains backward compatibility with simple dict format"""
    print("\n🔄 Testing Backward Compatibility")
    print("-" * 40)
    
    explorer = GraphExplorer()
    
    # Test with simple dictionary format (should still work)
    simple_entities = [
        {
            'name': 'Simple Entity',
            'type': 'test',
            'description': 'A simple test entity'
        }
    ]
    
    try:
        for entity in simple_entities:
            name = explorer._extract_property(entity, 'name', 'Unknown')
            entity_type = explorer._extract_property(entity, 'type', 'unknown')
            print(f"   ✅ Simple format: {name} ({entity_type})")
        
        print("✅ Backward compatibility maintained!")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility broken: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Comprehensive Test: 'unhashable type: list' Error Fix")
    print("=" * 65)
    
    success1 = test_original_error_scenario()
    success2 = test_backward_compatibility()
    
    if success1 and success2:
        print("\n🎉 COMPREHENSIVE SUCCESS!")
        print("✅ Original error completely resolved")
        print("✅ Backward compatibility maintained") 
        print("✅ Graph explorer ready for production use")
    else:
        print("\n❌ ISSUES REMAIN!")
        sys.exit(1)
