#!/usr/bin/env python3
"""
Test script to verify the "unhashable type: 'list'" error fix
This simulates the exact data format that was causing the issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed graph explorer
from demos.graph_explorer import GraphExplorer

def test_cosmos_data_format():
    """Test the helper method with Cosmos DB valueMap(true) format"""
    print("🧪 Testing Cosmos DB valueMap(true) format handling...")
      # Create a mock GraphExplorer instance
    explorer = GraphExplorer()  # Constructor takes no arguments
    
    # Test data in Cosmos DB valueMap(true) format (properties as lists)
    cosmos_entity = {
        'name': ['John Doe'],
        'type': ['person'],
        'description': ['A test person entity'],
        'confidence': ['0.95']
    }
    
    # Test data in simple dictionary format (for backward compatibility)
    simple_entity = {
        'name': 'Jane Smith',
        'type': 'person',
        'description': 'Another test person',
        'confidence': '0.88'
    }
    
    # Test the _extract_property helper method
    print("✅ Testing _extract_property method:")
    
    # Test Cosmos DB format
    name1 = explorer._extract_property(cosmos_entity, 'name', 'Unknown')
    type1 = explorer._extract_property(cosmos_entity, 'type', 'unknown')
    desc1 = explorer._extract_property(cosmos_entity, 'description', '')
    conf1 = explorer._extract_property(cosmos_entity, 'confidence', '1.0')
    
    print(f"   Cosmos format - Name: {name1}, Type: {type1}, Desc: {desc1}, Conf: {conf1}")
    
    # Test simple dictionary format
    name2 = explorer._extract_property(simple_entity, 'name', 'Unknown')
    type2 = explorer._extract_property(simple_entity, 'type', 'unknown')
    desc2 = explorer._extract_property(simple_entity, 'description', '')
    conf2 = explorer._extract_property(simple_entity, 'confidence', '1.0')
    
    print(f"   Simple format - Name: {name2}, Type: {type2}, Desc: {desc2}, Conf: {conf2}")
    
    # Test edge cases
    print("✅ Testing edge cases:")
    
    # Empty list
    empty_entity = {'name': [], 'type': ['person']}
    name3 = explorer._extract_property(empty_entity, 'name', 'Unknown')
    print(f"   Empty list handling - Name: {name3}")
    
    # Missing property
    incomplete_entity = {'type': ['person']}
    name4 = explorer._extract_property(incomplete_entity, 'name', 'Unknown')
    print(f"   Missing property handling - Name: {name4}")
    
    # Non-dict input
    name5 = explorer._extract_property("not a dict", 'name', 'Unknown')
    print(f"   Non-dict input handling - Name: {name5}")
    
    # Test that no "unhashable type: 'list'" error occurs
    try:
        # This would have failed before the fix
        entity_groups = {}
        test_entities = [cosmos_entity, simple_entity]
        
        for entity in test_entities:
            entity_type = explorer._extract_property(entity, 'type', 'unknown')
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity)
        
        print(f"✅ Entity grouping successful: {len(entity_groups)} groups created")
        
    except TypeError as e:
        if "unhashable type: 'list'" in str(e):
            print(f"❌ ERROR: The 'unhashable type: list' error still exists: {e}")
            return False
        else:
            print(f"❌ ERROR: Unexpected error: {e}")
            return False
    
    print("🎉 All tests passed! The 'unhashable type: list' error has been fixed.")
    return True

if __name__ == "__main__":
    print("🔧 Testing 'unhashable type: list' Error Fix")
    print("=" * 50)
    success = test_cosmos_data_format()
    if success:
        print("\n✅ SUCCESS: All fixes working correctly!")
    else:
        print("\n❌ FAILURE: Issues still exist!")
        sys.exit(1)
