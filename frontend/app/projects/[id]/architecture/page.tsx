'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeftIcon, 
  BrainIcon, 
  BuildingIcon, 
  CodeIcon,
  FileTextIcon,
  RefreshCwIcon,
  DownloadIcon,
  EyeIcon,
  EditIcon,
  PlusIcon,
  SaveIcon,
  TrashIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  ClockIcon,
  SparklesIcon
} from 'lucide-react';
import ArchitectureDiagrams from '@/components/ArchitectureDiagrams';
import { apiClient } from '@/lib/api-client';

interface ArchitectureProposal {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'generating' | 'completed' | 'failed';
  content: {
    overview: string;
    components: Array<{
      name: string;
      description: string;
      technology: string;
      dependencies: string[];
    }>;
    patterns: Array<{
      name: string;
      description: string;
      benefits: string[];
    }>;
    tradeoffs: Array<{
      aspect: string;
      pros: string[];
      cons: string[];
    }>;
  };
  generated_at: string;
  updated_at: string;
}

interface Diagram {
  id: string;
  name: string;
  type: 'c4_context' | 'c4_container' | 'c4_component' | 'sequence' | 'nfr_mapping';
  format: 'plantuml' | 'mermaid';
  content: string;
  is_editable: boolean;
  created_at: string;
  updated_at: string;
}

