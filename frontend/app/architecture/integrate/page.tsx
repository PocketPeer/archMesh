'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { 
  ArrowLeftIcon,
  LinkIcon,
  FileTextIcon,
  GithubIcon,
  UploadIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  BuildingIcon,
  Loader2Icon,
  ArrowRightIcon,
  ZapIcon,
  ShieldIcon,
  DatabaseIcon,
  GlobeIcon
} from 'lucide-react';

interface IntegrationInput {
  existingSystem: {
    type: 'github' | 'description' | 'document';
    content: string;
  };
  newRequirements: {
    type: 'description' | 'document';
    content: string;
  };
  integrationType: string;
  timeline: string;
  constraints: string[];
}

const integrationTypes = [
  {
    id: 'api-integration',
    name: 'API Integration',
    description: 'Connect new features via REST/GraphQL APIs',
    icon: <GlobeIcon className="h-5 w-5" />,
    color: 'bg-blue-500',
    complexity: 'Medium',
    time: '2-4 weeks'
  },
  {
    id: 'microservices',
    name: 'Microservices Integration',
    description: 'Add new microservices to existing architecture',
    icon: <BuildingIcon className="h-5 w-5" />,
    color: 'bg-purple-500',
    complexity: 'High',
    time: '4-8 weeks'
  },
  {
    id: 'data-integration',
    name: 'Data Integration',
    description: 'Integrate new data sources and processing',
    icon: <DatabaseIcon className="h-5 w-5" />,
    color: 'bg-green-500',
    complexity: 'Medium',
    time: '3-6 weeks'
  },
  {
    id: 'ui-integration',
    name: 'UI/UX Integration',
    description: 'Add new user interfaces to existing system',
    icon: <ZapIcon className="h-5 w-5" />,
    color: 'bg-orange-500',
    complexity: 'Low',
    time: '1-3 weeks'
  },
  {
    id: 'legacy-modernization',
    name: 'Legacy Modernization',
    description: 'Modernize legacy systems with new capabilities',
    icon: <ShieldIcon className="h-5 w-5" />,
    color: 'bg-red-500',
    complexity: 'High',
    time: '6-12 weeks'
  }
];

const timelines = [
  {
    id: 'urgent',
    name: 'Urgent (1-2 weeks)',
    description: 'Quick integration with minimal changes',
    features: ['Basic integration', 'Minimal testing', 'Quick deployment']
  },
  {
    id: 'standard',
    name: 'Standard (1-2 months)',
    description: 'Thorough integration with proper testing',
    features: ['Comprehensive integration', 'Full testing', 'Proper documentation']
  },
  {
    id: 'extended',
    name: 'Extended (3+ months)',
    description: 'Complex integration with extensive planning',
    features: ['Complex integration', 'Extensive testing', 'Migration planning', 'Risk mitigation']
  }
];

