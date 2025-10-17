/**
 * Architecture Comparison Demo Component.
 * 
 * Demonstrates the ArchitectureComparison component with sample data
 * showing current and proposed architectures with detailed changes.
 */

import React, { useState, useCallback } from 'react';
import { ArchitectureComparison } from './ArchitectureComparison';
import { 
  ArchitectureGraph, 
  ArchitectureChange, 
  ImpactAnalysis,
  ApprovalDecision 
} from '../../types/architecture-comparison';

// Sample current architecture
const currentArchitecture: ArchitectureGraph = {
  services: [
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
  ],
  dependencies: [
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
  ],
  metadata: {
    lastUpdated: '2024-01-15T10:30:00Z',
    version: '1.0.0',
    totalServices: 4,
    totalDependencies: 2,
    architectureStyle: 'microservices',
  },
};

// Sample proposed architecture (with new features)
const proposedArchitecture: ArchitectureGraph = {
  services: [
    // Modified user service
    {
      id: 'user-service',
      name: 'User Service',
      type: 'service',
      technology: 'Node.js + Express',
      status: 'healthy',
      description: 'Handles user authentication, profile management, and preferences',
      version: '2.2.0',
      owner: 'Backend Team',
      team: 'Platform',
      environment: 'production',
      position: { x: 100, y: 100 },
      metadata: {
        endpoints: ['/api/users', '/api/auth', '/api/preferences'],
        healthCheck: '/health',
        repository: 'https://github.com/company/user-service',
        lastDeployed: '2024-01-20T10:30:00Z',
        uptime: 99.9,
        responseTime: 120,
        errorRate: 0.001,
      },
    },
    // Unchanged user database
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
    // Modified payment service
    {
      id: 'payment-service',
      name: 'Payment Service',
      type: 'service',
      technology: 'Java + Spring Boot',
      status: 'healthy',
      description: 'Processes payments, manages billing, and handles refunds',
      version: '1.9.0',
      owner: 'Payment Team',
      team: 'Business',
      environment: 'production',
      position: { x: 400, y: 100 },
      metadata: {
        endpoints: ['/api/payments', '/api/billing', '/api/refunds'],
        healthCheck: '/health',
        repository: 'https://github.com/company/payment-service',
        lastDeployed: '2024-01-20T14:20:00Z',
        uptime: 99.7,
        responseTime: 200,
        errorRate: 0.003,
      },
    },
    // Unchanged payment database
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
    // New notification service
    {
      id: 'notification-service',
      name: 'Notification Service',
      type: 'service',
      technology: 'Python + FastAPI',
      status: 'healthy',
      description: 'Sends notifications via email, SMS, and push notifications',
      version: '1.0.0',
      owner: 'Communication Team',
      team: 'Business',
      environment: 'production',
      position: { x: 700, y: 100 },
      metadata: {
        endpoints: ['/api/notifications', '/api/templates'],
        healthCheck: '/health',
        repository: 'https://github.com/company/notification-service',
        lastDeployed: '2024-01-20T09:15:00Z',
        uptime: 99.8,
        responseTime: 150,
        errorRate: 0.002,
      },
    },
    // New message queue
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
  ],
  dependencies: [
    // Existing dependencies
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
    // New dependencies
    {
      id: 'payment-to-notification',
      source: 'payment-service',
      target: 'notification-service',
      type: 'api',
      protocol: 'HTTP',
      description: 'Payment confirmation notifications',
      frequency: 'medium',
      criticality: 'important',
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
  ],
  metadata: {
    lastUpdated: '2024-01-20T10:30:00Z',
    version: '1.1.0',
    totalServices: 6,
    totalDependencies: 4,
    architectureStyle: 'microservices',
  },
};

// Sample changes
const changes: ArchitectureChange[] = [
  {
    id: 'user-service-modify',
    type: 'modify',
    entity: 'service',
    name: 'user-service',
    description: 'Added user preferences functionality and new API endpoints',
    impact: 'medium',
    affectedServices: ['user-service'],
    breakingChange: false,
    migrationRequired: false,
    estimatedEffort: 16,
    riskLevel: 'low',
    dependencies: ['user-database'],
    metadata: {
      reason: 'Business requirement for user customization',
      alternatives: ['Use external preferences service', 'Store in user database'],
      rollbackPlan: 'Revert to previous version',
      testingRequired: true,
      documentationRequired: true,
    },
  },
  {
    id: 'payment-service-modify',
    type: 'modify',
    entity: 'service',
    name: 'payment-service',
    description: 'Added refund functionality and improved performance',
    impact: 'high',
    affectedServices: ['payment-service'],
    breakingChange: false,
    migrationRequired: false,
    estimatedEffort: 24,
    riskLevel: 'medium',
    dependencies: ['payment-database', 'notification-service'],
    metadata: {
      reason: 'Customer support requirements and performance optimization',
      alternatives: ['Use external refund service', 'Implement async refunds'],
      rollbackPlan: 'Feature flag to disable refunds',
      testingRequired: true,
      documentationRequired: true,
    },
  },
  {
    id: 'notification-service-add',
    type: 'add',
    entity: 'service',
    name: 'notification-service',
    description: 'New service for handling all notification types',
    impact: 'medium',
    affectedServices: ['notification-service'],
    breakingChange: false,
    migrationRequired: false,
    estimatedEffort: 40,
    riskLevel: 'low',
    dependencies: ['message-queue'],
    metadata: {
      reason: 'Centralized notification management',
      alternatives: ['Use external notification service', 'Integrate with existing services'],
      rollbackPlan: 'Remove service and dependencies',
      testingRequired: true,
      documentationRequired: true,
    },
  },
  {
    id: 'message-queue-add',
    type: 'add',
    entity: 'service',
    name: 'message-queue',
    description: 'New message queue for asynchronous processing',
    impact: 'high',
    affectedServices: ['message-queue'],
    breakingChange: false,
    migrationRequired: false,
    estimatedEffort: 20,
    riskLevel: 'medium',
    dependencies: [],
    metadata: {
      reason: 'Support for async notification processing',
      alternatives: ['Use cloud message queue', 'Implement in-memory queue'],
      rollbackPlan: 'Remove queue and use direct API calls',
      testingRequired: true,
      documentationRequired: true,
    },
  },
  {
    id: 'payment-to-notification-dep',
    type: 'add',
    entity: 'dependency',
    name: 'payment-to-notification',
    description: 'New API dependency from payment service to notification service',
    impact: 'medium',
    affectedServices: ['payment-service', 'notification-service'],
    breakingChange: false,
    migrationRequired: false,
    estimatedEffort: 8,
    riskLevel: 'low',
    dependencies: [],
    metadata: {
      reason: 'Enable payment confirmation notifications',
      alternatives: ['Use event-driven architecture', 'Direct database integration'],
      rollbackPlan: 'Remove API calls and use fallback notifications',
      testingRequired: true,
      documentationRequired: false,
    },
  },
];

// Sample impact analysis
const impactAnalysis: ImpactAnalysis = {
  overallImpact: 'medium',
  affectedSystems: ['user-service', 'payment-service', 'notification-service', 'message-queue'],
  riskFactors: {
    breakingChanges: 0,
    dataMigrationRequired: false,
    downtimeRequired: false,
    rollbackComplexity: 'low',
    testingComplexity: 'medium',
  },
  recommendations: {
    implementation: [
      'Deploy notification service first',
      'Set up message queue infrastructure',
      'Update payment service with feature flags',
      'Implement gradual rollout for user preferences',
    ],
    testing: [
      'Comprehensive integration testing',
      'Load testing for notification service',
      'End-to-end payment flow testing',
      'User preference functionality testing',
    ],
    deployment: [
      'Blue-green deployment for new services',
      'Feature flags for gradual rollout',
      'Monitor system performance during deployment',
      'Prepare rollback procedures',
    ],
    monitoring: [
      'Set up alerts for new services',
      'Monitor notification delivery rates',
      'Track payment service performance',
      'Monitor message queue health',
    ],
  },
  timeline: {
    planning: 3,
    development: 10,
    testing: 5,
    deployment: 2,
    total: 20,
  },
};

export const ArchitectureComparisonDemo: React.FC = () => {
  const [isApproved, setIsApproved] = useState(false);
  const [isRejected, setIsRejected] = useState(false);

  const handleApprove = useCallback((decision: ApprovalDecision) => {
    console.log('Approval decision:', decision);
    setIsApproved(true);
    setIsRejected(false);
  }, []);

  const handleReject = useCallback((reason: string) => {
    console.log('Rejection reason:', reason);
    setIsRejected(true);
    setIsApproved(false);
  }, []);

  const handleExport = useCallback((format: 'pdf' | 'json' | 'html') => {
    console.log('Export format:', format);
    // In a real app, this would trigger the export functionality
  }, []);

  return (
    <div className="w-full h-screen bg-gray-100">
      {/* Status Banner */}
      {(isApproved || isRejected) && (
        <div className={`p-4 text-center font-medium ${
          isApproved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isApproved ? '✅ Architecture changes approved!' : '❌ Architecture changes rejected.'}
        </div>
      )}

      {/* Main Comparison Component */}
      <div className="h-full">
        <ArchitectureComparison
          currentArchitecture={currentArchitecture}
          proposedArchitecture={proposedArchitecture}
          changes={changes}
          impactAnalysis={impactAnalysis}
          onApprove={handleApprove}
          onReject={handleReject}
          onExport={handleExport}
          viewMode="side-by-side"
          showImpactAnalysis={true}
          showApprovalWorkflow={true}
        />
      </div>
    </div>
  );
};

export default ArchitectureComparisonDemo;
