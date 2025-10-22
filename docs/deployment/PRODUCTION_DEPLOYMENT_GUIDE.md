# 🚀 Production Deployment Guide - WebSocket Services

## 📋 Overview

This guide provides comprehensive instructions for deploying the ArchMesh WebSocket services to production environments. The services include real-time communication, notification systems, and comprehensive monitoring.

## 🏗️ Architecture Overview

### **Production Components**
- **Production WebSocket Service**: High-performance WebSocket service with full scalability
- **Async Message Processor**: Asynchronous message processing with worker pools
- **Cache Manager**: Redis-based caching with compression and optimization
- **Load Balancer**: Intelligent connection distribution with failover
- **Error Handler**: Centralized error management with circuit breakers
- **Enhanced Logger**: Structured logging with performance monitoring
- **Health Monitor**: Real-time health checks and performance metrics

### **Scalability Features**
- **Connection Pooling**: Efficient connection management
- **Auto-scaling**: Automatic worker scaling based on load
- **Load Balancing**: Multiple strategies with health checks
- **Caching**: High-performance caching with automatic management
- **Monitoring**: Real-time health checks and performance tracking

---

## 🚀 Quick Start

### **1. Environment Setup**

```bash
# Set environment variables
export ENVIRONMENT=production
export DEPLOYMENT_SIZE=medium
export REDIS_HOST=localhost
export REDIS_PORT=6379
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=archmesh
export DB_USER=archmesh
export DB_PASSWORD=your_password
```

### **2. Install Dependencies**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Redis (if not already installed)
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

### **3. Database Setup**

```bash
# Run database migrations
alembic upgrade head

# Create database user (if needed)
psql -c "CREATE USER archmesh WITH PASSWORD 'your_password';"
psql -c "CREATE DATABASE archmesh OWNER archmesh;"
```

### **4. Start Production Service**

```bash
# Start the production WebSocket service
python -m app.services.websocket.production_service
```

---

## ⚙️ Configuration

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `production` | No |
| `DEPLOYMENT_SIZE` | Deployment size | `medium` | No |
| `REDIS_HOST` | Redis server host | `localhost` | Yes |
| `REDIS_PORT` | Redis server port | `6379` | No |
| `REDIS_PASSWORD` | Redis password | None | No |
| `DB_HOST` | Database host | `localhost` | Yes |
| `DB_PORT` | Database port | `5432` | No |
| `DB_NAME` | Database name | `archmesh` | Yes |
| `DB_USER` | Database user | `archmesh` | Yes |
| `DB_PASSWORD` | Database password | None | Yes |
| `ENABLE_SSL` | Enable SSL/TLS | `true` | No |
| `SSL_CERT_PATH` | SSL certificate path | None | If SSL enabled |
| `SSL_KEY_PATH` | SSL private key path | None | If SSL enabled |

### **Deployment Sizes**

#### **Small (< 100 concurrent users)**
```python
config = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.SMALL
)
```

**Configuration:**
- Max connections: 100
- Workers: 5
- Queue size: 1,000
- Cache memory: 128MB
- Health check interval: 60s

#### **Medium (100-1,000 concurrent users)**
```python
config = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.MEDIUM
)
```

**Configuration:**
- Max connections: 1,000
- Workers: 20
- Queue size: 50,000
- Cache memory: 512MB
- Health check interval: 30s

#### **Large (1,000-10,000 concurrent users)**
```python
config = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.LARGE
)
```

**Configuration:**
- Max connections: 5,000
- Workers: 50
- Queue size: 100,000
- Cache memory: 1GB
- Health check interval: 15s

#### **Enterprise (> 10,000 concurrent users)**
```python
config = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.ENTERPRISE
)
```

**Configuration:**
- Max connections: 10,000
- Workers: 100
- Queue size: 500,000
- Cache memory: 2GB
- Health check interval: 10s

---

## 🐳 Docker Deployment

### **Docker Compose**

```yaml
version: '3.8'

services:
  websocket-service:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - DEPLOYMENT_SIZE=medium
      - REDIS_HOST=redis
      - DB_HOST=postgres
      - DB_PASSWORD=archmesh_password
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=archmesh
      - POSTGRES_USER=archmesh
      - POSTGRES_PASSWORD=archmesh_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### **Docker Run**

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_DB=archmesh \
  -e POSTGRES_USER=archmesh \
  -e POSTGRES_PASSWORD=archmesh_password \
  -p 5432:5432 \
  postgres:15

# Start WebSocket service
docker run -d --name websocket-service \
  -p 8080:8080 \
  -e ENVIRONMENT=production \
  -e DEPLOYMENT_SIZE=medium \
  -e REDIS_HOST=redis \
  -e DB_HOST=postgres \
  -e DB_PASSWORD=archmesh_password \
  --link redis:redis \
  --link postgres:postgres \
  archmesh-websocket:latest
```

---

## ☁️ Cloud Deployment

### **AWS Deployment**

#### **ECS with Fargate**

```yaml
# task-definition.json
{
  "family": "archmesh-websocket",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "websocket-service",
      "image": "your-account.dkr.ecr.region.amazonaws.com/archmesh-websocket:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEPLOYMENT_SIZE",
          "value": "medium"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:archmesh/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/archmesh-websocket",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### **ElastiCache for Redis**

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id archmesh-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --port 6379
```

#### **RDS for PostgreSQL**

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier archmesh-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username archmesh \
  --master-user-password your_password \
  --allocated-storage 20
