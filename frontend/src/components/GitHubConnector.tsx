import React, { useState, useCallback } from 'react';
import { ArchitectureGraph } from '../types/architecture';

export interface GitHubAnalysisResult {
  repository_url: string;
  branch: string;
  services: any[];
  dependencies: any[];
  technology_stack: Record<string, any>;
  quality_score: number;
  analysis_metadata: {
    analyzed_at: string;
    services_count: number;
    dependencies_count: number;
    technologies_detected: string[];
  };
}

interface GitHubConnectorProps {
  projectId: string;
  onAnalysisComplete: (result: GitHubAnalysisResult) => void;
  onError?: (error: string) => void;
  className?: string;
}

interface AnalysisProgress {
  stage: string;
  progress: number;
  message: string;
}

export const GitHubConnector: React.FC<GitHubConnectorProps> = ({
  projectId,
  onAnalysisComplete,
  onError,
  className = ''
}) => {
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [githubToken, setGithubToken] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgress | null>(null);
  const [analysisResult, setAnalysisResult] = useState<GitHubAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateRepositoryUrl = useCallback((url: string): boolean => {
    const githubUrlPattern = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+(?:\/)?$/;
    return githubUrlPattern.test(url);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!repositoryUrl.trim()) {
      setError('Please enter a GitHub repository URL');
      return;
    }

    if (!validateRepositoryUrl(repositoryUrl)) {
      setError('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisProgress({
      stage: 'initializing',
      progress: 0,
      message: 'Starting repository analysis...'
    });

    try {
      // Simulate analysis progress
      const progressStages = [
        { stage: 'cloning', progress: 20, message: 'Cloning repository...' },
        { stage: 'analyzing', progress: 40, message: 'Analyzing file structure...' },
        { stage: 'extracting', progress: 60, message: 'Extracting technology stack...' },
        { stage: 'mapping', progress: 80, message: 'Mapping service dependencies...' },
        { stage: 'finalizing', progress: 100, message: 'Finalizing analysis...' }
      ];

      for (const stage of progressStages) {
        setAnalysisProgress(stage);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate work
      }

      // In a real implementation, this would call the backend API
      const mockResult: GitHubAnalysisResult = {
        repository_url: repositoryUrl,
        branch: branch,
        services: [
          {
            id: 'user-service',
            name: 'User Service',
            type: 'service',
            technology: 'Node.js + Express',
            description: 'Handles user authentication and profiles',
            endpoints: ['/api/users', '/api/auth'],
            dependencies: ['user-database']
          },
          {
            id: 'user-database',
            name: 'User Database',
            type: 'database',
            technology: 'PostgreSQL',
            description: 'Stores user data and authentication info'
          },
          {
            id: 'payment-service',
            name: 'Payment Service',
            type: 'service',
            technology: 'Java + Spring Boot',
            description: 'Processes payments and billing',
            endpoints: ['/api/payments', '/api/billing'],
            dependencies: ['payment-database']
          }
        ],
        dependencies: [
          {
            from: 'user-service',
            to: 'user-database',
            type: 'database-call',
            description: 'User service reads/writes to user database'
          },
          {
            from: 'payment-service',
            to: 'user-service',
            type: 'api-call',
            description: 'Payment service validates users via user service'
          }
        ],
        technology_stack: {
          'Node.js': 1,
          'Java': 1,
          'PostgreSQL': 1,
          'Express': 1,
          'Spring Boot': 1
        },
        quality_score: 0.85,
        analysis_metadata: {
          analyzed_at: new Date().toISOString(),
          services_count: 3,
          dependencies_count: 2,
          technologies_detected: ['Node.js', 'Java', 'PostgreSQL', 'Express', 'Spring Boot']
        }
      };

      setAnalysisResult(mockResult);
      onAnalysisComplete(mockResult);
      setAnalysisProgress(null);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  }, [repositoryUrl, branch, githubToken, projectId, onAnalysisComplete, onError, validateRepositoryUrl]);

  const handleReset = useCallback(() => {
    setRepositoryUrl('');
    setBranch('main');
    setGithubToken('');
    setAnalysisResult(null);
    setError(null);
    setAnalysisProgress(null);
  }, []);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          GitHub Repository Analysis
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Connect your existing repository to analyze its architecture and understand the current system.
        </p>
      </div>

      {!analysisResult ? (
        <div className="space-y-4">
          {/* Repository URL Input */}
          <div>
            <label htmlFor="repository-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Repository URL *
            </label>
            <div className="flex space-x-2">
              <input
                id="repository-url"
                type="url"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                placeholder="https://github.com/owner/repository"
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                disabled={isAnalyzing}
              />
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !repositoryUrl.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isAnalyzing ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span>Analyze</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Branch Input */}
          <div>
            <label htmlFor="branch" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Branch
            </label>
            <input
              id="branch"
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              disabled={isAnalyzing}
            />
          </div>

          {/* GitHub Token (Optional) */}
          <div>
            <label htmlFor="github-token" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              GitHub Token (Optional)
            </label>
            <input
              id="github-token"
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              disabled={isAnalyzing}
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Required for private repositories. Generate a token with repository access.
            </p>
          </div>

          {/* Analysis Progress */}
          {analysisProgress && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
              <div className="flex items-center space-x-3">
                <svg className="animate-spin w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    {analysisProgress.message}
                  </p>
                  <div className="mt-2 bg-blue-200 dark:bg-blue-800 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${analysisProgress.progress}%` }}
                    ></div>
                  </div>
                </div>
                <span className="text-sm text-blue-700 dark:text-blue-300">
                  {analysisProgress.progress}%
                </span>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Analysis Results */
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Analysis Complete
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Repository: {analysisResult.repository_url}
              </p>
            </div>
            <button
              onClick={handleReset}
              className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Analyze Different Repository
            </button>
          </div>

          {/* Analysis Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Services</span>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {analysisResult.analysis_metadata.services_count}
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Dependencies</span>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {analysisResult.analysis_metadata.dependencies_count}
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Quality Score</span>
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {Math.round(analysisResult.quality_score * 100)}%
              </p>
            </div>
          </div>

          {/* Technologies Detected */}
          <div>
            <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Technologies Detected
            </h5>
            <div className="flex flex-wrap gap-2">
              {analysisResult.analysis_metadata.technologies_detected.map((tech) => (
                <span
                  key={tech}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>

          {/* Services List */}
          <div>
            <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Services Found
            </h5>
            <div className="space-y-2">
              {analysisResult.services.map((service) => (
                <div
                  key={service.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{service.name}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{service.description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{service.technology}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{service.type}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitHubConnector;
