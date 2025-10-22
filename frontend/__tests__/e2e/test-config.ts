/**
 * E2E Test Configuration
 * 
 * Centralized configuration for all E2E tests to ensure consistency
 * and realistic timing expectations.
 */

export const E2E_CONFIG = {
  // Application URLs
  baseUrl: 'http://localhost:3000', // Frontend development server
  apiBaseUrl: 'http://localhost:8000', // Backend API server
  
  // Timeout configurations (in milliseconds)
  timeouts: {
    // Overall test timeout
    test: 180000, // 3 minutes
    
    // Workflow execution timeout (based on real execution times)
    workflow: 120000, // 2 minutes
    
    // UI interaction timeouts
    navigation: 15000, // 15 seconds
    element: 10000, // 10 seconds
    form: 5000, // 5 seconds
    
    // Network timeouts
    api: 30000, // 30 seconds
    fileUpload: 60000, // 1 minute
  },
  
  // Polling intervals (in milliseconds)
  polling: {
    workflow: 3000, // 3 seconds between workflow status checks
    ui: 1000, // 1 second for UI state changes
  },
  
  // Test data
  testData: {
    // User credentials
    user: {
      email: `test-${Date.now()}@example.com`,
      password: 'TestPassword123!',
      name: 'E2E Test User'
    },
    
    // Project data
    project: {
      name: `E2E Test Project ${Date.now()}`,
      description: 'Project created during E2E testing',
      domain: 'cloud-native'
    },
    
    // File upload data
    upload: {
      fileName: 'test-requirements.txt',
      content: 'Test requirements document for E2E testing',
      context: 'This is a test project context for E2E testing purposes.'
    }
  },
  
  // Selectors for common elements
  selectors: {
    // Authentication
    emailInput: 'input[id="email"]',
    passwordInput: 'input[id="password"]',
    confirmPasswordInput: 'input[id="confirmPassword"]',
    submitButton: 'button[type="submit"]',
    
    // Project creation
    projectNameInput: 'input[placeholder="Enter project name"]',
    projectDescriptionInput: 'textarea[placeholder="Enter project description (optional)"]',
    projectDomainSelect: 'select[name="domain"]',
    createProjectButton: 'button:has-text("Create Project")',
    
    // Workflow
    workflowStatus: '[data-testid="workflow-status"]',
    startWorkflowButton: 'button:has-text("Start Workflow")',
    uploadFileInput: 'input[type="file"]',
    projectContextInput: 'textarea[placeholder="Enter project context"]',
    
    // Navigation
    projectsLink: 'text=Projects',
    workflowsLink: 'text=Workflows',
    createProjectLink: 'text=Create New Project',
    
    // Common UI elements
    loadingSpinner: '[data-testid="loading-spinner"]',
    errorMessage: '[role="alert"]',
    successMessage: '[data-testid="success-message"]'
  },
  
  // Expected workflow stages
  workflowStages: {
    starting: 'starting',
    documentAnalysis: 'document_analysis',
    requirementsReview: 'requirements_review',
    architectureDesign: 'architecture_design',
    architectureReview: 'architecture_review',
    completed: 'completed',
    failed: 'failed'
  },
  
  // Realistic timing expectations
  expectations: {
    // How long workflows typically take (based on real execution)
    workflowExecution: {
      requirements: 30000, // 30 seconds
      architecture: 60000, // 1 minute
      full: 120000 // 2 minutes for complete workflow
    },
    
    // UI response times
    uiResponse: {
      navigation: 2000, // 2 seconds
      formSubmission: 3000, // 3 seconds
      apiCall: 5000 // 5 seconds
    }
  }
};

/**
 * Helper function to calculate polling attempts based on timeout and interval
 */
export function calculatePollingAttempts(timeoutMs: number, intervalMs: number): number {
  return Math.ceil(timeoutMs / intervalMs);
}

/**
 * Helper function to get realistic timeout for workflow type
 */
export function getWorkflowTimeout(workflowType: 'requirements' | 'architecture' | 'full'): number {
  return E2E_CONFIG.expectations.workflowExecution[workflowType];
}

/**
 * Helper function to wait for workflow completion with realistic timing
 */
export async function waitForWorkflowCompletion(
  page: any,
  workflowType: 'requirements' | 'architecture' | 'full' = 'full'
): Promise<string> {
  const timeout = getWorkflowTimeout(workflowType);
  const interval = E2E_CONFIG.polling.workflow;
  const maxAttempts = calculatePollingAttempts(timeout, interval);
  
  console.log(`Monitoring ${workflowType} workflow for up to ${timeout / 1000} seconds...`);
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const statusElement = page.locator(E2E_CONFIG.selectors.workflowStatus);
    const statusText = await statusElement.textContent();
    
    console.log(`Workflow status (attempt ${attempt + 1}/${maxAttempts}): ${statusText}`);
    
    if (statusText && ['completed', 'failed'].includes(statusText.toLowerCase())) {
      console.log(`Workflow finished with status: ${statusText}`);
      return statusText;
    }
    
    await page.waitForTimeout(interval);
  }
  
  throw new Error(`Workflow did not complete within ${timeout / 1000} seconds`);
}