```

### **Google Cloud Deployment**

#### **Cloud Run**

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: archmesh-websocket
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 1000
      containers:
      - image: gcr.io/your-project/archmesh-websocket:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DEPLOYMENT_SIZE
          value: "medium"
        - name: REDIS_HOST
          value: "redis-ip"
        - name: DB_HOST
          value: "db-ip"
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

#### **Cloud Memorystore for Redis**

```bash
# Create Redis instance
gcloud redis instances create archmesh-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x
```

#### **Cloud SQL for PostgreSQL**

```bash
# Create Cloud SQL instance
gcloud sql instances create archmesh-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

---

## 📊 Monitoring and Observability

### **Health Checks**

The service provides comprehensive health check endpoints:

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed health check
curl http://localhost:8080/health/detailed

# Metrics endpoint
curl http://localhost:8080/metrics
```

### **Key Metrics**

- **Connection Metrics**: Active connections, total connections, connection rate
- **Message Metrics**: Messages per second, message latency, queue depth
- **Performance Metrics**: Response time, throughput, error rate
- **Resource Metrics**: Memory usage, CPU usage, worker utilization
- **Cache Metrics**: Hit rate, miss rate, cache size

### **Alerting**

Configure alerts for:
- **High Error Rate**: > 5% error rate
- **High Response Time**: > 1 second average response time
- **High Memory Usage**: > 80% memory usage
- **High CPU Usage**: > 80% CPU usage
- **Connection Failures**: > 10% connection failure rate

### **Logging**

The service provides structured logging with:
- **Connection Events**: Connection establishment, disconnection, errors
- **Message Events**: Message processing, queuing, delivery
- **Performance Events**: Response times, throughput, resource usage
- **Error Events**: Detailed error information with stack traces

---

## 🔒 Security

### **Authentication**

- **JWT Tokens**: Secure authentication with JWT tokens
- **Token Validation**: Automatic token validation and refresh
- **Rate Limiting**: Configurable rate limiting per user/IP
- **CORS**: Configurable CORS settings

### **SSL/TLS**

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Set environment variables
export ENABLE_SSL=true
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

### **Network Security**

- **Firewall Rules**: Restrict access to necessary ports only
- **VPC**: Use private networks for internal communication
- **Load Balancer**: Use application load balancer with SSL termination
- **DDoS Protection**: Enable DDoS protection at the load balancer level

---

## 🚨 Troubleshooting

### **Common Issues**

#### **High Memory Usage**
```bash
# Check memory usage
curl http://localhost:8080/metrics | grep memory

# Adjust cache configuration
export CACHE_MAX_MEMORY_MB=256
```

#### **Connection Failures**
```bash
# Check connection metrics
curl http://localhost:8080/metrics | grep connections

# Check Redis connectivity
redis-cli ping
```

#### **High Error Rate**
```bash
# Check error logs
tail -f logs/error.log

# Check health status
curl http://localhost:8080/health/detailed
```

### **Performance Tuning**

#### **Worker Scaling**
```python
# Adjust worker configuration
config.async_processor_config["max_workers"] = 50
config.async_processor_config["scale_threshold"] = 0.7
```

#### **Cache Optimization**
```python
# Adjust cache configuration
config.cache_config["default_ttl"] = 7200  # 2 hours
config.cache_config["max_memory_mb"] = 1024
```

#### **Load Balancer Tuning**
```python
# Adjust load balancer configuration
config.load_balancer_config["health_check_interval"] = 15
config.load_balancer_config["circuit_breaker_threshold"] = 3
```

---

## 📈 Scaling

### **Horizontal Scaling**

1. **Multiple Instances**: Deploy multiple service instances
2. **Load Balancer**: Use application load balancer for distribution
3. **Session Affinity**: Configure session affinity if needed
4. **Database Scaling**: Use read replicas for database scaling

### **Vertical Scaling**

1. **Increase Resources**: Increase CPU and memory allocation
2. **Worker Scaling**: Increase worker pool size
3. **Cache Scaling**: Increase cache memory allocation
4. **Queue Scaling**: Increase queue size limits

### **Auto-scaling**

Configure auto-scaling based on:
- **CPU Usage**: Scale up when CPU > 70%
- **Memory Usage**: Scale up when memory > 80%
- **Queue Depth**: Scale up when queue depth > 1000
- **Connection Count**: Scale up when connections > 80% of limit

---

## 🔄 Backup and Recovery

### **Database Backup**

```bash
# Create database backup
pg_dump -h localhost -U archmesh archmesh > backup.sql

# Restore database backup
psql -h localhost -U archmesh archmesh < backup.sql
```

### **Redis Backup**

```bash
# Create Redis backup
redis-cli BGSAVE

# Copy backup file
cp /var/lib/redis/dump.rdb /backup/redis-backup.rdb
```

### **Configuration Backup**

```bash
# Backup configuration files
tar -czf config-backup.tar.gz config/ logs/
```

---

## 📚 Additional Resources

- **API Documentation**: `/docs/api/websocket_api_documentation.md`
- **Performance Testing**: `/tests/performance/test_websocket_performance.py`
- **Security Testing**: `/tests/security/test_security_vulnerabilities.py`
- **Monitoring Setup**: `/docs/monitoring/monitoring_setup.md`
- **Troubleshooting Guide**: `/docs/troubleshooting/troubleshooting_guide.md`

---

## 🆘 Support

For production support and issues:
- **Documentation**: Check the comprehensive documentation
- **Logs**: Review application and system logs
- **Metrics**: Monitor health and performance metrics
- **Community**: Join the ArchMesh community for support
- **Professional Support**: Contact for enterprise support

---

**Production Deployment Complete** 🚀

The WebSocket services are now ready for high-volume production deployment with comprehensive monitoring, security, and scalability features.

