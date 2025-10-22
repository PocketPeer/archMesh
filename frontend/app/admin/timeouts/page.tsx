"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Save, Clock, CheckCircle, XCircle } from "lucide-react";
import { toast } from "sonner";

interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  status: string;
  timeout_seconds: number;
  max_tokens: number;
  temperature: number;
  cost_per_1k_tokens: {
    prompt: number;
    completion: number;
  };
}

export default function AdminTimeoutsPage() {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<{ [key: string]: boolean }>({});
  const [timeouts, setTimeouts] = useState<{ [key: string]: number }>({});
  const [error, setError] = useState<string | null>(null);

  // Mock data for now since admin endpoints aren't working
  const mockModels: ModelConfig[] = [
    {
      id: "deepseek-r1",
      name: "DeepSeek R1 (Local)",
      provider: "deepseek",
      status: "active",
      timeout_seconds: 300,
      max_tokens: 4000,
      temperature: 0.3,
      cost_per_1k_tokens: { prompt: 0.0, completion: 0.0 }
    },
    {
      id: "gpt-4o-mini",
      name: "GPT-4o Mini",
      provider: "openai",
      status: "active",
      timeout_seconds: 30,
      max_tokens: 4000,
      temperature: 0.3,
      cost_per_1k_tokens: { prompt: 0.00015, completion: 0.0006 }
    },
    {
      id: "gpt-4o",
      name: "GPT-4o",
      provider: "openai",
      status: "active",
      timeout_seconds: 30,
      max_tokens: 4000,
      temperature: 0.3,
      cost_per_1k_tokens: { prompt: 0.005, completion: 0.015 }
    },
    {
      id: "claude-3-sonnet-20240229",
      name: "Claude 3 Sonnet",
      provider: "anthropic",
      status: "active",
      timeout_seconds: 30,
      max_tokens: 4000,
      temperature: 0.3,
      cost_per_1k_tokens: { prompt: 0.003, completion: 0.015 }
    },
    {
      id: "llama3.2-3b",
      name: "Llama 3.2 3B",
      provider: "ollama",
      status: "active",
      timeout_seconds: 60,
      max_tokens: 4000,
      temperature: 0.3,
      cost_per_1k_tokens: { prompt: 0.0, completion: 0.0 }
    }
  ];

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let modelsData: ModelConfig[] = [];
      
      // Try to fetch from API first
      const response = await fetch('/api/v1/models');
      if (response.ok) {
        const data = await response.json();
        modelsData = data.models || [];
        setModels(modelsData);
      } else {
        // Fallback to mock data
        console.log('Admin API not available, using mock data');
        modelsData = mockModels;
        setModels(modelsData);
      }
      
      // Initialize timeouts
      const initialTimeouts: { [key: string]: number } = {};
      modelsData.forEach((model: ModelConfig) => {
        initialTimeouts[model.id] = model.timeout_seconds;
      });
      setTimeouts(initialTimeouts);
      
    } catch (err) {
      console.error('Failed to load models:', err);
      setError('Failed to load model configurations');
      setModels(mockModels);
      
      // Initialize timeouts with mock data
      const initialTimeouts: { [key: string]: number } = {};
      mockModels.forEach((model: ModelConfig) => {
        initialTimeouts[model.id] = model.timeout_seconds;
      });
      setTimeouts(initialTimeouts);
    } finally {
      setLoading(false);
    }
  };

  const updateTimeout = async (modelId: string, newTimeout: number) => {
    try {
      setSaving(prev => ({ ...prev, [modelId]: true }));
      
      const response = await fetch(`/api/v1/models/${modelId}/timeout`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ timeout_seconds: newTimeout }),
      });

      if (response.ok) {
        setTimeouts(prev => ({ ...prev, [modelId]: newTimeout }));
        toast.success(`Timeout updated for ${models.find(m => m.id === modelId)?.name}`);
      } else {
        throw new Error(`Failed to update timeout: ${response.statusText}`);
      }
    } catch (err) {
      console.error('Failed to update timeout:', err);
      toast.error(`Failed to update timeout for ${models.find(m => m.id === modelId)?.name}`);
    } finally {
      setSaving(prev => ({ ...prev, [modelId]: false }));
    }
  };

  const handleTimeoutChange = (modelId: string, value: string) => {
    const timeout = parseInt(value);
    if (!isNaN(timeout) && timeout > 0) {
      setTimeouts(prev => ({ ...prev, [modelId]: timeout }));
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case 'openai': return 'bg-green-100 text-green-800';
      case 'anthropic': return 'bg-purple-100 text-purple-800';
      case 'deepseek': return 'bg-blue-100 text-blue-800';
      case 'ollama': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading model configurations...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Model Timeout Configuration</h1>
          <p className="text-muted-foreground mt-2">
            Configure timeout settings for different LLM models
          </p>
        </div>
      </div>

      {error && (
        <Alert>
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6">
        {models.map((model) => (
          <Card key={model.id} className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(model.status)}
                  <div>
                    <CardTitle className="text-lg">{model.name}</CardTitle>
                    <CardDescription>
                      Model ID: {model.id} • Provider: {model.provider}
                    </CardDescription>
                  </div>
                </div>
                <Badge className={getProviderColor(model.provider)}>
                  {model.provider.toUpperCase()}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor={`timeout-${model.id}`}>Timeout (seconds)</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      id={`timeout-${model.id}`}
                      type="number"
                      min="1"
                      max="3600"
                      value={timeouts[model.id] || model.timeout_seconds}
                      onChange={(e) => handleTimeoutChange(model.id, e.target.value)}
                      className="w-24"
                    />
                    <Button
                      size="sm"
                      onClick={() => updateTimeout(model.id, timeouts[model.id] || model.timeout_seconds)}
                      disabled={saving[model.id]}
                    >
                      {saving[model.id] ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Max Tokens</Label>
                  <div className="text-sm text-muted-foreground">
                    {model.max_tokens.toLocaleString()}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Temperature</Label>
                  <div className="text-sm text-muted-foreground">
                    {model.temperature}
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <Label className="text-xs text-muted-foreground">Cost per 1K tokens</Label>
                  <div className="text-sm">
                    Prompt: ${model.cost_per_1k_tokens.prompt.toFixed(6)} • 
                    Completion: ${model.cost_per_1k_tokens.completion.toFixed(6)}
                  </div>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Current Timeout</Label>
                  <div className="text-sm font-medium">
                    {timeouts[model.id] || model.timeout_seconds} seconds
                    {timeouts[model.id] !== model.timeout_seconds && (
                      <span className="text-orange-500 ml-2">(Modified)</span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="bg-muted/50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">Timeout Guidelines</h3>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• <strong>Local models (DeepSeek, Llama):</strong> 60-600 seconds (1-10 minutes)</li>
          <li>• <strong>Cloud models (OpenAI, Anthropic):</strong> 30-120 seconds (30 seconds - 2 minutes)</li>
          <li>• <strong>Complex reasoning tasks:</strong> Use higher timeouts (300-600 seconds)</li>
          <li>• <strong>Simple tasks:</strong> Lower timeouts (30-60 seconds) for faster responses</li>
        </ul>
      </div>
    </div>
  );
}
