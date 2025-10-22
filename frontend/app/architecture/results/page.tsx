'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { 
  ArrowLeftIcon,
  DownloadIcon,
  ShareIcon,
  BuildingIcon,
  SearchIcon,
  LinkIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  LightbulbIcon,
  FileTextIcon,
  BarChart3Icon,
  ClockIcon,
  SparklesIcon,
  EyeIcon,
  CopyIcon
} from 'lucide-react';
import ExportDialog from '@/components/ExportDialog';
import DiagramViewer from '@/components/DiagramViewer';
import RecommendationSelector from '@/components/RecommendationSelector';

interface ArchitectureResult {
  id: string;
  type: 'new' | 'evaluate' | 'integrate';
  title: string;
  summary: string;
  architecture: {
    overview: string;
    components: Array<{
      name: string;
      description: string;
      technology: string;
      purpose: string;
    }>;
    patterns: Array<{
      name: string;
      description: string;
      benefits: string[];
    }>;
    diagrams: Array<{
      type: string;
      title: string;
      description: string;
      code: string;
    }>;
  };
  recommendations: Array<{
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    impact: string;
  }>;
  implementation?: {
    phases: Array<{
      name: string;
      duration: string;
      tasks: string[];
    }>;
    timeline: string;
    risks: Array<{
      risk: string;
      mitigation: string;
      probability: 'high' | 'medium' | 'low';
    }>;
  };
  metrics: {
    complexity: string;
    estimatedCost: string;
    developmentTime: string;
    maintenanceEffort: string;
  };
  // Enhanced LLM analysis data
  architecture_details?: {
    name: string;
    style: string;
    description: string;
    rationale: string;
    quality_attributes: string[];
  };
  components_detailed?: Array<{
    id: string;
    name: string;
    type: string;
    description: string;
    responsibilities: string[];
    technologies: string[];
    interfaces: Array<{
      name: string;
      type: string;
      description: string;
      endpoints: string[];
    }>;
    dependencies: string[];
    scalability: string;
    security_considerations: string[];
    performance_characteristics: {
      expected_load: string;
      response_time: string;
      resource_requirements: string;
    };
    data_model: {
      entities: string[];
      relationships: string[];
      storage_requirements: string;
    };
  }>;
  diagrams_enhanced?: {
    c4_context: {
      title: string;
      description: string;
      code: string;
    };
    c4_container: {
      title: string;
      description: string;
      code: string;
    };
    sequence_diagrams: Array<{
      title: string;
      description: string;
      code: string;
    }>;
  };
  implementation_plan?: {
    phases: Array<{
      id: string;
      name: string;
      description: string;
      duration: string;
      deliverables: string[];
      dependencies: string[];
      risks: string[];
      success_criteria: string[];
    }>;
    tasks: Array<{
      id: string;
      title: string;
      description: string;
      phase_id: string;
      effort: string;
      assignee: string;
      dependencies: string[];
      acceptance_criteria: string[];
    }>;
    timeline: {
      total_duration: string;
      critical_path: string[];
      milestones: Array<{
        name: string;
        date: string;
        deliverables: string[];
      }>;
    };
  };
  quality_analysis?: {
    scalability: {
      current_capacity: string;
      scaling_strategy: string;
      bottlenecks: string[];
      mitigation: string[];
    };
    security: {
      threats: string[];
      mitigations: string[];
      compliance: string[];
      authentication: string;
      authorization: string;
    };
    performance: {
      targets: {
        response_time: string;
        throughput: string;
        availability: string;
      };
      optimization_strategies: string[];
    };
  };
  tradeoffs?: Array<{
    aspect: string;
    pros: string[];
    cons: string[];
    recommendation: string;
  }>;
  risks?: Array<{
    id: string;
    title: string;
    description: string;
    probability: string;
    impact: string;
    mitigation: string;
  }>;
}

