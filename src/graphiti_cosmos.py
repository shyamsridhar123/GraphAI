"""
Graphiti-Cosmos Bridge: A Graphiti-inspired implementation for Azure Cosmos DB

This module provides Graphiti-like functionality using Azure Cosmos DB Gremlin API
instead of Neo4j. It maintains the core concepts of episodic data ingestion,
temporal tracking, and hybrid search while adapting to Cosmos DB's capabilities.
"""

import os
import json
import asyncio
import platform
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import numpy as np
from openai import AsyncAzureOpenAI
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EntityType(Enum):
    """Supported entity types for knowledge graph"""
    PERSON = "person"
    ORGANIZATION = "organization"
    PRODUCT = "product"
    CONCEPT = "concept"
    EVENT = "event"
    LOCATION = "location"


class RelationType(Enum):
    """Supported relationship types"""
    RELATED_TO = "related_to"
    WORKS_FOR = "works_for"
    LOCATED_IN = "located_in"
    CREATED_BY = "created_by"
    BELONGS_TO = "belongs_to"
    HAPPENED_AT = "happened_at"


@dataclass
class Episode:
    """Represents a data episode for ingestion"""
    content: str
    episode_id: str
    source: str = "user_input"
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Entity:
    """Represents a knowledge graph entity"""
    name: str
    entity_type: EntityType
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    source_entity: str
    target_entity: str
    relation_type: RelationType
    description: Optional[str] = None
    confidence: float = 1.0
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    properties: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.valid_from is None:
            self.valid_from = datetime.now(timezone.utc)
        if self.properties is None:
            self.properties = {}


