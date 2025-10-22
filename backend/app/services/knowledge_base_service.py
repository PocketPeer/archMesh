"""
Knowledge Base Service for ArchMesh PoC.

This service provides RAG (Retrieval-Augmented Generation) capabilities for storing
and retrieving architecture context using vector embeddings, graph databases, and
structured metadata storage.

Components:
- Pinecone: Vector embeddings for semantic search
- Neo4j: Graph database for architecture relationships
- PostgreSQL: Structured metadata and project information
- Sentence Transformers: Text embeddings for semantic similarity
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pinecone
from loguru import logger
from py2neo import Graph, Node, Relationship
from sentence_transformers import SentenceTransformer

from app.config import settings


class KnowledgeBaseService:
    """
    Service for storing and retrieving architecture knowledge using RAG.
    
    This service combines multiple storage technologies to provide comprehensive
    architecture knowledge management:
    
    - Vector Search (Pinecone): Semantic search across architecture descriptions
    - Graph Database (Neo4j): Relationship mapping between services and components
    - Relational Database (PostgreSQL): Structured metadata and project information
    - Embeddings (Sentence Transformers): Text-to-vector conversion for similarity
    
    Capabilities:
    - Index repository analysis results
    - Semantic search for similar architectures
    - Graph-based dependency analysis
    - Context generation for new features
    - Architecture pattern recommendations
    - Technology stack analysis
    """

    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        pinecone_environment: Optional[str] = None,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the Knowledge Base Service.
        
        Args:
            pinecone_api_key: Pinecone API key (optional, uses config if not provided)
            pinecone_environment: Pinecone environment (optional, uses config if not provided)
            neo4j_uri: Neo4j connection URI (optional, uses config if not provided)
            neo4j_user: Neo4j username (optional, uses config if not provided)
            neo4j_password: Neo4j password (optional, uses config if not provided)
            embedding_model: Sentence transformer model for embeddings
        """
        # Configuration
        self.pinecone_api_key = pinecone_api_key or getattr(settings, 'pinecone_api_key', None)
        self.pinecone_environment = pinecone_environment or getattr(settings, 'pinecone_environment', None)
        self.neo4j_uri = neo4j_uri or getattr(settings, 'neo4j_uri', 'bolt://localhost:7687')
        self.neo4j_user = neo4j_user or getattr(settings, 'neo4j_user', 'neo4j')
        self.neo4j_password = neo4j_password or getattr(settings, 'neo4j_password', 'password123')
        
        # Initialize components
        self.index = None
        self.embedder = None
        self.graph = None
        
        # Embedding model configuration
        self.embedding_model = embedding_model
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
        # Index configuration
        self.index_name = "archmesh-knowledge"
        
        # Initialize services
        self._initialize_services()
        
        logger.info("Knowledge Base Service initialized", extra={"service": "knowledge_base"})

    def _initialize_services(self) -> None:
        """Initialize Pinecone, Neo4j, and embedding model."""
        try:
            # Initialize Pinecone (updated for newer API)
            if self.pinecone_api_key and self.pinecone_environment:
                # For newer Pinecone versions, use PC() instead of init()
                try:
                    # Try new API first
                    from pinecone import Pinecone
                    pc = Pinecone(api_key=self.pinecone_api_key)
                    self.index = pc.Index(self.index_name)
                except (ImportError, AttributeError):
                    # Fallback to old API
                    pinecone.init(
                        api_key=self.pinecone_api_key,
                        environment=self.pinecone_environment
                    )
                    # Create or connect to index
                    if self.index_name not in pinecone.list_indexes():
                        pinecone.create_index(
                            name=self.index_name,
                            dimension=self.embedding_dimension,
                            metric="cosine",
                            pod_type="p1.x1"  # Small pod for development
                        )
                        logger.info(f"Created Pinecone index: {self.index_name}")
                    
                    self.index = pinecone.Index(self.index_name)
                    logger.info("Pinecone initialized successfully")
            else:
                logger.warning("Pinecone credentials not provided, vector search disabled")
            
            # Initialize embedding model
            self.embedder = SentenceTransformer(self.embedding_model)
            logger.info(f"Embedding model loaded: {self.embedding_model}")
            
            # Initialize Neo4j
            self.graph = Graph(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            # Test Neo4j connection
            self.graph.run("RETURN 1").data()
            logger.info("Neo4j connected successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Knowledge Base services: {str(e)}")
            raise

    async def index_repository_analysis(
        self,
        project_id: str,
        analysis: Dict[str, Any],
        repository_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index repository analysis results into knowledge base.
        
        This method stores architecture information across multiple storage systems:
        1. Creates embeddings for searchable content and stores in Pinecone
        2. Creates graph structure in Neo4j for relationship queries
        3. Stores structured metadata for project tracking
        
        Args:
            project_id: Unique identifier for the project
            repository_url: URL of the analyzed repository
            analysis: Complete repository analysis results
            metadata: Additional metadata for the project
            
        Returns:
            Dictionary with indexing results and statistics
            
        Raises:
            Exception: If indexing fails
        """
        try:
            logger.info(
                f"Starting repository analysis indexing",
                extra={
                    "project_id": project_id,
                    "repository_url": repository_url,
                    "service": "knowledge_base"
                }
            )
            
            # 1. Create text chunks for embedding
            chunks = self._create_searchable_chunks(project_id, analysis)
            logger.debug(f"Created {len(chunks)} text chunks for embedding")
            
            # 2. Generate embeddings and store in Pinecone
            repo_url = repository_url or analysis.get("repository_url", "")
            vector_results = await self._index_vectors(project_id, repo_url, chunks)
            
            # 3. Create graph structure in Neo4j
            graph_queries = self._create_architecture_graph(project_id, analysis)
            graph_results = await self._execute_graph_queries(graph_queries)
            
            # 4. Store metadata (would integrate with PostgreSQL in full implementation)
            metadata_results = await self._store_project_metadata(
                project_id, repo_url, analysis, metadata
            )
            
            result = {
                "project_id": project_id,
                "indexed_at": datetime.utcnow().isoformat(),
                "indexed_chunks": vector_results["chunks_indexed"],
                "created_nodes": graph_results["nodes_created"],
                "created_relationships": graph_results["relationships_created"],
                "metadata_stored": metadata_results["success"],
                "total_services": len(analysis.get("services", [])),
                "total_technologies": len(analysis.get("technology_stack", {}))
            }
            
            logger.info(
                f"Repository analysis indexing completed",
                extra={
                    "project_id": project_id,
                    "chunks_indexed": result["indexed_chunks"],
                    "nodes_created": result["created_nodes"],
                    "service": "knowledge_base"
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Failed to index repository analysis: {str(e)}",
                extra={
                    "project_id": project_id,
                    "repository_url": repository_url,
                    "service": "knowledge_base"
                }
            )
            raise

    def _create_searchable_chunks(self, project_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create text chunks from analysis for embedding.
        
        Args:
            project_id: Project identifier
            analysis: Repository analysis results
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        
        # Architecture overview chunk
        if "architecture" in analysis:
            arch = analysis["architecture"]
            text = f"""
            Architecture Style: {arch.get('architecture_style', 'Unknown')}
            Communication Patterns: {', '.join(arch.get('communication_patterns', []))}
            Data Storage: {json.dumps(arch.get('data_storage', {}), indent=2)}
            Deployment Strategy: {json.dumps(arch.get('deployment', {}), indent=2)}
            Security Approach: {json.dumps(arch.get('security', {}), indent=2)}
            Scalability Features: {json.dumps(arch.get('scalability', {}), indent=2)}
            """
            chunks.append({
                "id": f"{project_id}_arch_{len(chunks)}",
                "values": self._generate_embedding(text.strip()),
                "metadata": {
                    "project_id": project_id,
                    "chunk_type": "architecture",
                    "content": text.strip()[:1000],
                    "architecture_style": arch.get('architecture_style'),
                    "patterns": arch.get('architecture_patterns', [])
                }
            })
        
        # Service chunks
        if "services" in analysis:
            for service in analysis["services"]:
                text = f"""
                Service Name: {service.get('name', 'Unknown')}
                Service Type: {service.get('type', 'Unknown')}
                Technology Stack: {service.get('technology', 'Unknown')}
                Responsibilities: {', '.join(service.get('responsibilities', []))}
                Interfaces: {', '.join(service.get('interfaces', []))}
                Dependencies: {', '.join(service.get('dependencies', []))}
                Scalability: {service.get('scalability', 'Unknown')}
                """
                chunks.append({
                    "id": f"{project_id}_service_{len(chunks)}",
                    "values": self._generate_embedding(text.strip()),
                    "metadata": {
                        "project_id": project_id,
                        "chunk_type": "service",
                        "content": text.strip()[:1000],
                        "service_name": service.get('name'),
                        "service_type": service.get('type'),
                        "technology": service.get('technology')
                    }
                })
        
        # Technology stack chunk
        if "technology_stack" in analysis:
            tech = analysis["technology_stack"]
            text = f"""
            Programming Languages: {json.dumps(tech.get('languages', {}), indent=2)}
            Frameworks: {', '.join(tech.get('frameworks', []))}
            Databases: {', '.join(tech.get('databases', []))}
            Infrastructure Tools: {', '.join(tech.get('infrastructure', []))}
            Development Tools: {', '.join(tech.get('tools', []))}
            Build Tools: {', '.join(tech.get('build_tools', []))}
            Testing Frameworks: {', '.join(tech.get('testing_frameworks', []))}
            """
            chunks.append({
                "id": f"{project_id}_tech_{len(chunks)}",
                "values": self._generate_embedding(text.strip()),
                "metadata": {
                    "project_id": project_id,
                    "chunk_type": "technology",
                    "content": text.strip()[:1000],
                    "languages": list(tech.get('languages', {}).keys()) if isinstance(tech.get('languages'), dict) else [],
                    "frameworks": tech.get('frameworks', []),
                    "databases": tech.get('databases', [])
                }
            })
        
        # API contracts chunk
        if "api_contracts" in analysis and analysis["api_contracts"]:
            for contract in analysis["api_contracts"]:
                text = f"""
                API Contract: {contract.get('title', 'Unknown')}
                Type: {contract.get('type', 'Unknown')}
                Version: {contract.get('version', 'Unknown')}
                Endpoints: {contract.get('endpoints', 0)}
                Components: {', '.join(contract.get('components', []))}
                """
                chunks.append({
                    "id": f"{project_id}_api_{len(chunks)}",
                    "values": self._generate_embedding(text.strip()),
                    "metadata": {
                        "project_id": project_id,
                        "chunk_type": "api_contract",
                        "content": text.strip()[:1000],
                        "api_type": contract.get('type'),
                        "api_version": contract.get('version'),
                        "endpoints_count": contract.get('endpoints')
                    }
                })
        
        # Recommendations chunk
        if "recommendations" in analysis and analysis["recommendations"]:
            recommendations_text = []
            for rec in analysis["recommendations"]:
                recommendations_text.append(
                    f"Category: {rec.get('category', 'Unknown')} - "
                    f"Priority: {rec.get('priority', 'Unknown')} - "
                    f"Recommendation: {rec.get('recommendation', 'Unknown')}"
                )
            
            text = f"""
            Architecture Recommendations:
            {chr(10).join(recommendations_text)}
            """
            chunks.append({
                "id": f"{project_id}_rec_{len(chunks)}",
                "values": self._generate_embedding(text.strip()),
                "metadata": {
                    "project_id": project_id,
                    "chunk_type": "recommendations",
                    "content": text.strip()[:1000],
                    "recommendations_count": len(analysis["recommendations"]),
                    "categories": list(set(rec.get('category', 'Unknown') for rec in analysis["recommendations"]))
                }
            })
        
        return chunks

    async def _index_vectors(
        self,
        project_id: str,
        repository_url: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate embeddings and store vectors in Pinecone.
        
        Args:
            project_id: Project identifier
            repository_url: Repository URL
            chunks: Text chunks to embed
            
        Returns:
            Dictionary with indexing results
        """
        if not self.index or not self.embedder:
            logger.warning("Pinecone or embedder not available, skipping vector indexing")
            return {"chunks_indexed": 0, "success": False}
        
        try:
            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedder.encode(texts).tolist()
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                vector_id = f"{project_id}_{uuid.uuid4().hex[:8]}_{i}"
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "project_id": project_id,
                        "repository_url": repository_url,
                        "chunk_type": chunk["type"],
                        "content": chunk["text"][:1000],  # Truncate for metadata
                        "indexed_at": datetime.utcnow().isoformat(),
                        **chunk.get("metadata", {})
                    }
                })
            
            # Upload to Pinecone
            self.index.upsert(vectors=vectors)
            
            logger.debug(f"Indexed {len(vectors)} vectors in Pinecone")
            return {"chunks_indexed": len(vectors), "success": True}
            
        except Exception as e:
            logger.error(f"Error indexing vectors: {str(e)}")
            return {"chunks_indexed": 0, "success": False, "error": str(e)}

    def _create_architecture_graph(
        self,
        project_id: str,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Create graph representation queries for Neo4j.
        
        Args:
            project_id: Project identifier
            analysis: Repository analysis results
            
        Returns:
            List of Cypher queries
        """
        queries = []
        
        # Create project node query
        queries.append(f"""
        CREATE (p:Project {{
            id: '{project_id}',
            repository_url: '{analysis.get("repository_url", "")}',
            name: '{analysis.get("name", "")}',
            description: '{analysis.get("description", "")}',
            created_at: '{datetime.utcnow().isoformat()}'
        }})
        """)
        
        # Create service nodes
        if "services" in analysis:
            for service in analysis["services"]:
                queries.append(f"""
                CREATE (s:Service {{
                    project_id: '{project_id}',
                    name: '{service.get("name", "")}',
                    type: '{service.get("type", "")}',
                    technology: '{service.get("technology", "")}',
                    description: '{service.get("description", "")}'
                }})
                """)
                
                # Link service to project
                queries.append(f"""
                MATCH (p:Project {{id: '{project_id}'}})
                MATCH (s:Service {{name: '{service.get("name", "")}', project_id: '{project_id}'}})
                CREATE (p)-[:HAS_SERVICE]->(s)
                """)
        
        # Create dependency relationships
        if "dependencies" in analysis:
            for dep in analysis["dependencies"]:
                queries.append(f"""
                MATCH (s1:Service {{name: '{dep.get("from", "")}', project_id: '{project_id}'}})
                MATCH (s2:Service {{name: '{dep.get("to", "")}', project_id: '{project_id}'}})
                CREATE (s1)-[:DEPENDS_ON {{type: '{dep.get("type", "")}', description: '{dep.get("description", "")}'}}]->(s2)
                """)
        
        return queries

    async def _execute_graph_queries(self, queries: List[str]) -> Dict[str, Any]:
        """
        Execute graph queries in Neo4j.
        
        Args:
            queries: List of Cypher queries
            
        Returns:
            Dictionary with execution results
        """
        if not self.graph:
            logger.warning("Neo4j not available, skipping graph execution")
            return {"nodes_created": 0, "relationships_created": 0, "success": False}
        
        try:
            nodes_created = 0
            relationships_created = 0
            
            for query in queries:
                result = self.graph.run(query)
                # Count nodes and relationships created (simplified)
                if "CREATE" in query:
                    if "Service" in query or "Project" in query:
                        nodes_created += 1
                    if "HAS_SERVICE" in query or "DEPENDS_ON" in query:
                        relationships_created += 1
            
            logger.debug(f"Executed {len(queries)} graph queries")
            return {
                "nodes_created": nodes_created,
                "relationships_created": relationships_created,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error executing graph queries: {str(e)}")
            return {"nodes_created": 0, "relationships_created": 0, "success": False, "error": str(e)}

    async def _store_project_metadata(
        self,
        project_id: str,
        repository_url: str,
        analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Store project metadata (placeholder for PostgreSQL integration).
        
        Args:
            project_id: Project identifier
            repository_url: Repository URL
            analysis: Repository analysis results
            metadata: Additional metadata
            
        Returns:
            Dictionary with storage results
        """
        # In a full implementation, this would store data in PostgreSQL
        # For now, we'll just log the metadata
        try:
            project_metadata = {
                "project_id": project_id,
                "repository_url": repository_url,
                "analysis_summary": {
                    "services_count": len(analysis.get("architecture", {}).get("services", [])),
                    "languages_count": len(analysis.get("tech_stack", {}).get("languages", {})),
                    "frameworks_count": len(analysis.get("tech_stack", {}).get("frameworks", [])),
                    "architecture_style": analysis.get("architecture", {}).get("architecture_style", "Unknown")
                },
                "indexed_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            logger.debug(f"Project metadata prepared for storage: {project_metadata}")
            return {"success": True, "metadata": project_metadata}
            
        except Exception as e:
            logger.error(f"Error storing project metadata: {str(e)}")
            return {"success": False, "error": str(e)}

    async def search_similar_architectures(
        self,
        query: str,
        project_id: Optional[str] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar architectures using semantic search.
        
        Args:
            query: Natural language query
            project_id: Optional filter by project
            top_k: Number of results to return
            filters: Optional filter dictionary
            
        Returns:
            List of similar architecture results with scores and metadata
        """
        if not self.index or not self.embedder:
            logger.warning("Pinecone or embedder not available, returning empty results")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode([query])[0].tolist()
            
            # Prepare filter
            filter_dict = {}
            if project_id:
                filter_dict["project_id"] = project_id
            if filters:
                filter_dict.update(filters)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results
            formatted_results = []
            for match in results["matches"]:
                formatted_results.append({
                    "id": match["id"],
                    "similarity_score": match["score"],
                    "metadata": match["metadata"]
                })
            
            logger.debug(f"Found {len(formatted_results)} similar architectures for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar architectures: {str(e)}")
            return []

    async def get_service_dependencies(
        self,
        service_id: str
    ) -> List[Dict[str, Any]]:
        """
        Query Neo4j for service dependencies and relationships.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of service dependency information
        """
        if not self.graph:
            logger.warning("Neo4j not available, returning empty results")
            return []
        
        try:
            # Get specific service and its dependencies
            query = """
            MATCH (s:Service {name: $service_id})
            OPTIONAL MATCH (s)-[r:DEPENDS_ON]->(dep:Service)
            OPTIONAL MATCH (dep_by:Service)-[r2:DEPENDS_ON]->(s)
            RETURN s, r, dep, dep_by, r2
            """
            params = {"service_id": service_id}
            
            result = self.graph.run(query, params)
            records = [dict(record) for record in result]
            
            logger.debug(f"Retrieved {len(records)} service dependency records")
            return records
            
        except Exception as e:
            logger.error(f"Error querying service dependencies: {str(e)}")
            return []

    async def get_architecture_patterns(
        self,
        project_id: str
    ) -> List[Dict[str, Any]]:
        """
        Query Neo4j for architecture patterns.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of architecture patterns
        """
        if not self.graph:
            logger.warning("Neo4j not available, returning empty results")
            return []
        
        try:
            query = """
            MATCH (p:Project {id: $project_id})-[:HAS_ARCHITECTURE]->(a:Architecture)
            RETURN a
            """
            params = {"project_id": project_id}
            
            result = self.graph.run(query, params)
            records = [dict(record) for record in result]
            
            logger.debug(f"Retrieved {len(records)} architecture patterns")
            return records
            
        except Exception as e:
            logger.error(f"Error querying architecture patterns: {str(e)}")
            return []

    async def get_context_for_new_feature(
        self,
        feature_description: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Get relevant context for adding a new feature to existing project.
        
        This method provides RAG capabilities by retrieving relevant architecture
        context that can be used to inform new feature development.
        
        Args:
            feature_description: Description of the new feature
            project_id: Project identifier
            
        Returns:
            Dictionary with relevant context for feature development
        """
        try:
            logger.info(
                f"Getting context for new feature",
                extra={
                    "project_id": project_id,
                    "feature_description": feature_description[:100],
                    "service": "knowledge_base"
                }
            )
            
            # Search for similar features and patterns
            similar_results = await self.search_similar_architectures(
                query=feature_description,
                project_id=project_id,
                top_k=5
            )
            
            # Get existing services in project
            existing_services = await self.get_service_dependencies(project_id)
            
            # Get architecture patterns
            architecture_patterns = await self.get_architecture_patterns(project_id)
            
            # Get technology stack information
            tech_stack_context = await self._get_technology_context(project_id)
            
            # Generate recommendations
            recommendations = await self._generate_feature_recommendations(
                feature_description, similar_results, existing_services, tech_stack_context
            )
            
            context = {
                "feature_description": feature_description,
                "similar_features": similar_results,
                "existing_services": existing_services,
                "integration_patterns": architecture_patterns,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Generated context for new feature",
                extra={
                    "project_id": project_id,
                    "similar_patterns_count": len(similar_results),
                    "existing_services_count": len(existing_services),
                    "service": "knowledge_base"
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context for new feature: {str(e)}")
            return {
                "error": str(e),
                "feature_description": feature_description,
                "generated_at": datetime.utcnow().isoformat()
            }

    async def _get_technology_context(self, project_id: str) -> Dict[str, Any]:
        """Get technology stack context for a project."""
        if not self.graph:
            return {}
        
        try:
            query = """
            MATCH (p:Project {id: $project_id})
            OPTIONAL MATCH (p)-[:USES_LANGUAGE]->(l:Language)
            OPTIONAL MATCH (p)-[:USES_FRAMEWORK]->(f:Framework)
            OPTIONAL MATCH (p)-[:USES_DATABASE]->(d:Database)
            RETURN collect(DISTINCT l.name) as languages,
                   collect(DISTINCT f.name) as frameworks,
                   collect(DISTINCT d.name) as databases
            """
            
            result = self.graph.run(query, {"project_id": project_id}).data()
            if result:
                return result[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting technology context: {str(e)}")
            return {}

    async def _generate_feature_recommendations(
        self,
        feature_description: str,
        similar_results: List[Dict[str, Any]],
        existing_services: List[Dict[str, Any]],
        tech_stack_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendations for new feature development."""
        recommendations = {
            "reuse_patterns": [],
            "integration_points": [],
            "technology_suggestions": [],
            "architecture_considerations": []
        }
        
        # Analyze similar patterns
        if similar_results:
            recommendations["reuse_patterns"].append(
                f"Found {len(similar_results)} similar patterns that could be reused"
            )
            
            # Extract common technologies from similar patterns
            common_tech = set()
            for result in similar_results:
                if "metadata" in result:
                    if "technology" in result["metadata"]:
                        common_tech.add(result["metadata"]["technology"])
                    if "frameworks" in result["metadata"]:
                        common_tech.update(result["metadata"]["frameworks"])
            
            if common_tech:
                recommendations["technology_suggestions"].append(
                    f"Consider using technologies from similar patterns: {', '.join(common_tech)}"
                )
        
        # Analyze existing services for integration points
        if existing_services:
            service_names = []
            for service in existing_services:
                if "s" in service and service["s"]:
                    service_names.append(service["s"].get("name", "Unknown"))
            
            recommendations["integration_points"].append(
                f"Consider integrating with existing services: {', '.join(service_names[:5])}"
            )
        
        # Technology stack recommendations
        if tech_stack_context:
            languages = tech_stack_context.get("languages", [])
            frameworks = tech_stack_context.get("frameworks", [])
            
            if languages:
                recommendations["technology_suggestions"].append(
                    f"Leverage existing languages: {', '.join(languages)}"
                )
            
            if frameworks:
                recommendations["technology_suggestions"].append(
                    f"Consider existing frameworks: {', '.join(frameworks)}"
                )
        
        # Architecture considerations
        recommendations["architecture_considerations"].extend([
            "Ensure consistency with existing architecture patterns",
            "Consider service boundaries and responsibilities",
            "Plan for scalability and maintainability",
            "Define clear interfaces and contracts"
        ])
        
        return recommendations

    async def delete_project_data(self, project_id: str) -> Dict[str, Any]:
        """
        Delete all data for a project from the knowledge base.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary with deletion results
        """
        try:
            results = {"pinecone": False, "neo4j": False, "metadata": False}
            
            # Delete from Pinecone
            if self.index:
                try:
                    # Delete vectors by project_id
                    self.index.delete(filter={"project_id": project_id})
                    results["pinecone"] = True
                    logger.debug(f"Deleted Pinecone vectors for project {project_id}")
                except Exception as e:
                    logger.error(f"Error deleting Pinecone vectors: {str(e)}")
            
            # Delete from Neo4j
            if self.graph:
                try:
                    # Delete all nodes and relationships for project
                    delete_query = """
                    MATCH (p:Project {id: $project_id})
                    DETACH DELETE p
                    """
                    self.graph.run(delete_query, {"project_id": project_id})
                    results["neo4j"] = True
                    logger.debug(f"Deleted Neo4j data for project {project_id}")
                except Exception as e:
                    logger.error(f"Error deleting Neo4j data: {str(e)}")
            
            # Delete metadata (placeholder for PostgreSQL)
            results["metadata"] = True
            
            logger.info(f"Deleted project data for {project_id}", extra={"results": results})
            return results
            
        except Exception as e:
            logger.error(f"Error deleting project data: {str(e)}")
            return {"error": str(e)}

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of all knowledge base services.
        
        Returns:
            Dictionary with service status information
        """
        status = {
            "pinecone": False,
            "neo4j": False,
            "embedder": False,
            "overall": False
        }
        
        try:
            # Check Pinecone
            if self.index:
                try:
                    # Simple query to test connection
                    self.index.query(vector=[0.0] * self.embedding_dimension, top_k=1)
                    status["pinecone"] = True
                except Exception:
                    pass
            
            # Check Neo4j
            if self.graph:
                try:
                    self.graph.run("RETURN 1").data()
                    status["neo4j"] = True
                except Exception:
                    pass
            
            # Check embedder
            if self.embedder:
                try:
                    self.embedder.encode(["test"])
                    status["embedder"] = True
                except Exception:
                    pass
            
            # Overall status
            status["overall"] = all([status["pinecone"], status["neo4j"], status["embedder"]])
            
        except Exception as e:
            logger.error(f"Error checking service status: {str(e)}")
            status["error"] = str(e)
        
        return status

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        if not self.embedder:
            return []
        
        try:
            embedding = self.embedder.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []

    def _create_chunk_metadata(
        self,
        project_id: str,
        chunk_type: str,
        content: str,
        repository_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create metadata for a chunk.
        
        Args:
            project_id: Project identifier
            chunk_type: Type of chunk
            content: Chunk content
            repository_data: Repository analysis data
            
        Returns:
            Metadata dictionary
        """
        return {
            "project_id": project_id,
            "chunk_type": chunk_type,
            "content": content,
            "repository_url": repository_data.get("repository_url", ""),
            "technologies": repository_data.get("technology_stack", {}),
            "quality_score": repository_data.get("quality_score", 0.0),
            "created_at": datetime.utcnow().isoformat()
        }

    async def get_technology_recommendations(
        self,
        existing_technologies: List[str],
        project_context: str
    ) -> List[Dict[str, Any]]:
        """
        Get technology recommendations based on existing stack and context.
        
        Args:
            existing_technologies: List of existing technologies
            project_context: Project context description
            
        Returns:
            List of technology recommendations
        """
        try:
            # Search for similar projects with these technologies
            query = f"technologies: {', '.join(existing_technologies)} {project_context}"
            similar_results = await self.search_similar_architectures(query, top_k=10)
            
            recommendations = []
            tech_counts = {}
            
            # Analyze technology patterns from similar projects
            for result in similar_results:
                if "metadata" in result and "technologies" in result["metadata"]:
                    techs = result["metadata"]["technologies"]
                    if isinstance(techs, dict):
                        for tech, count in techs.items():
                            if tech not in existing_technologies:
                                tech_counts[tech] = tech_counts.get(tech, 0) + count
            
            # Generate recommendations
            for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                recommendations.append({
                    "technology": tech,
                    "confidence": min(count / len(similar_results), 1.0),
                    "reason": f"Found in {count} similar projects"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting technology recommendations: {str(e)}")
            return []

    async def get_integration_patterns(
        self,
        source_technology: str,
        target_technology: str
    ) -> List[Dict[str, Any]]:
        """
        Get integration patterns between technologies.
        
        Args:
            source_technology: Source technology
            target_technology: Target technology
            
        Returns:
            List of integration patterns
        """
        try:
            # Search for integration patterns
            query = f"integration {source_technology} {target_technology}"
            similar_results = await self.search_similar_architectures(query, top_k=5)
            
            patterns = []
            for result in similar_results:
                patterns.append({
                    "pattern": f"{source_technology} to {target_technology}",
                    "description": result.get("content", ""),
                    "confidence": result.get("score", 0.0)
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting integration patterns: {str(e)}")
            return []

    def get_service_capabilities(self) -> Dict[str, Any]:
        """
        Get service capabilities and configuration.
        
        Returns:
            Dictionary with service capabilities
        """
        return {
            "service_name": "Knowledge Base Service",
            "version": "1.0.0",
            "capabilities": [
                "Vector-based semantic search",
                "Graph-based relationship queries",
                "Architecture pattern recognition",
                "Technology stack analysis",
                "RAG context generation",
                "Multi-modal knowledge storage",
                "Project metadata management"
            ],
            "storage_backends": {
                "vector_search": "Pinecone",
                "graph_database": "Neo4j",
                "metadata_store": "PostgreSQL (planned)",
                "embeddings": "Sentence Transformers"
            },
            "supported_operations": [
                "Index repository analysis",
                "Search similar architectures",
                "Query service dependencies",
                "Get architecture patterns",
                "Generate feature context",
                "Delete project data"
            ],
            "configuration": {
                "embedding_model": self.embedding_model,
                "embedding_dimension": self.embedding_dimension,
                "index_name": self.index_name,
                "neo4j_uri": self.neo4j_uri
            }
        }
