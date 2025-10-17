/**
 * Architecture Demo Component.
 * 
 * Demonstrates the ArchitectureVisualizer with sample data
 * and shows all the interactive features.
 */

import React, { useState, useCallback } from 'react';
import { ArchitectureVisualizer } from './ArchitectureVisualizer';
import { Service, Dependency, ZoomLevel } from '../../types/architecture';

// Sample data for demonstration
const sampleServices: Service[] = [
  {
    id: 'user-service',
    name: 'User Service',
    type: 'service',
    technology: 'Node.js + Express',
    status: 'healthy',
    description: 'Handles user authentication and profile management',
    version: '2.1.0',
    owner: 'Backend Team',
    team: 'Platform',
    environment: 'production',
    position: { x: 100, y: 100 },
    metadata: {
      endpoints: ['/api/users', '/api/auth'],
      healthCheck: '/health',
      repository: 'https://github.com/company/user-service',
      lastDeployed: '2024-01-15T10:30:00Z',
      uptime: 99.9,
      responseTime: 120,
      errorRate: 0.001,
    },
  },
  {
    id: 'user-database',
    name: 'User Database',
    type: 'database',
    technology: 'PostgreSQL',
    status: 'healthy',
    description: 'Stores user data and authentication information',
    version: '13.4',
    owner: 'Database Team',
    team: 'Infrastructure',
    environment: 'production',
    position: { x: 100, y: 300 },
    metadata: {
      healthCheck: '/health',
      uptime: 99.95,
      responseTime: 5,
      errorRate: 0.0001,
    },
  },
  {
    id: 'payment-service',
    name: 'Payment Service',
    type: 'service',
    technology: 'Java + Spring Boot',
    status: 'warning',
    description: 'Processes payments and manages billing',
    version: '1.8.2',
    owner: 'Payment Team',
    team: 'Business',
    environment: 'production',
    position: { x: 400, y: 100 },
    metadata: {
      endpoints: ['/api/payments', '/api/billing'],
      healthCheck: '/health',
      repository: 'https://github.com/company/payment-service',
      lastDeployed: '2024-01-10T14:20:00Z',
      uptime: 99.5,
      responseTime: 250,
      errorRate: 0.005,
    },
  },
  {
    id: 'payment-database',
    name: 'Payment Database',
    type: 'database',
    technology: 'MySQL',
    status: 'healthy',
    description: 'Stores payment and transaction data',
    version: '8.0.28',
    owner: 'Database Team',
    team: 'Infrastructure',
    environment: 'production',
    position: { x: 400, y: 300 },
    metadata: {
      healthCheck: '/health',
      uptime: 99.8,
      responseTime: 8,
      errorRate: 0.0002,
    },
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    type: 'gateway',
    technology: 'Kong',
    status: 'healthy',
    description: 'Routes requests and handles authentication',
    version: '2.8.1',
    owner: 'Platform Team',
    team: 'Platform',
    environment: 'production',
    position: { x: 250, y: 50 },
    metadata: {
      endpoints: ['/api/*'],
      healthCheck: '/health',
      uptime: 99.9,
      responseTime: 15,
      errorRate: 0.0005,
    },
  },
  {
    id: 'notification-service',
    name: 'Notification Service',
    type: 'service',
    technology: 'Python + FastAPI',
    status: 'critical',
    description: 'Sends notifications via email and SMS',
    version: '1.2.0',
    owner: 'Communication Team',
    team: 'Business',
    environment: 'production',
    position: { x: 700, y: 100 },
    metadata: {
      endpoints: ['/api/notifications'],
      healthCheck: '/health',
      repository: 'https://github.com/company/notification-service',
      lastDeployed: '2024-01-05T09:15:00Z',
      uptime: 95.2,
      responseTime: 500,
      errorRate: 0.02,
    },
  },
  {
    id: 'message-queue',
    name: 'Message Queue',
    type: 'queue',
    technology: 'RabbitMQ',
    status: 'healthy',
    description: 'Handles asynchronous message processing',
    version: '3.11.5',
    owner: 'Infrastructure Team',
    team: 'Infrastructure',
    environment: 'production',
    position: { x: 700, y: 300 },
    metadata: {
      healthCheck: '/health',
      uptime: 99.7,
      responseTime: 2,
      errorRate: 0.0001,
    },
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    type: 'monitoring',
    technology: 'Prometheus + Grafana',
    status: 'healthy',
    description: 'System monitoring and alerting',
    version: '2.40.0',
    owner: 'DevOps Team',
    team: 'Infrastructure',
    environment: 'production',
    position: { x: 250, y: 400 },
    metadata: {
      endpoints: ['/metrics', '/alerts'],
      healthCheck: '/health',
      uptime: 99.9,
      responseTime: 10,
      errorRate: 0.0001,
    },
  },
];

