"""
Interactive Graph Explorer for Graphiti-Cosmos
Allows natural language exploration of entities, relationships, communities, and subgraphs
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
import traceback

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.graphiti_cosmos import GraphitiCosmos

class GraphExplorer:
    """Interactive exploration tool for knowledge graphs"""
    
    def __init__(self):
        self.graphiti = None
        self.session_history = []
        self.bookmark_entities = []
        self.bookmark_relationships = []
        
    async def initialize(self):
        """Initialize the Graphiti-Cosmos system"""
        print("🔍 INTERACTIVE GRAPH EXPLORER")
        print("=" * 60)
        print("🎨 Initializing Graphiti-Cosmos...")
        
        self.graphiti = GraphitiCosmos()
        await self.graphiti.initialize()
        print("✅ Connected to Azure Cosmos DB and OpenAI")
        print("🌟 Ready for graph exploration!")
        print()
        
    def display_main_menu(self):
        """Display the main exploration menu"""
        print("🔍 GRAPH EXPLORATION MENU")
        print("-" * 50)
        print("1. 🔎 Search Entities (Natural Language)")
        print("2. 🔗 Search Relationships")
        print("3. 🏘️  Explore Communities")
        print("4. 🧩 Analyze Subgraphs")
        print("5. 🌐 Graph Overview & Statistics")
        print("6. 📊 Entity Deep Dive")
        print("7. 🔄 Relationship Analysis")
        print("8. 🎯 Advanced Query Builder")
        print("9. 📋 Session History")
        print("10. 🔖 Manage Bookmarks")
        print("11. 📈 Export Analysis")
        print("0. 🚪 Exit")
        print("-" * 50)

    async def run_interactive_session(self):
        """Main interactive session loop"""
        await self.initialize()
        
        while True:
            self.display_main_menu()
            choice = input("Enter your choice (0-11): ").strip()
            
            try:
                if choice == "0":
                    print("👋 Thanks for exploring! Session saved.")
                    await self._save_session()
                    break
                elif choice == "1":
                    await self._search_entities_nl()
                elif choice == "2":
                    await self._search_relationships()
                elif choice == "3":
                    await self._explore_communities()
                elif choice == "4":
                    await self._analyze_subgraphs()
                elif choice == "5":
                    await self._graph_overview()
                elif choice == "6":
                    await self._entity_deep_dive()
                elif choice == "7":
                    await self._relationship_analysis()
                elif choice == "8":
                    await self._advanced_query_builder()
                elif choice == "9":
                    await self._show_session_history()
                elif choice == "10":
                    await self._manage_bookmarks()
                elif choice == "11":
                    await self._export_analysis()
                else:
                    print("❌ Invalid choice! Please try again.")
                
                print("\nPress Enter to continue...")
                input()
                print("\n" + "="*60 + "\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                traceback.print_exc()
                print("\nPress Enter to continue...")
                    
    async def _search_entities_nl(self):
        """Natural language entity search"""
        print("🔎 NATURAL LANGUAGE ENTITY SEARCH")
        print("-" * 40)
        print("💡 Examples:")
        print("   - 'Find all people in the graph'")
        print("   - 'Show me products related to sustainability'")
        print("   - 'List organizations and their relationships'")
        print("   - 'Find entities connected to Sarah Johnson'")
        print()
        
        query = input("🗣️  Enter your search query: ").strip()
        if not query:
            print("ℹ️  No query entered.")
            return
            
        # Log the search
        self.session_history.append({
            'type': 'entity_search',
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        print(f"\n🔍 Analyzing query: '{query}'")
        print("-" * 40)
        
        try:
            # Step 1: Interpret the natural language query using LLM
            interpretation = await self._interpret_search_query(query)
            
            print(f"🎯 Query intent: {interpretation['intent']}")
            print(f"📋 Search terms: {', '.join(interpretation['search_terms'])}")
            print(f"🔧 Strategy: {interpretation['strategy']}")
            print(f"🎪 Confidence: {interpretation['confidence']:.2f}")
            print("💡 Searching with AI-enhanced strategy...")
            print()
            
            # Step 2: Execute search based on interpretation
            entities = []
            search_terms = interpretation['search_terms']
            
            if interpretation['strategy'] == 'exact_match':
                # Use exact matching for specific entity searches
                for term in search_terms[:2]:
                    results = await self.graphiti.search_entities(term, limit=10)
                    entities.extend(results)
            elif interpretation['strategy'] == 'broad_exploration':
                # Get broader results for exploratory queries
                for term in search_terms[:1]:
                    results = await self.graphiti.search_entities(term, limit=30)
                    entities.extend(results)
            else:  # semantic_search (default)
                # Use semantic search for most queries
                for term in search_terms[:3]:
                    results = await self.graphiti.search_entities(term, limit=15)
                    entities.extend(results)
              # Step 3: Remove duplicates and enhance results with LLM
            unique_entities = {}
            for entity in entities:
                entity_id = self._extract_property(entity, 'id') or self._extract_property(entity, 'name')
                if entity_id not in unique_entities:
                    unique_entities[entity_id] = entity
            
            entities = list(unique_entities.values())
            
            # Step 4: Enhance results with LLM insights
            if entities:
                print("🧠 Enhancing results with AI insights...")
                entities = await self._enhance_search_results_with_llm(query, entities, interpretation)
            
            if entities:
                print(f"\n✅ Found {len(entities)} entities:")
                
                # Display LLM insights if available
                if hasattr(self, '_last_enhancement'):
                    enhancement = self._last_enhancement
                    print(f"\n🔍 AI Insights: {enhancement.get('insights', 'No insights available')}")
                    
                    if enhancement.get('follow_up_queries'):
                        print("\n💡 Suggested follow-up queries:")
                        for i, suggestion in enumerate(enhancement['follow_up_queries'][:3], 1):
                            print(f"   {i}. {suggestion}")
                    
                    if enhancement.get('gaps'):
                        print(f"\n⚠️  Consider exploring: {enhancement['gaps']}")
                    print()
                  # Group by type
                entity_groups = defaultdict(list)
                for entity in entities:
                    entity_type = self._extract_property(entity, 'type', 
                                                       self._extract_property(entity, 'entity_type', 'unknown'))
                    entity_groups[entity_type].append(entity)
                
                for entity_type, type_entities in entity_groups.items():
                    print(f"\n📍 {entity_type.upper()} ({len(type_entities)} entities):")
                    for i, entity in enumerate(type_entities[:5], 1):
                        name = self._extract_property(entity, 'name', 
                                                    self._extract_property(entity, 'id', 'Unknown'))
                        description = self._extract_property(entity, 'description', '')
                        if description:
                            print(f"   {i}. {name}: {description[:100]}{'...' if len(description) > 100 else ''}")
                        else:
                            print(f"   {i}. {name}")
                
                # Show bookmark option
                print("\n🔖 Enter entity name to bookmark (or press Enter to continue):")
                bookmark_choice = input().strip()
                if bookmark_choice:
                    self.bookmark_entities.append(bookmark_choice)
                    print(f"✅ Bookmarked: {bookmark_choice}")
                    
            else:
                print("❌ No entities found matching your query.")
                print("💡 Try:")
                print("   - Using broader search terms")
                print("   - Checking spelling")
                print("   - Using different keywords")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            print("💡 Trying fallback search...")
            
            try:
                # Fallback to basic keyword search
                keywords = await self._extract_search_keywords(query)
                entities = []
                for keyword in keywords:
                    results = await self.graphiti.search_entities(keyword, limit=20)
                    entities.extend(results)
                if entities:
                    print(f"✅ Found {len(entities)} entities using fallback search:")
                    for i, entity in enumerate(entities[:10], 1):
                        # Handle both dictionary and Cosmos DB valueMap(true) list formats
                        if isinstance(entity, dict):
                            name = self._extract_property(entity, 'name', 'Unknown')
                            entity_type = self._extract_property(entity, 'type', 
                                         self._extract_property(entity, 'entity_type', 'unknown'))
                        else:
                            name = str(entity) if entity else 'Unknown'
                            entity_type = 'unknown'
                        print(f"   {i}. {name} ({entity_type})")
                else:
                    print("❌ No entities found.")
                print()
                
            except Exception as fallback_error:
                print(f"❌ Fallback search also failed: {fallback_error}")
                print("💡 Try these alternatives:")
                print("   - Use more general terms")
                print("   - Try searching for entity types: 'person', 'product', 'organization'")
                print("   - Browse all entities with an empty search")

    async def _search_relationships(self):
        """Search and explore relationships"""
        print("🔗 RELATIONSHIP SEARCH & EXPLORATION")
        print("-" * 40)
        print("💡 Search options:")
        print("   1. By relationship type (e.g., 'works_for', 'related_to')")
        print("   2. By entities (e.g., 'Sarah Johnson')")
        print("   3. By pattern (e.g., 'person → organization')")
        print()
        
        search_type = input("Choose search type (1-3): ").strip()
        
        if search_type == "1":
            await self._search_relationships_by_type()
        elif search_type == "2":
            await self._search_relationships_by_entity()
        elif search_type == "3":
            await self._search_relationships_by_pattern()
        else:
            print("❌ Invalid choice!")

    async def _search_relationships_by_type(self):
        """Search relationships by type"""
        print("\n🏷️ SEARCH BY RELATIONSHIP TYPE")
        print("-" * 30)
        
        # Show available relationship types
        print("📋 Getting available relationship types...")        
        relationships = await self.graphiti.search_relationships("", limit=100)
        
        rel_types = Counter()
        for rel in relationships:
            rel_type = self._extract_property(rel, 'type', 'unknown')
            rel_types[rel_type] += 1
        
        print("🔗 Available relationship types:")
        for rel_type, count in rel_types.most_common(10):
            print(f"   • {rel_type} ({count} instances)")
        
        rel_type = input("\nEnter relationship type to explore: ").strip()
        if not rel_type:
            return
            
        # Search for this relationship type
        matching_rels = [rel for rel in relationships if self._extract_property(rel, 'type', '').lower() == rel_type.lower()]
        
        if matching_rels:
            print(f"\n✅ Found {len(matching_rels)} '{rel_type}' relationships:")
            
            for i, rel in enumerate(matching_rels[:10], 1):
                source = self._extract_property(rel, 'source', 'Unknown')
                target = self._extract_property(rel, 'target', 'Unknown')
                description = self._extract_property(rel, 'description', 'No description')
                confidence = self._extract_property(rel, 'confidence', '1.0')
                
                print(f"\n{i}. {source} → {rel_type} → {target}")
                if confidence < 1.0:
                    print(f"   🎯 Confidence: {confidence:.2f}")
                if description and description != 'No description':
                    desc_preview = description[:100] + "..." if len(description) > 100 else description
                    print(f"   💭 {desc_preview}")
            
            if len(matching_rels) > 10:
                print(f"\n... and {len(matching_rels) - 10} more relationships")
        else:
            print(f"❌ No relationships found of type '{rel_type}'")

    async def _search_relationships_by_entity(self):
        """Search relationships involving specific entities"""
        print("\n👤 SEARCH BY ENTITY")
        print("-" * 20)
        
        entity_name = input("Enter entity name: ").strip()
        if not entity_name:
            return
            
        relationships = await self._get_entity_relationships(entity_name)
        
        if relationships:
            print(f"\n✅ Found {len(relationships)} relationships for '{entity_name}':")
              # Group by relationship type
            rel_groups = defaultdict(list)
            for rel in relationships:
                rel_type = self._extract_property(rel, 'type', 'unknown')
                rel_groups[rel_type].append(rel)
            
            for rel_type, type_rels in rel_groups.items():
                print(f"\n🔗 {rel_type} ({len(type_rels)} instances):")
                for rel in type_rels[:5]:
                    source = self._extract_property(rel, 'source', 'Unknown')
                    target = self._extract_property(rel, 'target', 'Unknown')
                    
                    # Determine direction
                    if source.lower() == entity_name.lower():
                        print(f"   → {target}")
                    else:
                        print(f"   ← {source}")
                
                if len(type_rels) > 5:
                    print(f"   ... and {len(type_rels) - 5} more")
        else:
            print(f"❌ No relationships found for '{entity_name}'")

    async def _explore_communities(self):
        """Explore entity communities and clusters"""
        print("🏘️ COMMUNITY EXPLORATION")
        print("-" * 40)
        
        print("🔍 Analyzing entity communities...")
        
        # Get all entities
        entities = await self.graphiti.search_entities("", limit=200)
        
        if len(entities) < 3:
            print("ℹ️  Not enough entities for community analysis")
            return
          # Group entities by type (basic community detection)
        type_communities = defaultdict(list)
        for entity in entities:
            entity_type = self._extract_property(entity, 'type', 'unknown')
            type_communities[entity_type].append(entity)
        
        print(f"✅ Found {len(type_communities)} entity type communities:")
        
        for community_type, members in type_communities.items():
            print(f"\n📍 {community_type.upper()} Community ({len(members)} members)")
              # Show top members
            for i, member in enumerate(members[:5], 1):
                name = self._extract_property(member, 'name', 'Unknown')
                description = self._extract_property(member, 'description', 'No description')
                desc_preview = description[:50] + "..." if len(description) > 50 else description
                print(f"   {i}. {name} - {desc_preview}")
            
            if len(members) > 5:
                print(f"   ... and {len(members) - 5} more members")
        
        # Advanced community analysis
        print(f"\n🔬 ADVANCED COMMUNITY ANALYSIS")
        print("-" * 30)
        
        community_choice = input("Enter community type to analyze deeply (or press Enter to skip): ").strip()
        if community_choice:
            await self._deep_community_analysis(community_choice, type_communities.get(community_choice.lower(), []))

    async def _deep_community_analysis(self, community_type: str, members: List[Dict]):
        """Perform deep analysis of a specific community"""
        print(f"\n🔬 DEEP ANALYSIS: {community_type.upper()} COMMUNITY")
        print("-" * 40)
        
        if not members:
            print("❌ No members found in this community")
            return
        
        print(f"👥 Community Size: {len(members)} members")
        
        # Analyze internal connections
        print("\n🔗 Analyzing internal connections...")
        internal_connections = 0
        connection_map = defaultdict(list)
        for member in members:
            member_name = self._extract_property(member, 'name', '')
            relationships = await self._get_entity_relationships(member_name)
            
            for rel in relationships:
                source = self._extract_property(rel, 'source', '')
                target = self._extract_property(rel, 'target', '')
                
                # Check if both entities are in this community
                member_names = [self._extract_property(m, 'name', '') for m in members]
                if source in member_names and target in member_names:
                    internal_connections += 1
                    connection_map[member_name].append({
                        'target': target if source == member_name else source,
                        'type': self._extract_property(rel, 'type', 'unknown')
                    })
        
        print(f"🔄 Internal connections: {internal_connections}")
        
        # Find most connected members
        connection_counts = [(name, len(connections)) for name, connections in connection_map.items()]
        connection_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n⭐ Most connected members:")
        for name, count in connection_counts[:5]:
            print(f"   • {name}: {count} connections")
        
        # Find external connections
        print(f"\n🌐 External connections...")
        external_targets = defaultdict(int)
        for member in members[:10]:  # Limit for performance
            member_name = self._extract_property(member, 'name', '')
            relationships = await self._get_entity_relationships(member_name)
            
            for rel in relationships:
                source = self._extract_property(rel, 'source', '')
                target = self._extract_property(rel, 'target', '')
                
                # Find external targets
                member_names = [self._extract_property(m, 'name', '') for m in members]
                external_target = None
                if source == member_name and target not in member_names:
                    external_target = target
                elif target == member_name and source not in member_names:
                    external_target = source
                
                if external_target:
                    external_targets[external_target] += 1
        
        if external_targets:
            print(f"🔗 Top external connections:")
            for target, count in Counter(external_targets).most_common(5):
                print(f"   • {target}: {count} connections")

    async def _analyze_subgraphs(self):
        """Analyze and explore subgraphs"""
        print("🧩 SUBGRAPH ANALYSIS")
        print("-" * 40)
        
        print("🔍 Choose subgraph analysis type:")
        print("1. 🎯 Ego network (around specific entity)")
        print("2. 🌊 Path analysis (between two entities)")
        print("3. 📊 Dense subgraphs")
        print("4. 🏷️  Type-based subgraphs")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            await self._ego_network_analysis()
        elif choice == "2":
            await self._path_analysis()
        elif choice == "3":
            await self._dense_subgraph_analysis()
        elif choice == "4":
            await self._type_based_subgraphs()
        else:
            print("❌ Invalid choice!")

    async def _ego_network_analysis(self):
        """Analyze ego network around a specific entity"""
        print("\n🎯 EGO NETWORK ANALYSIS")
        print("-" * 25)
        
        entity_name = input("Enter entity name for ego network: ").strip()
        if not entity_name:
            return
        
        depth = input("Enter network depth (1-3, default 2): ").strip()
        try:
            depth = int(depth) if depth else 2
            depth = max(1, min(depth, 3))  # Limit between 1-3
        except ValueError:
            depth = 2
        
        print(f"\n🔍 Analyzing {depth}-hop ego network for '{entity_name}'...")
          # Build ego network
        ego_entities = {entity_name}
        ego_relationships = []
        
        current_entities = {entity_name}
        for hop in range(depth):
            next_entities = set()
            for entity in current_entities:
                relationships = await self._get_entity_relationships(entity)
                
                for rel in relationships:
                    source = self._extract_property(rel, 'source', '')
                    target = self._extract_property(rel, 'target', '')
                    
                    ego_relationships.append(rel)
                    
                    # Add connected entities
                    if source == entity:
                        next_entities.add(target)
                        ego_entities.add(target)
                    elif target == entity:
                        next_entities.add(source)
                        ego_entities.add(source)
            
            current_entities = next_entities - ego_entities
            ego_entities.update(next_entities)
            
            print(f"   Hop {hop + 1}: Found {len(next_entities)} new entities")
        
        print(f"\n✅ Ego network summary:")
        print(f"   🏠 Center entity: {entity_name}")
        print(f"   👥 Total entities: {len(ego_entities)}")
        print(f"   🔗 Total relationships: {len(ego_relationships)}")
        
        # Analyze the ego network
        if len(ego_entities) > 1:
            print(f"\n🔬 Network analysis:")
              # Entity types in network
            entity_types = Counter()
            for entity_name_in_network in ego_entities:
                # Get entity type
                entities = await self.graphiti.search_entities(entity_name_in_network, limit=1)
                if entities:
                    entity_type = self._extract_property(entities[0], 'type', 'unknown')
                    entity_types[entity_type] += 1
            
            print(f"   📊 Entity types:")
            for entity_type, count in entity_types.most_common():
                print(f"      • {entity_type}: {count}")
              # Relationship types in network
            rel_types = Counter()
            for rel in ego_relationships:
                rel_type = self._extract_property(rel, 'type', 'unknown')
                rel_types[rel_type] += 1
            
            print(f"   🔗 Relationship types:")
            for rel_type, count in rel_types.most_common(5):
                print(f"      • {rel_type}: {count}")

    async def _graph_overview(self):
        """Provide comprehensive graph overview and statistics"""
        print("🌐 GRAPH OVERVIEW & STATISTICS")
        print("-" * 40)
        
        print("📊 Collecting graph statistics...")
          # Get basic stats
        stats = await self.graphiti.get_graph_stats()
        print(f"\n📈 Basic Statistics:")
        print(f"   📚 Episodes: {self._extract_property(stats, 'episodes', '0')}")
        print(f"   👥 Entities: {self._extract_property(stats, 'entities', '0')}")
        print(f"   🔗 Relationships: {self._extract_property(stats, 'relationships', '0')}")
        
        entities_count = int(self._extract_property(stats, 'entities', '0'))
        relationships_count = int(self._extract_property(stats, 'relationships', '0'))
        if entities_count > 0:
            density = relationships_count / entities_count
            print(f"   🎯 Density: {density:.2f} relationships per entity")
        
        # Entity type distribution
        print(f"\n🏷️  Entity Type Distribution:")
        entities = await self.graphiti.search_entities("", limit=200)
        entity_types = Counter()        
        for entity in entities:
            entity_type = self._extract_property(entity, 'type', 'unknown')
            entity_types[entity_type] += 1
        
        for entity_type, count in entity_types.most_common():
            percentage = (count / len(entities)) * 100 if entities else 0
            print(f"   📍 {entity_type}: {count} ({percentage:.1f}%)")
        
        # Relationship type distribution
        print(f"\n🔗 Relationship Type Distribution:")
        relationships = await self.graphiti.search_relationships("", limit=200)
        rel_types = Counter()
        for rel in relationships:
            rel_type = self._extract_property(rel, 'type', 'unknown')
            rel_types[rel_type] += 1
        
        for rel_type, count in rel_types.most_common(5):
            percentage = (count / len(relationships)) * 100 if relationships else 0
            print(f"   🔗 {rel_type}: {count} ({percentage:.1f}%)")
          # Find most connected entities
        print(f"\n⭐ Most Connected Entities:")
        entity_connections = defaultdict(int)
        
        for rel in relationships[:100]:  # Limit for performance
            source = self._extract_property(rel, 'source', '')
            target = self._extract_property(rel, 'target', '')
            entity_connections[source] += 1
            entity_connections[target] += 1
        
        top_connected = sorted(entity_connections.items(), key=lambda x: x[1], reverse=True)
        for entity, connections in top_connected[:5]:
            print(f"   🌟 {entity}: {connections} connections")

    async def _entity_deep_dive(self):
        """Deep dive analysis of a specific entity"""
        print("📊 ENTITY DEEP DIVE")
        print("-" * 40)
        
        entity_name = input("Enter entity name to analyze: ").strip()
        if not entity_name:
            return
            
        await self._entity_deep_dive_specific(entity_name)

    async def _entity_deep_dive_specific(self, entity_name: str):
        """Perform deep dive analysis on a specific entity"""
        print(f"\n🔬 DEEP DIVE: {entity_name}")
        print("-" * 40)
        
        # Get entity details
        entities = await self.graphiti.search_entities(entity_name, limit=5)
        target_entity = None
        for entity in entities:
            if self._extract_property(entity, 'name', '').lower() == entity_name.lower():
                target_entity = entity
                break
        
        if not target_entity and entities:
            target_entity = entities[0]  # Take the first match
        
        if target_entity:
            print(f"📋 Entity Details:")
            print(f"   🏷️  Name: {self._extract_property(target_entity, 'name', 'Unknown')}")
            print(f"   📂 Type: {self._extract_property(target_entity, 'type', 'Unknown')}")
            print(f"   📝 Description: {self._extract_property(target_entity, 'description', 'No description')}")
            
            # Get relationships
            relationships = await self._get_entity_relationships(entity_name)
            print(f"\n🔗 Relationships ({len(relationships)} total):")
            
            if relationships:                # Group by type
                rel_groups = defaultdict(list)
                for rel in relationships:
                    rel_type = self._extract_property(rel, 'type', 'unknown')
                    rel_groups[rel_type].append(rel)
                
                for rel_type, type_rels in rel_groups.items():
                    print(f"\n   📌 {rel_type} ({len(type_rels)} instances):")
                    for rel in type_rels[:3]:
                        source = self._extract_property(rel, 'source', 'Unknown')
                        target = self._extract_property(rel, 'target', 'Unknown')
                        confidence = float(self._extract_property(rel, 'confidence', '1.0'))
                        
                        if source.lower() == entity_name.lower():
                            direction = f"→ {target}"
                        else:
                            direction = f"← {source}"
                        
                        confidence_str = f" (conf: {confidence:.2f})" if confidence < 1.0 else ""
                        print(f"      {direction}{confidence_str}")
                    
                    if len(type_rels) > 3:
                        print(f"      ... and {len(type_rels) - 3} more")
            
            # Find related entities            print(f"\n🌐 Connected Entity Types:")
            connected_types = Counter()
            for rel in relationships:
                source = self._extract_property(rel, 'source', '')
                target = self._extract_property(rel, 'target', '')
                
                # Get the other entity's type
                other_entity = target if source.lower() == entity_name.lower() else source
                other_entities = await self.graphiti.search_entities(other_entity, limit=1)
                if other_entities:
                    other_type = self._extract_property(other_entities[0], 'type', 'unknown')
                    connected_types[other_type] += 1
            
            for conn_type, count in connected_types.most_common():
                print(f"   📍 {conn_type}: {count} connections")
        else:
            print(f"❌ Entity '{entity_name}' not found")

    async def _relationship_analysis(self):
        """Comprehensive relationship analysis"""
        print("🔄 RELATIONSHIP ANALYSIS")
        print("-" * 40)
        
        print("📊 Collecting relationship data...")
        relationships = await self.graphiti.search_relationships("", limit=200)
        
        if not relationships:
            print("❌ No relationships found in the graph")
            return
        
        print(f"✅ Analyzing {len(relationships)} relationships...")
          # Relationship type analysis
        rel_types = Counter()
        confidence_by_type = defaultdict(list)
        
        for rel in relationships:
            rel_type = self._extract_property(rel, 'type', 'unknown')
            confidence = float(self._extract_property(rel, 'confidence', '1.0'))
            rel_types[rel_type] += 1
            confidence_by_type[rel_type].append(confidence)
        
        print(f"\n🏷️  Relationship Types & Confidence:")
        for rel_type, count in rel_types.most_common():
            avg_confidence = sum(confidence_by_type[rel_type]) / len(confidence_by_type[rel_type])
            print(f"   🔗 {rel_type}: {count} instances (avg confidence: {avg_confidence:.2f})")
          # Find relationship patterns
        print(f"\n🔍 Relationship Patterns:")
        patterns = Counter()
        for rel in relationships:
            source = self._extract_property(rel, 'source', '')
            target = self._extract_property(rel, 'target', '')
            rel_type = self._extract_property(rel, 'type', 'unknown')
            
            # Get entity types
            source_entities = await self.graphiti.search_entities(source, limit=1)
            target_entities = await self.graphiti.search_entities(target, limit=1)
            
            source_type = self._extract_property(source_entities[0], 'type', 'unknown') if source_entities else 'unknown'
            target_type = self._extract_property(target_entities[0], 'type', 'unknown') if target_entities else 'unknown'
            
            pattern = f"{source_type} → {rel_type} → {target_type}"
            patterns[pattern] += 1
        
        print(f"   📈 Most common patterns:")
        for pattern, count in patterns.most_common(5):
            print(f"      • {pattern}: {count} times")

    async def _advanced_query_builder(self):
        """Advanced query builder for complex graph queries"""
        print("🎯 ADVANCED QUERY BUILDER")
        print("-" * 40)
        print("🔧 Build complex queries to explore your graph")
        print()
        
        print("1. 🔍 Multi-entity search")
        print("2. 🔗 Relationship chain queries")
        print("3. 📊 Conditional queries")
        print("4. 🎨 Custom pattern matching")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            await self._multi_entity_search()
        elif choice == "2":
            await self._relationship_chain_query()
        elif choice == "3":
            await self._conditional_query()
        elif choice == "4":
            await self._pattern_matching()
        else:
            print("❌ Invalid choice!")

    async def _multi_entity_search(self):
        """Search for multiple entities simultaneously"""        
        print("\n🔍 MULTI-ENTITY SEARCH")
        print("-" * 25)
        
        query = input("Enter entities to search (comma-separated): ").strip()
        if not query:
            return
            
        entity_names = [name.strip() for name in query.split(',')]
        print(f"\n🎯 Searching for: {', '.join(entity_names)}")
        
        found_entities = {}
        for entity_name in entity_names:
            entities = await self.graphiti.search_entities(entity_name, limit=5)
            if entities:
                found_entities[entity_name] = entities[0]
        
        print(f"\n✅ Found {len(found_entities)} entities:")
        for name, entity in found_entities.items():
            entity_type = self._extract_property(entity, 'type', 'unknown')
            print(f"   • {name} ({entity_type})")
        
        # Find connections between found entities
        print(f"\n🔗 Analyzing connections between entities...")
        connections = []
        
        for name1, entity1 in found_entities.items():
            relationships = await self._get_entity_relationships(name1)
            for rel in relationships:
                source = self._extract_property(rel, 'source', '')
                target = self._extract_property(rel, 'target', '')
                
                # Check if the other entity is in our search set
                other_entity = target if source == name1 else source
                if any(other_entity.lower() == name.lower() for name in entity_names):
                    connections.append(rel)
        
        if connections:
            print(f"   ✅ Found {len(connections)} connections:")
            for rel in connections:
                source = self._extract_property(rel, 'source', '')
                target = self._extract_property(rel, 'target', '')
                rel_type = self._extract_property(rel, 'type', 'unknown')
                print(f"      {source} → {rel_type} → {target}")
        else:
            print(f"   ℹ️  No direct connections found between these entities")

    async def _show_session_history(self):
        """Show session history"""
        print("📋 SESSION HISTORY")
        print("-" * 40)
        
        if not self.session_history:
            print("ℹ️  No history available for this session")
            return
        
        for i, entry in enumerate(self.session_history, 1):
            timestamp = entry.get('timestamp', 'Unknown')
            entry_type = entry.get('type', 'unknown')
            query = entry.get('query', 'No query')
            
            print(f"{i}. [{timestamp}] {entry_type}: {query}")

    async def _manage_bookmarks(self):
        """Manage bookmarked entities and relationships"""
        print("🔖 BOOKMARK MANAGER")
        print("-" * 40)
        
        print("1. 📋 View bookmarks")
        print("2. ➕ Add entity bookmark")
        print("3. ➕ Add relationship bookmark")
        print("4. ❌ Remove bookmark")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            await self._view_bookmarks()
        elif choice == "2":
            await self._add_entity_bookmark()
        elif choice == "3":
            await self._add_relationship_bookmark()
        elif choice == "4":
            await self._remove_bookmark()

    async def _view_bookmarks(self):
        """View all bookmarks"""
        print("\n📋 YOUR BOOKMARKS")
        print("-" * 20)
        
        if self.bookmark_entities:
            print(f"👥 Entity Bookmarks ({len(self.bookmark_entities)}):")
            for i, entity in enumerate(self.bookmark_entities, 1):
                print(f"   {i}. {entity}")
        
        if self.bookmark_relationships:
            print(f"\n🔗 Relationship Bookmarks ({len(self.bookmark_relationships)}):")
            for i, rel in enumerate(self.bookmark_relationships, 1):
                print(f"   {i}. {rel}")
        
        if not self.bookmark_entities and not self.bookmark_relationships:
            print("ℹ️  No bookmarks saved yet")

    async def _add_entity_bookmark(self):
        """Add entity to bookmarks"""
        entity_name = input("Enter entity name to bookmark: ").strip()
        if entity_name and entity_name not in self.bookmark_entities:
            self.bookmark_entities.append(entity_name)
            print(f"✅ Added '{entity_name}' to bookmarks")
        elif entity_name in self.bookmark_entities:
            print(f"ℹ️  '{entity_name}' is already bookmarked")

    async def _export_analysis(self):
        """Export analysis results"""
        print("📈 EXPORT ANALYSIS")
        print("-" * 40)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create analysis report
        report = {
            'timestamp': timestamp,
            'session_history': self.session_history,
            'bookmarks': {
                'entities': self.bookmark_entities,
                'relationships': self.bookmark_relationships
            }
        }
        
        # Add graph statistics
        stats = await self.graphiti.get_graph_stats()
        report['graph_stats'] = stats
        
        # Save report
        reports_dir = "exploration_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"graph_exploration_{timestamp}.json"
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis exported to: {filepath}")

    async def _save_session(self):
        """Save session data"""
        if not self.session_history:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_data = {
            'timestamp': timestamp,
            'history': self.session_history,
            'bookmarks': {
                'entities': self.bookmark_entities,
                'relationships': self.bookmark_relationships
            }        }
        
        sessions_dir = "exploration_sessions"
        os.makedirs(sessions_dir, exist_ok=True)
        
        filename = f"session_{timestamp}.json"
        filepath = os.path.join(sessions_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    # Helper methods
    async def _extract_search_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords and intent from natural language query using LLM"""
        try:
            prompt = f"""
            Analyze this natural language graph search query and extract the most relevant search terms and concepts.
            Focus on entities, relationships, and graph concepts that would be found in a knowledge graph.
            
            Query: "{query}"
            
            Extract:
            1. Key entities or entity types to search for
            2. Relationship types or patterns
            3. Important descriptive terms
            4. Graph concepts (communities, networks, etc.)
            
            Return a JSON array of the most relevant search terms (max 5), ordered by importance:
            ["term1", "term2", "term3", "term4", "term5"]
            
            Only return valid JSON, no other text.
            """
            
            response = await self.graphiti.openai_client.chat.completions.create(
                model=self.graphiti.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            keywords = json.loads(response.choices[0].message.content)
            return keywords[:5]  # Ensure max 5 keywords
            
        except Exception as e:
            print(f"⚠️  LLM keyword extraction failed, using fallback: {e}")
            # Fallback to basic extraction
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'find', 'show', 'list', 'get', 'all', 'me'}
            words = query.lower().split()
            keywords = [word.strip('.,!?') for word in words if word not in stop_words and len(word) > 2]
            return keywords[:5]

    async def _get_entity_relationships(self, entity_name: str) -> List[Dict]:
        """Get all relationships for a specific entity"""
        try:            # Search for relationships where entity is source or target
            all_relationships = await self.graphiti.search_relationships("", limit=200)
            entity_relationships = []
            for rel in all_relationships:
                source = self._extract_property(rel, 'source', '').lower()
                target = self._extract_property(rel, 'target', '').lower()
                
                if entity_name.lower() in source or entity_name.lower() in target:
                    entity_relationships.append(rel)
            
            return entity_relationships
        except Exception as e:
            print(f"Error getting relationships for {entity_name}: {e}")
            return []

