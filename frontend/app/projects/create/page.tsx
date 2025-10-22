'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { ProjectCreate } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { 
  ArrowLeftIcon,
  BuildingIcon,
  CloudIcon,
  DatabaseIcon,
  BriefcaseIcon,
  InfoIcon,
  CheckCircleIcon,
  SparklesIcon,
  ZapIcon,
  ShieldIcon,
  UsersIcon,
  GlobeIcon,
  ServerIcon,
  BrainIcon
} from 'lucide-react';

interface EnhancedWorkflowTemplate {
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
  benefits: string[];
  workflowSteps: string[];
  diagramTypes: string[];
  knowledgeBaseIntegration: boolean;
}

const enhancedTemplates: EnhancedWorkflowTemplate[] = [
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
    color: 'bg-blue-500',
    benefits: [
      'Scalable architecture patterns',
      'Modern development practices',
      'Security best practices',
      'Performance optimization'
    ],
    workflowSteps: [
      'Requirements Analysis',
      'Architecture Design',
      'Technology Selection',
      'Security Planning',
      'Deployment Strategy'
    ],
    diagramTypes: ['C4 Context', 'C4 Container', 'Sequence Diagrams'],
    knowledgeBaseIntegration: true
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
    color: 'bg-purple-500',
    benefits: [
      'Independent service deployment',
      'Technology diversity',
      'Fault isolation',
      'Team autonomy'
    ],
    workflowSteps: [
      'Domain Analysis',
      'Service Decomposition',
      'API Design',
      'Data Management',
      'Communication Patterns',
      'Monitoring & Observability'
    ],
    diagramTypes: ['C4 Context', 'C4 Container', 'C4 Component', 'Sequence Diagrams', 'NFR Mapping'],
    knowledgeBaseIntegration: true
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
    color: 'bg-green-500',
    benefits: [
      'Real-time data processing',
      'Scalable analytics',
      'ML integration',
      'Data governance'
    ],
    workflowSteps: [
      'Data Requirements Analysis',
      'Data Architecture Design',
      'Pipeline Design',
      'Storage Strategy',
      'Processing Framework',
      'ML Integration'
    ],
    diagramTypes: ['C4 Context', 'C4 Container', 'Sequence Diagrams', 'NFR Mapping'],
    knowledgeBaseIntegration: true
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
    technologies: ['Java', 'Spring Boot', 'Oracle', 'ActiveMQ', 'LDAP'],
    icon: <BuildingIcon className="h-6 w-6" />,
    color: 'bg-orange-500',
    benefits: [
      'Enterprise-grade security',
      'Compliance readiness',
      'High availability',
      'Integration capabilities'
    ],
    workflowSteps: [
      'Business Requirements',
      'Compliance Analysis',
      'Security Architecture',
      'Integration Design',
      'Scalability Planning',
      'Disaster Recovery'
    ],
    diagramTypes: ['C4 Context', 'C4 Container', 'C4 Component', 'Sequence Diagrams', 'NFR Mapping'],
    knowledgeBaseIntegration: true
  },
  {
    id: 'ai-ml-platform',
    name: 'AI/ML Platform',
    description: 'Intelligent system with machine learning capabilities',
    category: 'ai-ml',
    complexity: 'complex',
    estimatedTime: '6-10 hours',
    features: [
      'ML model training pipeline',
      'Model serving infrastructure',
      'Data preprocessing',
      'Model monitoring',
      'A/B testing framework'
    ],
    technologies: ['Python', 'TensorFlow', 'Kubernetes', 'MLflow', 'Prometheus'],
    icon: <BrainIcon className="h-6 w-6" />,
    color: 'bg-indigo-500',
    benefits: [
      'Automated ML workflows',
      'Model versioning',
      'Performance monitoring',
      'Scalable inference'
    ],
    workflowSteps: [
      'Data Requirements',
      'ML Architecture',
      'Model Training Pipeline',
      'Serving Infrastructure',
      'Monitoring & Observability'
    ],
    diagramTypes: ['C4 Context', 'C4 Container', 'Sequence Diagrams', 'NFR Mapping'],
    knowledgeBaseIntegration: true
  }
];