class GraphitiCosmosConfig:
    """Configuration for Graphiti-Cosmos integration"""
    
    def __init__(self):
        # Cosmos DB Configuration
        self.cosmos_endpoint = f"wss://{os.getenv('COSMOS_ENDPOINT')}:443/"
        self.cosmos_username = os.getenv('COSMOS_USERNAME')
        self.cosmos_password = os.getenv('COSMOS_PASSWORD')
        
        # Azure OpenAI Configuration
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        self.azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        
        # Model Configuration
        self.llm_deployment = os.getenv('AZURE_OPENAI_LLM_DEPLOYMENT', 'gpt-4o')
        self.embeddings_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT', 'text-embedding-3-large')
        
        # Graphiti Configuration
        self.group_name = os.getenv('GRAPHITI_GROUP_NAME', 'default_graph')
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present"""
        required_vars = [
            'COSMOS_ENDPOINT', 'COSMOS_USERNAME', 'COSMOS_PASSWORD',
            'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")


class GraphitiCosmos:
    """
    Graphiti-inspired knowledge graph implementation using Azure Cosmos DB.
    
    This class provides similar functionality to Graphiti but adapted for Cosmos DB
    Gremlin API, including episodic data ingestion, entity extraction, relationship
    mapping, and hybrid search capabilities.
    """
    
    def __init__(self, config: Optional[GraphitiCosmosConfig] = None):
        self.config = config or GraphitiCosmosConfig()
        self.gremlin_client = None
        self.openai_client = None
        self.group_name = self.config.group_name
        
    async def initialize(self):
        """Initialize the Graphiti-Cosmos system"""
        await self._initialize_cosmos_client()
        await self._initialize_openai_client()
        await self._setup_graph_schema()
        
    async def _initialize_cosmos_client(self):
        """Initialize Cosmos DB Gremlin client"""
        try:
            # Create client with proper async handling
            import threading
            
            def create_client():
                return client.Client(
                    self.config.cosmos_endpoint,
                    'g',
                    username=self.config.cosmos_username,
                    password=self.config.cosmos_password,
                    message_serializer=serializer.GraphSONSerializersV2d0()
                )
            
            # Run client creation in a thread to avoid event loop conflicts
            loop = asyncio.get_event_loop()
            self.gremlin_client = await loop.run_in_executor(None, create_client)
            
            print("✅ Connected to Azure Cosmos DB")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Cosmos DB: {e}")
    
    async def _initialize_openai_client(self):
        """Initialize Azure OpenAI client"""
        try:
            self.openai_client = AsyncAzureOpenAI(
                api_key=self.config.azure_openai_key,
                api_version=self.config.azure_openai_api_version,
                azure_endpoint=self.config.azure_openai_endpoint
            )
            print("✅ Connected to Azure OpenAI")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Azure OpenAI: {e}")
    
    async def _execute_gremlin_query(self, query: str, bindings: Dict[str, Any] = None):
        """Execute Gremlin query safely in async context"""
        try:
            loop = asyncio.get_event_loop()
            
            def execute_query():
                result = self.gremlin_client.submit(query, bindings or {})
                return result.all().result()
            
            return await loop.run_in_executor(None, execute_query)
        except Exception as e:
            print(f"❌ Error executing Gremlin query: {e}")
            raise
    
    async def _setup_graph_schema(self):
        """Setup basic graph schema for knowledge graph"""
        try:
            # Create episode vertex label
            print("🔧 Setting up graph schema...")
            
            # Note: Cosmos DB Gremlin doesn't require explicit schema creation
            # but we can create some initial structure
            
            print("✅ Graph schema setup complete")
        except Exception as e:
            print(f"⚠️  Warning: Schema setup failed: {e}")
    
    async def add_episode(self, episode: Episode) -> str:
        """Add an episode to the knowledge graph"""
        try:
            print(f"📝 Processing episode: {episode.episode_id}")
            
            # Extract entities and relationships from the episode
            entities = await self._extract_entities(episode.content)
            relationships = await self._extract_relationships(episode.content, entities)
            
            # Create episode vertex
            episode_vertex_id = await self._create_episode_vertex(episode)
            
            # Create or update entities
            entity_ids = []
            for entity in entities:
                entity_id = await self._create_or_update_entity(entity, episode.episode_id)
                entity_ids.append(entity_id)
                
                # Connect episode to entity
                await self._create_relationship_edge(
                    episode_vertex_id, entity_id, "mentions", 
                    {"confidence": 0.8, "episode_id": episode.episode_id}
                )
            
            # Create relationships between entities
            for relationship in relationships:
                await self._create_relationship_from_entities(relationship, episode.episode_id)
            
            print(f"✅ Episode {episode.episode_id} processed successfully")
            print(f"   - Entities: {len(entities)}")
            print(f"   - Relationships: {len(relationships)}")
            
            return episode_vertex_id
            
        except Exception as e:
            print(f"❌ Error processing episode {episode.episode_id}: {e}")
            raise
    
    async def _extract_entities(self, content: str) -> List[Entity]:
        """Extract entities from text using Azure OpenAI"""
        try:
            prompt = f"""
            Extract entities from the following text. For each entity, determine:
            1. Name (exact text from content)
            2. Type (person, organization, product, concept, event, location)
            3. Brief description
            
            Text: {content}
            
            Return a JSON array of entities in this format:
            [
                {{
                    "name": "entity name",
                    "type": "entity_type",
                    "description": "brief description"
                }}
            ]
            
            Only return valid JSON, no other text.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            entities_data = json.loads(response.choices[0].message.content)
            entities = []
            
            for entity_data in entities_data:
                try:
                    entity_type = EntityType(entity_data['type'].lower())
                    entity = Entity(
                        name=entity_data['name'],
                        entity_type=entity_type,
                        description=entity_data.get('description', '')
                    )
                    
                    # Generate embedding for the entity
                    entity.embedding = await self._generate_embedding(
                        f"{entity.name} {entity.description}"
                    )
                    
                    entities.append(entity)
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Skipping invalid entity: {entity_data} - {e}")
            
            return entities
            
        except Exception as e:
            print(f"❌ Error extracting entities: {e}")
            return []
    
    async def _extract_relationships(self, content: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities"""
        if len(entities) < 2:
            return []
        
        try:
            entity_names = [entity.name for entity in entities]
            
            prompt = f"""
            Given the following text and entities, identify relationships between entities.
            
            Text: {content}
            Entities: {entity_names}
            
            For each relationship, determine:
            1. Source entity (must be from the entity list)
            2. Target entity (must be from the entity list)
            3. Relationship type (related_to, works_for, located_in, created_by, belongs_to, happened_at)
            4. Description of the relationship
            5. Confidence (0.0 to 1.0)
            
            Return a JSON array:
            [
                {{
                    "source": "source entity name",
                    "target": "target entity name", 
                    "type": "relationship_type",
                    "description": "relationship description",
                    "confidence": 0.8
                }}
            ]
            
            Only return valid JSON, no other text.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            relationships_data = json.loads(response.choices[0].message.content)
            relationships = []
            
            for rel_data in relationships_data:
                try:
                    relation_type = RelationType(rel_data['type'].lower())
                    relationship = Relationship(
                        source_entity=rel_data['source'],
                        target_entity=rel_data['target'],
                        relation_type=relation_type,
                        description=rel_data.get('description', ''),
                        confidence=float(rel_data.get('confidence', 0.5))
                    )
                    relationships.append(relationship)
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Skipping invalid relationship: {rel_data} - {e}")
            
            return relationships
            
        except Exception as e:
            print(f"❌ Error extracting relationships: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Azure OpenAI"""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.config.embeddings_deployment,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return []
    async def _create_episode_vertex(self, episode: Episode) -> str:
        """Create or update episode vertex in Cosmos DB"""
        episode_id = f"episode_{episode.episode_id}"
        
        # Check if episode exists
        check_query = "g.V(episodeId).hasLabel('episode')"
        existing = await self._execute_gremlin_query(check_query, {'episodeId': episode_id})
        
        if existing:
            # Update existing episode
            print(f"📝 Episode {episode.episode_id} already exists, updating...")
            query = """
            g.V(episodeId)
                .property('content', content)
                .property('source', source)
                .property('timestamp', timestamp)
                .property('last_updated', lastUpdated)
            """
            
            bindings = {
                'episodeId': episode_id,
                'content': episode.content[:2000],  # Limit content length
                'source': episode.source,
                'timestamp': episode.timestamp.isoformat(),
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
        else:
            # Create new episode
            print(f"📝 Creating new episode: {episode.episode_id}")
            query = """
            g.addV('episode')
                .property('id', episodeId)
                .property('partitionKey', pk)
                .property('content', content)
                .property('source', source)
                .property('timestamp', timestamp)
                .property('created_at', createdAt)
                .property('group_name', groupName)
            """
            
            bindings = {
                'episodeId': episode_id,
                'pk': self.group_name,
                'content': episode.content[:2000],  # Limit content length
                'source': episode.source,
                'timestamp': episode.timestamp.isoformat(),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'groupName': self.group_name
            }
        
        result = await self._execute_gremlin_query(query, bindings)
        
        return episode_id
    
    async def _create_or_update_entity(self, entity: Entity, episode_id: str) -> str:
        """Create or update entity vertex"""
        entity_id = f"entity_{entity.name.replace(' ', '_').lower()}"
        
        # Check if entity exists
        check_query = "g.V(entityId).hasLabel('entity')"
        existing = await self._execute_gremlin_query(check_query, {'entityId': entity_id})
        
        if existing:
            # Update existing entity
            update_query = """
            g.V(entityId)
                .property('description', description)
                .property('last_updated', timestamp)
                .property('last_episode', episodeId)
            """
            
            bindings = {
                'entityId': entity_id,
                'description': entity.description,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'episodeId': episode_id
            }
        else:
            # Create new entity
            update_query = """
            g.addV('entity')
                .property('id', entityId)
                .property('partitionKey', pk)
                .property('name', name)
                .property('entity_type', entityType)
                .property('description', description)
                .property('created_at', timestamp)
                .property('group_name', groupName)
                .property('first_episode', episodeId)
            """
            
            bindings = {
                'entityId': entity_id,
                'pk': self.group_name,
                'name': entity.name,
                'entityType': entity.entity_type.value,
                'description': entity.description or '',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'groupName': self.group_name,
                'episodeId': episode_id
            }
        
        result = await self._execute_gremlin_query(update_query, bindings)
        
        # Store embedding if available
        if entity.embedding:
            await self._store_entity_embedding(entity_id, entity.embedding)
        
        return entity_id
    async def _store_entity_embedding(self, entity_id: str, embedding: List[float]):
        """Store entity embedding (simplified - Gremlin API doesn't support vector search)"""
        # Note: Cosmos DB Gremlin API doesn't support vector storage/search
        # Azure Cosmos DB DOES support embeddings via NoSQL API with vector indexing
        # In production, you'd use either:
        # 1. Azure Cosmos DB NoSQL API with vector search capabilities
        # 2. Azure Cognitive Search for hybrid vector + text search
        # 3. Dual storage: Gremlin for graph + NoSQL for vectors
        
        # Store embedding as a property (truncated for demo)
        embedding_str = json.dumps(embedding[:10])  # Store only first 10 dimensions
        
        query = "g.V(entityId).property('embedding_sample', embeddingStr)"
        bindings = {
            'entityId': entity_id,
            'embeddingStr': embedding_str
        }
        
        try:
            result = await self._execute_gremlin_query(query, bindings)
        except Exception as e:
            print(f"⚠️  Warning: Could not store embedding for {entity_id}: {e}")
    
    async def _create_relationship_edge(self, source_id: str, target_id: str, 
                                      relation_type: str, properties: Dict[str, Any] = None):
        """Create relationship edge between vertices"""
        properties = properties or {}
        
        query = """
        g.V(sourceId).addE(relationType).to(g.V(targetId))
            .property('created_at', timestamp)
            .property('group_name', groupName)
        """
        
        bindings = {
            'sourceId': source_id,
            'targetId': target_id,
            'relationType': relation_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'groupName': self.group_name
        }
        
        # Add additional properties
        for key, value in properties.items():
            query += f".property('{key}', {key})"
            bindings[key] = value
        
        try:
            result = await self._execute_gremlin_query(query, bindings)
        except Exception as e:
            print(f"⚠️  Warning: Could not create relationship {source_id} -> {target_id}: {e}")
    
    async def _create_relationship_from_entities(self, relationship: Relationship, episode_id: str):
        """Create relationship edge from relationship object"""
        source_id = f"entity_{relationship.source_entity.replace(' ', '_').lower()}"
        target_id = f"entity_{relationship.target_entity.replace(' ', '_').lower()}"
        
        properties = {
            'description': relationship.description,
            'confidence': relationship.confidence,
            'episode_id': episode_id,
            'valid_from': relationship.valid_from.isoformat()        }
        
        await self._create_relationship_edge(
            source_id, target_id, relationship.relation_type.value, properties
        )
        
    async def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities using text similarity"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # First try exact name match
            exact_match_query = """
            g.V().hasLabel('entity')
                .has('group_name', groupName)
                .has('name', searchTerm)
                .valueMap(true)
                .limit(limitCount)
            """
            
            # Try a simpler approach - get all entities first then filter in Python
            all_entities_query = """
            g.V().hasLabel('entity')
                .has('group_name', groupName)
                .valueMap(true)
                .limit(100)
            """
            
            bindings = {
                'groupName': self.group_name,
                'limitCount': limit
            }
            
            # Try exact match first
            entities = await self._execute_gremlin_query(exact_match_query, {
                'groupName': self.group_name,
                'searchTerm': query,
                'limitCount': limit
            })
            
            if not entities:
                # Get all entities and filter in Python for better compatibility
                all_entities = await self._execute_gremlin_query(all_entities_query, bindings)
                
                # Filter entities that contain the search term
                entities = []
                query_lower = query.lower()
                for entity in all_entities:
                    name = entity.get('name', [''])[0] if isinstance(entity.get('name', ['']), list) else entity.get('name', '')
                    description = entity.get('description', [''])[0] if isinstance(entity.get('description', ['']), list) else entity.get('description', '')
                    
                    if (query_lower in name.lower() or query_lower in description.lower()):
                        entities.append(entity)
                        if len(entities) >= limit:
                            break
            
            # Format results
            formatted_entities = []
            for entity in entities:
                try:
                    formatted_entity = {
                        'id': entity.get('id', [''])[0] if isinstance(entity.get('id', ['']), list) else entity.get('id', ''),
                        'name': entity.get('name', [''])[0] if isinstance(entity.get('name', ['']), list) else entity.get('name', ''),
                        'type': entity.get('entity_type', [''])[0] if isinstance(entity.get('entity_type', ['']), list) else entity.get('entity_type', ''),
                        'description': entity.get('description', [''])[0] if isinstance(entity.get('description', ['']), list) else entity.get('description', '')
                    }
                    formatted_entities.append(formatted_entity)
                except Exception as format_error:
                    print(f"Warning: Could not format entity: {format_error}")
                    print(f"Raw entity: {entity}")
            
            return formatted_entities
            
        except Exception as e:
            print(f"❌ Error searching entities: {e}")
            return []
            
    async def search_relationships(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search relationships using text similarity"""
        try:
            # Simplified approach - get edges with basic info
            simple_edges_query = """
            g.E()
                .has('group_name', groupName)
                .limit(limitCount)
                .as('edge')
                .project('edge_props', 'edge_label', 'source_id', 'target_id')
                .by(valueMap(true))
                .by(label())
                .by(outV().id())
                .by(inV().id())
            """
            
            bindings = {
                'groupName': self.group_name,
                'limitCount': limit * 2  # Get more to filter
            }
            
            # Get relationships
            relationships_data = await self._execute_gremlin_query(simple_edges_query, bindings)
            
            # Now get the vertex names separately for each relationship
            formatted_relationships = []
            query_lower = query.lower()
            
            for rel_data in relationships_data:
                try:
                    edge_props = rel_data.get('edge_props', {})
                    edge_label = rel_data.get('edge_label', 'unknown')
                    source_id = rel_data.get('source_id')
                    target_id = rel_data.get('target_id')
                    
                    # Handle list vs single results
                    if isinstance(edge_label, list) and edge_label:
                        edge_label = edge_label[0]
                    
                    # Get vertex names separately
                    source_name = "Unknown"
                    target_name = "Unknown"
                    
                    try:
                        # Get source vertex name
                        source_query = "g.V(sourceId).values('name')"
                        source_result = await self._execute_gremlin_query(source_query, {'sourceId': source_id})
                        if source_result and isinstance(source_result, list) and source_result:
                            source_name = source_result[0]
                            if isinstance(source_name, list):
                                source_name = source_name[0]
                    except:
                        pass
                    
                    try:
                        # Get target vertex name
                        target_query = "g.V(targetId).values('name')"
                        target_result = await self._execute_gremlin_query(target_query, {'targetId': target_id})
                        if target_result and isinstance(target_result, list) and target_result:
                            target_name = target_result[0]
                            if isinstance(target_name, list):
                                target_name = target_name[0]
                    except:
                        pass
                    
                    # Check if the query matches
                    edge_description = edge_props.get('description', [''])[0] if isinstance(edge_props.get('description', ['']), list) else edge_props.get('description', '')
                    
                    if (query_lower in edge_label.lower() or 
                        query_lower in edge_description.lower() or
                        query_lower in source_name.lower() or 
                        query_lower in target_name.lower()):
                        
                        # Create a formatted relationship
                        formatted_rel = {
                            'source': source_name,
                            'target': target_name,
                            'relationship': edge_label,
                            'properties': edge_props
                        }
                        
                        formatted_relationships.append(formatted_rel)
                        if len(formatted_relationships) >= limit:
                            break
                            
                except Exception as e:
                    print(f"Warning: Could not process relationship: {e}")
            
            return formatted_relationships
            
        except Exception as e:
            print(f"❌ Error searching relationships: {e}")
            return []
            
    async def get_entity_neighbors(self, entity_name: str, max_hops: int = 2) -> Dict[str, Any]:
        """Get neighboring entities and relationships"""
        try:
            # First, search for the entity to get the correct ID
            search_results = await self.search_entities(entity_name, limit=1)
            
            if not search_results:
                print(f"Entity '{entity_name}' not found")
                return {'center_entity': entity_name, 'entities': [], 'relationships': [], 'paths': []}
            
            # Get the ID from the search result
            entity_id = search_results[0]['id']
            
            # Find direct neighbors without using complex path queries
            direct_query = """
            g.V(entityId)
                .bothE()
                .as('e')
                .bothV()
                .as('v')
                .select('e', 'v')
                .by(valueMap(true))
                .by(valueMap(true))
                .limit(20)
            """
            
            bindings = {
                'entityId': entity_id
            }
            
            neighbors_data = await self._execute_gremlin_query(direct_query, bindings)
            
            # Format the results into entities and relationships
            entities = set()
            relationships = []
            
            for item in neighbors_data:
                if isinstance(item, dict) and 'e' in item and 'v' in item:
                    # Extract edge data
                    edge = item['e']
                    vertex = item['v']
                    
                    # Format vertex as entity
                    if isinstance(vertex, dict) and 'name' in vertex:
                        entity_name = vertex['name']
                        if isinstance(entity_name, list):
                            entity_name = entity_name[0]
                        entities.add(entity_name)
                    
                    # Format edge as relationship
                    if isinstance(edge, dict) and 'label' in edge:
                        rel_type = edge.get('label', 'unknown')
                        relationships.append({
                            'relationship': rel_type,
                            'properties': edge
                        })
            
            # Process and format the neighborhood
            neighborhood = {
                'center_entity': entity_name,
                'entities': list(entities),
                'relationships': relationships,
                'paths': []  # Complex paths handling is problematic, use simpler approach
            }
            
            return neighborhood
            
        except Exception as e:
            print(f"❌ Error getting entity neighbors: {e}")
            return {'center_entity': entity_name, 'entities': [], 'relationships': [], 'paths': []}
    
    async def get_graph_stats(self) -> Dict[str, int]:
        """Get basic statistics about the knowledge graph"""
        try:
            stats = {}
            
            # Count episodes
            episode_query = "g.V().hasLabel('episode').has('group_name', groupName).count()"
            episode_result = await self._execute_gremlin_query(episode_query, {'groupName': self.group_name})
            stats['episodes'] = episode_result[0] if episode_result else 0
            
            # Count entities
            entity_query = "g.V().hasLabel('entity').has('group_name', groupName).count()"
            entity_result = await self._execute_gremlin_query(entity_query, {'groupName': self.group_name})
            stats['entities'] = entity_result[0] if entity_result else 0
            
            # Count relationships
            rel_query = "g.E().has('group_name', groupName).count()"
            rel_result = await self._execute_gremlin_query(rel_query, {'groupName': self.group_name})
            stats['relationships'] = rel_result[0] if rel_result else 0
            
            return stats
        except Exception as e:
            print(f"❌ Error getting graph stats: {e}")
            return {'episodes': 0, 'entities': 0, 'relationships': 0}
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """General search method that searches both entities and relationships"""
        try:
            # Search entities
            entity_results = await self.search_entities(query, limit//2)
            
            # Search relationships  
            relationship_results = await self.search_relationships(query, limit//2)
            
            # Combine and flatten results for easier access
            combined_results = []
            
            # Add entities in a simplified format
            for entity in entity_results:
                combined_results.append({
                    'type': 'entity',
                    'name': entity.get('name', ''),
                    'description': entity.get('description', ''),
                    'entity_type': entity.get('type', ''),
                    'source': 'entity_search'
                })
            
            # Add relationships in a simplified format
            for rel in relationship_results:
                combined_results.append({
                    'type': 'relationship', 
                    'name': f"{rel.get('source', '')} → {rel.get('target', '')}",
                    'description': rel.get('relationship', ''),
                    'relationship_type': rel.get('relationship', ''),
                    'source': 'relationship_search'
                })
            
            return combined_results[:limit]
            
        except Exception as e:
            print(f"❌ Error in general search: {e}")
            return []

    async def close(self):
        """Clean up resources"""
        try:
            if self.openai_client:
                await self.openai_client.close()
            if self.gremlin_client:
                # Use executor to avoid event loop conflicts
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.gremlin_client.close)
            print("✅ Graphiti-Cosmos client closed")
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {e}")
            # Don't raise - cleanup should be best effort


# Example usage functions
async def demo_graphiti_cosmos():
    """Demonstrate Graphiti-Cosmos functionality"""
    print("🚀 Starting Graphiti-Cosmos Demo")
    
    # Initialize the system
    graphiti = GraphitiCosmos()
    await graphiti.initialize()
    
    try:
        # Add some sample episodes
        episodes = [
            Episode(
                content="Alice works for Microsoft and is based in Seattle. She's working on AI projects.",
                episode_id="ep_001",
                source="demo"
            ),
            Episode(
                content="Microsoft released a new AI model called GPT-4 Turbo. Alice was part of the team that worked on it.",
                episode_id="ep_002", 
                source="demo"
            ),
            Episode(
                content="The AI model GPT-4 Turbo is used in many Microsoft products including Azure OpenAI Service.",
                episode_id="ep_003",
                source="demo"
            )
        ]
        
        # Process episodes
        for episode in episodes:
            await graphiti.add_episode(episode)
        
        # Search for entities
        print("\n🔍 Searching for entities related to 'Microsoft':")
        entities = await graphiti.search_entities("Microsoft", limit=5)
        for entity in entities:
            print(f"  - {entity['name']} ({entity['type']}): {entity['description']}")
        
        # Search for relationships
        print("\n🔗 Searching for relationships related to 'works':")
        relationships = await graphiti.search_relationships("works", limit=5)
        for rel in relationships:
            print(f"  - {rel['source']} → {rel['relationship']} → {rel['target']}")
        
        # Get graph statistics
        print("\n📊 Graph Statistics:")
        stats = await graphiti.get_graph_stats()
        for key, value in stats.items():
            print(f"  - {key.title()}: {value}")
        
        print("\n✅ Demo completed successfully!")
        
    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(demo_graphiti_cosmos())
