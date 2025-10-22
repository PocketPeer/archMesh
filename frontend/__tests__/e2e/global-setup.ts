/**
 * Global Setup for E2E Tests
 * 
 * This file handles global setup tasks that need to run before all tests,
 * such as database setup, test data creation, and environment configuration.
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global E2E test setup...');
  
  // Setup test database
  await setupTestDatabase();
  
  // Create test data
  await createTestData();
  
  // Verify backend is running
  await verifyBackendHealth();
  
  console.log('✅ Global E2E test setup completed');
}

async function setupTestDatabase() {
  console.log('📊 Setting up test database...');
  
  try {
    // This would typically involve:
    // 1. Creating a test database
    // 2. Running migrations
    // 3. Seeding with test data
    
    // For now, we'll just verify the database is accessible
    const response = await fetch('http://localhost:8000/api/v1/health');
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }
    
    console.log('✅ Test database setup completed');
  } catch (error) {
    console.error('❌ Test database setup failed:', error);
    throw error;
  }
}

async function createTestData() {
  console.log('📝 Creating test data...');
  
  try {
    // Create test projects
    const testProjects = [
      {
        name: 'E2E Test Project 1',
        description: 'Project for E2E testing',
        domain: 'cloud-native'
      },
      {
        name: 'E2E Test Project 2',
        description: 'Another project for E2E testing',
        domain: 'data-platform'
      }
    ];
    
    for (const project of testProjects) {
      const response = await fetch('http://localhost:8000/api/v1/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(project)
      });
      
      if (!response.ok) {
        console.warn(`Failed to create test project: ${project.name}`);
      }
    }
    
    console.log('✅ Test data creation completed');
  } catch (error) {
    console.error('❌ Test data creation failed:', error);
    // Don't throw here as this is not critical for all tests
  }
}

async function verifyBackendHealth() {
  console.log('🏥 Verifying backend health...');
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/health');
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }
    
    const health = await response.json();
    if (health.status !== 'healthy') {
      throw new Error(`Backend is not healthy: ${health.status}`);
    }
    
    console.log('✅ Backend health verification completed');
  } catch (error) {
    console.error('❌ Backend health verification failed:', error);
    throw error;
  }
}

export default globalSetup;
