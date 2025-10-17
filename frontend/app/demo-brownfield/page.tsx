'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import ModeSelector from '@/src/components/ModeSelector';
import GitHubConnector from '@/src/components/GitHubConnector';
import ArchitectureComparison from '@/src/components/architecture/ArchitectureComparison';
import { ArchitectureGraph } from '@/src/types/architecture';
import { ExistingArchitecture, ProposedArchitecture, ArchitectureChange } from '@/types';
import { toast } from 'sonner';
import { 
  BuildingIcon,
  ActivityIcon,
  BarChart3Icon,
  CheckCircleIcon,
  AlertCircleIcon,
  ArrowRightIcon
} from 'lucide-react';

export default function BrownfieldDemoPage() {
  const [projectMode, setProjectMode] = useState<'greenfield' | 'brownfield'>('brownfield');
  const [existingArchitecture, setExistingArchitecture] = useState<ExistingArchitecture | null>(null);
  const [proposedArchitecture, setProposedArchitecture] = useState<ProposedArchitecture | null>(null);
  const [architectureChanges, setArchitectureChanges] = useState<ArchitectureChange[]>([]);

  // Mock data for demonstration
  const mockExistingArchitecture: ExistingArchitecture = {
    repository_url: 'https://github.com/example/e-commerce-platform',
    branch: 'main',
    services: [
      {
        id: 'user-service',
        name: 'User Service',
        type: 'service',
        technology: 'Node.js + Express',
        description: 'Handles user authentication and profiles',
        endpoints: ['/api/users', '/api/auth'],
        dependencies: ['user-database']
      },
      {
        id: 'user-database',
        name: 'User Database',
        type: 'database',
        technology: 'PostgreSQL',
        description: 'Stores user data and authentication info'
      },
      {
        id: 'payment-service',
        name: 'Payment Service',
        type: 'service',
        technology: 'Java + Spring Boot',
        description: 'Processes payments and billing',
        endpoints: ['/api/payments', '/api/billing'],
        dependencies: ['payment-database']
      },
      {
        id: 'payment-database',
        name: 'Payment Database',
        type: 'database',
        technology: 'PostgreSQL',
        description: 'Stores payment and transaction data'
      }
    ],
    dependencies: [
      {
        from: 'user-service',
        to: 'user-database',
        type: 'database-call',
        description: 'User service reads/writes to user database'
      },
      {
        from: 'payment-service',
        to: 'payment-database',
        type: 'database-call',
        description: 'Payment service reads/writes to payment database'
      },
      {
        from: 'payment-service',
        to: 'user-service',
        type: 'api-call',
        description: 'Payment service validates users via user service'
      }
    ],
    technology_stack: {
      'Node.js': 1,
      'Java': 1,
      'PostgreSQL': 2,
      'Express': 1,
      'Spring Boot': 1
    },
    quality_score: 0.85,
    analysis_metadata: {
      analyzed_at: new Date().toISOString(),
      services_count: 4,
      dependencies_count: 3,
      technologies_detected: ['Node.js', 'Java', 'PostgreSQL', 'Express', 'Spring Boot']
    }
  };

  const mockProposedArchitecture: ProposedArchitecture = {
    architecture_overview: {
      style: 'microservices',
      integration_approach: 'Event-driven integration',
      rationale: 'Extends existing microservices architecture with new notification capabilities'
    },
    new_services: [
      {
        id: 'notification-service',
        name: 'Notification Service',
        type: 'service',
        technology: 'Node.js + Express',
        description: 'Handles real-time notifications via email, SMS, and push notifications',
        endpoints: ['/api/notifications', '/api/templates'],
        dependencies: ['notification-database', 'message-queue']
      },
      {
        id: 'notification-database',
        name: 'Notification Database',
        type: 'database',
        technology: 'MongoDB',
        description: 'Stores notification templates and delivery status'
      },
      {
        id: 'message-queue',
        name: 'Message Queue',
        type: 'component',
        technology: 'Apache Kafka',
        description: 'Handles asynchronous message processing for notifications'
      }
    ],
    modified_services: [
      {
        id: 'user-service',
        name: 'User Service',
        type: 'service',
        technology: 'Node.js + Express',
        description: 'Enhanced with notification preferences and event publishing',
        endpoints: ['/api/users', '/api/auth', '/api/preferences'],
        dependencies: ['user-database', 'message-queue']
      }
    ],
    integration_points: [
      {
        from_service: 'user-service',
        to_service: 'message-queue',
        type: 'event-stream',
        description: 'Publishes user events for notification processing',
        implementation_notes: 'Use event sourcing pattern for reliable delivery'
      },
      {
        from_service: 'notification-service',
        to_service: 'message-queue',
        type: 'message-queue',
        description: 'Consumes user events and processes notifications',
        implementation_notes: 'Implement idempotent processing for reliability'
      },
      {
        from_service: 'payment-service',
        to_service: 'message-queue',
        type: 'event-stream',
        description: 'Publishes payment events for order notifications',
        implementation_notes: 'Add event publishing to existing payment flow'
      }
    ],
    impact_analysis: {
      risk_level: 'medium',
      breaking_changes: false,
      downtime_required: false
    }
  };

  const mockArchitectureChanges: ArchitectureChange[] = [
    {
      id: '1',
      type: 'add',
      entity: 'service',
      name: 'Notification Service',
      description: 'New service for handling real-time notifications',
      impact: 'low',
      affectedServices: ['notification-service'],
      breakingChange: false,
      migrationRequired: false,
      estimatedEffort: 40,
      riskLevel: 'low',
      dependencies: ['message-queue'],
      metadata: {
        reason: 'Business requirement for real-time notifications',
        alternatives: ['Third-party notification service', 'Email-only notifications'],
        rollbackPlan: 'Remove notification service and disable event publishing',
        testingRequired: true,
        documentationRequired: true
      }
    },
    {
      id: '2',
      type: 'modify',
      entity: 'service',
      name: 'User Service',
      description: 'Enhanced with notification preferences and event publishing',
      impact: 'medium',
      affectedServices: ['user-service'],
      breakingChange: false,
      migrationRequired: true,
      estimatedEffort: 20,
      riskLevel: 'medium',
      dependencies: ['message-queue'],
      metadata: {
        reason: 'Integration with notification system',
        alternatives: ['Polling-based approach', 'Direct API calls'],
        rollbackPlan: 'Remove event publishing and revert to original version',
        testingRequired: true,
        documentationRequired: true
      }
    },
    {
      id: '3',
      type: 'add',
      entity: 'component',
      name: 'Message Queue',
      description: 'Apache Kafka for asynchronous message processing',
      impact: 'high',
      affectedServices: ['user-service', 'notification-service', 'payment-service'],
      breakingChange: true,
      migrationRequired: true,
      estimatedEffort: 60,
      riskLevel: 'high',
      dependencies: [],
      metadata: {
        reason: 'Enable event-driven architecture for notifications',
        alternatives: ['RabbitMQ', 'AWS SQS', 'Direct API calls'],
        rollbackPlan: 'Remove Kafka and implement direct API calls',
        testingRequired: true,
        documentationRequired: true
      }
    }
  ];

  const handleModeChange = (mode: 'greenfield' | 'brownfield') => {
    setProjectMode(mode);
    if (mode === 'greenfield') {
      setExistingArchitecture(null);
      setProposedArchitecture(null);
      setArchitectureChanges([]);
    }
  };

  const handleGitHubAnalysisComplete = (analysis: any) => {
    setExistingArchitecture(mockExistingArchitecture);
    toast.success('Repository analysis completed successfully');
  };

  const handleGitHubAnalysisError = (error: string) => {
    toast.error(`Repository analysis failed: ${error}`);
  };

  const loadMockData = () => {
    setExistingArchitecture(mockExistingArchitecture);
    setProposedArchitecture(mockProposedArchitecture);
    setArchitectureChanges(mockArchitectureChanges);
    toast.success('Mock data loaded successfully');
  };

  const convertToArchitectureGraph = (architecture: ExistingArchitecture | ProposedArchitecture): ArchitectureGraph => {
    if ('services' in architecture) {
      // ExistingArchitecture
      const services = architecture.services.map((service, index) => ({
        id: service.id,
        name: service.name,
        type: (service.type === 'database' ? 'database' : 'service') as any,
        technology: service.technology,
        status: 'healthy' as const,
        description: service.description,
        position: { x: (index % 3) * 200, y: Math.floor(index / 3) * 150 },
        metadata: {
          endpoints: service.endpoints,
          dependencies: service.dependencies
        }
      }));

      const dependencies = architecture.dependencies.map((dep, index) => ({
        id: `e-${dep.from}-${dep.to}`,
        source: dep.from,
        target: dep.to,
        type: dep.type as any,
        description: dep.description
      }));

      return { services, dependencies };
    } else {
      // ProposedArchitecture
      const allServices = [...architecture.new_services, ...architecture.modified_services];
      const services = allServices.map((service, index) => ({
        id: service.id,
        name: service.name,
        type: (service.type === 'database' ? 'database' : 'service') as any,
        technology: service.technology,
        status: 'healthy' as const,
        description: service.description,
        position: { x: (index % 3) * 200, y: Math.floor(index / 3) * 150 },
        metadata: {
          endpoints: service.endpoints,
          dependencies: service.dependencies
        }
      }));

      const dependencies = architecture.integration_points.map((point, index) => ({
        id: `e-${point.from_service}-${point.to_service}`,
        source: point.from_service,
        target: point.to_service,
        type: point.type as any,
        description: point.description
      }));

      return { services, dependencies };
    }
  };

  const approveIntegration = async () => {
    toast.success('Integration approved successfully');
  };

  const rejectIntegration = async () => {
    toast.error('Integration rejected');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              Brownfield Project Demo
            </h1>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto">
              Experience how ArchMesh handles existing system integration with new features.
              This demo shows the complete brownfield workflow from repository analysis to architecture comparison.
            </p>
          </div>

          {/* Mode Selector */}
          <ModeSelector
            value={projectMode}
            onChange={handleModeChange}
            className="mb-8"
          />

          {/* Demo Controls */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <ActivityIcon className="h-5 w-5 text-blue-600" />
                <span>Demo Controls</span>
              </CardTitle>
              <CardDescription>
                Use these controls to simulate the brownfield workflow
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-4">
                <Button
                  onClick={loadMockData}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  Load Mock Data
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setExistingArchitecture(null);
                    setProposedArchitecture(null);
                    setArchitectureChanges([]);
                  }}
                >
                  Clear Data
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Brownfield-specific sections */}
          {projectMode === 'brownfield' && (
            <div className="space-y-6">
              {/* GitHub Repository Analysis */}
              {!existingArchitecture && (
                <GitHubConnector
                  projectId="demo-project"
                  onAnalysisComplete={handleGitHubAnalysisComplete}
                  onError={handleGitHubAnalysisError}
                />
              )}

              {/* Existing Architecture Visualization */}
              {existingArchitecture && (
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BuildingIcon className="h-5 w-5 text-blue-600" />
                      <span>Current Architecture</span>
                    </CardTitle>
                    <CardDescription>
                      Existing system architecture from {existingArchitecture.repository_url}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center space-x-2">
                          <BuildingIcon className="h-5 w-5 text-blue-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Services</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                          {existingArchitecture.analysis_metadata.services_count}
                        </p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center space-x-2">
                          <ActivityIcon className="h-5 w-5 text-green-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Dependencies</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                          {existingArchitecture.analysis_metadata.dependencies_count}
                        </p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center space-x-2">
                          <BarChart3Icon className="h-5 w-5 text-purple-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Quality Score</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                          {Math.round(existingArchitecture.quality_score * 100)}%
                        </p>
                      </div>
                    </div>

                    {/* Technologies */}
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                        Technologies Detected
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {existingArchitecture.analysis_metadata.technologies_detected.map((tech) => (
                          <Badge key={tech} variant="secondary">{tech}</Badge>
                        ))}
                      </div>
                    </div>

                    {/* Services List */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                        Services Found
                      </h5>
                      <div className="space-y-2">
                        {existingArchitecture.services.map((service) => (
                          <div
                            key={service.id}
                            className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                          >
                            <div>
                              <p className="font-medium text-gray-900 dark:text-gray-100">{service.name}</p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">{service.description}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{service.technology}</p>
                              <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{service.type}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Architecture Comparison */}
              {existingArchitecture && proposedArchitecture && (
                <Card className="border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <ActivityIcon className="h-5 w-5 text-orange-600" />
                      <span>Architecture Comparison</span>
                    </CardTitle>
                    <CardDescription>
                      Compare current architecture with proposed changes
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ArchitectureComparison
                      currentArchitecture={convertToArchitectureGraph(existingArchitecture)}
                      proposedArchitecture={convertToArchitectureGraph(proposedArchitecture)}
                      changes={architectureChanges}
                      impactAnalysis={{
                        overallImpact: 'high',
                        affectedSystems: ['user-service', 'payment-service', 'notification-service'],
                        riskFactors: {
                          breakingChanges: 1,
                          dataMigrationRequired: false,
                          downtimeRequired: false,
                          rollbackComplexity: 'medium',
                          testingComplexity: 'high'
                        },
                        recommendations: {
                          implementation: ['Implement feature flags', 'Use gradual rollout', 'Add comprehensive monitoring'],
                          testing: ['Integration testing', 'Performance testing', 'Load testing'],
                          deployment: ['Blue-green deployment', 'Canary releases', 'Database migration scripts'],
                          monitoring: ['Enhanced logging', 'Performance metrics', 'Error tracking']
                        },
                        timeline: {
                          planning: 5,
                          development: 15,
                          testing: 10,
                          deployment: 5,
                          total: 35
                        }
                      }}
                      onApprove={(approval) => {
                        console.log('Approval:', approval);
                        approveIntegration();
                      }}
                      onReject={(reason) => {
                        console.log('Rejection reason:', reason);
                        rejectIntegration();
                      }}
                      onExport={(format) => {
                        console.log('Export format:', format);
                        toast.success(`Exporting comparison as ${format.toUpperCase()}`);
                      }}
                    />
                  </CardContent>
                </Card>
              )}

              {/* Next Steps */}
              {existingArchitecture && proposedArchitecture && (
                <Card className="border-0 shadow-lg bg-gradient-to-r from-green-50 to-blue-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      <span>Next Steps</span>
                    </CardTitle>
                    <CardDescription>
                      Your brownfield integration is ready for implementation
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                          <span className="text-green-600 font-semibold">1</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Repository Analysis Complete</p>
                          <p className="text-sm text-gray-600">Existing architecture has been analyzed and indexed</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                          <span className="text-green-600 font-semibold">2</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Integration Design Ready</p>
                          <p className="text-sm text-gray-600">Proposed architecture with minimal disruption</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <ArrowRightIcon className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Ready for Implementation</p>
                          <p className="text-sm text-gray-600">Start the brownfield workflow to begin development</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Greenfield Mode Info */}
          {projectMode === 'greenfield' && (
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BuildingIcon className="h-5 w-5 text-green-600" />
                  <span>Greenfield Mode</span>
                </CardTitle>
                <CardDescription>
                  Building a new system from scratch
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <BuildingIcon className="h-16 w-16 text-green-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">New Project Mode</h3>
                  <p className="text-gray-600 mb-6">
                    In greenfield mode, you can design a completely new system architecture
                    without any existing constraints. Switch back to brownfield mode to see
                    the integration capabilities.
                  </p>
                  <Button
                    onClick={() => setProjectMode('brownfield')}
                    variant="outline"
                    className="border-green-600 text-green-600 hover:bg-green-50"
                  >
                    Switch to Brownfield Mode
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
