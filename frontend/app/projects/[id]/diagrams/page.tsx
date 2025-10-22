'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BuildingIcon, 
  ArrowRightIcon, 
  TargetIcon, 
  DownloadIcon, 
  EyeIcon,
  CodeIcon,
  FileTextIcon,
  RefreshCwIcon,
  CheckCircleIcon,
  AlertCircleIcon
} from 'lucide-react';
import ArchitectureDiagrams from '@/components/ArchitectureDiagrams';

export default function ProjectDiagramsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [loading, setLoading] = useState(false);
  const [diagrams, setDiagrams] = useState<any[]>([]);
  const [selectedDiagram, setSelectedDiagram] = useState<any | null>(null);

  const handleDiagramGenerated = (diagram: any) => {
    setDiagrams(prev => [diagram, ...prev]);
    setSelectedDiagram(diagram);
  };

  const handleBackToProject = () => {
    router.push(`/projects/${projectId}`);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Architecture Diagrams</h1>
              <p className="text-slate-600 mt-2">
                Generate comprehensive architecture diagrams including C4 models, sequence diagrams, and NFR mapping
              </p>
            </div>
            <Button onClick={handleBackToProject} variant="outline">
              Back to Project
            </Button>
          </div>

          {/* Diagram Generation Component */}
          <ArchitectureDiagrams 
            projectId={projectId}
            onDiagramGenerated={handleDiagramGenerated}
          />

          {/* Generated Diagrams */}
          {diagrams.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                  Generated Diagrams
                </CardTitle>
                <CardDescription>
                  {diagrams.length} diagram{diagrams.length !== 1 ? 's' : ''} generated successfully
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
                              {new Date(diagram.created_at).toLocaleString()}
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
                              onClick={() => {
                                const content = diagram.mermaid_code;
                                const filename = `${diagram.diagram_type}_${diagram.diagram_id}.md`;
                                const blob = new Blob([content], { type: 'text/plain' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = filename;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                              }}
                            >
                              <DownloadIcon className="h-4 w-4 mr-2" />
                              Mermaid
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                const content = diagram.plantuml_code;
                                const filename = `${diagram.diagram_type}_${diagram.diagram_id}.puml`;
                                const blob = new Blob([content], { type: 'text/plain' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = filename;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                              }}
                            >
                              <DownloadIcon className="h-4 w-4 mr-2" />
                              PlantUML
                            </Button>
                          </div>

                          {diagram.metadata && (
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              {diagram.metadata.component_count && (
                                <span>Components: {diagram.metadata.component_count}</span>
                              )}
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

          {/* Diagram Preview */}
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
                <Tabs defaultValue="mermaid" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="mermaid">
                      <CodeIcon className="h-4 w-4 mr-2" />
                      Mermaid
                    </TabsTrigger>
                    <TabsTrigger value="plantuml">
                      <FileTextIcon className="h-4 w-4 mr-2" />
                      PlantUML
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="mermaid" className="mt-4">
                    <div className="border rounded-lg p-4 bg-gray-50">
                      <pre className="text-sm overflow-auto">
                        <code>{selectedDiagram.mermaid_code}</code>
                      </pre>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="plantuml" className="mt-4">
                    <div className="border rounded-lg p-4 bg-gray-50">
                      <pre className="text-sm overflow-auto">
                        <code>{selectedDiagram.plantuml_code}</code>
                      </pre>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common diagram generation tasks for your project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center gap-2"
                  onClick={() => router.push(`/projects/${projectId}`)}
                >
                  <BuildingIcon className="h-6 w-6" />
                  <span>Back to Project</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center gap-2"
                  onClick={() => window.location.reload()}
                >
                  <RefreshCwIcon className="h-6 w-6" />
                  <span>Refresh</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center gap-2"
                  onClick={() => setDiagrams([])}
                >
                  <AlertCircleIcon className="h-6 w-6" />
                  <span>Clear All</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
