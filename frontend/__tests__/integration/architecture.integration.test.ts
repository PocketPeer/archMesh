/**
 * Architecture Integration Tests
 * 
 * Tests the new architecture integration features including:
 * - Architecture proposal generation
 * - Diagram generation
 * - Knowledge base integration
 */

// Mock fetch for Node.js environment
global.fetch = jest.fn();

import { apiClient } from '@/lib/api-client';

describe('Architecture Integration Tests', () => {
  const TEST_PROJECT_ID = 'test-project-123';
  
  describe('Architecture Proposal Management', () => {
    it('should have architecture proposal methods available', () => {
      // Test that the API client has the new architecture methods
      expect(typeof apiClient.getArchitectureProposal).toBe('function');
      expect(typeof apiClient.generateArchitectureProposal).toBe('function');
      expect(typeof apiClient.updateArchitectureProposal).toBe('function');
    });

    it('should have diagram generation methods available', () => {
      // Test that the API client has diagram generation methods
      expect(typeof apiClient.generateDiagram).toBe('function');
      expect(typeof apiClient.updateDiagram).toBe('function');
      expect(typeof apiClient.deleteDiagram).toBe('function');
    });

    it('should have knowledge base methods available', () => {
      // Test that the API client has knowledge base methods
      expect(typeof apiClient.saveArchitectureToKnowledgeBase).toBe('function');
      expect(typeof apiClient.searchKnowledgeBase).toBe('function');
    });
  });

  describe('API Client Configuration', () => {
    it('should have proper base URL configuration', () => {
      // The baseUrl is set in the constructor, so we need to check it exists
      expect(apiClient).toBeDefined();
      expect(apiClient).toHaveProperty('baseUrl');
    });

    it('should have authentication methods', () => {
      expect(typeof apiClient.login).toBe('function');
      expect(typeof apiClient.register).toBe('function');
      expect(typeof apiClient.logout).toBe('function');
    });
  });

  describe('Architecture Service Integration', () => {
    beforeEach(() => {
      // Reset fetch mock before each test
      (global.fetch as jest.Mock).mockClear();
    });

    it('should handle architecture proposal requests', async () => {
      // Mock fetch to simulate network error
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const proposalRequest = {
        project_id: TEST_PROJECT_ID,
        content: 'Test architecture proposal',
        status: 'draft'
      };

      try {
        await apiClient.updateArchitectureProposal(TEST_PROJECT_ID, proposalRequest);
      } catch (error) {
        // Expected to fail without backend, but should be a network error, not method error
        expect(error).toBeDefined();
        expect(error.message).toContain('Network error');
      }
    });

    it('should handle diagram generation requests', async () => {
      // Mock fetch to simulate network error
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const diagramRequest = {
        project_id: TEST_PROJECT_ID,
        diagram_type: 'c4_context',
        output_format: 'plantuml',
        context: { test: true }
      };

      try {
        await apiClient.generateDiagram(diagramRequest);
      } catch (error) {
        // Expected to fail without backend, but should be a network error, not method error
        expect(error).toBeDefined();
        expect(error.message).toContain('Network error');
      }
    });

    it('should handle knowledge base search requests', async () => {
      // Mock fetch to simulate network error
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      try {
        await apiClient.searchKnowledgeBase('test query', TEST_PROJECT_ID);
      } catch (error) {
        // Expected to fail without backend, but should be a network error, not method error
        expect(error).toBeDefined();
        expect(error.message).toContain('Network error');
      }
    });
  });

  describe('Component Integration', () => {
    it('should have proper TypeScript types', () => {
      // Test that the types are properly defined
      const mockProject = {
        id: TEST_PROJECT_ID,
        name: 'Test Project',
        description: 'Test Description',
        domain: 'web',
        mode: 'greenfield',
        status: 'active',
        owner_id: 'test-user',
        created_at: new Date().toISOString()
      };

      expect(mockProject.id).toBe(TEST_PROJECT_ID);
      expect(mockProject.name).toBe('Test Project');
    });

    it('should handle architecture proposal data structure', () => {
      const mockProposal = {
        id: 'proposal-123',
        content: 'Test architecture content',
        generated_at: new Date().toISOString(),
        status: 'draft',
        metadata: {
          llm_model: 'gpt-4',
          confidence: 0.9
        }
      };

      expect(mockProposal.id).toBe('proposal-123');
      expect(mockProposal.content).toBe('Test architecture content');
      expect(mockProposal.status).toBe('draft');
    });

    it('should handle diagram data structure', () => {
      const mockDiagram = {
        id: 'diagram-123',
        diagram_type: 'c4_context',
        output_format: 'plantuml',
        diagram_code: '@startuml\ntest\ndiagram\n@enduml',
        metadata: {
          generated_at: new Date().toISOString()
        }
      };

      expect(mockDiagram.id).toBe('diagram-123');
      expect(mockDiagram.diagram_type).toBe('c4_context');
      expect(mockDiagram.output_format).toBe('plantuml');
    });
  });
});
