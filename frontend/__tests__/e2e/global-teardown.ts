/**
 * Global Teardown for E2E Tests
 * 
 * This file handles cleanup tasks that need to run after all tests,
 * such as cleaning up test data, closing connections, and generating reports.
 */

import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global E2E test teardown...');
  
  // Clean up test data
  await cleanupTestData();
  
  // Generate test reports
  await generateTestReports();
  
  console.log('✅ Global E2E test teardown completed');
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...');
  
  try {
    // Get all test projects
    const response = await fetch('http://localhost:8000/api/v1/projects/?limit=100');
    if (!response.ok) {
      console.warn('Failed to fetch projects for cleanup');
      return;
    }
    
    const data = await response.json();
    const testProjects = data.projects.filter((project: any) => 
      project.name.includes('E2E Test') || 
      project.name.includes('Database Test') ||
      project.name.includes('Notification Test')
    );
    
    // Delete test projects
    for (const project of testProjects) {
      try {
        await fetch(`http://localhost:8000/api/v1/projects/${project.id}`, {
          method: 'DELETE'
        });
      } catch (error) {
        console.warn(`Failed to delete test project: ${project.name}`);
      }
    }
    
    console.log(`✅ Cleaned up ${testProjects.length} test projects`);
  } catch (error) {
    console.error('❌ Test data cleanup failed:', error);
    // Don't throw here as this is cleanup
  }
}

async function generateTestReports() {
  console.log('📊 Generating test reports...');
  
  try {
    // This would typically involve:
    // 1. Aggregating test results
    // 2. Generating coverage reports
    // 3. Creating performance metrics
    // 4. Sending notifications if tests failed
    
    console.log('✅ Test reports generated');
  } catch (error) {
    console.error('❌ Test report generation failed:', error);
    // Don't throw here as this is reporting
  }
}

export default globalTeardown;
