/**
 * Integration Tests for API Client
 * 
 * These tests run against the real backend API without mocks.
 * They verify actual functionality and catch real integration issues.
 */

import { apiClient } from '@/lib/api-client';

// Test configuration
const TEST_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  timeout: 30000, // 30 seconds for integration tests
};

describe('API Client Integration Tests', () => {
  // Test data
  let testProjectId: string;
  let testWorkflowId: string;

  beforeAll(async () => {
    // Verify backend is running
    try {
      const healthResponse = await fetch(`${TEST_CONFIG.baseUrl}/api/v1/health`);
      if (!healthResponse.ok) {
        throw new Error('Backend is not running');
      }
    } catch (error) {
      throw new Error(`Backend not available at ${TEST_CONFIG.baseUrl}. Please start the backend server.`);
    }
  });

  describe('Health Check', () => {
    it('should connect to backend successfully', async () => {
      const health = await apiClient.getHealth();
      expect(health.status).toBe('healthy');
    });
  });

  describe('Project Management', () => {
    it('should list projects', async () => {
      const response = await apiClient.getProjects(0, 10);
      
      expect(response).toHaveProperty('projects');
      expect(response).toHaveProperty('total');
      expect(response).toHaveProperty('page');
      expect(response).toHaveProperty('page_size');
      expect(response).toHaveProperty('has_next');
      expect(Array.isArray(response.projects)).toBe(true);
    });

    it('should create a new project', async () => {
      const projectData = {
        name: `Integration Test Project ${Date.now()}`,
        description: 'Project created during integration testing',
        domain: 'cloud-native' as const,
      };

      const project = await apiClient.createProject(projectData);
      
      expect(project).toHaveProperty('id');
      expect(project.name).toBe(projectData.name);
      expect(project.description).toBe(projectData.description);
      expect(project.domain).toBe(projectData.domain);
      expect(project.status).toBe('pending');
      
      // Store for cleanup
      testProjectId = project.id;
    });

    it('should retrieve created project', async () => {
      expect(testProjectId).toBeDefined();
      
      const project = await apiClient.getProject(testProjectId);
      
      expect(project.id).toBe(testProjectId);
      expect(project.name).toContain('Integration Test Project');
    });

    it('should update project', async () => {
      expect(testProjectId).toBeDefined();
      
      const updateData = {
        name: `Updated Integration Test Project ${Date.now()}`,
        description: 'Updated description',
      };

      const updatedProject = await apiClient.updateProject(testProjectId, updateData);
      
      expect(updatedProject.id).toBe(testProjectId);
      expect(updatedProject.name).toBe(updateData.name);
      expect(updatedProject.description).toBe(updateData.description);
    });
  });

  describe('Workflow Management', () => {
    it('should list workflows for project', async () => {
      expect(testProjectId).toBeDefined();
      
      const response = await apiClient.listWorkflows(0, 10, testProjectId);
      
      expect(response).toHaveProperty('items');
      expect(Array.isArray(response.items)).toBe(true);
    });

    it('should start architecture workflow', async () => {
      expect(testProjectId).toBeDefined();
      
      // Create a test file
      const testContent = `
# Test Requirements Document

## Business Goals
- Build a scalable e-commerce platform
- Support 10,000+ concurrent users
- Ensure 99.9% uptime

## Functional Requirements
- User registration and authentication
- Product catalog management
- Shopping cart functionality
- Order processing
- Payment integration

## Non-Functional Requirements
- Performance: Page load times < 2 seconds
- Security: PCI DSS compliance
- Scalability: Horizontal scaling capability
- Reliability: 99.9% uptime SLA
      `;
      
      const testFile = new File([testContent], 'test-requirements.txt', {
        type: 'text/plain',
      });

      const workflowResponse = await apiClient.startArchitectureWorkflow(
        testFile,
        testProjectId,
        'cloud-native',
        'Integration test project context',
        'deepseek'
      );

      expect(workflowResponse).toHaveProperty('session_id');
      expect(workflowResponse).toHaveProperty('project_id', testProjectId);
      expect(workflowResponse).toHaveProperty('status');
      
      // Store for further tests
      testWorkflowId = workflowResponse.session_id;
    }, TEST_CONFIG.timeout);

    it('should get workflow status', async () => {
      expect(testWorkflowId).toBeDefined();
      
      const status = await apiClient.getWorkflowStatus(testWorkflowId);
      
      expect(status).toHaveProperty('session_id', testWorkflowId);
      expect(status).toHaveProperty('project_id', testProjectId);
      expect(status).toHaveProperty('current_stage');
      expect(status).toHaveProperty('errors');
      expect(Array.isArray(status.errors)).toBe(true);
    });

    it('should handle workflow timeout gracefully', async () => {
      expect(testWorkflowId).toBeDefined();
      
      // Wait a bit for workflow to process
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const status = await apiClient.getWorkflowStatus(testWorkflowId);
      
      // Should have a valid status even if it's still processing
      expect(['starting', 'document_analysis', 'requirements_review', 'architecture_design', 'completed', 'failed']).toContain(status.current_stage);
    }, TEST_CONFIG.timeout);
  });

  describe('Authentication', () => {
    it('should handle authentication errors gracefully', async () => {
      // Test with invalid token
      const originalToken = localStorage.getItem('accessToken');
      localStorage.setItem('accessToken', 'invalid-token');
      
      try {
        await apiClient.getProjects(0, 10);
        // If this doesn't throw, the token refresh should have worked
      } catch (error) {
        // Expected for invalid token
        expect(error).toBeDefined();
      } finally {
        // Restore original token
        if (originalToken) {
          localStorage.setItem('accessToken', originalToken);
        } else {
          localStorage.removeItem('accessToken');
        }
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors', async () => {
      await expect(apiClient.getProject('non-existent-id')).rejects.toThrow();
    });

    it('should handle network errors gracefully', async () => {
      // Temporarily change base URL to invalid endpoint
      const originalBaseUrl = apiClient['baseUrl'];
      apiClient['baseUrl'] = 'http://localhost:9999';
      
      try {
        await expect(apiClient.getHealth()).rejects.toThrow();
      } finally {
        apiClient['baseUrl'] = originalBaseUrl;
      }
    });
  });

  // Cleanup
  afterAll(async () => {
    if (testProjectId) {
      try {
        await apiClient.deleteProject(testProjectId);
      } catch (error) {
        console.warn('Failed to cleanup test project:', error);
      }
    }
  });
});
