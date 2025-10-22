'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { 
  DownloadIcon,
  FileTextIcon,
  CodeIcon,
  ImageIcon,
  DatabaseIcon,
  GlobeIcon,
  Loader2Icon,
  CheckCircleIcon,
  AlertCircleIcon
} from 'lucide-react';
import { ExportService, ExportOptions, ArchitectureData } from '@/lib/export-service';

interface ExportDialogProps {
  data: ArchitectureData;
  trigger?: React.ReactNode;
}

const exportFormats = [
  {
    id: 'pdf',
    name: 'PDF Document',
    description: 'Professional PDF with diagrams and formatting',
    icon: <FileTextIcon className="h-5 w-5" />,
    color: 'text-red-600',
    features: ['Professional formatting', 'Diagrams included', 'Print-ready', 'Shareable']
  },
  {
    id: 'markdown',
    name: 'Markdown',
    description: 'Plain text format for documentation',
    icon: <CodeIcon className="h-5 w-5" />,
    color: 'text-blue-600',
    features: ['GitHub compatible', 'Version control friendly', 'Easy to edit', 'Lightweight']
  },
  {
    id: 'html',
    name: 'HTML',
    description: 'Web-ready format with styling',
    icon: <GlobeIcon className="h-5 w-5" />,
    color: 'text-green-600',
    features: ['Web-ready', 'Interactive', 'Styled', 'Shareable URL']
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'Structured data format for integration',
    icon: <DatabaseIcon className="h-5 w-5" />,
    color: 'text-purple-600',
    features: ['Machine readable', 'API integration', 'Structured data', 'Programmatic access']
  },
  {
    id: 'plantuml',
    name: 'PlantUML',
    description: 'Diagram source code for PlantUML',
    icon: <ImageIcon className="h-5 w-5" />,
    color: 'text-orange-600',
    features: ['Diagram source', 'Editable', 'Version control', 'Tool integration']
  },
  {
    id: 'mermaid',
    name: 'Mermaid',
    description: 'Diagram source code for Mermaid',
    icon: <ImageIcon className="h-5 w-5" />,
    color: 'text-pink-600',
    features: ['GitHub compatible', 'Web rendering', 'Simple syntax', 'Version control']
  }
];

const contentSections = [
  {
    id: 'includeDiagrams',
    name: 'Architecture Diagrams',
    description: 'Include C4 diagrams, sequence diagrams, and other visual representations'
  },
  {
    id: 'includeCode',
    name: 'Code Examples',
    description: 'Include implementation code and configuration examples'
  },
  {
    id: 'includeRecommendations',
    name: 'Recommendations',
    description: 'Include prioritized recommendations and improvement suggestions'
  },
  {
    id: 'includeImplementation',
    name: 'Implementation Plan',
    description: 'Include phases, timeline, and risk assessment'
  },
  {
    id: 'includeMetrics',
    name: 'Key Metrics',
    description: 'Include complexity, cost, and effort estimates'
  }
];

export default function ExportDialog({ data, trigger }: ExportDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [options, setOptions] = useState<ExportOptions>({
    format: 'pdf',
    includeDiagrams: true,
    includeCode: true,
    includeRecommendations: true,
    includeImplementation: true,
    includeMetrics: true
  });

  const handleExport = async () => {
    if (!selectedFormat) {
      toast.error('Please select an export format');
      return;
    }

    try {
      setIsExporting(true);
      
      const exportOptions: ExportOptions = {
        format: selectedFormat as any,
        includeDiagrams: options.includeDiagrams,
        includeCode: options.includeCode,
        includeRecommendations: options.includeRecommendations,
        includeImplementation: options.includeImplementation,
        includeMetrics: options.includeMetrics
      };

      let content: string | Blob;
      let filename: string;
      let mimeType: string;

      switch (selectedFormat) {
        case 'pdf':
          content = await ExportService.exportToPDF(data, exportOptions);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
          mimeType = 'application/pdf';
          break;
        case 'markdown':
          content = ExportService.exportToMarkdown(data, exportOptions);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.md`;
          mimeType = 'text/markdown';
          break;
        case 'html':
          content = ExportService.exportToHTML(data, exportOptions);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.html`;
          mimeType = 'text/html';
          break;
        case 'json':
          content = ExportService.exportToJSON(data, exportOptions);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
          mimeType = 'application/json';
          break;
        case 'plantuml':
          content = ExportService.exportToPlantUML(data);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.puml`;
          mimeType = 'text/plain';
          break;
        case 'mermaid':
          content = ExportService.exportToMermaid(data);
          filename = `${data.title.replace(/[^a-zA-Z0-9]/g, '_')}.md`;
          mimeType = 'text/markdown';
          break;
        default:
          throw new Error('Unsupported export format');
      }

      ExportService.downloadFile(content, filename, mimeType);
      toast.success(`Exported as ${selectedFormat.toUpperCase()}`);
      setIsOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const updateOption = (key: keyof ExportOptions, value: boolean) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  const selectedFormatInfo = exportFormats.find(f => f.id === selectedFormat);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <DownloadIcon className="h-4 w-4 mr-2" />
            Export
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Export Architecture Results</DialogTitle>
          <DialogDescription>
            Choose the format and content sections to include in your export
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Format Selection */}
          <div>
            <Label className="text-base font-medium mb-4 block">Export Format</Label>
            <RadioGroup value={selectedFormat} onValueChange={setSelectedFormat}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {exportFormats.map((format) => (
                  <div key={format.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                    <RadioGroupItem value={format.id} id={format.id} className="mt-1" />
                    <div className="flex-1">
                      <Label htmlFor={format.id} className="cursor-pointer">
                        <div className="flex items-center mb-2">
                          <div className={format.color}>{format.icon}</div>
                          <div className="ml-2">
                            <div className="font-medium">{format.name}</div>
                            <div className="text-sm text-slate-600">{format.description}</div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {format.features.map((feature, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </Label>
                    </div>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </div>

          {/* Content Sections */}
          <div>
            <Label className="text-base font-medium mb-4 block">Include Content</Label>
            <div className="space-y-3">
              {contentSections.map((section) => (
                <div key={section.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                  <Checkbox
                    id={section.id}
                    checked={options[section.id as keyof ExportOptions] as boolean}
                    onCheckedChange={(checked) => updateOption(section.id as keyof ExportOptions, checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor={section.id} className="cursor-pointer">
                      <div className="font-medium">{section.name}</div>
                      <div className="text-sm text-slate-600">{section.description}</div>
                    </Label>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Export Preview */}
          {selectedFormatInfo && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Format:</span>
                    <div className="flex items-center">
                      <div className={selectedFormatInfo.color}>{selectedFormatInfo.icon}</div>
                      <span className="ml-2 font-medium">{selectedFormatInfo.name}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Content sections:</span>
                    <span className="text-sm font-medium">
                      {Object.values(options).filter(Boolean).length} of {contentSections.length} selected
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">File size:</span>
                    <span className="text-sm font-medium">~{selectedFormat === 'pdf' ? '2-5 MB' : '50-200 KB'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Export Actions */}
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleExport} 
              disabled={isExporting}
              className="min-w-[120px]"
            >
              {isExporting ? (
                <>
                  <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <DownloadIcon className="mr-2 h-4 w-4" />
                  Export
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
