'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BuildingIcon, 
  CloudIcon, 
  DatabaseIcon, 
  ServerIcon,
  GlobeIcon,
  ShieldIcon,
  ZapIcon,
  UsersIcon,
  ArrowRightIcon,
  CheckIcon
} from 'lucide-react';

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'web-app' | 'microservices' | 'data-platform' | 'enterprise' | 'mobile' | 'ai-ml';
  complexity: 'simple' | 'medium' | 'complex';
  estimatedTime: string;
  features: string[];
  technologies: string[];
  icon: React.ReactNode;
  color: string;
}

const workflowTemplates: WorkflowTemplate[] = [
  {
    id: 'modern-web-app',
    name: 'Modern Web Application',
    description: 'Full-stack web application with modern architecture patterns',
    category: 'web-app',
    complexity: 'medium',
    estimatedTime: '2-4 hours',
    features: [
      'User authentication & authorization',
      'Real-time features with WebSockets',
      'API-first design',
      'Responsive frontend',
      'Database design & optimization'
    ],
    technologies: ['React', 'Node.js', 'PostgreSQL', 'Redis', 'Docker'],
    icon: <GlobeIcon className="h-6 w-6" />,
    color: 'bg-blue-500'
  },
  {
    id: 'microservices-architecture',
    name: 'Microservices Architecture',
    description: 'Scalable microservices system with service mesh',
    category: 'microservices',
    complexity: 'complex',
    estimatedTime: '4-8 hours',
    features: [
      'Service decomposition strategy',
      'API Gateway implementation',
      'Service mesh configuration',
      'Event-driven architecture',
      'Container orchestration'
    ],
    technologies: ['Kubernetes', 'Istio', 'gRPC', 'Kafka', 'Prometheus'],
    icon: <ServerIcon className="h-6 w-6" />,
    color: 'bg-purple-500'
  },
  {
    id: 'data-platform',
    name: 'Data Platform',
    description: 'Comprehensive data processing and analytics platform',
    category: 'data-platform',
    complexity: 'complex',
    estimatedTime: '6-12 hours',
    features: [
      'Data ingestion pipelines',
      'Real-time stream processing',
      'Data warehouse design',
      'Analytics & reporting',
      'ML model deployment'
    ],
    technologies: ['Apache Kafka', 'Apache Spark', 'Airflow', 'Snowflake', 'TensorFlow'],
    icon: <DatabaseIcon className="h-6 w-6" />,
    color: 'bg-green-500'
  },
  {
    id: 'enterprise-system',
    name: 'Enterprise System',
    description: 'Large-scale enterprise application with compliance',
    category: 'enterprise',
    complexity: 'complex',
    estimatedTime: '8-16 hours',
    features: [
      'Multi-tenant architecture',
      'Security & compliance',
      'Integration patterns',
      'Scalability planning',
      'Disaster recovery'
    ],
    technologies: ['Java', 'Spring Boot', 'Oracle', 'Active Directory', 'Kubernetes'],
    icon: <BuildingIcon className="h-6 w-6" />,
    color: 'bg-orange-500'
  },
  {
    id: 'mobile-backend',
    name: 'Mobile Backend',
    description: 'Backend services for mobile applications',
    category: 'mobile',
    complexity: 'medium',
    estimatedTime: '2-4 hours',
    features: [
      'RESTful API design',
      'Push notifications',
      'Offline synchronization',
      'User management',
      'Content delivery'
    ],
    technologies: ['Node.js', 'MongoDB', 'Firebase', 'AWS S3', 'CloudFront'],
    icon: <ZapIcon className="h-6 w-6" />,
    color: 'bg-yellow-500'
  },
  {
    id: 'ai-ml-platform',
    name: 'AI/ML Platform',
    description: 'Machine learning platform with model serving',
    category: 'ai-ml',
    complexity: 'complex',
    estimatedTime: '6-10 hours',
    features: [
      'Model training pipelines',
      'Feature engineering',
      'Model serving infrastructure',
      'A/B testing framework',
      'Monitoring & observability'
    ],
    technologies: ['Python', 'TensorFlow', 'Kubeflow', 'MLflow', 'Prometheus'],
    icon: <ShieldIcon className="h-6 w-6" />,
    color: 'bg-red-500'
  }
];