export default function CreateProjectPage() {
  const router = useRouter();
  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: '',
    description: '',
    domain: 'cloud-native',
    mode: 'greenfield'
  });
  const [isCreating, setIsCreating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<EnhancedWorkflowTemplate | null>(null);
  const [activeTab, setActiveTab] = useState('template');

  const handleCreateProject = async () => {
    if (!newProject.name.trim()) {
      toast.error('Please enter a project name');
      return;
    }

    if (newProject.name.trim().length < 3) {
      toast.error('Project name must be at least 3 characters long');
      return;
    }

    try {
      setIsCreating(true);
      
      // Create project with template-specific configuration
      const projectData = {
        ...newProject,
        template_id: selectedTemplate?.id,
        template_config: selectedTemplate ? {
          workflowSteps: selectedTemplate.workflowSteps,
          diagramTypes: selectedTemplate.diagramTypes,
          knowledgeBaseIntegration: selectedTemplate.knowledgeBaseIntegration,
          complexity: selectedTemplate.complexity,
          estimatedTime: selectedTemplate.estimatedTime
        } : null
      };

      const response = await apiClient.createProject(projectData);
      toast.success('Project created successfully!');
      router.push(`/projects/${response.id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleTemplateSelect = (template: EnhancedWorkflowTemplate) => {
    setSelectedTemplate(template);
    
    // Auto-fill project details based on template
    setNewProject(prev => ({
      ...prev,
      name: template.name,
      description: template.description,
      domain: template.category === 'data-platform' ? 'data-platform' : 
              template.category === 'enterprise' ? 'enterprise' : 'cloud-native'
    }));
  };

  const getProjectTypeIcon = (mode: string) => {
    switch (mode) {
      case 'greenfield':
        return <BuildingIcon className="w-6 h-6 text-green-600" />;
      case 'brownfield':
        return <BriefcaseIcon className="w-6 h-6 text-orange-600" />;
      default:
        return <BuildingIcon className="w-6 h-6 text-gray-600" />;
    }
  };

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'cloud-native':
        return <CloudIcon className="w-5 h-5" />;
      case 'data-platform':
        return <DatabaseIcon className="w-5 h-5" />;
      case 'enterprise':
        return <BuildingIcon className="w-5 h-5" />;
      default:
        return <BuildingIcon className="w-5 h-5" />;
    }
  };

  const getDomainBadge = (domain: string) => {
    const colors = {
      'cloud-native': 'bg-blue-100 text-blue-800',
      'data-platform': 'bg-purple-100 text-purple-800',
      'enterprise': 'bg-orange-100 text-orange-800'
    };
    return colors[domain as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getComplexityBadge = (complexity: string) => {
    const colors = {
      'simple': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'complex': 'bg-red-100 text-red-800'
    };
    return colors[complexity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => router.push('/projects')}>
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Projects
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Create New Project</h1>
              <p className="text-slate-600">Choose a template and configure your project</p>
            </div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="template">Choose Template</TabsTrigger>
            <TabsTrigger value="configure">Configure Project</TabsTrigger>
            <TabsTrigger value="review">Review & Create</TabsTrigger>
          </TabsList>

          {/* Template Selection */}
          <TabsContent value="template" className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Choose Your Project Template</h2>
              <p className="text-slate-600 max-w-2xl mx-auto">
                Select a template that best matches your project type. Each template includes 
                pre-configured workflows, diagram types, and knowledge base integration.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {enhancedTemplates.map((template) => (
                <Card 
                  key={template.id} 
                  className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                    selectedTemplate?.id === template.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                  }`}
                  onClick={() => handleTemplateSelect(template)}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-lg ${template.color} text-white`}>
                        {template.icon}
                      </div>
                      <div className="flex space-x-2">
                        <Badge className={getComplexityBadge(template.complexity)}>
                          {template.complexity}
                        </Badge>
                        <Badge variant="outline">
                          {template.estimatedTime}
                        </Badge>
                      </div>
                    </div>
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <CardDescription>{template.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-sm mb-2">Key Features</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {template.features.slice(0, 3).map((feature, index) => (
                            <li key={index} className="flex items-center">
                              <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2" />
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
                      
                      <div>
                        <h4 className="font-medium text-sm mb-2">Technologies</h4>
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

                      <div>
                        <h4 className="font-medium text-sm mb-2">Benefits</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {template.benefits.slice(0, 2).map((benefit, index) => (
                            <li key={index} className="flex items-center">
                              <SparklesIcon className="h-3 w-3 text-blue-500 mr-2" />
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {template.knowledgeBaseIntegration && (
                        <div className="flex items-center text-sm text-blue-600">
                          <BrainIcon className="h-4 w-4 mr-2" />
                          AI-powered knowledge base integration
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {selectedTemplate && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-blue-900">Selected Template: {selectedTemplate.name}</CardTitle>
                  <CardDescription className="text-blue-700">
                    This template will guide you through {selectedTemplate.workflowSteps.length} workflow steps 
                    and generate {selectedTemplate.diagramTypes.length} types of diagrams.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-sm mb-2">Workflow Steps</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        {selectedTemplate.workflowSteps.map((step, index) => (
                          <li key={index} className="flex items-center">
                            <span className="w-6 h-6 bg-blue-200 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                              {index + 1}
                            </span>
                            {step}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium text-sm mb-2">Generated Diagrams</h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedTemplate.diagramTypes.map((type, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {type}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Project Configuration */}
          <TabsContent value="configure" className="space-y-6">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Configure Your Project</h2>
              
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Basic Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="project-name">Project Name</Label>
                      <Input
                        id="project-name"
                        value={newProject.name}
                        onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter project name"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="project-description">Description</Label>
                      <Textarea
                        id="project-description"
                        value={newProject.description}
                        onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Describe your project"
                        className="mt-1"
                        rows={3}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Project Type</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>Project Mode</Label>
                      <RadioGroup 
                        value={newProject.mode} 
                        onValueChange={(value) => setNewProject(prev => ({ ...prev, mode: value as 'greenfield' | 'brownfield' }))}
                        className="mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="greenfield" id="greenfield" />
                          <Label htmlFor="greenfield" className="flex items-center space-x-2">
                            {getProjectTypeIcon('greenfield')}
                            <div>
                              <div className="font-medium">Greenfield</div>
                              <div className="text-sm text-gray-600">New project from scratch</div>
                            </div>
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="brownfield" id="brownfield" />
                          <Label htmlFor="brownfield" className="flex items-center space-x-2">
                            {getProjectTypeIcon('brownfield')}
                            <div>
                              <div className="font-medium">Brownfield</div>
                              <div className="text-sm text-gray-600">Existing system analysis</div>
                            </div>
                          </Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div>
                      <Label>Domain</Label>
                      <RadioGroup 
                        value={newProject.domain} 
                        onValueChange={(value) => setNewProject(prev => ({ ...prev, domain: value as any }))}
                        className="mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="cloud-native" id="cloud-native" />
                          <Label htmlFor="cloud-native" className="flex items-center space-x-2">
                            {getDomainIcon('cloud-native')}
                            <div>
                              <div className="font-medium">Cloud Native</div>
                              <div className="text-sm text-gray-600">Modern cloud-based applications</div>
                            </div>
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="data-platform" id="data-platform" />
                          <Label htmlFor="data-platform" className="flex items-center space-x-2">
                            {getDomainIcon('data-platform')}
                            <div>
                              <div className="font-medium">Data Platform</div>
                              <div className="text-sm text-gray-600">Data processing and analytics</div>
                            </div>
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="enterprise" id="enterprise" />
                          <Label htmlFor="enterprise" className="flex items-center space-x-2">
                            {getDomainIcon('enterprise')}
                            <div>
                              <div className="font-medium">Enterprise</div>
                              <div className="text-sm text-gray-600">Large-scale enterprise systems</div>
                            </div>
                          </Label>
                        </div>
                      </RadioGroup>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Review & Create */}
          <TabsContent value="review" className="space-y-6">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Review & Create</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Project Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Project Name</Label>
                      <p className="text-lg font-semibold">{newProject.name || 'Not specified'}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Domain</Label>
                      <div className="flex items-center space-x-2">
                        {getDomainIcon(newProject.domain)}
                        <Badge className={getDomainBadge(newProject.domain)}>
                          {newProject.domain}
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Mode</Label>
                      <div className="flex items-center space-x-2">
                        {getProjectTypeIcon(newProject.mode)}
                        <span className="capitalize">{newProject.mode}</span>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Template</Label>
                      <p className="text-sm">{selectedTemplate?.name || 'No template selected'}</p>
                    </div>
                  </div>
                  
                  {newProject.description && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Description</Label>
                      <p className="text-sm text-gray-800">{newProject.description}</p>
                    </div>
                  )}

                  {selectedTemplate && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Template Benefits</Label>
                      <ul className="text-sm text-gray-800 space-y-1">
                        {selectedTemplate.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-center">
                            <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2" />
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="flex justify-end space-x-4">
                <Button variant="outline" onClick={() => setActiveTab('configure')}>
                  Back to Configure
                </Button>
                <Button 
                  onClick={handleCreateProject} 
                  disabled={isCreating || !newProject.name.trim()}
                  className="min-w-[120px]"
                >
                  {isCreating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </>
                  ) : (
                    <>
                      <CheckCircleIcon className="h-4 w-4 mr-2" />
                      Create Project
                    </>
                  )}
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}