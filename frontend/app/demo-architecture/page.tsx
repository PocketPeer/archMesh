'use client';

import React, { useState } from 'react';
import { ArchitectureViewer } from '@/components/ArchitectureViewer';
import { Architecture } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

// Mock architecture data for demonstration
const mockArchitecture: Architecture = {
  id: 'arch-123',
  project_id: 'proj-456',
  architecture_style: 'Microservices',
  components: [
    {
      name: 'User Service',
      type: 'Microservice',
      description: 'Handles user authentication, registration, and profile management',
      technologies: ['Node.js', 'Express', 'JWT', 'MongoDB'],
      responsibilities: [
        'User registration and authentication',
        'Profile management',
        'Password reset functionality',
        'User session management'
      ]
    },
    {
      name: 'API Gateway',
      type: 'Gateway',
      description: 'Central entry point for all client requests',
      technologies: ['Kong', 'Nginx', 'Docker'],
      responsibilities: [
        'Request routing and load balancing',
        'Rate limiting and throttling',
        'Authentication and authorization',
        'API versioning'
      ]
    },
    {
      name: 'Product Catalog Service',
      type: 'Microservice',
      description: 'Manages product information and inventory',
      technologies: ['Python', 'FastAPI', 'PostgreSQL', 'Redis'],
      responsibilities: [
        'Product CRUD operations',
        'Inventory management',
        'Product search and filtering',
        'Category management'
      ]
    },
    {
      name: 'Order Service',
      type: 'Microservice',
      description: 'Handles order processing and payment integration',
      technologies: ['Java', 'Spring Boot', 'PostgreSQL', 'RabbitMQ'],
      responsibilities: [
        'Order creation and management',
        'Payment processing',
        'Order status tracking',
        'Inventory updates'
      ]
    },
    {
      name: 'Notification Service',
      type: 'Microservice',
      description: 'Sends notifications via email, SMS, and push notifications',
      technologies: ['Go', 'Gin', 'MongoDB', 'AWS SNS'],
      responsibilities: [
        'Email notifications',
        'SMS notifications',
        'Push notifications',
        'Notification templates'
      ]
    },
    {
      name: 'Analytics Service',
      type: 'Microservice',
      description: 'Collects and processes analytics data',
      technologies: ['Python', 'Django', 'ClickHouse', 'Kafka'],
      responsibilities: [
        'Event tracking',
        'Data aggregation',
        'Report generation',
        'Real-time analytics'
      ]
    }
  ],
  c4_diagram_context: `C4Context
    title System Context Diagram for E-commerce Platform
    
    Person(customer, "Customer", "A customer who wants to buy products")
    Person(admin, "Admin", "A system administrator")
    
    System(ecommerce, "E-commerce Platform", "Online shopping platform for customers")
    System_Ext(payment, "Payment Gateway", "External payment processing service")
    System_Ext(email, "Email Service", "External email service provider")
    System_Ext(sms, "SMS Service", "External SMS service provider")
    
    Rel(customer, ecommerce, "Browse products, place orders", "HTTPS")
    Rel(admin, ecommerce, "Manage products, view analytics", "HTTPS")
    Rel(ecommerce, payment, "Process payments", "HTTPS")
    Rel(ecommerce, email, "Send notifications", "SMTP")
    Rel(ecommerce, sms, "Send SMS notifications", "HTTPS")`,
  technology_stack: {
    frontend: [
      { name: 'React', version: '18.2.0', description: 'Frontend framework' },
      { name: 'TypeScript', version: '4.9.0', description: 'Type-safe JavaScript' },
      { name: 'Tailwind CSS', version: '3.3.0', description: 'Utility-first CSS framework' },
      { name: 'Next.js', version: '14.0.0', description: 'React framework with SSR' }
    ],
    backend: [
      { name: 'Node.js', version: '18.17.0', description: 'JavaScript runtime' },
      { name: 'Python', version: '3.11.0', description: 'Programming language' },
      { name: 'Java', version: '17', description: 'Programming language' },
      { name: 'Go', version: '1.21', description: 'Programming language' }
    ],
    database: [
      { name: 'PostgreSQL', version: '15.0', description: 'Primary relational database' },
      { name: 'MongoDB', version: '6.0', description: 'Document database' },
      { name: 'Redis', version: '7.0', description: 'In-memory cache' },
      { name: 'ClickHouse', version: '23.0', description: 'Analytics database' }
    ],
    infrastructure: [
      { name: 'Docker', version: '24.0', description: 'Containerization' },
      { name: 'Kubernetes', version: '1.28', description: 'Container orchestration' },
      { name: 'AWS', description: 'Cloud platform' },
      { name: 'Terraform', version: '1.6', description: 'Infrastructure as code' }
    ]
  },
  alternatives: [
    {
      name: 'Monolithic Architecture',
      description: 'Single deployable unit containing all functionality',
      status: 'Rejected',
      pros: [
        'Simpler deployment and testing',
        'Easier to develop initially',
        'No network latency between components',
        'Simpler data consistency'
      ],
      cons: [
        'Difficult to scale individual components',
        'Technology lock-in',
        'Single point of failure',
        'Harder to maintain as system grows'
      ],
      trade_offs: 'While simpler initially, monolithic architecture becomes a bottleneck as the system scales and requires different teams to work on different parts.',
      reason_for_rejection: 'System needs to handle high traffic and requires independent scaling of different components. Microservices provide better scalability and team autonomy.'
    },
    {
      name: 'Serverless Architecture',
      description: 'Event-driven architecture using cloud functions',
      status: 'Considered',
      pros: [
        'Automatic scaling',
        'Pay-per-execution pricing',
        'No server management',
        'Built-in high availability'
      ],
      cons: [
        'Cold start latency',
        'Vendor lock-in',
        'Limited execution time',
        'Complex debugging'
      ],
      trade_offs: 'Serverless is great for event-driven workloads but may not be suitable for all use cases due to cold starts and execution time limits.',
      reason_for_rejection: 'Some services require long-running processes and consistent performance. Hybrid approach with containers provides better control.'
    },
    {
      name: 'Event-Driven Architecture',
      description: 'Asynchronous communication through events',
      status: 'Partially Adopted',
      pros: [
        'Loose coupling between services',
        'High scalability',
        'Fault tolerance',
        'Real-time processing'
      ],
      cons: [
        'Complex event ordering',
        'Eventual consistency challenges',
        'Debugging complexity',
        'Message ordering issues'
      ],
      trade_offs: 'Event-driven architecture provides excellent scalability but adds complexity in ensuring data consistency and debugging.',
      reason_for_rejection: 'Adopted for notification and analytics services where eventual consistency is acceptable, but not for core business operations.'
    }
  ],
  status: 'completed',
  created_at: '2024-01-15T10:30:00Z'
};

