'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
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
  BuildingIcon,
  FileTextIcon,
  GithubIcon,
  UploadIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  ZapIcon,
  ShieldIcon,
  GlobeIcon,
  DatabaseIcon,
  ServerIcon,
  BrainIcon,
  Loader2Icon
} from 'lucide-react';

interface ArchitectureInput {
  type: 'document' | 'description' | 'github';
  content: string;
  domain: string;
  complexity: string;
  constraints: string[];
}

const domains = [
  {
    id: 'cloud-native',
    name: 'Cloud Native',
    description: 'Modern cloud-based applications with microservices',
    icon: <GlobeIcon className="h-5 w-5" />,
    color: 'bg-blue-500',
    patterns: ['Microservices', 'API Gateway', 'Event-Driven', 'Serverless']
  },
  {
    id: 'data-platform',
    name: 'Data Platform',
    description: 'Data processing, analytics, and ML systems',
    icon: <DatabaseIcon className="h-5 w-5" />,
    color: 'bg-green-500',
    patterns: ['Data Pipeline', 'Stream Processing', 'ML Pipeline', 'Data Lake']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'Large-scale enterprise systems with compliance',
    icon: <BuildingIcon className="h-5 w-5" />,
    color: 'bg-purple-500',
    patterns: ['SOA', 'ESB', 'Security', 'Compliance']
  }
];

const complexityLevels = [
  {
    id: 'simple',
    name: 'Simple',
    description: 'Single service or small application',
    time: '5-10 minutes',
    features: ['Basic architecture', 'Simple diagrams', 'Technology stack']
  },
  {
    id: 'medium',
    name: 'Medium',
    description: 'Multi-service application with integrations',
    time: '10-20 minutes',
    features: ['Microservices design', 'API design', 'Database design', 'Security patterns']
  },
  {
    id: 'complex',
    name: 'Complex',
    description: 'Large-scale distributed system',
    time: '20-30 minutes',
    features: ['Full architecture', 'Multiple diagrams', 'Integration patterns', 'Scalability design']
  }
];

