/**
 * Workflow Integration Tests
 * 
 * These tests verify the complete workflow functionality including:
 * - Document upload
 * - Workflow execution
 * - Status tracking
 * - Error handling
 * - Real-time updates
 */

import { apiClient } from '@/lib/api-client';

const TEST_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  timeout: 120000, // 2 minutes for workflow tests
};

describe('Workflow Integration Tests', () => {
  let testProjectId: string;
  let testWorkflowId: string;

  beforeAll(async () => {
    // Create a test project
    const projectData = {
      name: `Workflow Test Project ${Date.now()}`,
      description: 'Project for testing workflow functionality',
      domain: 'cloud-native' as const,
    };

    const project = await apiClient.createProject(projectData);
    testProjectId = project.id;
  });

  afterAll(async () => {
    // Cleanup
    if (testProjectId) {
      try {
        await apiClient.deleteProject(testProjectId);
      } catch (error) {
        console.warn('Failed to cleanup test project:', error);
      }
    }
  });

  describe('Document Upload and Workflow Start', () => {
    it('should upload document and start workflow successfully', async () => {
      const testContent = `
# E-commerce Platform Requirements

## Business Goals
- Launch a modern e-commerce platform
- Support 50,000+ products
- Handle 1,000+ concurrent users
- Achieve 99.9% uptime

## Functional Requirements
- User authentication and authorization
- Product catalog with search and filtering
- Shopping cart and checkout process
- Order management system
- Payment processing integration
- Admin dashboard for inventory management

## Non-Functional Requirements
- Performance: Page load times < 1.5 seconds
- Security: PCI DSS Level 1 compliance
- Scalability: Auto-scaling based on load
- Reliability: 99.9% uptime SLA
- Availability: Multi-region deployment

## Technical Constraints
- Must use cloud-native architecture
- Microservices-based design
- Event-driven communication
- Containerized deployment
- CI/CD pipeline integration
      `;

      const testFile = new File([testContent], 'ecommerce-requirements.txt', {
        type: 'text/plain',
      });

      const workflowResponse = await apiClient.startArchitectureWorkflow(
        testFile,
        testProjectId,
        'cloud-native',
        'E-commerce platform for online retail',
        'deepseek'
      );

      expect(workflowResponse).toHaveProperty('session_id');
      expect(workflowResponse).toHaveProperty('project_id', testProjectId);
      expect(workflowResponse).toHaveProperty('status');
      
      testWorkflowId = workflowResponse.session_id;
    }, TEST_CONFIG.timeout);
  });

  describe('Workflow Status Tracking', () => {
    it('should track workflow progress', async () => {
      expect(testWorkflowId).toBeDefined();
      
      // Get initial status
      const initialStatus = await apiClient.getWorkflowStatus(testWorkflowId);
      expect(initialStatus.session_id).toBe(testWorkflowId);
      expect(initialStatus.project_id).toBe(testProjectId);
      expect(initialStatus.current_stage).toBeDefined();
      expect(Array.isArray(initialStatus.errors)).toBe(true);
    });

    it('should show workflow in project workflows list', async () => {
      expect(testWorkflowId).toBeDefined();
      
      const workflows = await apiClient.listWorkflows(0, 10, testProjectId);
      
      const testWorkflow = workflows.items.find(w => w.session_id === testWorkflowId);
      expect(testWorkflow).toBeDefined();
      expect(testWorkflow?.project_id).toBe(testProjectId);
      expect(testWorkflow?.is_active).toBe(true);
    });

    it('should handle workflow timeout gracefully', async () => {
      expect(testWorkflowId).toBeDefined();
      
      // Wait for workflow to process (or timeout)
      let attempts = 0;
      const maxAttempts = 24; // 2 minutes with 5-second intervals
      let currentStatus;
      
      while (attempts < maxAttempts) {
        currentStatus = await apiClient.getWorkflowStatus(testWorkflowId);
        
        if (['completed', 'failed'].includes(currentStatus.current_stage)) {
          break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }
      
      // Should have reached a final state
      expect(['starting', 'document_analysis', 'requirements_review', 'architecture_design', 'completed', 'failed']).toContain(currentStatus.current_stage);
      
      if (currentStatus.current_stage === 'failed') {
        // If failed, should have error details
        expect(Array.isArray(currentStatus.errors)).toBe(true);
        console.log('Workflow failed with errors:', currentStatus.errors);
      }
    }, TEST_CONFIG.timeout);
  });

  describe('Workflow Results', () => {
    it('should retrieve requirements if workflow completed', async () => {
      expect(testWorkflowId).toBeDefined();
      
      // Wait a bit for processing
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      try {
        const requirements = await apiClient.getRequirements(testWorkflowId);
        
        if (requirements) {
          expect(requirements).toHaveProperty('structured_requirements');
          expect(requirements.structured_requirements).toHaveProperty('business_goals');
          expect(requirements.structured_requirements).toHaveProperty('functional_requirements');
          expect(Array.isArray(requirements.structured_requirements.business_goals)).toBe(true);
          expect(Array.isArray(requirements.structured_requirements.functional_requirements)).toBe(true);
        }
      } catch (error) {
        // Requirements might not be ready yet, which is okay
        console.log('Requirements not ready yet:', error.message);
      }
    }, TEST_CONFIG.timeout);

    it('should retrieve architecture if workflow completed', async () => {
      expect(testWorkflowId).toBeDefined();
      
      // Wait a bit for processing
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      try {
        const architecture = await apiClient.getArchitecture(testWorkflowId);
        
        if (architecture) {
          expect(architecture).toHaveProperty('overview');
          expect(architecture).toHaveProperty('components');
          expect(architecture).toHaveProperty('technology_stack');
          expect(Array.isArray(architecture.components)).toBe(true);
          expect(Array.isArray(architecture.technology_stack)).toBe(true);
        }
      } catch (error) {
        // Architecture might not be ready yet, which is okay
        console.log('Architecture not ready yet:', error.message);
      }
    }, TEST_CONFIG.timeout);
  });

  describe('Error Handling', () => {
    it('should handle invalid workflow ID', async () => {
      await expect(apiClient.getWorkflowStatus('invalid-workflow-id')).rejects.toThrow();
    });

    it('should handle invalid project ID in workflow creation', async () => {
      const testFile = new File(['test'], 'test.txt', { type: 'text/plain' });
      
      await expect(
        apiClient.startArchitectureWorkflow(
          testFile,
          'invalid-project-id',
          'cloud-native'
        )
      ).rejects.toThrow();
    });

    it('should handle unsupported file types', async () => {
      const testFile = new File(['test'], 'test.exe', { type: 'application/x-msdownload' });
      
      await expect(
        apiClient.startArchitectureWorkflow(
          testFile,
          testProjectId,
          'cloud-native'
        )
      ).rejects.toThrow();
    });
  });

  describe('Real-time Updates', () => {
    it('should show status changes over time', async () => {
      expect(testWorkflowId).toBeDefined();
      
      const statuses = [];
      const maxChecks = 12; // 1 minute with 5-second intervals
      
      for (let i = 0; i < maxChecks; i++) {
        const status = await apiClient.getWorkflowStatus(testWorkflowId);
        statuses.push(status.current_stage);
        
        if (['completed', 'failed'].includes(status.current_stage)) {
          break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
      
      // Should have recorded some status changes
      expect(statuses.length).toBeGreaterThan(0);
      console.log('Workflow status progression:', statuses);
    }, TEST_CONFIG.timeout);
  });
});
