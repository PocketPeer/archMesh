/**
 * Simple Architecture Integration Test
 * 
 * Basic test to verify the new architecture integration works
 */

// Mock fetch for Node.js environment
global.fetch = jest.fn();

describe('Simple Architecture Integration', () => {
  it('should import API client successfully', () => {
    // Dynamic import to avoid module resolution issues
    const { apiClient } = require('../../lib/api-client');
    
    expect(apiClient).toBeDefined();
    expect(apiClient).toHaveProperty('baseUrl');
    expect(apiClient.baseUrl).toBeDefined();
  });

  it('should have architecture methods', () => {
    const { apiClient } = require('../../lib/api-client');
    
    // Check if methods exist
    expect(typeof apiClient.getArchitectureProposal).toBe('function');
    expect(typeof apiClient.generateArchitectureProposal).toBe('function');
    expect(typeof apiClient.updateArchitectureProposal).toBe('function');
  });

  it('should have diagram methods', () => {
    const { apiClient } = require('../../lib/api-client');
    
    expect(typeof apiClient.generateDiagram).toBe('function');
    expect(typeof apiClient.updateDiagram).toBe('function');
    expect(typeof apiClient.deleteDiagram).toBe('function');
  });

  it('should have knowledge base methods', () => {
    const { apiClient } = require('../../lib/api-client');
    
    expect(typeof apiClient.saveArchitectureToKnowledgeBase).toBe('function');
    expect(typeof apiClient.searchKnowledgeBase).toBe('function');
  });

  it('should have authentication methods', () => {
    const { apiClient } = require('../../lib/api-client');
    
    expect(typeof apiClient.login).toBe('function');
    expect(typeof apiClient.register).toBe('function');
    expect(typeof apiClient.logout).toBe('function');
  });
});
