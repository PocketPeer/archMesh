'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Architecture } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  CheckCircle2Icon, 
  XCircleIcon, 
  DownloadIcon, 
  BuildingIcon, 
  LayersIcon, 
  CpuIcon, 
  DatabaseIcon, 
  GlobeIcon, 
  ShieldIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  FileTextIcon,
  ZapIcon,
  UsersIcon,
  SettingsIcon
} from 'lucide-react';
import mermaid from 'mermaid';

interface ArchitectureViewerProps {
  architecture: Architecture;
  onApprove: () => void;
  onReject: () => void;
}

export function ArchitectureViewer({ architecture, onApprove, onReject }: ArchitectureViewerProps) {
  const mermaidRef = useRef<HTMLDivElement>(null);
  const [isDiagramLoaded, setIsDiagramLoaded] = useState(false);
  const [expandedAlternatives, setExpandedAlternatives] = useState<number[]>([]);

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

  // Render C4 diagram when component mounts or architecture changes
  useEffect(() => {
    if (architecture.c4_diagram_context && mermaidRef.current && !isDiagramLoaded) {
      const renderDiagram = async () => {
        try {
          const element = mermaidRef.current;
          if (element) {
            element.innerHTML = '';
            const { svg } = await mermaid.render('c4-diagram', architecture.c4_diagram_context || '');
            element.innerHTML = svg;
            setIsDiagramLoaded(true);
          }
        } catch (error) {
          console.error('Error rendering Mermaid diagram:', error);
          if (mermaidRef.current) {
            mermaidRef.current.innerHTML = '<p class="text-red-500">Error rendering diagram</p>';
          }
        }
      };
      renderDiagram();
    }
  }, [architecture.c4_diagram_context, isDiagramLoaded]);

  const downloadDiagram = () => {
    if (mermaidRef.current) {
      const svg = mermaidRef.current.querySelector('svg');
      if (svg) {
        const svgData = new XMLSerializer().serializeToString(svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx?.drawImage(img, 0, 0);
          
          const link = document.createElement('a');
          link.download = `architecture-diagram-${architecture.project_id}.png`;
          link.href = canvas.toDataURL();
          link.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
      }
    }
  };

  const downloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(architecture, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `architecture-${architecture.project_id}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const toggleAlternative = (index: number) => {
    setExpandedAlternatives(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const getTechnologyIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'frontend': return <GlobeIcon className="h-4 w-4 mr-2" />;
      case 'backend': return <CpuIcon className="h-4 w-4 mr-2" />;
      case 'database': return <DatabaseIcon className="h-4 w-4 mr-2" />;
      case 'infrastructure': return <BuildingIcon className="h-4 w-4 mr-2" />;
      case 'security': return <ShieldIcon className="h-4 w-4 mr-2" />;
      case 'monitoring': return <ZapIcon className="h-4 w-4 mr-2" />;
      default: return <SettingsIcon className="h-4 w-4 mr-2" />;
    }
  };

  const getComponentIcon = (component: any) => {
    if (component.type?.toLowerCase().includes('database')) return <DatabaseIcon className="h-4 w-4 mr-2" />;
    if (component.type?.toLowerCase().includes('api')) return <GlobeIcon className="h-4 w-4 mr-2" />;
    if (component.type?.toLowerCase().includes('service')) return <CpuIcon className="h-4 w-4 mr-2" />;
    if (component.type?.toLowerCase().includes('user')) return <UsersIcon className="h-4 w-4 mr-2" />;
    return <FileTextIcon className="h-4 w-4 mr-2" />;
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-2xl font-bold">Architecture Design</CardTitle>
        <div className="flex space-x-2">
          <Button onClick={onApprove} className="bg-green-600 hover:bg-green-700 text-white">
            <CheckCircle2Icon className="mr-2 h-4 w-4" /> Approve
          </Button>
          <Button onClick={onReject} variant="destructive">
            <XCircleIcon className="mr-2 h-4 w-4" /> Reject
          </Button>
          <Button variant="outline" onClick={downloadDiagram}>
            <DownloadIcon className="mr-2 h-4 w-4" /> Export Diagram
          </Button>
          <Button variant="outline" onClick={downloadJson}>
            <FileTextIcon className="mr-2 h-4 w-4" /> Download JSON
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-8 pt-6">
        {/* Architecture Overview */}
        <div>
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <BuildingIcon className="mr-2 h-5 w-5 text-blue-600" /> 
            Architecture Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Architecture Style</CardTitle>
                <CardDescription>Primary architectural pattern</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="default" className="text-lg px-3 py-1">
                  {architecture.architecture_style}
                </Badge>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Status</CardTitle>
                <CardDescription>Current design status</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge 
                  variant={architecture.status === 'completed' ? 'default' : 'secondary'}
                  className="text-lg px-3 py-1"
                >
                  {architecture.status}
                </Badge>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* C4 Diagram */}
        {architecture.c4_diagram_context && (
          <div>
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <LayersIcon className="mr-2 h-5 w-5 text-purple-600" /> 
              C4 Architecture Diagram
            </h3>
            <Card>
              <CardContent className="p-6">
                <div 
                  ref={mermaidRef} 
                  className="w-full overflow-auto border rounded-lg p-4 bg-white"
                  style={{ minHeight: '400px' }}
                >
                  {!isDiagramLoaded && (
                    <div className="flex items-center justify-center h-96">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        <p className="text-slate-600">Loading diagram...</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Components List */}
        <div>
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <CpuIcon className="mr-2 h-5 w-5 text-green-600" /> 
            System Components
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {architecture.components?.map((component, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center text-lg">
                    {getComponentIcon(component)}
                    {component.name || `Component ${index + 1}`}
                  </CardTitle>
                  <CardDescription>
                    {component.type || 'System Component'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {component.description && (
                    <p className="text-sm text-slate-600 mb-3">{component.description}</p>
                  )}
                  {component.technologies && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm">Technologies:</h4>
                      <div className="flex flex-wrap gap-1">
                        {component.technologies.map((tech: string, techIndex: number) => (
                          <Badge key={techIndex} variant="secondary" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {component.responsibilities && (
                    <div className="mt-3">
                      <h4 className="font-medium text-sm mb-2">Responsibilities:</h4>
                      <ul className="text-xs text-slate-600 space-y-1">
                        {component.responsibilities.map((resp: string, respIndex: number) => (
                          <li key={respIndex} className="flex items-start">
                            <span className="mr-1">•</span>
                            {resp}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Technology Stack */}
        <div>
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <LayersIcon className="mr-2 h-5 w-5 text-orange-600" /> 
            Technology Stack
          </h3>
          <Tabs defaultValue={Object.keys(architecture.technology_stack || {})[0]} className="w-full">
            <TabsList className="grid w-full grid-cols-2 md:grid-cols-4">
              {Object.keys(architecture.technology_stack || {}).map(category => (
                <TabsTrigger key={category} value={category} className="capitalize">
                  {getTechnologyIcon(category)}{category}
                </TabsTrigger>
              ))}
            </TabsList>
            {Object.entries(architecture.technology_stack || {}).map(([category, technologies]) => (
              <TabsContent key={category} value={category} className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="capitalize">{category} Technologies</CardTitle>
                    <CardDescription>Technologies used in the {category} layer</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Array.isArray(technologies) ? (
                        technologies.map((tech: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div>
                              <p className="font-medium">{tech.name || tech}</p>
                              {tech.description && (
                                <p className="text-sm text-slate-600">{tech.description}</p>
                              )}
                            </div>
                            {tech.version && (
                              <Badge variant="outline">{tech.version}</Badge>
                            )}
                          </div>
                        ))
                      ) : (
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{technologies}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>

        {/* Alternatives Considered */}
        {architecture.alternatives && architecture.alternatives.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <FileTextIcon className="mr-2 h-5 w-5 text-indigo-600" /> 
              Alternatives Considered
            </h3>
            <div className="space-y-4">
              {architecture.alternatives.map((alternative, index) => (
                <Collapsible 
                  key={index}
                  open={expandedAlternatives.includes(index)}
                  onOpenChange={() => toggleAlternative(index)}
                >
                  <Card>
                    <CollapsibleTrigger asChild>
                      <CardHeader className="cursor-pointer hover:bg-slate-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {expandedAlternatives.includes(index) ? (
                              <ChevronDownIcon className="h-4 w-4 mr-2" />
                            ) : (
                              <ChevronRightIcon className="h-4 w-4 mr-2" />
                            )}
                            <CardTitle className="text-lg">
                              {alternative.name || `Alternative ${index + 1}`}
                            </CardTitle>
                          </div>
                          <Badge variant="outline">
                            {alternative.status || 'Considered'}
                          </Badge>
                        </div>
                        <CardDescription>
                          {alternative.description || 'Click to view details'}
                        </CardDescription>
                      </CardHeader>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <CardContent className="pt-0">
                        <div className="space-y-4">
                          {alternative.pros && alternative.pros.length > 0 && (
                            <div>
                              <h4 className="font-medium text-green-700 mb-2">Advantages:</h4>
                              <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                {alternative.pros.map((pro: string, proIndex: number) => (
                                  <li key={proIndex}>{pro}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {alternative.cons && alternative.cons.length > 0 && (
                            <div>
                              <h4 className="font-medium text-red-700 mb-2">Disadvantages:</h4>
                              <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                {alternative.cons.map((con: string, conIndex: number) => (
                                  <li key={conIndex}>{con}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {alternative.trade_offs && (
                            <div>
                              <h4 className="font-medium text-orange-700 mb-2">Trade-offs:</h4>
                              <p className="text-sm text-slate-600">{alternative.trade_offs}</p>
                            </div>
                          )}
                          {alternative.reason_for_rejection && (
                            <div>
                              <h4 className="font-medium text-red-700 mb-2">Reason for Rejection:</h4>
                              <p className="text-sm text-slate-600">{alternative.reason_for_rejection}</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </CollapsibleContent>
                  </Card>
                </Collapsible>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