export default function DemoArchitecturePage() {
  const [actionHistory, setActionHistory] = useState<string[]>([]);

  const handleApprove = async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const message = `Architecture approved at ${new Date().toLocaleTimeString()}`;
    setActionHistory(prev => [message, ...prev]);
    toast.success('Architecture approved successfully!');
  };

  const handleReject = async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const message = `Architecture rejected at ${new Date().toLocaleTimeString()}`;
    setActionHistory(prev => [message, ...prev]);
    toast.error('Architecture rejected');
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Architecture Viewer Demo
          </h1>
          <p className="text-slate-600">
            Interactive demonstration of the ArchitectureViewer component with mock data
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Architecture Viewer */}
          <div className="lg:col-span-3">
            <ArchitectureViewer
              architecture={mockArchitecture}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          </div>

          {/* Sidebar with Info and Actions */}
          <div className="space-y-6">
            {/* Architecture Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Architecture Info</CardTitle>
                <CardDescription>Details about this design</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium text-sm text-slate-700 mb-2">Style</h4>
                  <Badge variant="default">{mockArchitecture.architecture_style}</Badge>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-slate-700 mb-2">Components</h4>
                  <p className="text-sm text-slate-600">{mockArchitecture.components?.length || 0} services</p>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-slate-700 mb-2">Status</h4>
                  <Badge variant={mockArchitecture.status === 'completed' ? 'default' : 'secondary'}>
                    {mockArchitecture.status}
                  </Badge>
                </div>
                <div>
                  <h4 className="font-medium text-sm text-slate-700 mb-2">Created</h4>
                  <p className="text-sm text-slate-600">
                    {new Date(mockArchitecture.created_at).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Action History */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Action History</CardTitle>
                <CardDescription>Recent actions taken</CardDescription>
              </CardHeader>
              <CardContent>
                {actionHistory.length === 0 ? (
                  <p className="text-sm text-slate-500 italic">No actions taken yet</p>
                ) : (
                  <div className="space-y-2">
                    {actionHistory.map((action, index) => (
                      <div key={index} className="text-sm p-2 bg-slate-50 rounded border-l-2 border-blue-500">
                        {action}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Demo Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Demo Controls</CardTitle>
                <CardDescription>Test the component features</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={handleApprove} 
                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                  Test Approve Action
                </Button>
                <Button 
                  onClick={handleReject} 
                  variant="destructive" 
                  className="w-full"
                >
                  Test Reject Action
                </Button>
                <Button 
                  onClick={() => setActionHistory([])} 
                  variant="outline" 
                  className="w-full"
                >
                  Clear History
                </Button>
              </CardContent>
            </Card>

            {/* Component Features */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Component Features</CardTitle>
                <CardDescription>What this component includes</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-slate-600">
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    C4 Diagram rendering with Mermaid
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Interactive component cards
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Technology stack tabs
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Expandable alternatives
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Diagram export functionality
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    JSON download feature
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
