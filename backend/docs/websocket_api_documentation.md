# WebSocket API Documentation

## Overview

The ArchMesh WebSocket API provides real-time communication for workflow updates, notifications, and system events. This document describes the API endpoints, message formats, and usage patterns.

## Table of Contents

1. [Authentication](#authentication)
2. [Connection Management](#connection-management)
3. [Message Types](#message-types)
4. [Error Handling](#error-handling)
5. [Performance Considerations](#performance-considerations)
6. [Examples](#examples)

## Authentication

### Connection Authentication

WebSocket connections require authentication via token in the connection URL:

```
wss://api.archmesh.com/ws?token=<auth_token>
```

### Token Validation

- Tokens are validated on connection establishment
- Invalid tokens result in immediate connection closure
- Token expiration is handled gracefully with reconnection prompts

## Connection Management

### Connection Lifecycle

1. **Establish Connection**: Client connects with valid token
2. **Heartbeat**: Regular ping/pong messages maintain connection
3. **Message Exchange**: Bidirectional message communication
4. **Graceful Disconnect**: Clean connection termination

### Connection States

- `connecting`: Initial connection state
- `connected`: Active connection
- `disconnected`: Connection closed
- `reconnecting`: Attempting to reconnect
- `failed`: Connection failed

### Connection Limits

- **Maximum Connections**: 1000 per server instance
- **Connection Timeout**: 300 seconds of inactivity
- **Heartbeat Interval**: 30 seconds
- **Reconnection Attempts**: 5 maximum attempts

## Message Types

### Message Format

All messages follow this JSON structure:

```json
{
  "type": "message_type",
  "id": "unique_message_id",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    // Message-specific data
  }
}
```

### Core Message Types

#### 1. Ping/Pong Messages

**Ping Message** (Client → Server):
```json
{
  "type": "ping",
  "id": "ping_123",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Pong Message** (Server → Client):
```json
{
  "type": "pong",
  "id": "pong_123",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 2. Workflow Update Messages

**Workflow Update** (Server → Client):
```json
{
  "type": "workflow_update",
  "id": "workflow_update_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workflow_id": "workflow_456",
    "status": "in_progress",
    "stage": "architecture_design",
    "progress": 50,
    "message": "Generating architecture components...",
    "estimated_completion": "2024-01-01T00:05:00Z"
  }
}
```

**Workflow Status Values**:
- `pending`: Workflow queued
- `in_progress`: Workflow executing
- `completed`: Workflow finished successfully
- `failed`: Workflow failed
- `cancelled`: Workflow cancelled

**Workflow Stages**:
- `requirements_analysis`: Analyzing requirements
- `architecture_design`: Designing architecture
- `component_generation`: Generating components
- `validation`: Validating results
- `review`: Awaiting human review

#### 3. Notification Messages

**Notification** (Server → Client):
```json
{
  "type": "notification",
  "id": "notification_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "notification_id": "notif_456",
    "user_id": "user_789",
    "title": "Workflow Complete",
    "message": "Your architecture design is ready for review",
    "category": "workflow_complete",
    "priority": "high",
    "action": {
      "label": "Review Now",
      "url": "/projects/123/workflows/456/review"
    },
    "metadata": {
      "project_id": "project_123",
      "workflow_id": "workflow_456"
    }
  }
}
```

**Notification Categories**:
- `workflow_update`: Workflow progress updates
- `workflow_complete`: Workflow completion
- `workflow_failed`: Workflow failure
- `system_alert`: System notifications
- `user_action`: User action confirmations

**Notification Priorities**:
- `low`: Informational messages
- `normal`: Standard notifications
- `high`: Important updates
- `critical`: Urgent notifications

#### 4. Error Messages

**Error Message** (Server → Client):
```json
{
  "type": "error",
  "id": "error_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "error_code": "CONNECTION_TIMEOUT",
    "error_message": "Connection timed out",
    "error_details": {
      "session_id": "session_456",
      "retry_after": 30
    }
  }
}
```

**Error Codes**:
- `CONNECTION_TIMEOUT`: Connection timeout
- `AUTHENTICATION_FAILED`: Invalid authentication
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `MESSAGE_TOO_LARGE`: Message exceeds size limit
- `INVALID_MESSAGE_FORMAT`: Malformed message
- `SYSTEM_ERROR`: Internal server error

#### 5. Large Data Messages

**Large Data Chunk** (Client ↔ Server):
```json
{
  "type": "large_data",
  "id": "large_data_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "data_id": "data_456",
    "chunk_index": 1,
    "total_chunks": 5,
    "chunk_data": "base64_encoded_data",
    "checksum": "sha256_hash"
  }
}
```

**Large Data Received** (Server → Client):
```json
{
  "type": "large_data_received",
  "id": "large_data_received_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "data_id": "data_456",
    "status": "received",
    "total_size": 1024000
  }
}
```

## Error Handling

### Error Recovery Strategies

1. **Connection Errors**: Automatic reconnection with exponential backoff
2. **Message Errors**: Retry with error logging
3. **Authentication Errors**: Prompt for re-authentication
4. **Rate Limiting**: Wait and retry after specified delay

### Error Logging

All errors are logged with:
- Error type and message
- Session and user context
- Timestamp and stack trace
- Recovery attempt results

### Circuit Breaker Pattern

The system implements circuit breakers for:
- Connection establishment
- Message processing
- External service calls

Circuit breaker states:
- `closed`: Normal operation
- `open`: Failing, blocking requests
- `half-open`: Testing recovery

## Performance Considerations

### Message Size Limits

- **Maximum Message Size**: 1MB
- **Large Data Chunk Size**: 64KB
- **Maximum Chunks**: 1000 per data transfer

### Connection Management

- **Connection Pooling**: Efficient connection reuse
- **Health Monitoring**: Automatic cleanup of stale connections
- **Load Balancing**: Distribute connections across instances

### Message Processing

- **Priority Queuing**: Critical messages processed first
- **Batch Processing**: Process multiple messages together
- **Async Processing**: Non-blocking message handling

### Performance Metrics

The system tracks:
- Connection count and duration
- Message throughput and latency
- Error rates and recovery times
- Resource usage and efficiency

## Examples

### JavaScript Client Example

```javascript
class ArchMeshWebSocketClient {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = `wss://api.archmesh.com/ws?token=${this.token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('Connected to ArchMesh WebSocket');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('WebSocket connection closed');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'pong':
        console.log('Received pong');
        break;
      case 'workflow_update':
        this.handleWorkflowUpdate(message.data);
        break;
      case 'notification':
        this.handleNotification(message.data);
        break;
      case 'error':
        this.handleError(message.data);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  handleWorkflowUpdate(data) {
    console.log(`Workflow ${data.workflow_id}: ${data.status} (${data.progress}%)`);
    // Update UI with workflow progress
  }

  handleNotification(data) {
    console.log(`Notification: ${data.title} - ${data.message}`);
    // Show notification to user
  }

  handleError(data) {
    console.error(`Error: ${data.error_code} - ${data.error_message}`);
    // Handle error appropriately
  }

  sendMessage(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: type,
        id: this.generateMessageId(),
        timestamp: new Date().toISOString(),
        data: data
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  startHeartbeat() {
    setInterval(() => {
      this.sendMessage('ping', {});
    }, 30000); // 30 seconds
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }

  generateMessageId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const client = new ArchMeshWebSocketClient('your_auth_token');
client.connect();
```

### Python Client Example

```python
import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, Any, Optional

class ArchMeshWebSocketClient:
    def __init__(self, token: str):
        self.token = token
        self.websocket = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.running = False

    async def connect(self):
        """Connect to WebSocket server"""
        uri = f"wss://api.archmesh.com/ws?token={self.token}"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.reconnect_attempts = 0
            self.running = True
            print("Connected to ArchMesh WebSocket")
            
            # Start heartbeat task
            asyncio.create_task(self.heartbeat_loop())
            
            # Start message handling
            await self.message_loop()
            
        except Exception as e:
            print(f"Connection failed: {e}")
            await self.attempt_reconnect()

    async def message_loop(self):
        """Handle incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            await self.attempt_reconnect()
        except Exception as e:
            print(f"Message loop error: {e}")

    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        message_type = message.get("type")
        data = message.get("data", {})

        if message_type == "pong":
            print("Received pong")
        elif message_type == "workflow_update":
            await self.handle_workflow_update(data)
        elif message_type == "notification":
            await self.handle_notification(data)
        elif message_type == "error":
            await self.handle_error(data)
        else:
            print(f"Unknown message type: {message_type}")

    async def handle_workflow_update(self, data: Dict[str, Any]):
        """Handle workflow update"""
        workflow_id = data.get("workflow_id")
        status = data.get("status")
        progress = data.get("progress", 0)
        print(f"Workflow {workflow_id}: {status} ({progress}%)")

    async def handle_notification(self, data: Dict[str, Any]):
        """Handle notification"""
        title = data.get("title")
        message = data.get("message")
        print(f"Notification: {title} - {message}")

    async def handle_error(self, data: Dict[str, Any]):
        """Handle error"""
        error_code = data.get("error_code")
        error_message = data.get("error_message")
        print(f"Error: {error_code} - {error_message}")

    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message to server"""
        if self.websocket and not self.websocket.closed:
            message = {
                "type": message_type,
                "id": self.generate_message_id(),
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            await self.websocket.send(json.dumps(message))

    async def heartbeat_loop(self):
        """Send periodic heartbeat"""
        while self.running:
            await asyncio.sleep(30)  # 30 seconds
            if self.websocket and not self.websocket.closed:
                await self.send_message("ping", {})

    async def attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = 2 ** self.reconnect_attempts  # Exponential backoff
            print(f"Attempting to reconnect in {delay} seconds ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            await asyncio.sleep(delay)
            await self.connect()
        else:
            print("Max reconnection attempts reached")

    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"msg_{int(datetime.utcnow().timestamp())}_{id(self)}"

    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()

# Usage
async def main():
    client = ArchMeshWebSocketClient("your_auth_token")
    try:
        await client.connect()
    except KeyboardInterrupt:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Monitoring and Debugging

### Health Check Endpoint

```
GET /api/v1/websocket/health
```

Response:
```json
{
  "status": "healthy",
  "connections": {
    "total": 150,
    "active": 150,
    "idle": 0
  },
  "performance": {
    "messages_per_second": 25.5,
    "average_response_time": 0.045,
    "error_rate": 0.001
  },
  "uptime": 3600
}
```

### Metrics Endpoint

```
GET /api/v1/websocket/metrics
```

Response:
```json
{
  "connections": {
    "total_connections": 150,
    "active_connections": 150,
    "connection_duration_avg": 1800,
    "connection_duration_max": 7200
  },
  "messages": {
    "total_sent": 45000,
    "total_received": 45000,
    "messages_per_second": 25.5,
    "average_message_size": 1024
  },
  "errors": {
    "total_errors": 5,
    "error_rate": 0.001,
    "recovery_success_rate": 0.95
  }
}
```

## Best Practices

### Client Implementation

1. **Connection Management**:
   - Implement exponential backoff for reconnections
   - Handle connection state changes gracefully
   - Use heartbeat to maintain connection health

2. **Message Handling**:
   - Validate message format before processing
   - Handle unknown message types gracefully
   - Implement message queuing for offline scenarios

3. **Error Handling**:
   - Log all errors with context
   - Implement retry logic for transient errors
   - Provide user feedback for critical errors

4. **Performance**:
   - Batch multiple operations when possible
   - Use message compression for large data
   - Implement client-side caching

### Server Configuration

1. **Connection Limits**:
   - Set appropriate connection limits
   - Monitor connection usage
   - Implement connection cleanup

2. **Message Processing**:
   - Use priority queues for message processing
   - Implement message batching
   - Monitor message throughput

3. **Error Recovery**:
   - Implement circuit breakers
   - Use exponential backoff for retries
   - Monitor error rates and recovery

## Troubleshooting

### Common Issues

1. **Connection Timeouts**:
   - Check network connectivity
   - Verify token validity
   - Increase heartbeat frequency

2. **Message Delivery Failures**:
   - Check message format
   - Verify message size limits
   - Monitor server logs

3. **High Error Rates**:
   - Check server health
   - Monitor resource usage
   - Review error logs

### Debug Tools

1. **WebSocket Inspector**: Browser developer tools
2. **Server Logs**: Application and system logs
3. **Metrics Dashboard**: Real-time performance monitoring
4. **Health Checks**: Automated health monitoring

## Support

For technical support and questions:
- Email: support@archmesh.com
- Documentation: https://docs.archmesh.com
- GitHub Issues: https://github.com/archmesh/archmesh/issues

