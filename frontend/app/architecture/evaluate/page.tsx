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
  SearchIcon,
  FileTextIcon,
  GithubIcon,
  UploadIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  BuildingIcon,
  Loader2Icon,
  EyeIcon,
  BarChart3Icon,
  ShieldIcon,
  ZapIcon
} from 'lucide-react';

interface EvaluationInput {
  type: 'github' | 'description' | 'document';
  content: string;
  focusAreas: string[];
  evaluationDepth: string;
}

const focusAreas = [
  {
    id: 'performance',
    name: 'Performance',
    description: 'Scalability, response times, resource utilization',
    icon: <ZapIcon className="h-5 w-5" />,
    color: 'text-blue-600'
  },
  {
    id: 'security',
    name: 'Security',
    description: 'Authentication, authorization, data protection',
    icon: <ShieldIcon className="h-5 w-5" />,
    color: 'text-red-600'
  },
  {
    id: 'maintainability',
    name: 'Maintainability',
    description: 'Code quality, documentation, testing',
    icon: <FileTextIcon className="h-5 w-5" />,
    color: 'text-green-600'
  },
  {
    id: 'scalability',
    name: 'Scalability',
    description: 'Horizontal scaling, load handling, growth capacity',
    icon: <BarChart3Icon className="h-5 w-5" />,
    color: 'text-purple-600'
  },
  {
    id: 'reliability',
    name: 'Reliability',
    description: 'Fault tolerance, error handling, monitoring',
    icon: <CheckCircleIcon className="h-5 w-5" />,
    color: 'text-orange-600'
  },
  {
    id: 'cost',
    name: 'Cost Optimization',
    description: 'Resource efficiency, cloud costs, operational expenses',
    icon: <BuildingIcon className="h-5 w-5" />,
    color: 'text-yellow-600'
  }
];

const evaluationDepths = [
  {
    id: 'quick',
    name: 'Quick Assessment',
    description: 'High-level overview with key recommendations',
    time: '5-10 minutes',
    features: ['Basic analysis', 'Key issues identified', 'Top 3 recommendations']
  },
  {
    id: 'standard',
    name: 'Standard Evaluation',
    description: 'Comprehensive analysis with detailed findings',
    time: '10-20 minutes',
    features: ['Detailed analysis', 'All issues identified', 'Detailed recommendations', 'Priority ranking']
  },
  {
    id: 'deep',
    name: 'Deep Analysis',
    description: 'Thorough evaluation with implementation roadmap',
    time: '20-30 minutes',
    features: ['Comprehensive analysis', 'Root cause analysis', 'Implementation roadmap', 'Risk assessment']
  }
];

