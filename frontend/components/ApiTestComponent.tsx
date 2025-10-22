'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { testApiConnection, testProjectOperations } from '@/lib/test-api';
import { toast } from 'sonner';

export function ApiTestComponent() {
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<{
    health?: any;
    projects?: any;
    testProject?: any;
    error?: string;
  }>({});

  const runTests = async () => {
    setTesting(true);
    setResults({});

    try {
      // Test API connection
      const healthResult = await testApiConnection();
      setResults(prev => ({ ...prev, health: healthResult }));

      // Test project operations
      const projectsResult = await testProjectOperations();
      setResults(prev => ({ ...prev, projects: projectsResult }));

      toast.success('API tests completed successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setResults(prev => ({ ...prev, error: errorMessage }));
      toast.error('API tests failed: ' + errorMessage);
    } finally {
      setTesting(false);
    }
  };

  const createTestProject = async () => {
    try {
      const project = await apiClient.createProject({
        name: 'API Test Project',
        description: 'Created via API test component',
        domain: 'cloud-native'
      });
      
      toast.success(`Test project created: ${project.name}`);
      setResults(prev => ({ ...prev, testProject: project }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error('Failed to create test project: ' + errorMessage);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>API Client Test</CardTitle>
        <CardDescription>
          Test the API client functionality and backend connectivity
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex space-x-2">
          <Button 
            onClick={runTests} 
            disabled={testing}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            {testing ? 'Testing...' : 'Run API Tests'}
          </Button>
          <Button 
            onClick={createTestProject} 
            variant="outline"
          >
            Create Test Project
          </Button>
        </div>

        {results.health !== undefined && (
          <div className="space-y-2">
            <h4 className="font-medium text-slate-900">Health Check</h4>
            <Badge variant={results.health ? "default" : "destructive"}>
              {results.health ? 'Connected' : 'Failed'}
            </Badge>
          </div>
        )}

        {results.projects !== undefined && (
          <div className="space-y-2">
            <h4 className="font-medium text-slate-900">Project Operations</h4>
            <Badge variant={results.projects ? "default" : "destructive"}>
              {results.projects ? 'Working' : 'Failed'}
            </Badge>
          </div>
        )}

        {results.error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <h4 className="font-medium text-red-800 mb-1">Error</h4>
            <p className="text-sm text-red-700">{results.error}</p>
          </div>
        )}

        {results.testProject && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <h4 className="font-medium text-green-800 mb-1">Test Project Created</h4>
            <p className="text-sm text-green-700">
              ID: {results.testProject.id}<br />
              Name: {results.testProject.name}
            </p>
          </div>
        )}

        <div className="text-xs text-slate-500">
          <p>API URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
          <p>Make sure the backend server is running before testing.</p>
        </div>
      </CardContent>
    </Card>
  );
}