export default function ProjectArchitecturePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [loading, setLoading] = useState(false);
  const [proposal, setProposal] = useState<ArchitectureProposal | null>(null);
  const [diagrams, setDiagrams] = useState<Diagram[]>([]);
  const [activeTab, setActiveTab] = useState('proposal');
  const [isGenerating, setIsGenerating] = useState(false);
  const [editingDiagram, setEditingDiagram] = useState<string | null>(null);

  useEffect(() => {
    loadArchitectureData();
  }, [projectId]);

  const loadArchitectureData = async () => {
    setLoading(true);
    try {
      // Load architecture proposal
      const proposalResponse = await apiClient.getArchitectureProposal(projectId);
      setProposal(proposalResponse.data);

      // Load diagrams
      const diagramsResponse = await apiClient.getProjectDiagrams(projectId);
      setDiagrams(diagramsResponse.data);
    } catch (error) {
      console.error('Failed to load architecture data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateArchitectureProposal = async () => {
    setIsGenerating(true);
    try {
      const response = await apiClient.generateArchitectureProposal(projectId);
      setProposal(response.data);
      
      // Auto-generate diagrams based on the proposal
      await generateDiagramsFromProposal(response.data);
    } catch (error) {
      console.error('Failed to generate architecture proposal:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateDiagramsFromProposal = async (proposal: ArchitectureProposal) => {
    try {
      // Generate C4 Context diagram
      const contextResponse = await apiClient.generateDiagram({
        project_id: projectId,
        diagram_type: 'c4_context',
        output_format: 'plantuml',
        context: {
          architecture_proposal: proposal,
          auto_generated: true
        }
      });

      // Generate C4 Container diagram
      const containerResponse = await apiClient.generateDiagram({
        project_id: projectId,
        diagram_type: 'c4_container',
        output_format: 'plantuml',
        context: {
          architecture_proposal: proposal,
          auto_generated: true
        }
      });

      // Generate Sequence diagram
      const sequenceResponse = await apiClient.generateDiagram({
        project_id: projectId,
        diagram_type: 'sequence',
        output_format: 'plantuml',
        context: {
          architecture_proposal: proposal,
          auto_generated: true
        }
      });

      // Add generated diagrams to the list
      const newDiagrams = [
        {
          id: contextResponse.data.diagram_id,
          name: 'System Context',
          type: 'c4_context' as const,
          format: 'plantuml' as const,
          content: contextResponse.data.diagram_code,
          is_editable: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: containerResponse.data.diagram_id,
          name: 'Container View',
          type: 'c4_container' as const,
          format: 'plantuml' as const,
          content: containerResponse.data.diagram_code,
          is_editable: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: sequenceResponse.data.diagram_id,
          name: 'Key Interactions',
          type: 'sequence' as const,
          format: 'plantuml' as const,
          content: sequenceResponse.data.diagram_code,
          is_editable: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ];

      setDiagrams(prev => [...newDiagrams, ...prev]);
    } catch (error) {
      console.error('Failed to generate diagrams:', error);
    }
  };

  const createNewDiagram = async (type: string, format: string) => {
    try {
      const response = await apiClient.generateDiagram({
        project_id: projectId,
        diagram_type: type,
        output_format: format,
        context: {
          architecture_proposal: proposal,
          manual_creation: true
        }
      });

      const newDiagram: Diagram = {
        id: response.data.diagram_id,
        name: `${type.replace('_', ' ')} Diagram`,
        type: type as any,
        format: format as any,
        content: response.data.diagram_code,
        is_editable: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      setDiagrams(prev => [newDiagram, ...prev]);
    } catch (error) {
      console.error('Failed to create diagram:', error);
    }
  };

  const updateDiagram = async (diagramId: string, content: string) => {
    try {
      await apiClient.updateDiagram(diagramId, { content });
      setDiagrams(prev => prev.map(d => 
        d.id === diagramId ? { ...d, content, updated_at: new Date().toISOString() } : d
      ));
    } catch (error) {
      console.error('Failed to update diagram:', error);
    }
  };

  const deleteDiagram = async (diagramId: string) => {
    try {
      await apiClient.deleteDiagram(diagramId);
      setDiagrams(prev => prev.filter(d => d.id !== diagramId));
    } catch (error) {
      console.error('Failed to delete diagram:', error);
    }
  };

  const saveToKnowledgeBase = async () => {
    try {
      await apiClient.saveArchitectureToKnowledgeBase(projectId, {
        proposal,
        diagrams
      });
      // Show success notification
    } catch (error) {
      console.error('Failed to save to knowledge base:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'generating': return <ClockIcon className="h-4 w-4 text-blue-500" />;
      case 'failed': return <AlertCircleIcon className="h-4 w-4 text-red-500" />;
      default: return <ClockIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'generating': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCwIcon className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-slate-600">Loading architecture data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/projects/${projectId}`)}
                className="flex items-center space-x-2"
              >
                <ArrowLeftIcon className="h-4 w-4" />
                <span>Back to Project</span>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
                  <BuildingIcon className="h-8 w-8 text-blue-600" />
                  Architecture Design
                </h1>
                <p className="text-slate-600 mt-1">
                  AI-generated architecture proposals with interactive diagrams
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                onClick={saveToKnowledgeBase}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <SaveIcon className="h-4 w-4" />
                <span>Save to Knowledge Base</span>
              </Button>
              <Button
                onClick={generateArchitectureProposal}
                disabled={isGenerating}
                className="flex items-center space-x-2"
              >
                {isGenerating ? (
                  <RefreshCwIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <SparklesIcon className="h-4 w-4" />
                )}
                <span>{isGenerating ? 'Generating...' : 'Generate Architecture'}</span>
              </Button>
            </div>
          </div>

          {/* Main Content */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="proposal" className="flex items-center space-x-2">
                <BrainIcon className="h-4 w-4" />
                <span>Architecture Proposal</span>
              </TabsTrigger>
              <TabsTrigger value="diagrams" className="flex items-center space-x-2">
                <CodeIcon className="h-4 w-4" />
                <span>Diagrams ({diagrams.length})</span>
              </TabsTrigger>
              <TabsTrigger value="knowledge" className="flex items-center space-x-2">
                <FileTextIcon className="h-4 w-4" />
                <span>Knowledge Base</span>
              </TabsTrigger>
            </TabsList>

            {/* Architecture Proposal Tab */}
            <TabsContent value="proposal" className="space-y-6">
              {proposal ? (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {getStatusIcon(proposal.status)}
                          {proposal.title}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {proposal.description}
                        </CardDescription>
                      </div>
                      <Badge className={getStatusColor(proposal.status)}>
                        {proposal.status.toUpperCase()}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Overview */}
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Architecture Overview</h3>
                      <p className="text-slate-700 leading-relaxed">
                        {proposal.content.overview}
                      </p>
                    </div>

                    <Separator />

                    {/* Components */}
                    <div>
                      <h3 className="text-lg font-semibold mb-3">System Components</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        {proposal.content.components.map((component, index) => (
                          <Card key={index} className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium">{component.name}</h4>
                              <Badge variant="outline">{component.technology}</Badge>
                            </div>
                            <p className="text-sm text-slate-600 mb-3">{component.description}</p>
                            {component.dependencies.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-slate-500 mb-1">Dependencies:</p>
                                <div className="flex flex-wrap gap-1">
                                  {component.dependencies.map((dep, depIndex) => (
                                    <Badge key={depIndex} variant="secondary" className="text-xs">
                                      {dep}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </Card>
                        ))}
                      </div>
                    </div>

                    <Separator />

                    {/* Patterns */}
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Architectural Patterns</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        {proposal.content.patterns.map((pattern, index) => (
                          <Card key={index} className="p-4">
                            <h4 className="font-medium mb-2">{pattern.name}</h4>
                            <p className="text-sm text-slate-600 mb-3">{pattern.description}</p>
                            <div>
                              <p className="text-xs font-medium text-slate-500 mb-1">Benefits:</p>
                              <ul className="text-xs text-slate-600 space-y-1">
                                {pattern.benefits.map((benefit, benefitIndex) => (
                                  <li key={benefitIndex} className="flex items-start gap-2">
                                    <CheckCircleIcon className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                                    {benefit}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </Card>
                        ))}
                      </div>
                    </div>

                    <Separator />

                    {/* Tradeoffs */}
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Design Tradeoffs</h3>
                      <div className="space-y-4">
                        {proposal.content.tradeoffs.map((tradeoff, index) => (
                          <Card key={index} className="p-4">
                            <h4 className="font-medium mb-3">{tradeoff.aspect}</h4>
                            <div className="grid md:grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium text-green-700 mb-2">Pros:</p>
                                <ul className="text-sm text-slate-600 space-y-1">
                                  {tradeoff.pros.map((pro, proIndex) => (
                                    <li key={proIndex} className="flex items-start gap-2">
                                      <CheckCircleIcon className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                                      {pro}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-red-700 mb-2">Cons:</p>
                                <ul className="text-sm text-slate-600 space-y-1">
                                  {tradeoff.cons.map((con, conIndex) => (
                                    <li key={conIndex} className="flex items-start gap-2">
                                      <AlertCircleIcon className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                                      {con}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </Card>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="p-12 text-center">
                  <BrainIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    No Architecture Proposal Yet
                  </h3>
                  <p className="text-slate-600 mb-6">
                    Generate an AI-powered architecture proposal based on your project requirements.
                  </p>
                  <Button onClick={generateArchitectureProposal} disabled={isGenerating}>
                    {isGenerating ? (
                      <>
                        <RefreshCwIcon className="h-4 w-4 animate-spin mr-2" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <SparklesIcon className="h-4 w-4 mr-2" />
                        Generate Architecture Proposal
                      </>
                    )}
                  </Button>
                </Card>
              )}
            </TabsContent>

            {/* Diagrams Tab */}
            <TabsContent value="diagrams" className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Architecture Diagrams</h2>
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => createNewDiagram('c4_context', 'plantuml')}
                    variant="outline"
                    size="sm"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    New C4 Context
                  </Button>
                  <Button
                    onClick={() => createNewDiagram('c4_container', 'plantuml')}
                    variant="outline"
                    size="sm"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    New C4 Container
                  </Button>
                  <Button
                    onClick={() => createNewDiagram('sequence', 'plantuml')}
                    variant="outline"
                    size="sm"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    New Sequence
                  </Button>
                </div>
              </div>

              {diagrams.length > 0 ? (
                <div className="grid gap-6">
                  {diagrams.map((diagram) => (
                    <Card key={diagram.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="flex items-center gap-2">
                              <CodeIcon className="h-5 w-5" />
                              {diagram.name}
                            </CardTitle>
                            <CardDescription>
                              {diagram.type.replace('_', ' ')} • {diagram.format}
                            </CardDescription>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">
                              {diagram.is_editable ? 'Editable' : 'Read-only'}
                            </Badge>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setEditingDiagram(
                                editingDiagram === diagram.id ? null : diagram.id
                              )}
                            >
                              <EditIcon className="h-4 w-4 mr-2" />
                              {editingDiagram === diagram.id ? 'Done' : 'Edit'}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deleteDiagram(diagram.id)}
                            >
                              <TrashIcon className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {editingDiagram === diagram.id ? (
                          <div className="space-y-4">
                            <textarea
                              value={diagram.content}
                              onChange={(e) => {
                                const updatedDiagrams = diagrams.map(d => 
                                  d.id === diagram.id ? { ...d, content: e.target.value } : d
                                );
                                setDiagrams(updatedDiagrams);
                              }}
                              className="w-full h-96 p-4 border rounded-lg font-mono text-sm"
                              placeholder="Edit diagram code..."
                            />
                            <div className="flex justify-end space-x-2">
                              <Button
                                variant="outline"
                                onClick={() => setEditingDiagram(null)}
                              >
                                Cancel
                              </Button>
                              <Button
                                onClick={() => {
                                  updateDiagram(diagram.id, diagram.content);
                                  setEditingDiagram(null);
                                }}
                              >
                                <SaveIcon className="h-4 w-4 mr-2" />
                                Save Changes
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="bg-slate-50 p-4 rounded-lg">
                            <pre className="text-sm font-mono text-slate-700 whitespace-pre-wrap">
                              {diagram.content}
                            </pre>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <CodeIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    No Diagrams Yet
                  </h3>
                  <p className="text-slate-600 mb-6">
                    Create architecture diagrams to visualize your system design.
                  </p>
                  <div className="flex justify-center space-x-2">
                    <Button
                      onClick={() => createNewDiagram('c4_context', 'plantuml')}
                      variant="outline"
                    >
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Create C4 Context
                    </Button>
                    <Button
                      onClick={() => createNewDiagram('sequence', 'plantuml')}
                      variant="outline"
                    >
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Create Sequence
                    </Button>
                  </div>
                </Card>
              )}
            </TabsContent>

            {/* Knowledge Base Tab */}
            <TabsContent value="knowledge" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileTextIcon className="h-5 w-5" />
                    Knowledge Base Integration
                  </CardTitle>
                  <CardDescription>
                    Your architecture proposals and diagrams are automatically indexed in the knowledge base
                    for future reference and pattern matching.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Vector Search</h4>
                      <p className="text-sm text-blue-700">
                        Semantic search across all your architecture decisions and patterns.
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-medium text-green-900 mb-2">Pattern Matching</h4>
                      <p className="text-sm text-green-700">
                        Find similar architectures and reuse proven patterns.
                      </p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h4 className="font-medium text-purple-900 mb-2">Context Generation</h4>
                      <p className="text-sm text-purple-700">
                        Get relevant context for new features based on existing knowledge.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Knowledge Base Status</h4>
                      <p className="text-sm text-slate-600">
                        {proposal ? 'Architecture proposal indexed' : 'No proposal to index'} • 
                        {diagrams.length} diagrams stored
                      </p>
                    </div>
                    <Button onClick={saveToKnowledgeBase} variant="outline">
                      <SaveIcon className="h-4 w-4 mr-2" />
                      Update Knowledge Base
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