interface WorkflowTemplatesProps {
  onSelectTemplate: (template: WorkflowTemplate) => void;
  selectedTemplate?: string;
}

export default function WorkflowTemplates({ 
  onSelectTemplate, 
  selectedTemplate 
}: WorkflowTemplatesProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = [
    { id: 'all', name: 'All Templates', icon: <BuildingIcon className="h-4 w-4" /> },
    { id: 'web-app', name: 'Web Apps', icon: <GlobeIcon className="h-4 w-4" /> },
    { id: 'microservices', name: 'Microservices', icon: <ServerIcon className="h-4 w-4" /> },
    { id: 'data-platform', name: 'Data Platform', icon: <DatabaseIcon className="h-4 w-4" /> },
    { id: 'enterprise', name: 'Enterprise', icon: <BuildingIcon className="h-4 w-4" /> },
    { id: 'mobile', name: 'Mobile', icon: <ZapIcon className="h-4 w-4" /> },
    { id: 'ai-ml', name: 'AI/ML', icon: <ShieldIcon className="h-4 w-4" /> }
  ];

  const filteredTemplates = selectedCategory === 'all' 
    ? workflowTemplates 
    : workflowTemplates.filter(template => template.category === selectedCategory);

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'complex': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <Button
            key={category.id}
            variant={selectedCategory === category.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory(category.id)}
            className="flex items-center gap-2"
          >
            {category.icon}
            {category.name}
          </Button>
        ))}
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <Card 
            key={template.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedTemplate === template.id 
                ? 'ring-2 ring-blue-500 bg-blue-50' 
                : 'hover:border-blue-300'
            }`}
            onClick={() => onSelectTemplate(template)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${template.color} text-white`}>
                    {template.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {template.description}
                    </CardDescription>
                  </div>
                </div>
                {selectedTemplate === template.id && (
                  <CheckIcon className="h-5 w-5 text-blue-500" />
                )}
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Complexity and Time */}
              <div className="flex items-center gap-2">
                <Badge className={getComplexityColor(template.complexity)}>
                  {template.complexity}
                </Badge>
                <Badge variant="outline">
                  {template.estimatedTime}
                </Badge>
              </div>

              {/* Features */}
              <div>
                <h4 className="font-medium text-sm mb-2">Key Features:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {template.features.slice(0, 3).map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                      {feature}
                    </li>
                  ))}
                  {template.features.length > 3 && (
                    <li className="text-xs text-gray-500">
                      +{template.features.length - 3} more features
                    </li>
                  )}
                </ul>
              </div>

              {/* Technologies */}
              <div>
                <h4 className="font-medium text-sm mb-2">Technologies:</h4>
                <div className="flex flex-wrap gap-1">
                  {template.technologies.slice(0, 4).map((tech, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {tech}
                    </Badge>
                  ))}
                  {template.technologies.length > 4 && (
                    <Badge variant="outline" className="text-xs">
                      +{template.technologies.length - 4}
                    </Badge>
                  )}
                </div>
              </div>

              {/* Select Button */}
              <Button 
                className="w-full"
                variant={selectedTemplate === template.id ? 'default' : 'outline'}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectTemplate(template);
                }}
              >
                {selectedTemplate === template.id ? (
                  <>
                    <CheckIcon className="h-4 w-4 mr-2" />
                    Selected
                  </>
                ) : (
                  <>
                    Select Template
                    <ArrowRightIcon className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-8">
          <BuildingIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600">
            Try selecting a different category to see more templates.
          </p>
        </div>
      )}
    </div>
  );
}
