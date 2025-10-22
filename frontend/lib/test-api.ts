// Simple test file to verify API client functionality
import { apiClient } from './api-client';

export async function testApiConnection() {
  try {
    console.log('Testing API connection...');
    const health = await apiClient.getHealth();
    console.log('✅ API Health Check:', health);
    return true;
  } catch (error) {
    console.error('❌ API Health Check failed:', error);
    return false;
  }
}

export async function testProjectOperations() {
  try {
    console.log('Testing project operations...');
    
    // Test list projects
    const projects = await apiClient.listProjects();
    console.log('✅ List Projects:', projects);
    
    return true;
  } catch (error) {
    console.error('❌ Project operations failed:', error);
    return false;
  }
}

// Export for use in browser console or components
if (typeof window !== 'undefined') {
  (window as any).testApi = {
    testApiConnection,
    testProjectOperations
  };
}
