'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  DownloadIcon, 
  RefreshCwIcon, 
  EyeIcon, 
  CodeIcon,
  FileTextIcon,
  BuildingIcon,
  ZapIcon,
  TargetIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  AlertCircleIcon
} from 'lucide-react';
import mermaid from 'mermaid';

interface DiagramData {
  diagram_id: string;
  diagram_type: string;
  title: string;
  description: string;
  plantuml_code: string;
  mermaid_code: string;
  metadata: {
    generated_at: string;
    component_count?: number;
    relationship_count?: number;
    nfr_count?: number;
  };
}

interface ArchitectureDiagramsProps {
  projectId: string;
  workflowId?: string;
  onDiagramGenerated?: (diagram: DiagramData) => void;
}

function ArchitectureDiagrams({ 
  projectId, 
  workflowId, 
  onDiagramGenerated 
}: ArchitectureDiagramsProps) {
  const [diagrams, setDiagrams] = useState<DiagramData[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('c4');
  const [selectedDiagram, setSelectedDiagram] = useState<DiagramData | null>(null);
  const [diagramView, setDiagramView] = useState<'mermaid' | 'plantuml'>('mermaid');

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
      },
    });
  }, []);

  const generateC4Diagram = async (level: 'context' | 'container' | 'component') => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/diagrams/c4', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project_id: projectId,
          workflow_id: workflowId,
          diagram_type: `c4_${level}`,
          title: `${level.charAt(0).toUpperCase() + level.slice(1)} View`,
          description: `C4 ${level} diagram for the system architecture`,
          include_nfr: true,
          include_technology_stack: true,
          include_data_flows: true,
          include_security: true,
          include_monitoring: true
        })
      });

      if (response.ok) {
        const diagram = await response.json();
        setDiagrams(prev => [diagram, ...prev]);
        setSelectedDiagram(diagram);
        onDiagramGenerated?.(diagram);
      }
    } catch (error) {
      console.error('Error generating C4 diagram:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSequenceDiagram = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/diagrams/sequence', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project_id: projectId,
          workflow_id: workflowId,
          use_cases: [
            'User Registration',
            'Order Processing',
            'Payment Flow',
            'Data Synchronization'
          ],
          title: 'Key Use-Case Sequences',
          description: 'Sequence diagrams for main use-cases'
        })
      });

      if (response.ok) {
        const diagram = await response.json();
        setDiagrams(prev => [diagram, ...prev]);
        setSelectedDiagram(diagram);
        onDiagramGenerated?.(diagram);
      }
    } catch (error) {
      console.error('Error generating sequence diagram:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNFRMapping = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/diagrams/nfr-mapping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project_id: projectId,
          workflow_id: workflowId,
          nfr_requirements: [
            {
              id: 'performance',
              name: 'Response Time',
              description: 'API response time requirement',
              metric: 'latency',
              target_value: '200',
              unit: 'ms',
              priority: 'high',
              affected_components: ['api-gateway', 'web-app']
            },
            {
              id: 'scalability',
              name: 'Throughput',
              description: 'System throughput requirement',
              metric: 'requests_per_second',
              target_value: '1000',
              unit: 'rps',
              priority: 'high',
              affected_components: ['api-gateway', 'load-balancer']
            },
            {
              id: 'security',
              name: 'Authentication',
              description: 'User authentication requirement',
              metric: 'security_level',
              target_value: 'OAuth2',
              unit: 'standard',
              priority: 'critical',
              affected_components: ['auth-service', 'api-gateway']
            }
          ],
          title: 'NFR Mapping & Trade-offs',
          description: 'Non-functional requirements mapping and trade-off analysis'
        })
      });

      if (response.ok) {
        const diagram = await response.json();
        setDiagrams(prev => [diagram, ...prev]);
        setSelectedDiagram(diagram);
        onDiagramGenerated?.(diagram);
      }
    } catch (error) {
      console.error('Error generating NFR mapping:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadDiagram = (diagram: DiagramData, format: 'mermaid' | 'plantuml') => {
    const content = format === 'mermaid' ? diagram.mermaid_code : diagram.plantuml_code;
    const filename = `${diagram.diagram_type}_${diagram.diagram_id}.${format === 'mermaid' ? 'md' : 'puml'}`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderDiagram = (diagram: DiagramData) => {
    if (diagramView === 'mermaid') {
      return (
        <div 
          className="mermaid-diagram"
          dangerouslySetInnerHTML={{ __html: '' }}
        />
      );
    } else {
      return (
        <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm">
          <code>{diagram.plantuml_code}</code>
        </pre>
      );
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BuildingIcon className="h-5 w-5" />
            Architecture Diagrams
          </CardTitle>
          <CardDescription>
            Generate comprehensive architecture diagrams including C4 models, sequence diagrams, and NFR mapping
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="c4">C4 Diagrams</TabsTrigger>
              <TabsTrigger value="sequence">Sequence</TabsTrigger>
              <TabsTrigger value="nfr">NFR Mapping</TabsTrigger>
            </TabsList>

            <TabsContent value="c4" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button 
                  onClick={() => generateC4Diagram('context')}
                  disabled={loading}
                  className="h-20 flex flex-col items-center gap-2"
                >
                  <EyeIcon className="h-6 w-6" />
                  <span>Context View</span>
                </Button>
                <Button 
                  onClick={() => generateC4Diagram('container')}
                  disabled={loading}
                  className="h-20 flex flex-col items-center gap-2"
                >
                  <BuildingIcon className="h-6 w-6" />
                  <span>Container View</span>
                </Button>
                <Button 
                  onClick={() => generateC4Diagram('component')}
                  disabled={loading}
                  className="h-20 flex flex-col items-center gap-2"
                >
                  <ZapIcon className="h-6 w-6" />
                  <span>Component View</span>
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="sequence" className="space-y-4">
              <div className="text-center">
                <Button 
                  onClick={generateSequenceDiagram}
                  disabled={loading}
                  className="h-20 w-full flex flex-col items-center gap-2"
                >
                  <ArrowRightIcon className="h-6 w-6" />
                  <span>Generate Sequence Diagrams</span>
                </Button>
                <p className="text-sm text-gray-600 mt-2">
                  Creates sequence diagrams for key use-cases from workflow data
                </p>
              </div>
            </TabsContent>

            <TabsContent value="nfr" className="space-y-4">
              <div className="text-center">
                <Button 
                  onClick={generateNFRMapping}
                  disabled={loading}
                  className="h-20 w-full flex flex-col items-center gap-2"
                >
                  <TargetIcon className="h-6 w-6" />
                  <span>Generate NFR Mapping</span>
                </Button>
                <p className="text-sm text-gray-600 mt-2">
                  Maps non-functional requirements to components with trade-off analysis
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {diagrams.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Diagrams</CardTitle>
            <CardDescription>
              {diagrams.length} diagram{diagrams.length !== 1 ? 's' : ''} generated
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {diagrams.map((diagram) => (
                <Card key={diagram.diagram_id} className="border-l-4 border-l-blue-500">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{diagram.title}</CardTitle>
                        <CardDescription>{diagram.description}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{diagram.diagram_type}</Badge>
                        <Badge variant="secondary">
                          {new Date(diagram.metadata.generated_at).toLocaleString()}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedDiagram(diagram)}
                        >
                          <EyeIcon className="h-4 w-4 mr-2" />
                          View
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadDiagram(diagram, 'mermaid')}
                        >
                          <DownloadIcon className="h-4 w-4 mr-2" />
                          Mermaid
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadDiagram(diagram, 'plantuml')}
                        >
                          <DownloadIcon className="h-4 w-4 mr-2" />
                          PlantUML
                        </Button>
                      </div>

                      {diagram.metadata.component_count && (
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>Components: {diagram.metadata.component_count}</span>
                          {diagram.metadata.relationship_count && (
                            <span>Relationships: {diagram.metadata.relationship_count}</span>
                          )}
                          {diagram.metadata.nfr_count && (
                            <span>NFRs: {diagram.metadata.nfr_count}</span>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedDiagram && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedDiagram.title}</CardTitle>
                <CardDescription>{selectedDiagram.description}</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant={diagramView === 'mermaid' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDiagramView('mermaid')}
                >
                  <CodeIcon className="h-4 w-4 mr-2" />
                  Mermaid
                </Button>
                <Button
                  variant={diagramView === 'plantuml' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDiagramView('plantuml')}
                >
                  <FileTextIcon className="h-4 w-4 mr-2" />
                  PlantUML
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedDiagram(null)}
                >
                  Close
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg p-4 bg-gray-50">
              {renderDiagram(selectedDiagram)}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default ArchitectureDiagrams;