export default function ArchitectureResultsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [result, setResult] = useState<ArchitectureResult | null>(null);
  const [loading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([]);
  const [updatedDiagrams, setUpdatedDiagrams] = useState<any[]>([]);
  const [updatedMetrics, setUpdatedMetrics] = useState<any>(null);
  const [appliedRecommendations, setAppliedRecommendations] = useState<string[]>([]);

  useEffect(() => {
    // Load architecture results from simple modular system
    const loadResults = async () => {
      setIsLoading(true);
      
      try {
        // Check if we have results from the simple modular system
        const storedResults = localStorage.getItem('architectureResults');
        const type = searchParams.get('type') || 'new';
        
        if (storedResults) {
          // Use data from simple modular system
          const simpleData = JSON.parse(storedResults);
          
          const result: ArchitectureResult = {
            id: 'simple-arch-' + Date.now(),
            type: type as any,
            title: type === 'new' ? 'New Architecture Design' : 
                   type === 'evaluate' ? 'Architecture Evaluation' : 
                   'Integration Plan',
            summary: simpleData.architecture.description,
            architecture: {
              overview: simpleData.architecture.description,
              components: simpleData.architecture.components.map((comp: any) => ({
                name: comp.name,
                description: comp.responsibilities.join(', '),
                technology: comp.technologies.join(', '),
                purpose: comp.responsibilities[0] || 'System component'
              })),
              patterns: [
                {
                  name: simpleData.architecture.style,
                  description: `Architecture style: ${simpleData.architecture.style}`,
                  benefits: ['Scalability', 'Maintainability', 'Performance']
                }
              ],
              diagrams: simpleData.diagrams.map((diagram: any) => ({
                type: diagram.type,
                title: diagram.title,
                description: diagram.description,
                code: diagram.code
              }))
            },
            requirements: {
              business_goals: simpleData.requirements.business_goals,
              functional_requirements: simpleData.requirements.functional_requirements,
              non_functional_requirements: simpleData.requirements.non_functional_requirements,
              constraints: simpleData.requirements.constraints,
              stakeholders: simpleData.requirements.stakeholders,
              validation_score: simpleData.requirements.validation_score,
              validation_status: simpleData.requirements.validation_status
            },
            recommendations: simpleData.recommendations.map((rec: any) => ({
              id: rec.id,
              priority: rec.priority,
              title: rec.title,
              description: rec.description,
              impact: rec.impact,
              architectureChanges: [rec.description]
            })),
            // Pass through implementation data only if provided by backend
            implementation: simpleData.implementation ? {
              phases: Array.isArray(simpleData.implementation.phases) ? simpleData.implementation.phases : [],
              timeline: simpleData.implementation.timeline || '',
              risks: Array.isArray(simpleData.implementation.risks) ? simpleData.implementation.risks : []
            } : undefined,
            metrics: {
              complexity: simpleData.architecture.quality_score > 0.8 ? 'High' : simpleData.architecture.quality_score > 0.6 ? 'Medium' : 'Low',
              estimatedCost: '$50,000 - $75,000',
              developmentTime: '7-10 weeks',
              maintenanceEffort: '2-3 developers'
            },
            // Enhanced LLM analysis data
            architecture_details: simpleData.architecture_details,
            components_detailed: simpleData.components_detailed,
            diagrams_enhanced: simpleData.diagrams_enhanced,
            implementation_plan: simpleData.implementation_plan,
            quality_analysis: simpleData.quality_analysis,
            tradeoffs: simpleData.tradeoffs,
            risks: simpleData.risks
          };
          
          setResult(result);
        } else {
          // Fallback to mock data if no stored results
          const mockResult: ArchitectureResult = {
        id: 'result-123',
        type: type as any,
        title: type === 'new' ? 'New Architecture Design' : 
               type === 'evaluate' ? 'Architecture Evaluation' : 
               'Integration Plan',
        summary: type === 'new' ? 
          'A modern microservices architecture designed for scalability and maintainability' :
          type === 'evaluate' ?
          'Comprehensive evaluation of your existing architecture with improvement recommendations' :
          'Detailed integration strategy for adding new capabilities to your existing system',
        architecture: {
          overview: 'This architecture follows modern cloud-native principles with microservices, API-first design, and event-driven communication patterns.',
          components: [
            {
              name: 'API Gateway',
              description: 'Central entry point for all client requests',
              technology: 'Kong/NGINX',
              purpose: 'Routing, authentication, rate limiting'
            },
            {
              name: 'User Service',
              description: 'Handles user management and authentication',
              technology: 'Node.js/Express',
              purpose: 'User CRUD operations, JWT tokens'
            },
            {
              name: 'Product Service',
              description: 'Manages product catalog and inventory',
              technology: 'Python/FastAPI',
              purpose: 'Product management, search, recommendations'
            },
            {
              name: 'Database',
              description: 'Primary data storage',
              technology: 'PostgreSQL',
              purpose: 'Reliable data persistence'
            }
          ],
          patterns: [
            {
              name: 'Microservices',
              description: 'Decompose application into small, independent services',
              benefits: ['Scalability', 'Technology diversity', 'Team autonomy']
            },
            {
              name: 'API Gateway',
              description: 'Single entry point for client requests',
              benefits: ['Security', 'Rate limiting', 'Request routing']
            },
            {
              name: 'Event-Driven',
              description: 'Services communicate through events',
              benefits: ['Loose coupling', 'Scalability', 'Resilience']
            }
          ],
          diagrams: [
            {
              type: 'C4 Context',
              title: 'System Context',
              description: 'High-level view of the system and its users',
              code: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n\nPerson(user, "User", "End user of the system")\nSystem(system, "E-commerce Platform", "Online shopping platform")\n\nRel(user, system, "Uses")\n@enduml'
            },
            {
              type: 'C4 Container',
              title: 'Container Diagram',
              description: 'Architecture of the system showing containers',
              code: '@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\nPerson(user, "User", "End user")\nSystem_Boundary(system, "E-commerce Platform") {\n  Container(api, "API Gateway", "Kong", "Routes requests")\n  Container(userService, "User Service", "Node.js", "User management")\n  Container(productService, "Product Service", "Python", "Product catalog")\n  ContainerDb(database, "Database", "PostgreSQL", "Data storage")\n}\n\nRel(user, api, "Uses")\nRel(api, userService, "Routes to")\nRel(api, productService, "Routes to")\nRel(userService, database, "Stores data in")\nRel(productService, database, "Stores data in")\n@enduml'
            }
          ]
        },
        recommendations: [
          {
            id: 'api-gateway',
            priority: 'high',
            title: 'Implement API Gateway',
            description: 'Add an API gateway for centralized request handling',
            impact: 'Improved security and scalability',
            architectureChanges: [
              'Enhanced API Gateway with rate limiting and authentication',
              'Updated container diagram to show security features'
            ]
          },
          {
            id: 'monitoring',
            priority: 'medium',
            title: 'Add Monitoring',
            description: 'Implement comprehensive monitoring and logging',
            impact: 'Better observability and debugging',
            architectureChanges: [
              'Added Prometheus monitoring service',
              'Added ELK Stack for centralized logging',
              'Updated container diagram with monitoring components'
            ]
          },
          {
            id: 'caching',
            priority: 'low',
            title: 'Consider Caching',
            description: 'Add Redis for caching frequently accessed data',
            impact: 'Improved performance',
            architectureChanges: [
              'Added Redis cache layer',
              'Updated container diagram with caching components'
            ]
          }
        ],
        implementation: {
          phases: [
            {
              name: 'Phase 1: Foundation',
              duration: '2-3 weeks',
              tasks: ['Set up infrastructure', 'Implement API Gateway', 'Create basic services']
            },
            {
              name: 'Phase 2: Core Features',
              duration: '3-4 weeks',
              tasks: ['Implement user service', 'Build product service', 'Add database']
            },
            {
              name: 'Phase 3: Integration',
              duration: '2-3 weeks',
              tasks: ['Connect services', 'Add monitoring', 'Testing and deployment']
            }
          ],
          timeline: '7-10 weeks total',
          risks: [
            {
              risk: 'Integration complexity',
              mitigation: 'Use API contracts and thorough testing',
              probability: 'medium'
            },
            {
              risk: 'Performance issues',
              mitigation: 'Load testing and optimization',
              probability: 'low'
            }
          ]
        },
        metrics: {
          complexity: 'Medium',
          estimatedCost: '$50,000 - $75,000',
          developmentTime: '7-10 weeks',
          maintenanceEffort: '2-3 developers'
        }
      };
      
          setResult(mockResult);
        }
      } catch (error) {
        console.error('Error loading architecture results:', error);
        toast.error('Failed to load architecture results');
      } finally {
        setIsLoading(false);
      }
    };

    loadResults();
  }, [searchParams]);


  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Link copied to clipboard');
  };

  const handleRecommendationsChange = (selectedIds: string[], newDiagrams: any[], newMetrics: any) => {
    setSelectedRecommendations(selectedIds);
    setUpdatedDiagrams(newDiagrams);
    setUpdatedMetrics(newMetrics);
    setAppliedRecommendations(prev => [...prev, ...selectedIds]);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (probability: string) => {
    switch (probability) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Generating your architecture guidance...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-600">No results found</p>
          <Button onClick={() => router.push('/')} className="mt-4">
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={handleShare}>
              <ShareIcon className="h-4 w-4 mr-2" />
              Share
            </Button>
            <ExportDialog 
              data={result}
              trigger={
                <Button>
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  Export
                </Button>
              }
            />
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">{result.title}</h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">{result.summary}</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            <TabsTrigger value="implementation">Implementation</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="components">Components</TabsTrigger>
            <TabsTrigger value="diagrams">Diagrams</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BuildingIcon className="h-5 w-5 mr-2 text-blue-600" />
                    Architecture Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">{result.architecture.overview}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3Icon className="h-5 w-5 mr-2 text-green-600" />
                    Key Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-600">Complexity:</span>
                      <Badge variant="outline" className={updatedMetrics ? 'bg-blue-100 text-blue-800' : ''}>
                        {updatedMetrics ? updatedMetrics.complexity : result.metrics.complexity}
                        {updatedMetrics && <span className="ml-1">📈</span>}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Estimated Cost:</span>
                      <span className={`font-medium ${updatedMetrics ? 'text-blue-600' : ''}`}>
                        {updatedMetrics ? updatedMetrics.estimatedCost : result.metrics.estimatedCost}
                        {updatedMetrics && <span className="ml-1">📈</span>}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Development Time:</span>
                      <span className={`font-medium ${updatedMetrics ? 'text-blue-600' : ''}`}>
                        {updatedMetrics ? updatedMetrics.developmentTime : result.metrics.developmentTime}
                        {updatedMetrics && <span className="ml-1">📈</span>}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Maintenance Effort:</span>
                      <span className={`font-medium ${updatedMetrics ? 'text-blue-600' : ''}`}>
                        {updatedMetrics ? updatedMetrics.maintenanceEffort : result.metrics.maintenanceEffort}
                        {updatedMetrics && <span className="ml-1">📈</span>}
                      </span>
                    </div>
                    {updatedMetrics && (
                      <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
                        📊 Metrics updated based on applied recommendations
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Architecture Tab */}
          <TabsContent value="architecture" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Components</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.architecture.components.map((component, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{component.name}</h4>
                          <Badge variant="outline">{component.technology}</Badge>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{component.description}</p>
                        <p className="text-xs text-slate-500">{component.purpose}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Architecture Patterns</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.architecture.patterns.map((pattern, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <h4 className="font-medium mb-2">{pattern.name}</h4>
                        <p className="text-sm text-slate-600 mb-3">{pattern.description}</p>
                        <div className="flex flex-wrap gap-1">
                          {pattern.benefits.map((benefit, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {benefit}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Architecture Diagrams</CardTitle>
                <CardDescription>
                  Interactive diagrams showing your system architecture. 
                  {selectedRecommendations.length > 0 && (
                    <span className="text-blue-600 font-medium">
                      {' '}Updated with {selectedRecommendations.length} selected recommendation{selectedRecommendations.length > 1 ? 's' : ''}.
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {(updatedDiagrams.length > 0 ? updatedDiagrams : result.architecture.diagrams).map((diagram, index) => (
                    <DiagramViewer
                      key={index}
                      title={diagram.title}
                      description={diagram.description}
                      code={diagram.code}
                      type={diagram.type}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            {appliedRecommendations.length > 0 && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center text-green-700 mb-2">
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  <span className="font-medium">Applied Recommendations</span>
                </div>
                <p className="text-sm text-green-600">
                  {appliedRecommendations.length} recommendation(s) have been applied to your architecture. 
                  The diagrams and metrics have been updated accordingly.
                </p>
              </div>
            )}
            <RecommendationSelector
              recommendations={result.recommendations.filter(rec => !appliedRecommendations.includes(rec.id))}
              onRecommendationsChange={handleRecommendationsChange}
            />
          </TabsContent>

          {/* Implementation Tab (render only if implementation data exists) */}
          <TabsContent value="implementation" className="space-y-6">
            {result.implementation ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ClockIcon className="h-5 w-5 mr-2 text-blue-600" />
                    Implementation Phases
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(result.implementation?.phases || []).map((phase, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{phase.name}</h4>
                          <Badge variant="outline">{phase.duration}</Badge>
                        </div>
                        <ul className="text-sm text-slate-600 space-y-1">
                          {phase.tasks.map((task, i) => (
                            <li key={i} className="flex items-center">
                              <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2" />
                              {task}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <AlertTriangleIcon className="h-5 w-5 mr-2 text-red-600" />
                    Risk Assessment
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(result.implementation?.risks || []).map((risk, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{risk.risk}</h4>
                          <Badge className={getRiskColor(risk.probability)}>
                            {risk.probability.toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-600">{risk.mitigation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ClockIcon className="h-5 w-5 mr-2 text-blue-600" />
                    Implementation Plan
                  </CardTitle>
                  <CardDescription>
                    No implementation details provided by the analysis. You can generate a plan later.
                  </CardDescription>
                </CardHeader>
              </Card>
            )}
          </TabsContent>

          {/* Metrics Tab */}
          <TabsContent value="metrics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Complexity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-600">{result.metrics.complexity}</div>
                  <p className="text-sm text-slate-600">Architecture complexity level</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Estimated Cost</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{result.metrics.estimatedCost}</div>
                  <p className="text-sm text-slate-600">Total development cost</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Development Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-600">{result.metrics.developmentTime}</div>
                  <p className="text-sm text-slate-600">Time to completion</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Maintenance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">{result.metrics.maintenanceEffort}</div>
                  <p className="text-sm text-slate-600">Ongoing maintenance</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Components Tab */}
          <TabsContent value="components" className="space-y-6">
            {result.components_detailed && result.components_detailed.length > 0 ? (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-slate-900">Detailed Components</h2>
                {result.components_detailed.map((component, index) => (
                  <Card key={component.id || index}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BuildingIcon className="h-5 w-5" />
                        {component.name}
                      </CardTitle>
                      <CardDescription>{component.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-semibold text-slate-700 mb-2">Responsibilities</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {component.responsibilities.map((resp, i) => (
                              <li key={i} className="text-sm text-slate-600">{resp}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-700 mb-2">Technologies</h4>
                          <div className="flex flex-wrap gap-2">
                            {component.technologies.map((tech, i) => (
                              <Badge key={i} variant="secondary">{tech}</Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      {component.interfaces && component.interfaces.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-slate-700 mb-2">Interfaces</h4>
                          {component.interfaces.map((iface, i) => (
                            <div key={i} className="bg-slate-50 p-3 rounded-lg mb-2">
                              <div className="font-medium">{iface.name}</div>
                              <div className="text-sm text-slate-600">{iface.description}</div>
                              <div className="text-xs text-slate-500 mt-1">Type: {iface.type}</div>
                            </div>
                          ))}
                        </div>
                      )}

                      {component.performance_characteristics && (
                        <div>
                          <h4 className="font-semibold text-slate-700 mb-2">Performance Characteristics</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <div className="text-sm font-medium text-blue-900">Expected Load</div>
                              <div className="text-blue-700">{component.performance_characteristics.expected_load}</div>
                            </div>
                            <div className="bg-green-50 p-3 rounded-lg">
                              <div className="text-sm font-medium text-green-900">Response Time</div>
                              <div className="text-green-700">{component.performance_characteristics.response_time}</div>
                            </div>
                            <div className="bg-purple-50 p-3 rounded-lg">
                              <div className="text-sm font-medium text-purple-900">Resources</div>
                              <div className="text-purple-700">{component.performance_characteristics.resource_requirements}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {component.security_considerations && component.security_considerations.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-slate-700 mb-2">Security Considerations</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {component.security_considerations.map((consideration, i) => (
                              <li key={i} className="text-sm text-slate-600">{consideration}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BuildingIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">No detailed component information available</p>
              </div>
            )}
          </TabsContent>

          {/* Diagrams Tab */}
          <TabsContent value="diagrams" className="space-y-6">
            {result.diagrams_enhanced ? (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-slate-900">Enhanced Diagrams</h2>
                
                {result.diagrams_enhanced.c4_context && (
                  <Card>
                    <CardHeader>
                      <CardTitle>{result.diagrams_enhanced.c4_context.title}</CardTitle>
                      <CardDescription>{result.diagrams_enhanced.c4_context.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DiagramViewer 
                        code={result.diagrams_enhanced.c4_context.code}
                        type="plantuml"
                        title={result.diagrams_enhanced.c4_context.title}
                      />
                    </CardContent>
                  </Card>
                )}

                {result.diagrams_enhanced.c4_container && (
                  <Card>
                    <CardHeader>
                      <CardTitle>{result.diagrams_enhanced.c4_container.title}</CardTitle>
                      <CardDescription>{result.diagrams_enhanced.c4_container.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DiagramViewer 
                        code={result.diagrams_enhanced.c4_container.code}
                        type="plantuml"
                        title={result.diagrams_enhanced.c4_container.title}
                      />
                    </CardContent>
                  </Card>
                )}

                {result.diagrams_enhanced.sequence_diagrams && result.diagrams_enhanced.sequence_diagrams.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold text-slate-900">Sequence Diagrams</h3>
                    {result.diagrams_enhanced.sequence_diagrams.map((diagram, index) => (
                      <Card key={index}>
                        <CardHeader>
                          <CardTitle>{diagram.title}</CardTitle>
                          <CardDescription>{diagram.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <DiagramViewer 
                            code={diagram.code}
                            type="plantuml"
                            title={diagram.title}
                          />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileTextIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">No enhanced diagrams available</p>
              </div>
            )}
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-slate-900">Technical Analysis</h2>
              
              {/* Quality Analysis */}
              {result.quality_analysis && (
                <Card>
                  <CardHeader>
                    <CardTitle>Quality Analysis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {result.quality_analysis.scalability && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Scalability</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <div className="text-sm font-medium text-blue-900 mb-1">Current Capacity</div>
                            <div className="text-blue-700">{result.quality_analysis.scalability.current_capacity}</div>
                          </div>
                          <div className="bg-green-50 p-4 rounded-lg">
                            <div className="text-sm font-medium text-green-900 mb-1">Scaling Strategy</div>
                            <div className="text-green-700">{result.quality_analysis.scalability.scaling_strategy}</div>
                          </div>
                        </div>
                        {result.quality_analysis.scalability.bottlenecks && result.quality_analysis.scalability.bottlenecks.length > 0 && (
                          <div className="mt-4">
                            <div className="text-sm font-medium text-slate-700 mb-2">Potential Bottlenecks</div>
                            <ul className="list-disc list-inside space-y-1">
                              {result.quality_analysis.scalability.bottlenecks.map((bottleneck, i) => (
                                <li key={i} className="text-sm text-slate-600">{bottleneck}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {result.quality_analysis.security && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Security</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <div className="text-sm font-medium text-slate-700 mb-2">Authentication</div>
                            <div className="text-slate-600">{result.quality_analysis.security.authentication}</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-slate-700 mb-2">Authorization</div>
                            <div className="text-slate-600">{result.quality_analysis.security.authorization}</div>
                          </div>
                        </div>
                        {result.quality_analysis.security.threats && result.quality_analysis.security.threats.length > 0 && (
                          <div className="mt-4">
                            <div className="text-sm font-medium text-slate-700 mb-2">Identified Threats</div>
                            <ul className="list-disc list-inside space-y-1">
                              {result.quality_analysis.security.threats.map((threat, i) => (
                                <li key={i} className="text-sm text-slate-600">{threat}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {result.quality_analysis.performance && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Performance</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <div className="text-sm font-medium text-blue-900 mb-1">Response Time</div>
                            <div className="text-blue-700">{result.quality_analysis.performance.targets.response_time}</div>
                          </div>
                          <div className="bg-green-50 p-4 rounded-lg">
                            <div className="text-sm font-medium text-green-900 mb-1">Throughput</div>
                            <div className="text-green-700">{result.quality_analysis.performance.targets.throughput}</div>
                          </div>
                          <div className="bg-purple-50 p-4 rounded-lg">
                            <div className="text-sm font-medium text-purple-900 mb-1">Availability</div>
                            <div className="text-purple-700">{result.quality_analysis.performance.targets.availability}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Tradeoffs */}
              {result.tradeoffs && result.tradeoffs.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Architectural Tradeoffs</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {result.tradeoffs.map((tradeoff, index) => (
                        <div key={index} className="border-l-4 border-blue-500 pl-4">
                          <h4 className="font-semibold text-slate-700 mb-2">{tradeoff.aspect}</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                            <div>
                              <div className="text-sm font-medium text-green-700 mb-1">Pros</div>
                              <ul className="list-disc list-inside space-y-1">
                                {tradeoff.pros.map((pro, i) => (
                                  <li key={i} className="text-sm text-slate-600">{pro}</li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <div className="text-sm font-medium text-red-700 mb-1">Cons</div>
                              <ul className="list-disc list-inside space-y-1">
                                {tradeoff.cons.map((con, i) => (
                                  <li key={i} className="text-sm text-slate-600">{con}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                          <div className="bg-slate-50 p-3 rounded-lg">
                            <div className="text-sm font-medium text-slate-700 mb-1">Recommendation</div>
                            <div className="text-slate-600">{tradeoff.recommendation}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Risks */}
              {result.risks && result.risks.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Risk Assessment</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {result.risks.map((risk, index) => (
                        <div key={risk.id || index} className="border rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-slate-700">{risk.title}</h4>
                            <div className="flex gap-2">
                              <Badge variant={risk.probability === 'high' ? 'destructive' : risk.probability === 'medium' ? 'secondary' : 'outline'}>
                                {risk.probability} probability
                              </Badge>
                              <Badge variant={risk.impact === 'high' ? 'destructive' : risk.impact === 'medium' ? 'secondary' : 'outline'}>
                                {risk.impact} impact
                              </Badge>
                            </div>
                          </div>
                          <p className="text-slate-600 mb-3">{risk.description}</p>
                          <div className="bg-slate-50 p-3 rounded-lg">
                            <div className="text-sm font-medium text-slate-700 mb-1">Mitigation Strategy</div>
                            <div className="text-slate-600">{risk.mitigation}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
