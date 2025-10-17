import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock data generators
export const mockProject = {
  id: 'test-project-id',
  name: 'Test Project',
  description: 'A test project for brownfield development',
  domain: 'cloud-native' as const,
  mode: 'brownfield' as const,
  status: 'processing' as const,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  repository_url: 'https://github.com/test/repo',
  existing_architecture: {
    repository_url: 'https://github.com/test/repo',
    branch: 'main',
    services: [
      {
        id: 'service-1',
        name: 'User Service',
        type: 'service' as const,
        technology: 'Node.js',
        description: 'Handles user management',
        endpoints: ['/api/users', '/api/auth'],
        dependencies: ['database-1'],
      },
    ],
    dependencies: [
      {
        from: 'service-1',
        to: 'database-1',
        type: 'database-call' as const,
        description: 'User data storage',
      },
    ],
    technology_stack: {
      backend: ['Node.js', 'Express'],
      database: ['PostgreSQL'],
      frontend: ['React'],
    },
    quality_score: 85,
    analysis_metadata: {
      analyzed_at: '2024-01-01T00:00:00Z',
      services_count: 1,
      dependencies_count: 1,
      technologies_detected: ['Node.js', 'PostgreSQL', 'React'],
    },
  },
  proposed_architecture: {
    architecture_overview: {
      style: 'Microservices',
      integration_approach: 'API Gateway',
      rationale: 'Scalable and maintainable architecture',
    },
    new_services: [
      {
        id: 'service-2',
        name: 'Notification Service',
        type: 'service' as const,
        technology: 'Node.js',
        description: 'Handles notifications',
        endpoints: ['/api/notifications'],
        dependencies: ['message-queue-1'],
      },
    ],
    modified_services: [],
    integration_points: [
      {
        from_service: 'service-1',
        to_service: 'service-2',
        type: 'API call',
        description: 'Send user notifications',
        implementation_notes: 'Use async messaging',
      },
    ],
    impact_analysis: {
      risk_level: 'medium' as const,
      breaking_changes: false,
      downtime_required: false,
    },
  },
  changes: [
    {
      id: 'change-1',
      type: 'add' as const,
      entity: 'service' as const,
      name: 'Notification Service',
      description: 'Add new notification service',
      impact: 'medium' as const,
      affectedServices: ['service-1'],
      breakingChange: false,
      migrationRequired: false,
      estimatedEffort: 40,
      riskLevel: 'medium' as const,
      dependencies: ['message-queue-1'],
      metadata: {
        reason: 'User requested notification feature',
        alternatives: ['Email service integration'],
        rollbackPlan: 'Remove service and revert API changes',
        testingRequired: true,
        documentationRequired: true,
      },
    },
  ],
}

export const mockWorkflowSession = {
  session_id: 'test-session-id',
  project_id: 'test-project-id',
  current_stage: 'design_integration',
  status: 'in_progress',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  context: {
    requirements: 'Add notification system',
    architecture: 'Microservices with API Gateway',
  },
}

export const mockArchitectureGraph = {
  services: [
    {
      id: 'service-1',
      name: 'User Service',
      type: 'service' as const,
      technology: 'Node.js',
      description: 'Handles user management',
      endpoints: ['/api/users', '/api/auth'],
      dependencies: ['database-1'],
    },
    {
      id: 'database-1',
      name: 'User Database',
      type: 'database' as const,
      technology: 'PostgreSQL',
      description: 'Stores user data',
      endpoints: [],
      dependencies: [],
    },
  ],
  dependencies: [
    {
      from: 'service-1',
      to: 'database-1',
      type: 'database-call' as const,
      description: 'User data storage',
    },
  ],
}

export const mockImpactAnalysis = {
  riskScore: 65,
  riskFactors: {
    technical: ['New service integration', 'Message queue setup'],
    business: ['User experience changes'],
    operational: ['Additional monitoring needed'],
  },
  recommendations: {
    immediate: ['Set up monitoring', 'Create rollback plan'],
    shortTerm: ['Implement feature flags', 'Add integration tests'],
    longTerm: ['Consider service mesh', 'Implement circuit breakers'],
  },
  effortEstimate: {
    development: 40,
    testing: 20,
    deployment: 8,
    total: 68,
  },
  timeline: {
    design: '1 week',
    development: '2 weeks',
    testing: '1 week',
    deployment: '1 day',
    total: '4 weeks',
  },
  affectedSystems: ['User Service', 'API Gateway', 'Message Queue'],
}

// Helper functions
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const mockApiResponse = <T>(data: T, delay = 0) => {
  return new Promise<T>(resolve => {
    setTimeout(() => resolve(data), delay)
  })
}

export const mockApiError = (message: string, delay = 0) => {
  return new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error(message)), delay)
  })
}

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }
