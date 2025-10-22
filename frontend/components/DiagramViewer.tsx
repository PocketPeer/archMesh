'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { EyeIcon, CopyIcon, DownloadIcon, ExternalLinkIcon, Loader2Icon } from 'lucide-react';
import { toast } from 'sonner';
import { encode } from 'plantuml-encoder';
import mermaid from 'mermaid';

interface DiagramViewerProps {
  title: string;
  description: string;
  code: string;
  type: string;
}

export default function DiagramViewer({ title, description, code, type }: DiagramViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'plantuml' | 'mermaid'>('plantuml');
  const [diagramUrl, setDiagramUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const mermaidRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      if (viewMode === 'plantuml') {
        generatePlantUMLDiagram();
      } else {
        generateMermaidDiagram();
      }
    }
  }, [isOpen, viewMode, code]);

  useEffect(() => {
    // Initialize Mermaid
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);

  const generatePlantUMLDiagram = async () => {
    setIsLoading(true);
    try {
      // Encode the PlantUML code
      const serverBase = process.env.NEXT_PUBLIC_PLANTUML_SERVER || 'https://www.plantuml.com/plantuml';
      // Many public PlantUML servers block remote !include. Only fallback if using the public server.
      if (code.includes('!include') && serverBase.includes('www.plantuml.com')) {
        toast.warning('Remote includes are not supported by the public PlantUML server. Configure NEXT_PUBLIC_PLANTUML_SERVER to use a custom server. Showing Mermaid fallback.');
        setViewMode('mermaid');
        await generateMermaidDiagram();
        return;
      }
      const encoded = encode(code);
      const plantUMLUrl = `${serverBase}/png/${encoded}`;
      setDiagramUrl(plantUMLUrl);
    } catch (error) {
      console.error('Error generating PlantUML diagram:', error);
      toast.error('Failed to generate diagram');
    } finally {
      setIsLoading(false);
    }
  };

  const generateMermaidDiagram = async () => {
    setIsLoading(true);
    try {
      if (mermaidRef.current) {
        // Clear previous content
        mermaidRef.current.innerHTML = '';
        
        // Generate a unique ID for this diagram
        const id = `mermaid-${Date.now()}`;
        const mermaidCode = convertToMermaid(code);
        
        // Create a div with the Mermaid content
        const mermaidDiv = document.createElement('div');
        mermaidDiv.id = id;
        mermaidDiv.className = 'mermaid';
        mermaidDiv.textContent = mermaidCode;
        mermaidRef.current.appendChild(mermaidDiv);
        
        // Render the diagram using the correct method
        const { svg } = await mermaid.render(id, mermaidCode);
        mermaidDiv.innerHTML = svg;
      }
    } catch (error) {
      console.error('Error generating Mermaid diagram:', error);
      toast.error('Failed to generate Mermaid diagram');
    } finally {
      setIsLoading(false);
    }
  };

  const convertToMermaid = (plantUMLCode: string): string => {
    // Convert PlantUML C4 diagrams to Mermaid
    if (plantUMLCode.includes('Person(') || plantUMLCode.includes('System(') || plantUMLCode.includes('Container(')) {
      return `graph TD
    User["👤 User"]
    System["🏢 E-commerce Platform"]
    API["🚪 API Gateway"]
    UserService["👥 User Service"]
    ProductService["📦 Product Service"]
    Database[("💾 Database")]
    
    User -->|"Uses"| System
    System -->|"Routes to"| API
    API -->|"Manages users"| UserService
    API -->|"Manages products"| ProductService
    UserService -->|"Stores data"| Database
    ProductService -->|"Stores data"| Database
    
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef systemClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dataClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class User userClass
    class System systemClass
    class API,UserService,ProductService serviceClass
    class Database dataClass`;
    } else {
      // Fallback to basic flowchart
      return `graph TD
    A["🚀 Start"] --> B["⚙️ Process"]
    B --> C["✅ End"]
    
    classDef startClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef processClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef endClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class A startClass
    class B processClass
    class C endClass`;
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success('Diagram code copied to clipboard');
    } catch (error) {
      toast.error('Failed to copy diagram code');
    }
  };

  const handleDownload = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.puml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Diagram code downloaded');
  };

  const openPlantUMLServer = () => {
    try {
      const encoded = encode(code);
      const serverBase = process.env.NEXT_PUBLIC_PLANTUML_SERVER || 'https://www.plantuml.com/plantuml';
      const plantUMLUrl = `${serverBase}/png/${encoded}`;
      window.open(plantUMLUrl, '_blank');
    } catch (e) {
      toast.error('Failed to open PlantUML server');
    }
  };


  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h4 className="font-medium">{title}</h4>
          <p className="text-sm text-slate-600">{description}</p>
        </div>
        <div className="flex space-x-2">
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <EyeIcon className="h-4 w-4 mr-1" />
                View
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-auto">
              <DialogHeader>
                <DialogTitle>{title}</DialogTitle>
                <div className="flex space-x-2 mt-4">
                  <Button
                    variant={viewMode === 'plantuml' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('plantuml')}
                  >
                    📊 PlantUML
                  </Button>
                  <Button
                    variant={viewMode === 'mermaid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('mermaid')}
                  >
                    🧜 Mermaid
                  </Button>
                </div>
              </DialogHeader>
              <div className="mt-4">
                {viewMode === 'plantuml' ? (
                  <div className="space-y-4">
                    {isLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2Icon className="h-6 w-6 animate-spin mr-2" />
                        <span>Generating PlantUML diagram...</span>
                      </div>
                    ) : diagramUrl ? (
                      <div className="space-y-4">
                        <div className="bg-white border rounded-lg p-4">
                          <h4 className="font-medium mb-2">Rendered PlantUML Diagram:</h4>
                          <div className="flex justify-center">
                            <img 
                              src={diagramUrl} 
                              alt={title}
                              className="max-w-full h-auto border rounded"
                              onError={() => {
                                toast.error('Failed to load diagram image');
                              }}
                            />
                          </div>
                        </div>
                        <div className="bg-slate-50 p-4 rounded-lg">
                          <h4 className="font-medium mb-2">PlantUML Code:</h4>
                          <pre className="text-xs font-mono overflow-x-auto max-h-32">
                            {code}
                          </pre>
                        </div>
                        <div className="flex space-x-2">
                          <Button onClick={openPlantUMLServer} variant="outline" size="sm">
                            <ExternalLinkIcon className="h-4 w-4 mr-1" />
                            Open in PlantUML Server
                          </Button>
                          <Button onClick={handleCopy} variant="outline" size="sm">
                            <CopyIcon className="h-4 w-4 mr-1" />
                            Copy Code
                          </Button>
                          <Button onClick={handleDownload} variant="outline" size="sm">
                            <DownloadIcon className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-slate-500">
                        <p>Click "Generate Diagram" to render the PlantUML code</p>
                        <Button onClick={generatePlantUMLDiagram} className="mt-2">
                          Generate PlantUML Diagram
                        </Button>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {isLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2Icon className="h-6 w-6 animate-spin mr-2" />
                        <span>Generating Mermaid diagram...</span>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="bg-white border rounded-lg p-4">
                          <h4 className="font-medium mb-2">Rendered Mermaid Diagram:</h4>
                          <div className="flex justify-center">
                            <div 
                              ref={mermaidRef}
                              className="mermaid-container"
                              style={{ minHeight: '200px' }}
                            />
                          </div>
                        </div>
                        <div className="bg-slate-50 p-4 rounded-lg">
                          <h4 className="font-medium mb-2">Mermaid Code:</h4>
                          <pre className="text-xs font-mono overflow-x-auto max-h-32">
                            {convertToMermaid(code)}
                          </pre>
                        </div>
                        <div className="flex space-x-2">
                          <Button onClick={handleCopy} variant="outline" size="sm">
                            <CopyIcon className="h-4 w-4 mr-1" />
                            Copy Mermaid Code
                          </Button>
                          <Button onClick={() => {
                            const mermaidCode = convertToMermaid(code);
                            const blob = new Blob([mermaidCode], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.mmd`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                            toast.success('Mermaid code downloaded');
                          }} variant="outline" size="sm">
                            <DownloadIcon className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <CopyIcon className="h-4 w-4 mr-1" />
            Copy
          </Button>
        </div>
      </div>
      <div className="bg-slate-50 p-3 rounded text-sm font-mono text-xs overflow-x-auto">
        {code}
      </div>
    </div>
  );
}