const sampleDependencies: Dependency[] = [
  {
    id: 'user-service-to-db',
    source: 'user-service',
    target: 'user-database',
    type: 'data',
    protocol: 'SQL',
    description: 'User data storage',
    frequency: 'high',
    criticality: 'critical',
  },
  {
    id: 'payment-service-to-db',
    source: 'payment-service',
    target: 'payment-database',
    type: 'data',
    protocol: 'SQL',
    description: 'Payment data storage',
    frequency: 'high',
    criticality: 'critical',
  },
  {
    id: 'gateway-to-user',
    source: 'api-gateway',
    target: 'user-service',
    type: 'api',
    protocol: 'HTTP',
    description: 'User API routing',
    frequency: 'high',
    criticality: 'important',
  },
  {
    id: 'gateway-to-payment',
    source: 'api-gateway',
    target: 'payment-service',
    type: 'api',
    protocol: 'HTTP',
    description: 'Payment API routing',
    frequency: 'medium',
    criticality: 'important',
  },
  {
    id: 'payment-to-notification',
    source: 'payment-service',
    target: 'notification-service',
    type: 'event',
    protocol: 'HTTP',
    description: 'Payment confirmation notifications',
    frequency: 'medium',
    criticality: 'normal',
  },
  {
    id: 'notification-to-queue',
    source: 'notification-service',
    target: 'message-queue',
    type: 'message',
    protocol: 'AMQP',
    description: 'Async notification processing',
    frequency: 'high',
    criticality: 'important',
  },
  {
    id: 'monitoring-to-all',
    source: 'monitoring',
    target: 'user-service',
    type: 'api',
    protocol: 'HTTP',
    description: 'Health monitoring',
    frequency: 'high',
    criticality: 'normal',
  },
];

export const ArchitectureDemo: React.FC = () => {
  const [selectedService, setSelectedService] = useState<Service | undefined>();
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>(1);

  const handleNodeClick = useCallback((service: Service) => {
    console.log('Node clicked:', service);
    setSelectedService(service);
  }, []);

  const handleNodeDoubleClick = useCallback((service: Service) => {
    console.log('Node double-clicked:', service);
    // In a real app, this might zoom into the service's internal components
  }, []);

  const handleZoomLevelChange = useCallback((level: ZoomLevel) => {
    console.log('Zoom level changed:', level);
    setZoomLevel(level);
  }, []);

  const handleDependencyClick = useCallback((dependency: Dependency) => {
    console.log('Dependency clicked:', dependency);
  }, []);

  return (
    <div className="w-full h-screen bg-gray-100">
      <div className="h-full">
        <ArchitectureVisualizer
          services={sampleServices}
          dependencies={sampleDependencies}
          onNodeClick={handleNodeClick}
          onNodeDoubleClick={handleNodeDoubleClick}
          onZoomLevelChange={handleZoomLevelChange}
          onDependencyClick={handleDependencyClick}
          initialZoomLevel={zoomLevel}
          selectedNodeId={selectedService?.id}
          showMinimap={true}
          showControls={true}
          showLegend={true}
          enableExport={true}
          enableSearch={true}
        />
      </div>
    </div>
  );
};

export default ArchitectureDemo;