export default function EvaluateArchitecturePage() {
  const router = useRouter();
  const [input, setInput] = useState<EvaluationInput>({
    type: 'github',
    content: '',
    focusAreas: ['performance', 'security'],
    evaluationDepth: 'standard'
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('input');

  const handleSubmit = async () => {
    if (!input.content.trim()) {
      toast.error('Please provide architecture information to evaluate');
      return;
    }

    try {
      setIsProcessing(true);
      
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      toast.success('Architecture evaluation completed!');
      router.push('/architecture/results?type=evaluate&focus=' + input.focusAreas.join(','));
    } catch (error) {
      console.error('Failed to evaluate architecture:', error);
      toast.error('Failed to evaluate architecture. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        // Check file type
        const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
          toast.error('Please upload a PDF, Word document, or text file');
          return;
        }

        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          toast.error('File size must be less than 10MB');
          return;
        }

        // Read file content
        const content = await readFileContent(file);
        setInput(prev => ({ ...prev, content }));
        toast.success('File uploaded and processed successfully');
      } catch (error) {
        console.error('Error reading file:', error);
        toast.error('Failed to read file. Please try again.');
      }
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };
      
      // Read as text for now (could be enhanced to handle PDFs properly)
      reader.readAsText(file);
    });
  };

  const toggleFocusArea = (areaId: string) => {
    setInput(prev => ({
      ...prev,
      focusAreas: prev.focusAreas.includes(areaId)
        ? prev.focusAreas.filter(id => id !== areaId)
        : [...prev.focusAreas, areaId]
    }));
  };

  const selectedFocusAreas = focusAreas.filter(area => input.focusAreas.includes(area.id));
  const selectedDepth = evaluationDepths.find(d => d.id === input.evaluationDepth);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            <SearchIcon className="h-6 w-6 mr-2 text-purple-600" />
            Evaluate Existing Architecture
          </h1>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="input">Provide Architecture</TabsTrigger>
            <TabsTrigger value="configure">Configure Analysis</TabsTrigger>
            <TabsTrigger value="review">Review & Evaluate</TabsTrigger>
          </TabsList>

          {/* Input Tab */}
          <TabsContent value="input" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>How would you like to provide your architecture?</CardTitle>
                  <CardDescription>
                    Choose the method that works best for your evaluation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <RadioGroup 
                    value={input.type} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, type: value as any }))}
                    className="space-y-4"
                  >
                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="github" id="github" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="github" className="flex items-center cursor-pointer">
                          <GithubIcon className="h-5 w-5 mr-2 text-purple-600" />
                          <div>
                            <div className="font-medium">Connect to GitHub Repository</div>
                            <div className="text-sm text-slate-600">Analyze existing codebase to understand current architecture</div>
                          </div>
                        </Label>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="description" id="description" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="description" className="flex items-center cursor-pointer">
                          <FileTextIcon className="h-5 w-5 mr-2 text-blue-600" />
                          <div>
                            <div className="font-medium">Describe Your Architecture</div>
                            <div className="text-sm text-slate-600">Provide a detailed description of your current system</div>
                          </div>
                        </Label>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="document" id="document" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="document" className="flex items-center cursor-pointer">
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
                  {input.type === 'github' && (
                    <div className="space-y-2">
                      <Label htmlFor="github-url">GitHub Repository URL</Label>
                      <Input
                        id="github-url"
                        value={input.content}
                        onChange={(e) => setInput(prev => ({ ...prev, content: e.target.value }))}
                        placeholder="https://github.com/username/repository"
                        className="font-mono"
                      />
                    </div>
                  )}

                  {input.type === 'description' && (
                    <div className="space-y-2">
                      <Label htmlFor="description-content">Describe your current architecture</Label>
                      <Textarea
                        id="description-content"
                        value={input.content}
                        onChange={(e) => setInput(prev => ({ ...prev, content: e.target.value }))}
                        placeholder="Describe your current system architecture, including components, technologies, integrations, and any known issues or concerns..."
                        className="min-h-[200px]"
                      />
                    </div>
                  )}

                  {input.type === 'document' && (
                    <div className="space-y-2">
                      <Label htmlFor="file-upload">Upload your architecture document</Label>
                      <div 
                        className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-slate-400 transition-colors"
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add('border-purple-400', 'bg-purple-50');
                        }}
                        onDragLeave={(e) => {
                          e.currentTarget.classList.remove('border-purple-400', 'bg-purple-50');
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove('border-purple-400', 'bg-purple-50');
                          const files = e.dataTransfer.files;
                          if (files.length > 0) {
                            const event = { target: { files } } as React.ChangeEvent<HTMLInputElement>;
                            handleFileUpload(event);
                          }
                        }}
                      >
                        <UploadIcon className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-sm text-slate-600 mb-2">Drop your file here or click to browse</p>
                        <p className="text-xs text-slate-500 mb-4">Supported formats: PDF, Word (.doc, .docx), Text (.txt)</p>
                        <input
                          id="file-upload"
                          type="file"
                          accept=".pdf,.doc,.docx,.txt"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                        <Button variant="outline" size="sm" onClick={() => document.getElementById('file-upload')?.click()}>
                          Choose File
                        </Button>
                      </div>
                      {input.content && input.content.startsWith('Uploaded file:') && (
                        <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <div className="flex items-center text-green-700">
                            <CheckCircleIcon className="h-4 w-4 mr-2" />
                            <span className="text-sm font-medium">File uploaded successfully</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Configure Tab */}
          <TabsContent value="configure" className="space-y-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Focus Areas */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Focus Areas</CardTitle>
                  <CardDescription>What aspects of your architecture would you like to evaluate?</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {focusAreas.map((area) => (
                      <div 
                        key={area.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-all ${
                          input.focusAreas.includes(area.id) 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                        onClick={() => toggleFocusArea(area.id)}
                      >
                        <div className="flex items-start space-x-3">
                          <div className={`${area.color} mt-1`}>
                            {area.icon}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium">{area.name}</h4>
                              {input.focusAreas.includes(area.id) && (
                                <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                              )}
                            </div>
                            <p className="text-sm text-slate-600 mt-1">{area.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Evaluation Depth */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Evaluation Depth</CardTitle>
                  <CardDescription>How thorough should the analysis be?</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup 
                    value={input.evaluationDepth} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, evaluationDepth: value }))}
                    className="space-y-4"
                  >
                    {evaluationDepths.map((depth) => (
                      <div key={depth.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={depth.id} id={depth.id} className="mt-1" />
                        <div className="flex-1">
                          <Label htmlFor={depth.id} className="cursor-pointer">
                            <div className="flex items-center justify-between mb-2">
                              <div className="font-medium">{depth.name}</div>
                              <div className="flex items-center text-sm text-slate-500">
                                <ClockIcon className="h-4 w-4 mr-1" />
                                {depth.time}
                              </div>
                            </div>
                            <div className="text-sm text-slate-600 mb-2">{depth.description}</div>
                            <div className="text-sm text-slate-500">
                              Includes: {depth.features.join(', ')}
                            </div>
                          </Label>
                        </div>
                      </div>
                    ))}
                  </RadioGroup>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Review Tab */}
          <TabsContent value="review" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>Review Your Evaluation Settings</CardTitle>
                  <CardDescription>Verify your settings before starting the evaluation</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Input Type</h4>
                      <div className="flex items-center space-x-2">
                        {input.type === 'github' && <GithubIcon className="h-4 w-4 text-purple-600" />}
                        {input.type === 'description' && <FileTextIcon className="h-4 w-4 text-blue-600" />}
                        {input.type === 'document' && <UploadIcon className="h-4 w-4 text-green-600" />}
                        <span className="capitalize">{input.type}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Evaluation Depth</h4>
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-slate-500" />
                        <span>{selectedDepth?.name} ({selectedDepth?.time})</span>
                      </div>
                    </div>

                    <div className="md:col-span-2">
                      <h4 className="font-medium text-slate-900 mb-2">Focus Areas</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedFocusAreas.map((area) => (
                          <Badge key={area.id} variant="outline" className="flex items-center gap-1">
                            <div className={area.color}>{area.icon}</div>
                            {area.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  {input.content && (
                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Content Preview</h4>
                      <div className="bg-slate-50 p-4 rounded-lg text-sm text-slate-700 max-h-32 overflow-y-auto">
                        {input.content.length > 200 ? input.content.substring(0, 200) + '...' : input.content}
                      </div>
                    </div>
                  )}

                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <EyeIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900">What to Expect</h4>
                        <p className="text-sm text-blue-800 mt-1">
                          You'll receive a comprehensive evaluation report with identified issues, 
                          improvement recommendations, and prioritized action items based on your selected focus areas.
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
                      disabled={isProcessing || !input.content.trim()}
                      className="min-w-[160px]"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
                          Evaluating...
                        </>
                      ) : (
                        <>
                          <SearchIcon className="mr-2 h-4 w-4" />
                          Start Evaluation
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
