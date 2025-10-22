import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useParams() {
    return {
      id: 'test-project-id',
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/projects/test-project-id'
  },
}))

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}))

// Mock API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    // Core methods
    getProject: jest.fn(),
    listWorkflows: jest.fn(),
    getWorkflowStatus: jest.fn(),
    getRequirements: jest.fn(),
    getArchitecture: jest.fn(),
    updateProject: jest.fn(),
    approveIntegration: jest.fn(),
    rejectIntegration: jest.fn(),
    
    // Authentication methods
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    
    // Architecture proposal methods
    getArchitectureProposal: jest.fn().mockResolvedValue({ data: null }),
    generateArchitectureProposal: jest.fn().mockResolvedValue({ data: { id: 'proposal-1', content: 'Mock proposal' } }),
    updateArchitectureProposal: jest.fn(),
    
    // Diagram methods
    generateDiagram: jest.fn().mockResolvedValue({ data: { id: 'diagram-1', content: 'Mock diagram' } }),
    updateDiagram: jest.fn(),
    deleteDiagram: jest.fn(),
    
    // Knowledge base methods
    saveArchitectureToKnowledgeBase: jest.fn(),
    searchKnowledgeBase: jest.fn(),
    
    // Project diagrams methods
    getProjectDiagrams: jest.fn().mockResolvedValue({ data: [] }),
    generateProjectDiagram: jest.fn(),
    regenerateDiagram: jest.fn(),
    getDiagramStatus: jest.fn(),
    
    // Base URL property
    baseUrl: '/api/v1',
  },
}))

// Mock UUID
jest.mock('uuid', () => ({
  v4: jest.fn(() => 'mock-uuid-123'),
}))

// Global test utilities
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: jest.fn(),
})

// Mock getComputedStyle
Object.defineProperty(window, 'getComputedStyle', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    getPropertyValue: jest.fn(),
  })),
})

// Suppress console warnings in tests
const originalWarn = console.warn
const originalError = console.error

beforeAll(() => {
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is deprecated')
    ) {
      return
    }
    originalWarn.call(console, ...args)
  }

  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning:') || args[0].includes('Error: Could not parse'))
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.warn = originalWarn
  console.error = originalError
})
