'use client';

import { useState } from 'react';
import { RequirementsViewer } from '@/components/RequirementsViewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Requirements } from '@/types';
import { toast } from 'sonner';

// Sample requirements data for demonstration
const sampleRequirements: Requirements = {
  id: 'req-123',
  project_id: 'proj-456',
  structured_requirements: {
    business_goals: [
      'Launch an online marketplace for handmade crafts',
      'Support 10,000 concurrent users',
      'Process payments securely',
      'Mobile-first experience'
    ],
    functional_requirements: [
      'User registration and authentication',
      'Product catalog with search and filtering',
      'Shopping cart and checkout process',
      'Payment processing with Stripe integration',
      'Order tracking and history',
      'Seller dashboard for inventory management',
      'Admin panel for platform management',
      'Review and rating system'
    ],
    non_functional_requirements: {
      performance: [
        'Page load time < 2 seconds',
        'API response time < 500ms',
        'Support 10,000 concurrent users',
        'Database query optimization'
      ],
      security: [
        'HTTPS only communication',
        'PCI DSS compliance for payments',
        'Data encryption at rest and in transit',
        'Regular security audits and penetration testing',
        'OAuth 2.0 authentication'
      ],
      scalability: [
        'Horizontal scaling capability',
        'Auto-scaling based on traffic',
        'CDN for static assets',
        'Microservices architecture',
        'Load balancing across multiple servers'
      ],
      reliability: [
        '99.9% uptime SLA',
        'Automated backup and recovery',
        'Graceful error handling',
        'Circuit breaker pattern implementation'
      ],
      maintainability: [
        'Modular code architecture',
        'Comprehensive test coverage',
        'API documentation',
        'Monitoring and logging',
        'CI/CD pipeline'
      ]
    },
    constraints: [
      'Budget: $50,000 for first 6 months',
      'Timeline: MVP in 3 months',
      'Team: 3 developers',
      'Cloud: AWS preferred',
      'Compliance: GDPR and CCPA'
    ],
    stakeholders: [
      {
        name: 'Sarah Johnson',
        role: 'CEO',
        concerns: ['Time to market', 'User adoption', 'Revenue growth']
      },
      {
        name: 'Michael Chen',
        role: 'CTO',
        concerns: ['Scalability', 'Security', 'Maintainability', 'Performance']
      },
      {
        name: 'Emily Rodriguez',
        role: 'CFO',
        concerns: ['Budget control', 'ROI', 'Cost optimization']
      },
      {
        name: 'David Kim',
        role: 'Marketing Director',
        concerns: ['User experience', 'Analytics integration', 'SEO optimization']
      }
    ]
  },
  clarification_questions: [
    {
      question: 'What is the expected daily user load during peak hours?',
      category: 'Performance',
      priority: 'high'
    },
    {
      question: 'Do you need real-time inventory updates across all sellers?',
      category: 'Functional',
      priority: 'high'
    },
    {
      question: 'What payment methods should be supported beyond credit cards?',
      category: 'Functional',
      priority: 'medium'
    },
    {
      question: 'Should the platform support international sellers and currencies?',
      category: 'Business',
      priority: 'medium'
    },
    {
      question: 'What level of seller verification is required?',
      category: 'Security',
      priority: 'low'
    }
  ],
  identified_gaps: [
    'Missing detailed user personas and use cases',
    'No specific performance benchmarks defined',
    'Unclear data retention and privacy policies',
    'Missing disaster recovery requirements'
  ],
  confidence_score: 0.85,
  status: 'pending',
  created_at: '2025-01-15T10:30:00Z'
};

export default function DemoRequirementsPage() {
  const [requirements, setRequirements] = useState<Requirements>(sampleRequirements);
  const [actionHistory, setActionHistory] = useState<string[]>([]);

  const handleApprove = async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const action = `Approved requirements at ${new Date().toLocaleTimeString()}`;
    setActionHistory(prev => [action, ...prev]);
    
    toast.success('Requirements approved successfully!');
  };

  const handleReject = async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const action = `Rejected requirements at ${new Date().toLocaleTimeString()}`;
    setActionHistory(prev => [action, ...prev]);
    
    toast.success('Requirements rejected');
  };

  const resetDemo = () => {
    setRequirements(sampleRequirements);
    setActionHistory([]);
    toast.info('Demo reset to initial state');
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-slate-900">Requirements Viewer Demo</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Explore the comprehensive requirements viewer component with structured data display,
          approval workflows, and interactive features.
        </p>
        <div className="flex justify-center space-x-4">
          <Button onClick={resetDemo} variant="outline">
            Reset Demo
          </Button>
          <Badge variant="secondary" className="px-3 py-1">
            Sample Data: E-Commerce Platform
          </Badge>
        </div>
      </div>

      <div className="max-w-6xl mx-auto">
        <RequirementsViewer 
          requirements={requirements}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      </div>

      {/* Action History */}
      {actionHistory.length > 0 && (
        <Card className="max-w-6xl mx-auto">
          <CardHeader>
            <CardTitle>Action History</CardTitle>
            <CardDescription>
              Track of actions performed on the requirements
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {actionHistory.map((action, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <span className="text-sm text-slate-700">{action}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Component Features */}
      <Card className="max-w-6xl mx-auto">
        <CardHeader>
          <CardTitle>Component Features</CardTitle>
          <CardDescription>
            The RequirementsViewer component includes the following features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="font-semibold text-slate-900">Display Features</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Structured requirements display</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Tabbed non-functional requirements</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Stakeholder cards with concerns</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Prioritized clarification questions</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Confidence score with progress bar</span>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-slate-900">Interactive Features</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Approve/Reject actions</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>JSON export functionality</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Color-coded priority indicators</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Summary statistics</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Responsive design</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage Example */}
      <Card className="max-w-6xl mx-auto">
        <CardHeader>
          <CardTitle>Usage Example</CardTitle>
          <CardDescription>
            How to use the RequirementsViewer component in your application
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto">
            <pre className="text-sm">
{`import { RequirementsViewer } from '@/components/RequirementsViewer';
import { Requirements } from '@/types';

function MyComponent() {
  const handleApprove = async () => {
    // Handle approval logic
    console.log('Requirements approved');
  };

  const handleReject = async () => {
    // Handle rejection logic
    console.log('Requirements rejected');
  };

  return (
    <RequirementsViewer 
      requirements={requirements}
      onApprove={handleApprove}
      onReject={handleReject}
    />
  );
}`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