export default function IntegrationPlanningPage() {
  const router = useRouter();
  const [input, setInput] = useState<IntegrationInput>({
    existingSystem: {
      type: 'github',
      content: ''
    },
    newRequirements: {
      type: 'description',
      content: ''
    },
    integrationType: 'api-integration',
    timeline: 'standard',
    constraints: []
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('existing');

  const handleSubmit = async () => {
    if (!input.existingSystem.content.trim() || !input.newRequirements.content.trim()) {
      toast.error('Please provide both existing system and new requirements');
      return;
    }

    try {
      setIsProcessing(true);
      
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 4000));
      
      toast.success('Integration plan completed!');
      router.push('/architecture/results?type=integrate&integration=' + input.integrationType);
    } catch (error) {
      console.error('Failed to generate integration plan:', error);
      toast.error('Failed to generate integration plan. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, type: 'existing' | 'new') => {
    const file = event.target.files?.[0];
    if (file) {
      const content = `Uploaded file: ${file.name}`;
      if (type === 'existing') {
        setInput(prev => ({ 
          ...prev, 
          existingSystem: { ...prev.existingSystem, content } 
        }));
      } else {
        setInput(prev => ({ 
          ...prev, 
          newRequirements: { ...prev.newRequirements, content } 
        }));
      }
      toast.success('File uploaded successfully');
    }
  };

  const addConstraint = (constraint: string) => {
    if (constraint.trim() && !input.constraints.includes(constraint)) {
      setInput(prev => ({ ...prev, constraints: [...prev.constraints, constraint] }));
    }
  };

  const removeConstraint = (index: number) => {
    setInput(prev => ({ 
      ...prev, 
      constraints: prev.constraints.filter((_, i) => i !== index) 
    }));
  };

  const selectedIntegrationType = integrationTypes.find(t => t.id === input.integrationType);
  const selectedTimeline = timelines.find(t => t.id === input.timeline);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-green-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            <LinkIcon className="h-6 w-6 mr-2 text-green-600" />
            Plan System Integration
          </h1>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="existing">Existing System</TabsTrigger>
            <TabsTrigger value="new">New Requirements</TabsTrigger>
            <TabsTrigger value="configure">Configure Integration</TabsTrigger>
            <TabsTrigger value="review">Review & Plan</TabsTrigger>
          </TabsList>

          {/* Existing System Tab */}
          <TabsContent value="existing" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>Describe Your Existing System</CardTitle>
                  <CardDescription>
                    Provide information about your current system architecture
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <RadioGroup 
                    value={input.existingSystem.type} 
                    onValueChange={(value) => setInput(prev => ({ 
                      ...prev, 
                      existingSystem: { ...prev.existingSystem, type: value as any } 
                    }))}
                    className="space-y-4"
                  >
                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="github" id="existing-github" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="existing-github" className="flex items-center cursor-pointer">
                          <GithubIcon className="h-5 w-5 mr-2 text-purple-600" />
                          <div>
                            <div className="font-medium">Connect to GitHub Repository</div>
                            <div className="text-sm text-slate-600">Analyze existing codebase to understand current architecture</div>
                          </div>
                        </Label>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="description" id="existing-description" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="existing-description" className="flex items-center cursor-pointer">
                          <FileTextIcon className="h-5 w-5 mr-2 text-blue-600" />
                          <div>
                            <div className="font-medium">Describe Your Current System</div>
                            <div className="text-sm text-slate-600">Provide a detailed description of your existing architecture</div>
                          </div>
                        </Label>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="document" id="existing-document" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="existing-document" className="flex items-center cursor-pointer">
                          <UploadIcon className="h-5 w-5 mr-2 text-green-600" />
                          <div>
                            <div className="font-medium">Upload Architecture Document</div>
                            <div className="text-sm text-slate-600">Upload existing architecture documentation</div>
                          </div>
                        </Label>
                      </div>
                    </div>
                  </RadioGroup>

                  {/* Input Content */}
                  {input.existingSystem.type === 'github' && (
                    <div className="space-y-2">
                      <Label htmlFor="existing-github-url">GitHub Repository URL</Label>
                      <Input
                        id="existing-github-url"
                        value={input.existingSystem.content}
                        onChange={(e) => setInput(prev => ({ 
                          ...prev, 
                          existingSystem: { ...prev.existingSystem, content: e.target.value } 
                        }))}
                        placeholder="https://github.com/username/repository"
                        className="font-mono"
                      />
                    </div>
                  )}

                  {input.existingSystem.type === 'description' && (
                    <div className="space-y-2">
                      <Label htmlFor="existing-description-content">Describe your existing system</Label>
                      <Textarea
                        id="existing-description-content"
                        value={input.existingSystem.content}
                        onChange={(e) => setInput(prev => ({ 
                          ...prev, 
                          existingSystem: { ...prev.existingSystem, content: e.target.value } 
                        }))}
                        placeholder="Describe your current system architecture, including components, technologies, integrations, APIs, databases, and any relevant details..."
                        className="min-h-[200px]"
                      />
                    </div>
                  )}

                  {input.existingSystem.type === 'document' && (
                    <div className="space-y-2">
                      <Label htmlFor="existing-file-upload">Upload your existing architecture document</Label>
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                        <UploadIcon className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-sm text-slate-600 mb-2">Drop your file here or click to browse</p>
                        <input
                          id="existing-file-upload"
                          type="file"
                          accept=".pdf,.doc,.docx,.txt"
                          onChange={(e) => handleFileUpload(e, 'existing')}
                          className="hidden"
                        />
                        <Button variant="outline" size="sm" onClick={() => document.getElementById('existing-file-upload')?.click()}>
                          Choose File
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* New Requirements Tab */}
          <TabsContent value="new" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>Describe New Requirements</CardTitle>
                  <CardDescription>
                    What new features or capabilities do you want to integrate?
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <RadioGroup 
                    value={input.newRequirements.type} 
                    onValueChange={(value) => setInput(prev => ({ 
                      ...prev, 
                      newRequirements: { ...prev.newRequirements, type: value as any } 
                    }))}
                    className="space-y-4"
                  >
                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="description" id="new-description" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="new-description" className="flex items-center cursor-pointer">
                          <FileTextIcon className="h-5 w-5 mr-2 text-blue-600" />
                          <div>
                            <div className="font-medium">Describe New Requirements</div>
                            <div className="text-sm text-slate-600">Write a detailed description of what you want to add</div>
                          </div>
                        </Label>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="document" id="new-document" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="new-document" className="flex items-center cursor-pointer">
                          <UploadIcon className="h-5 w-5 mr-2 text-green-600" />
                          <div>
                            <div className="font-medium">Upload Requirements Document</div>
                            <div className="text-sm text-slate-600">Upload a document with your new requirements</div>
                          </div>
                        </Label>
                      </div>
                    </div>
                  </RadioGroup>

                  {/* Input Content */}
                  {input.newRequirements.type === 'description' && (
                    <div className="space-y-2">
                      <Label htmlFor="new-description-content">Describe your new requirements</Label>
                      <Textarea
                        id="new-description-content"
                        value={input.newRequirements.content}
                        onChange={(e) => setInput(prev => ({ 
                          ...prev, 
                          newRequirements: { ...prev.newRequirements, content: e.target.value } 
                        }))}
                        placeholder="Describe the new features, capabilities, or requirements you want to integrate into your existing system. Include functional requirements, non-functional requirements, and any specific constraints..."
                        className="min-h-[200px]"
                      />
                    </div>
                  )}

                  {input.newRequirements.type === 'document' && (
                    <div className="space-y-2">
                      <Label htmlFor="new-file-upload">Upload your new requirements document</Label>
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                        <UploadIcon className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-sm text-slate-600 mb-2">Drop your file here or click to browse</p>
                        <input
                          id="new-file-upload"
                          type="file"
                          accept=".pdf,.doc,.docx,.txt"
                          onChange={(e) => handleFileUpload(e, 'new')}
                          className="hidden"
                        />
                        <Button variant="outline" size="sm" onClick={() => document.getElementById('new-file-upload')?.click()}>
                          Choose File
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Configure Tab */}
          <TabsContent value="configure" className="space-y-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Integration Type */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Integration Type</CardTitle>
                  <CardDescription>What type of integration are you planning?</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup 
                    value={input.integrationType} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, integrationType: value }))}
                    className="space-y-4"
                  >
                    {integrationTypes.map((type) => (
                      <div key={type.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={type.id} id={type.id} className="mt-1" />
                        <div className="flex-1">
                          <Label htmlFor={type.id} className="flex items-center cursor-pointer">
                            <div className={`p-2 rounded-lg ${type.color} text-white mr-3`}>
                              {type.icon}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <div className="font-medium">{type.name}</div>
                                <div className="flex items-center space-x-2 text-sm text-slate-500">
                                  <Badge variant="outline" className="text-xs">{type.complexity}</Badge>
                                  <span>{type.time}</span>
                                </div>
                              </div>
                              <div className="text-sm text-slate-600">{type.description}</div>
                            </div>
                          </Label>
                        </div>
                      </div>
                    ))}
                  </RadioGroup>
                </CardContent>
              </Card>

              {/* Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Timeline</CardTitle>
                  <CardDescription>How much time do you have for this integration?</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup 
                    value={input.timeline} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, timeline: value }))}
                    className="space-y-4"
                  >
                    {timelines.map((timeline) => (
                      <div key={timeline.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={timeline.id} id={timeline.id} className="mt-1" />
                        <div className="flex-1">
                          <Label htmlFor={timeline.id} className="cursor-pointer">
                            <div className="flex items-center justify-between mb-2">
                              <div className="font-medium">{timeline.name}</div>
                              <div className="flex items-center text-sm text-slate-500">
                                <ClockIcon className="h-4 w-4 mr-1" />
                                {timeline.description.split('(')[1]?.replace(')', '')}
                              </div>
                            </div>
                            <div className="text-sm text-slate-600 mb-2">{timeline.description}</div>
                            <div className="text-sm text-slate-500">
                              Includes: {timeline.features.join(', ')}
                            </div>
                          </Label>
                        </div>
                      </div>
                    ))}
                  </RadioGroup>
                </CardContent>
              </Card>

              {/* Constraints */}
              <Card>
                <CardHeader>
                  <CardTitle>Additional Constraints</CardTitle>
                  <CardDescription>Any specific requirements or limitations for the integration?</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      {input.constraints.map((constraint, index) => (
                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                          {constraint}
                          <button
                            onClick={() => removeConstraint(index)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Add a constraint (e.g., 'Must maintain backward compatibility', 'Budget under $50k')"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            addConstraint(e.currentTarget.value);
                            e.currentTarget.value = '';
                          }
                        }}
                      />
                      <Button variant="outline" onClick={() => {
                        const input = document.querySelector('input[placeholder*="constraint"]') as HTMLInputElement;
                        if (input?.value) {
                          addConstraint(input.value);
                          input.value = '';
                        }
                      }}>
                        Add
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Review Tab */}
          <TabsContent value="review" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>Review Your Integration Plan</CardTitle>
                  <CardDescription>Verify your settings before generating the integration plan</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Existing System</h4>
                      <div className="flex items-center space-x-2">
                        {input.existingSystem.type === 'github' && <GithubIcon className="h-4 w-4 text-purple-600" />}
                        {input.existingSystem.type === 'description' && <FileTextIcon className="h-4 w-4 text-blue-600" />}
                        {input.existingSystem.type === 'document' && <UploadIcon className="h-4 w-4 text-green-600" />}
                        <span className="capitalize">{input.existingSystem.type}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">New Requirements</h4>
                      <div className="flex items-center space-x-2">
                        {input.newRequirements.type === 'description' && <FileTextIcon className="h-4 w-4 text-blue-600" />}
                        {input.newRequirements.type === 'document' && <UploadIcon className="h-4 w-4 text-green-600" />}
                        <span className="capitalize">{input.newRequirements.type}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Integration Type</h4>
                      <div className="flex items-center space-x-2">
                        <div className={`p-1 rounded ${selectedIntegrationType?.color} text-white`}>
                          {selectedIntegrationType?.icon}
                        </div>
                        <span>{selectedIntegrationType?.name}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Timeline</h4>
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-slate-500" />
                        <span>{selectedTimeline?.name}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-slate-900 mb-2">Constraints</h4>
                    <div className="text-sm text-slate-600">
                      {input.constraints.length > 0 ? input.constraints.join(', ') : 'None specified'}
                    </div>
                  </div>

                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <ArrowRightIcon className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-green-900">What You'll Get</h4>
                        <p className="text-sm text-green-800 mt-1">
                          A comprehensive integration plan including architecture design, implementation strategy, 
                          migration roadmap, risk assessment, and detailed timeline with milestones.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-4">
                    <Button variant="outline" onClick={() => setActiveTab('configure')}>
                      Back to Configure
                    </Button>
                    <Button 
                      onClick={handleSubmit} 
                      disabled={isProcessing || !input.existingSystem.content.trim() || !input.newRequirements.content.trim()}
                      className="min-w-[160px]"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
                          Planning...
                        </>
                      ) : (
                        <>
                          <LinkIcon className="mr-2 h-4 w-4" />
                          Generate Plan
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
