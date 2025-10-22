#!/bin/bash

# ArchMesh Production Deployment Script
set -e

echo "🚀 Starting ArchMesh Production Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ .env.prod file not found. Please create it with your production configuration."
    echo "📝 Example .env.prod:"
    echo "POSTGRES_PASSWORD=your_secure_password"
    echo "REDIS_PASSWORD=your_secure_password"
    echo "NEO4J_PASSWORD=your_secure_password"
    echo "SECRET_KEY=your_very_secure_secret_key_minimum_32_characters"
    echo "OPENAI_API_KEY=your_openai_api_key"
    echo "ANTHROPIC_API_KEY=your_anthropic_api_key"
    exit 1
fi

# Load environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U archmesh -d archmesh_prod > /dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not healthy"
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not healthy"
    exit 1
fi

# Check Neo4j
if docker-compose -f docker-compose.prod.yml exec -T neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD "RETURN 1" > /dev/null 2>&1; then
    echo "✅ Neo4j is healthy"
else
    echo "❌ Neo4j is not healthy"
    exit 1
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not healthy"
    exit 1
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not healthy"
    exit 1
fi

echo "🎉 ArchMesh Production Deployment Complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Neo4j Browser: http://localhost:7474"
echo ""
echo "📋 To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.prod.yml down"