# Additional helper methods for advanced features
    async def _relationship_chain_query(self):
        """Query for relationship chains"""
        print("\n🔗 RELATIONSHIP CHAIN QUERY")
        print("-" * 30)
        print("Find entities connected through a chain of relationships")
        print("Example: A → works_for → B → located_in → C")
        
        start_entity = input("Enter starting entity: ").strip()
        if not start_entity:
            return
            
        max_hops = input("Enter maximum hops (1-3, default 2): ").strip()
        try:
            max_hops = int(max_hops) if max_hops else 2
            max_hops = max(1, min(max_hops, 3))
        except ValueError:
            max_hops = 2
        
        print(f"\n🔍 Finding relationship chains from '{start_entity}' (max {max_hops} hops)...")
        
        # Build relationship chains
        chains = []
        current_chains = [[start_entity]]
        for hop in range(max_hops):
            next_chains = []
            for chain in current_chains:
                last_entity = chain[-1]
                relationships = await self._get_entity_relationships(last_entity)
                
                for rel in relationships[:5]:  # Limit to prevent explosion
                    source = self._extract_property(rel, 'source', '')
                    target = self._extract_property(rel, 'target', '')
                    rel_type = self._extract_property(rel, 'type', 'unknown')
                    
                    # Determine next entity
                    next_entity = target if source.lower() == last_entity.lower() else source
                    
                    # Avoid cycles
                    if next_entity not in chain:
                        new_chain = chain + [f"→{rel_type}→", next_entity]
                        next_chains.append(new_chain)
                        
                        if len(new_chain) >= 3:  # At least one relationship
                            chains.append(new_chain.copy())
            
            current_chains = next_chains
            if not current_chains:
                break
        
        if chains:
            print(f"✅ Found {len(chains)} relationship chains:")
            for i, chain in enumerate(chains[:10], 1):
                chain_str = " ".join(chain)
                print(f"   {i}. {chain_str}")
            
            if len(chains) > 10:
                print(f"   ... and {len(chains) - 10} more chains")
        else:
            print("❌ No relationship chains found")

    async def _conditional_query(self):
        """Query with conditions"""
        print("\n📊 CONDITIONAL QUERY")
        print("-" * 20)
        print("Find entities/relationships that meet specific conditions")
        
        print("1. Entities with high connectivity (> X relationships)")
        print("2. Relationships with low confidence (< X)")
        print("3. Entities of specific type with specific relationship")
        
        condition_type = input("Choose condition type (1-3): ").strip()
        
        if condition_type == "1":
            threshold = input("Enter minimum relationship count (default 5): ").strip()
            try:
                threshold = int(threshold) if threshold else 5
            except ValueError:
                threshold = 5
            
            print(f"\n🔍 Finding entities with > {threshold} relationships...")
            entities = await self.graphiti.search_entities("", limit=100)
            high_connectivity = []
            for entity in entities:
                entity_name = self._extract_property(entity, 'name', '')
                relationships = await self._get_entity_relationships(entity_name)
                if len(relationships) > threshold:
                    high_connectivity.append((entity_name, len(relationships)))
            
            high_connectivity.sort(key=lambda x: x[1], reverse=True)
            
            if high_connectivity:
                print(f"✅ Found {len(high_connectivity)} highly connected entities:")
                for entity_name, count in high_connectivity[:10]:
                    print(f"   • {entity_name}: {count} relationships")
            else:
                print(f"❌ No entities found with > {threshold} relationships")
        
        elif condition_type == "2":
            threshold = input("Enter maximum confidence (0.0-1.0, default 0.8): ").strip()
            try:
                threshold = float(threshold) if threshold else 0.8
                threshold = max(0.0, min(threshold, 1.0))
            except ValueError:
                threshold = 0.8
            
            print(f"\n🔍 Finding relationships with confidence < {threshold}...")
            relationships = await self.graphiti.search_relationships("", limit=200)
            low_confidence = []
            for rel in relationships:
                confidence = float(self._extract_property(rel, 'confidence', '1.0'))
                if confidence < threshold:
                    low_confidence.append(rel)
            
            if low_confidence:
                print(f"✅ Found {len(low_confidence)} low-confidence relationships:")
                for rel in low_confidence[:10]:
                    source = self._extract_property(rel, 'source', 'Unknown')
                    target = self._extract_property(rel, 'target', 'Unknown')
                    rel_type = self._extract_property(rel, 'type', 'unknown')
                    confidence = float(self._extract_property(rel, 'confidence', '1.0'))
                    print(f"   • {source} → {rel_type} → {target} (conf: {confidence:.2f})")
            else:
                print(f"❌ No relationships found with confidence < {threshold}")

    async def _pattern_matching(self):
        """Custom pattern matching"""
        print("\n🎨 CUSTOM PATTERN MATCHING")
        print("-" * 30)
        print("Define custom patterns to search for in the graph")
        print("Example patterns:")
        print("  - person works_for organization")
        print("  - product related_to organization")
        print("  - * created_by person")
        
        pattern = input("Enter pattern (entity_type relationship entity_type): ").strip()
        if not pattern:
            return
        
        parts = pattern.split()
        if len(parts) != 3:
            print("❌ Invalid pattern format. Use: entity_type relationship entity_type")
            return
        
        source_type, rel_type, target_type = parts
        
        print(f"\n🔍 Searching for pattern: {source_type} → {rel_type} → {target_type}")
        relationships = await self.graphiti.search_relationships("", limit=200)
        matching_patterns = []
        for rel in relationships:
            rel_relationship = self._extract_property(rel, 'type', '').lower()
            source_name = self._extract_property(rel, 'source', '')
            target_name = self._extract_property(rel, 'target', '')
            
            # Check relationship type match
            if rel_type != '*' and rel_type.lower() != rel_relationship:
                continue
            
            # Get entity types
            source_entities = await self.graphiti.search_entities(source_name, limit=1)
            target_entities = await self.graphiti.search_entities(target_name, limit=1)
            
            source_entity_type = self._extract_property(source_entities[0], 'type', '').lower() if source_entities else ''
            target_entity_type = self._extract_property(target_entities[0], 'type', '').lower() if target_entities else ''
            
            # Check entity type matches
            source_match = source_type == '*' or source_type.lower() == source_entity_type
            target_match = target_type == '*' or target_type.lower() == target_entity_type
            
            if source_match and target_match:
                matching_patterns.append({
                    'source': source_name,
                    'source_type': source_entity_type,
                    'relationship': rel_relationship,
                    'target': target_name,
                    'target_type': target_entity_type,
                    'confidence': self._extract_property(rel, 'confidence', '1.0')
                })
        
        if matching_patterns:
            print(f"✅ Found {len(matching_patterns)} matching patterns:")
            for i, match in enumerate(matching_patterns[:10], 1):
                source = match['source']
                target = match['target']
                relationship = match['relationship']
                confidence = match['confidence']
                
                conf_str = f" (conf: {confidence:.2f})" if confidence < 1.0 else ""
                print(f"   {i}. {source} → {relationship} → {target}{conf_str}")
            
            if len(matching_patterns) > 10:
                print(f"   ... and {len(matching_patterns) - 10} more matches")
        else:
            print("❌ No patterns found matching your criteria")

    async def _path_analysis(self):
        """Analyze paths between entities"""
        print("\n🌊 PATH ANALYSIS")
        print("-" * 15)
        
        source_entity = input("Enter source entity: ").strip()
        target_entity = input("Enter target entity: ").strip()
        
        if not source_entity or not target_entity:
            return
        
        print(f"\n🔍 Finding paths from '{source_entity}' to '{target_entity}'...")
        
        # Simple BFS to find paths
        queue = [[source_entity]]
        visited = set()
        paths = []
        max_depth = 3
        
        for depth in range(max_depth):
            if not queue:
                break
                
            next_queue = []
            
            for path in queue:
                current_entity = path[-1]
                
                if current_entity.lower() == target_entity.lower():
                    paths.append(path)
                    continue
                
                if current_entity in visited:
                    continue
                    
                visited.add(current_entity)
                
                # Get relationships
                relationships = await self._get_entity_relationships(current_entity)
                for rel in relationships[:5]:  # Limit to prevent explosion
                    source = self._extract_property(rel, 'source', '')
                    target = self._extract_property(rel, 'target', '')
                    rel_type = self._extract_property(rel, 'type', 'unknown')
                    
                    next_entity = target if source.lower() == current_entity.lower() else source
                    
                    if next_entity not in path:  # Avoid cycles
                        new_path = path + [f"→{rel_type}→", next_entity]
                        next_queue.append(new_path)
            
            queue = next_queue
        
        if paths:
            print(f"✅ Found {len(paths)} paths:")
            for i, path in enumerate(paths[:5], 1):
                path_str = " ".join(path)
                print(f"   {i}. {path_str}")
        else:
            print("❌ No paths found between these entities")

    async def _dense_subgraph_analysis(self):
        """Find dense subgraphs"""
        print("\n📊 DENSE SUBGRAPH ANALYSIS")
        print("-" * 30)
        
        print("🔍 Finding densely connected regions...")
        
        # Get all relationships
        relationships = await self.graphiti.search_relationships("", limit=200)
          # Build adjacency count
        entity_connections = defaultdict(set)
        for rel in relationships:
            source = self._extract_property(rel, 'source', '')
            target = self._extract_property(rel, 'target', '')
            entity_connections[source].add(target)
            entity_connections[target].add(source)
        
        # Find entities with high local connectivity
        dense_regions = []
        
        for entity, connections in entity_connections.items():
            if len(connections) >= 3:  # At least 3 connections
                # Check how many of the connected entities are also connected to each other
                interconnections = 0
                total_possible = len(connections) * (len(connections) - 1) // 2
                
                connections_list = list(connections)
                for i, entity1 in enumerate(connections_list):
                    for entity2 in connections_list[i+1:]:
                        if entity2 in entity_connections.get(entity1, set()):
                            interconnections += 1
                
                density = interconnections / max(total_possible, 1)
                
                if density > 0.3:  # 30% interconnected
                    dense_regions.append({
                        'center': entity,
                        'connections': len(connections),
                        'density': density,
                        'members': list(connections)
                    })
        
        dense_regions.sort(key=lambda x: x['density'], reverse=True)
        
        if dense_regions:
            print(f"✅ Found {len(dense_regions)} dense regions:")
            for i, region in enumerate(dense_regions[:5], 1):
                center = region['center']
                connections = region['connections']
                density = region['density']
                print(f"   {i}. Center: {center}")
                print(f"      Connections: {connections}, Density: {density:.2f}")
                print(f"      Members: {', '.join(region['members'][:3])}{'...' if len(region['members']) > 3 else ''}")
                print()
        else:
            print("❌ No dense subgraphs found")

    async def _type_based_subgraphs(self):
        """Analyze subgraphs based on entity types"""
        print("\n🏷️ TYPE-BASED SUBGRAPH ANALYSIS")
        print("-" * 35)
          # Get all entities and group by type
        entities = await self.graphiti.search_entities("", limit=200)
        entity_types = defaultdict(list)
        for entity in entities:
            entity_type = self._extract_property(entity, 'type', 'unknown')
            entity_types[entity_type].append(self._extract_property(entity, 'name', 'Unknown'))
        
        print("📊 Available entity types:")
        for i, (entity_type, type_entities) in enumerate(entity_types.items(), 1):
            print(f"   {i}. {entity_type} ({len(type_entities)} entities)")
        
        choice = input("Enter type number to analyze: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(entity_types):
                selected_type = list(entity_types.keys())[choice_idx]
                selected_entities = entity_types[selected_type]
                
                print(f"\n🔬 Analyzing {selected_type} subgraph...")
                
                # Find relationships within this type
                internal_relationships = []
                external_relationships = []
                for entity_name in selected_entities:
                    relationships = await self._get_entity_relationships(entity_name)
                    for rel in relationships:
                        source = self._extract_property(rel, 'source', '')
                        target = self._extract_property(rel, 'target', '')
                        
                        other_entity = target if source == entity_name else source
                        
                        if other_entity in selected_entities:
                            internal_relationships.append(rel)
                        else:
                            external_relationships.append(rel)
                
                print(f"   📊 Subgraph statistics:")
                print(f"      👥 Entities: {len(selected_entities)}")
                print(f"      🔗 Internal relationships: {len(internal_relationships)}")
                print(f"      🌐 External relationships: {len(external_relationships)}")
                
                if len(selected_entities) > 1:
                    internal_density = len(internal_relationships) / len(selected_entities)
                    print(f"      📈 Internal density: {internal_density:.2f}")
                
                # Show sample relationships
                if internal_relationships:
                    print(f"\n   🔗 Sample internal relationships:")
                    for rel in internal_relationships[:3]:
                        source = self._extract_property(rel, 'source', '')
                        target = self._extract_property(rel, 'target', '')
                        rel_type = self._extract_property(rel, 'type', 'unknown')
                        print(f"      • {source} → {rel_type} → {target}")
                
                if external_relationships:
                    print(f"\n   🌐 Sample external relationships:")
                    external_targets = Counter()
                    for rel in external_relationships:
                        source = self._extract_property(rel, 'source', '')
                        target = self._extract_property(rel, 'target', '')
                        other_entity = target if source in selected_entities else source
                        external_targets[other_entity] += 1
                    
                    for target, count in external_targets.most_common(3):
                        print(f"      • {target}: {count} connections")
                        
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Invalid choice!")

    async def _interpret_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Use LLM to interpret natural language queries and suggest search strategies"""
        try:
            prompt = f"""
            Analyze this natural language query for graph exploration and provide structured guidance.
            
            Query: "{query}"
            
            Determine:
            1. Query intent (search_entities, search_relationships, explore_communities, analyze_subgraphs, or overview)
            2. Key search terms (entities, concepts, or patterns to look for)
            3. Suggested search strategy (exact_match, semantic_search, broad_exploration)
            4. Expected result type (specific_entities, relationship_patterns, community_structures, statistical_overview)
            5. Confidence level (0.0 to 1.0)
            
            Return JSON in this exact format:
            {{
                "intent": "search_entities|search_relationships|explore_communities|analyze_subgraphs|overview",
                "search_terms": ["term1", "term2", "term3"],
                "strategy": "exact_match|semantic_search|broad_exploration",
                "result_type": "specific_entities|relationship_patterns|community_structures|statistical_overview",
                "confidence": 0.85,
                "explanation": "Brief explanation of the interpretation"
            }}
            
            Only return valid JSON, no other text.
            """
            
            response = await self.graphiti.openai_client.chat.completions.create(
                model=self.graphiti.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            interpretation = json.loads(response.choices[0].message.content)
            return interpretation
            
        except Exception as e:
            print(f"⚠️  Query interpretation failed: {e}")
            # Fallback to basic interpretation
            return {
                "intent": "search_entities",
                "search_terms": await self._extract_search_keywords(query),
                "strategy": "semantic_search",
                "result_type": "specific_entities",
                "confidence": 0.5,
                "explanation": "Fallback interpretation due to LLM error"
            }

    async def _interpret_search_query(self, query: str) -> Dict[str, Any]:
        """Interpret natural language query to determine search strategy using LLM"""
        try:
            prompt = f"""
            Analyze this search query and determine the best search strategy and intent.
            
            Query: "{query}"
            
            Determine:
            1. Search intent (specific_entity, relationship_discovery, community_exploration, broad_exploration)
            2. Entity types likely to be relevant (person, organization, product, event, location, concept)
            3. Search strategy (exact_match, semantic_search, broad_exploration)
            4. Suggested search terms (3-5 terms)
            
            Return JSON in this format:
            {{
                "intent": "specific_entity|relationship_discovery|community_exploration|broad_exploration",
                "entity_types": ["person", "organization", "product"],
                "strategy": "exact_match|semantic_search|broad_exploration",
                "search_terms": ["term1", "term2", "term3"],
                "confidence": 0.8
            }}
            
            Only return valid JSON, no other text.
            """
            
            response = await self.graphiti.openai_client.chat.completions.create(
                model=self.graphiti.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            interpretation = json.loads(response.choices[0].message.content)
            return interpretation
            
        except Exception as e:
            print(f"⚠️  Query interpretation failed, using fallback: {e}")
            # Fallback interpretation
            return {
                "intent": "broad_exploration",
                "entity_types": ["person", "organization", "product"],
                "strategy": "semantic_search",
                "search_terms": query.split()[:3],
                "confidence": 0.5
            }

    async def _enhance_search_results_with_llm(self, query: str, entities: List[Dict], interpretation: Dict) -> List[Dict]:
        """Enhance search results with LLM insights and analysis"""
        try:
            # Prepare entity summaries for LLM
            entity_summaries = []
            for entity in entities[:10]:  # Limit to top 10 for LLM processing
                name = self._extract_property(entity, 'name', self._extract_property(entity, 'id', 'Unknown'))
                entity_type = self._extract_property(entity, 'type', self._extract_property(entity, 'entity_type', 'unknown'))
                description = self._extract_property(entity, 'description', '')
                entity_summaries.append(f"- {name} ({entity_type}): {description}")
            
            entities_text = "\n".join(entity_summaries)
            
            prompt = f"""
            Analyze these search results for the query: "{query}"
            
            Found entities:
            {entities_text}
            
            Provide:
            1. Key insights about the results
            2. Patterns or connections you notice
            3. 3 follow-up questions that would be valuable
            4. Any gaps or additional areas to explore
            
            Return JSON in this format:
            {{
                "insights": "Brief summary of key insights",
                "patterns": ["pattern1", "pattern2"],
                "follow_up_queries": ["question1", "question2", "question3"],
                "gaps": "Areas that might be missing or worth exploring"
            }}
            
            Only return valid JSON, no other text.
            """
            
            response = await self.graphiti.openai_client.chat.completions.create(
                model=self.graphiti.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )
            
            enhancement = json.loads(response.choices[0].message.content)
            self._last_enhancement = enhancement  # Store for display
            
            return entities
            
        except Exception as e:
            print(f"⚠️  Result enhancement failed: {e}")
            return entities

    def _extract_property(self, entity: Dict[str, Any], property_name: str, default: str = '') -> str:
        """Extract property from entity, handling both dict and Cosmos DB valueMap(true) list formats"""
        if not isinstance(entity, dict):
            return default
            
        value = entity.get(property_name, default)
        
        # Handle Cosmos DB valueMap(true) format where properties are lists
        if isinstance(value, list):
            return value[0] if value else default
        
        return str(value) if value is not None else default
        

async def main():
    """Main function to run the graph explorer"""
    explorer = GraphExplorer()
    await explorer.run_interactive_session()

if __name__ == "__main__":
    asyncio.run(main())