export default function NewArchitecturePage() {
  const router = useRouter();
  const [input, setInput] = useState<ArchitectureInput>({
    type: 'description',
    content: '',
    domain: 'cloud-native',
    complexity: 'medium',
    constraints: []
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('input');

  const handleSubmit = async () => {
    if (!input.content.trim()) {
      toast.error('Please provide requirements or description');
      return;
    }

    try {
      setIsProcessing(true);
      
      // Call the new simple modular architecture API
      const response = await apiClient.analyzeArchitecture({
        input_text: input.content,
        domain: input.domain,
        complexity: input.complexity
      });
      
      if (response.success) {
        // Store the results in localStorage for the results page
        localStorage.setItem('architectureResults', JSON.stringify(response.data));
        toast.success('Architecture design completed!');
        router.push('/architecture/results?type=new&domain=' + input.domain);
      } else {
        throw new Error(response.message || 'Architecture analysis failed');
      }
    } catch (error) {
      console.error('Failed to generate architecture:', error);
      toast.error('Failed to generate architecture. Please try again.');
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

  const selectedDomain = domains.find(d => d.id === input.domain);
  const selectedComplexity = complexityLevels.find(c => c.id === input.complexity);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            <BuildingIcon className="h-6 w-6 mr-2 text-blue-600" />
            Design New Architecture
          </h1>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="input">Provide Input</TabsTrigger>
            <TabsTrigger value="configure">Configure</TabsTrigger>
            <TabsTrigger value="review">Review & Generate</TabsTrigger>
          </TabsList>

          {/* Input Tab */}
          <TabsContent value="input" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>How would you like to provide your requirements?</CardTitle>
                  <CardDescription>
                    Choose the method that works best for your project
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <RadioGroup 
                    value={input.type} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, type: value as any }))}
                    className="space-y-4"
                  >
                    <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                      <RadioGroupItem value="description" id="description" className="mt-1" />
                      <div className="flex-1">
                        <Label htmlFor="description" className="flex items-center cursor-pointer">
                          <FileTextIcon className="h-5 w-5 mr-2 text-blue-600" />
                          <div>
                            <div className="font-medium">Describe Your Requirements</div>
                            <div className="text-sm text-slate-600">Write a detailed description of what you need to build</div>
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
                            <div className="font-medium">Upload Requirements Document</div>
                            <div className="text-sm text-slate-600">Upload a PDF, Word, or text document with your requirements</div>
                          </div>
                        </Label>
                      </div>
                    </div>

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
                  </RadioGroup>

                  {/* Input Content */}
                  {input.type === 'description' && (
                    <div className="space-y-2">
                      <Label htmlFor="description-content">Describe your requirements</Label>
                      <Textarea
                        id="description-content"
                        value={input.content}
                        onChange={(e) => setInput(prev => ({ ...prev, content: e.target.value }))}
                        placeholder="Describe what you need to build, including functional requirements, non-functional requirements, constraints, and any specific technologies or patterns you want to use..."
                        className="min-h-[200px]"
                      />
                    </div>
                  )}

                  {input.type === 'document' && (
                    <div className="space-y-2">
                      <Label htmlFor="file-upload">Upload your requirements document</Label>
                      <div 
                        className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-slate-400 transition-colors"
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add('border-blue-400', 'bg-blue-50');
                        }}
                        onDragLeave={(e) => {
                          e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
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
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Configure Tab */}
          <TabsContent value="configure" className="space-y-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Domain Selection */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Architecture Domain</CardTitle>
                  <CardDescription>Choose the type of system you're building</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup 
                    value={input.domain} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, domain: value }))}
                    className="space-y-4"
                  >
                    {domains.map((domain) => (
                      <div key={domain.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={domain.id} id={domain.id} className="mt-1" />
                        <div className="flex-1">
                          <Label htmlFor={domain.id} className="flex items-center cursor-pointer">
                            <div className={`p-2 rounded-lg ${domain.color} text-white mr-3`}>
                              {domain.icon}
                            </div>
                            <div>
                              <div className="font-medium">{domain.name}</div>
                              <div className="text-sm text-slate-600">{domain.description}</div>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {domain.patterns.map((pattern, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {pattern}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </Label>
                        </div>
                      </div>
                    ))}
                  </RadioGroup>
                </CardContent>
              </Card>

              {/* Complexity Selection */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Complexity Level</CardTitle>
                  <CardDescription>How complex is your system?</CardDescription>
                </CardHeader>
                <CardContent>
                  <RadioGroup 
                    value={input.complexity} 
                    onValueChange={(value) => setInput(prev => ({ ...prev, complexity: value }))}
                    className="space-y-4"
                  >
                    {complexityLevels.map((level) => (
                      <div key={level.id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={level.id} id={level.id} className="mt-1" />
                        <div className="flex-1">
                          <Label htmlFor={level.id} className="cursor-pointer">
                            <div className="flex items-center justify-between mb-2">
                              <div className="font-medium">{level.name}</div>
                              <div className="flex items-center text-sm text-slate-500">
                                <ClockIcon className="h-4 w-4 mr-1" />
                                {level.time}
                              </div>
                            </div>
                            <div className="text-sm text-slate-600 mb-2">{level.description}</div>
                            <div className="text-sm text-slate-500">
                              Includes: {level.features.join(', ')}
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
                  <CardDescription>Any specific requirements or limitations?</CardDescription>
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
                        placeholder="Add a constraint (e.g., 'Must use React', 'Budget under $10k')"
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
                  <CardTitle>Review Your Configuration</CardTitle>
                  <CardDescription>Verify your settings before generating the architecture</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Input Type</h4>
                      <div className="flex items-center space-x-2">
                        {input.type === 'description' && <FileTextIcon className="h-4 w-4 text-blue-600" />}
                        {input.type === 'document' && <UploadIcon className="h-4 w-4 text-green-600" />}
                        {input.type === 'github' && <GithubIcon className="h-4 w-4 text-purple-600" />}
                        <span className="capitalize">{input.type}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Domain</h4>
                      <div className="flex items-center space-x-2">
                        <div className={`p-1 rounded ${selectedDomain?.color} text-white`}>
                          {selectedDomain?.icon}
                        </div>
                        <span>{selectedDomain?.name}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Complexity</h4>
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-slate-500" />
                        <span>{selectedComplexity?.name} ({selectedComplexity?.time})</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-slate-900 mb-2">Constraints</h4>
                      <div className="text-sm text-slate-600">
                        {input.constraints.length > 0 ? input.constraints.join(', ') : 'None specified'}
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
                          Generating...
                        </>
                      ) : (
                        <>
                          <SparklesIcon className="mr-2 h-4 w-4" />
                          Generate Architecture
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
