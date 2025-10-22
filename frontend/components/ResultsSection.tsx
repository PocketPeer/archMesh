'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileTextIcon, 
  BuildingIcon, 
  DownloadIcon, 
  RefreshCwIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  EyeIcon,
  ShareIcon
} from 'lucide-react';
import RefinementButton, { QualityIndicator } from '@/components/RefinementButton';
import ArchitectureDiagrams from '@/components/ArchitectureDiagrams';

interface ResultsSectionProps {
  workflowResults: {
    requirements: any;
    architecture: any;
  } | null;
  projectId: string;
  onRefine: (type: string) => void;
  onExport: (type: string) => void;
  onShare: (type: string) => void;
}

export default function ResultsSection({ 
  workflowResults, 
  projectId, 
  onRefine, 
  onExport, 
  onShare 
}: ResultsSectionProps) {
  const [activeTab, setActiveTab] = useState('requirements');

  const hasResults = workflowResults && (workflowResults.requirements || workflowResults.architecture);

  if (!hasResults) {
    return (
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileTextIcon className="h-5 w-5 text-slate-600" />
            <span>Results & Outputs</span>
          </CardTitle>
          <CardDescription>
            Generated requirements and architecture will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <FileTextIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">No Results Yet</h3>
            <p className="text-slate-600 mb-6">
              Complete a workflow to see requirements analysis and architecture designs
            </p>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              Start Workflow
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileTextIcon className="h-5 w-5 text-slate-600" />
          <span>Results & Outputs</span>
        </CardTitle>
        <CardDescription>
          Generated requirements analysis and architecture designs
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="requirements" className="flex items-center space-x-2">
              <FileTextIcon className="h-4 w-4" />
              <span>Requirements</span>
            </TabsTrigger>
            <TabsTrigger value="architecture" className="flex items-center space-x-2">
              <BuildingIcon className="h-4 w-4" />
              <span>Architecture</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center space-x-2">
              <DownloadIcon className="h-4 w-4" />
              <span>Documents</span>
            </TabsTrigger>
          </TabsList>

          {/* Requirements Tab */}
          <TabsContent value="requirements" className="mt-6">
            {workflowResults?.requirements ? (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Requirements Analysis</h3>
                  <div className="flex items-center space-x-2">
                    <QualityIndicator quality={0.75} />
                    <RefinementButton
                      workflowId=""
                      projectId={projectId}
                      currentQuality={0.75}
                      onRefinementComplete={(result) => {
                        console.log('Requirements refined:', result);
                      }}
                      variant="outline"
                      size="sm"
                    />
                  </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h4 className="font-semibold text-slate-900 mb-3">Functional Requirements</h4>
                    <div className="space-y-2">
                      {workflowResults.requirements.functional_requirements?.map((req: any, index: number) => (
                        <div key={index} className="flex items-start space-x-2">
                          <CheckCircleIcon className="h-4 w-4 text-green-600 mt-1 flex-shrink-0" />
                          <span className="text-sm text-slate-700">{req}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h4 className="font-semibold text-slate-900 mb-3">Non-Functional Requirements</h4>
                    <div className="space-y-2">
                      {workflowResults.requirements.non_functional_requirements?.map((req: any, index: number) => (
                        <div key={index} className="flex items-start space-x-2">
                          <AlertCircleIcon className="h-4 w-4 text-orange-600 mt-1 flex-shrink-0" />
                          <span className="text-sm text-slate-700">{req}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center space-x-4">
                    <Button variant="outline" size="sm" onClick={() => onExport('requirements')}>
                      <DownloadIcon className="h-4 w-4 mr-1" />
                      Export
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => onShare('requirements')}>
                      <ShareIcon className="h-4 w-4 mr-1" />
                      Share
                    </Button>
                  </div>
                  <Badge variant="outline" className="text-green-600 border-green-300">
                    <CheckCircleIcon className="h-3 w-3 mr-1" />
                    Analysis Complete
                  </Badge>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <FileTextIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No Requirements Yet</h3>
                <p className="text-slate-600">Requirements analysis will appear here after workflow completion</p>
              </div>
            )}
          </TabsContent>

          {/* Architecture Tab */}
          <TabsContent value="architecture" className="mt-6">
            {workflowResults?.architecture ? (
              <ArchitectureDiagrams 
                architecture={workflowResults.architecture} 
                projectId={projectId} 
              />
            ) : (
              <div className="text-center py-8">
                <BuildingIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No Architecture Yet</h3>
                <p className="text-slate-600">Architecture designs will appear here after workflow completion</p>
              </div>
            )}
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="mt-6">
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Card className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-slate-900">Requirements Document</h4>
                      <Badge variant="outline">PDF</Badge>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">
                      Comprehensive requirements analysis document
                    </p>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" onClick={() => onExport('requirements-doc')}>
                        <DownloadIcon className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => onShare('requirements-doc')}>
                        <ShareIcon className="h-4 w-4 mr-1" />
                        Share
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-slate-900">Architecture Document</h4>
                      <Badge variant="outline">PDF</Badge>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">
                      System architecture and design documentation
                    </p>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" onClick={() => onExport('architecture-doc')}>
                        <DownloadIcon className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => onShare('architecture-doc')}>
                        <ShareIcon className="h-4 w-4 mr-1" />
                        Share
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="p-4 bg-slate-50 rounded-lg">
                <h4 className="font-medium text-slate-900 mb-2">Export All</h4>
                <p className="text-sm text-slate-600 mb-3">
                  Download all project documents and diagrams as a complete package
                </p>
                <Button onClick={() => onExport('all')}>
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  Export Complete Package
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
