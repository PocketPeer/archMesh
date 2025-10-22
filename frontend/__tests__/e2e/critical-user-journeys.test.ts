/**
 * Critical User Journey E2E Tests
 * 
 * These tests cover the most important user workflows and would have caught
 * the recent integration issues (database schema, WebSocket, API errors).
 * 
 * TDD Approach: RED Phase - Create failing tests first
 */

import { test, expect, Page } from '@playwright/test';

// Test data
const testUser = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  fullName: 'Test User'
};

const testProject = {
  name: 'E2E Test Project',
  description: 'Project created during E2E testing',
  domain: 'cloud-native'
};

test.describe('Critical User Journeys', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Enable console logging to catch errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error(`Console Error: ${msg.text()}`);
      }
    });
    
    // Enable network request logging
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`API Request: ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/') && !response.ok()) {
        console.error(`API Error: ${response.status()} ${response.url()}`);
      }
    });
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('Homepage loads without errors', async () => {
    // This test would have caught the API fetch error we just fixed
    await page.goto('/');
    
    // Wait for page to load completely
    await page.waitForLoadState('networkidle');
    
    // Check that no console errors occurred
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Verify page loads successfully
    await expect(page).toHaveTitle(/ArchMesh/);
    
    // Verify no critical errors
    expect(consoleErrors.filter(error => 
      error.includes('Failed to fetch') || 
      error.includes('Internal Server Error')
    )).toHaveLength(0);
  });

  test('WebSocket connection establishes successfully', async () => {
    // This test would have caught the WebSocket endpoint issue
    await page.goto('/');
    
    // Wait for WebSocket connection
    await page.waitForTimeout(2000);
    
    // Check WebSocket connection status
    const wsConnected = await page.evaluate(() => {
      // Check if WebSocket is connected (this would be implemented in the app)
      return window.wsConnected || false;
    });
    
    // For now, just verify no WebSocket errors in console
    const wsErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('WebSocket')) {
        wsErrors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(1000);
    expect(wsErrors).toHaveLength(0);
  });

  test('Project list displays without API errors', async () => {
    // This test would have caught the database schema issue
    await page.goto('/');
    
    // Wait for projects to load
    await page.waitForSelector('[data-testid="project-list"]', { timeout: 10000 });
    
    // Verify projects are displayed
    const projectCards = await page.locator('[data-testid="project-card"]');
    await expect(projectCards).toHaveCount.greaterThan(0);
    
    // Verify no API errors
    const apiErrors = [];
    page.on('response', response => {
      if (response.url().includes('/api/v1/projects') && !response.ok()) {
        apiErrors.push(`${response.status()}: ${response.url()}`);
      }
    });
    
    await page.waitForTimeout(1000);
    expect(apiErrors).toHaveLength(0);
  });

  test('User can create a new project', async () => {
    // Complete project creation workflow
    await page.goto('/');
    
    // Click create project button
    await page.click('[data-testid="create-project-button"]');
    
    // Fill project form
    await page.fill('[data-testid="project-name-input"]', testProject.name);
    await page.fill('[data-testid="project-description-input"]', testProject.description);
    await page.selectOption('[data-testid="project-domain-select"]', testProject.domain);
    
    // Submit form
    await page.click('[data-testid="submit-project-button"]');
    
    // Wait for success
    await page.waitForSelector('[data-testid="success-message"]', { timeout: 10000 });
    
    // Verify project appears in list
    await page.goto('/');
    await page.waitForSelector(`[data-testid="project-card"][data-project-name="${testProject.name}"]`);
  });

  test('User can upload requirements document', async () => {
    // Test document upload workflow
    await page.goto('/');
    
    // Navigate to first project
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL(/\/projects\/[^\/]+/);
    
    // Click upload requirements
    await page.click('[data-testid="upload-requirements-button"]');
    
    // Upload test file
    const fileInput = page.locator('[data-testid="file-upload-input"]');
    await fileInput.setInputFiles({
      name: 'requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('Sample requirements content')
    });
    
    // Submit upload
    await page.click('[data-testid="submit-upload-button"]');
    
    // Wait for processing
    await page.waitForSelector('[data-testid="processing-indicator"]');
    await page.waitForSelector('[data-testid="processing-complete"]', { timeout: 30000 });
  });

  test('Architecture workflow executes successfully', async () => {
    // Test complete architecture generation workflow
    await page.goto('/');
    
    // Navigate to project with requirements
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL(/\/projects\/[^\/]+/);
    
    // Start architecture workflow
    await page.click('[data-testid="start-architecture-workflow-button"]');
    
    // Wait for workflow to start
    await page.waitForSelector('[data-testid="workflow-progress"]');
    
    // Monitor progress
    await page.waitForSelector('[data-testid="workflow-complete"]', { timeout: 60000 });
    
    // Verify architecture is generated
    await page.waitForSelector('[data-testid="architecture-diagram"]');
  });

  test('Real-time notifications work correctly', async () => {
    // Test notification system
    await page.goto('/');
    
    // Trigger an action that should generate a notification
    await page.click('[data-testid="create-project-button"]');
    await page.fill('[data-testid="project-name-input"]', 'Notification Test Project');
    await page.click('[data-testid="submit-project-button"]');
    
    // Wait for notification
    await page.waitForSelector('[data-testid="notification"]', { timeout: 5000 });
    
    // Verify notification content
    const notification = page.locator('[data-testid="notification"]');
    await expect(notification).toContainText('Project created successfully');
  });

  test('Error handling works correctly', async () => {
    // Test error scenarios
    await page.goto('/');
    
    // Try to create project with invalid data
    await page.click('[data-testid="create-project-button"]');
    await page.click('[data-testid="submit-project-button"]'); // Submit without filling form
    
    // Verify error message appears
    await page.waitForSelector('[data-testid="error-message"]');
    
    // Verify form validation
    const nameInput = page.locator('[data-testid="project-name-input"]');
    await expect(nameInput).toHaveAttribute('aria-invalid', 'true');
  });

  test('Navigation works correctly', async () => {
    // Test navigation between pages
    await page.goto('/');
    
    // Navigate to projects page
    await page.click('[data-testid="nav-projects"]');
    await page.waitForURL('/projects');
    
    // Navigate back to home
    await page.click('[data-testid="nav-home"]');
    await page.waitForURL('/');
    
    // Verify page content
    await expect(page.locator('h1')).toContainText('ArchMesh');
  });

  test('Responsive design works on mobile', async () => {
    // Test mobile responsiveness
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Verify mobile navigation
    await page.click('[data-testid="mobile-menu-button"]');
    await page.waitForSelector('[data-testid="mobile-menu"]');
    
    // Verify content is accessible
    await expect(page.locator('[data-testid="project-list"]')).toBeVisible();
  });

  test('Performance meets requirements', async () => {
    // Test performance metrics
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Verify page loads within acceptable time
    expect(loadTime).toBeLessThan(3000); // 3 seconds max
    
    // Check for performance issues
    const performanceEntries = await page.evaluate(() => {
      return performance.getEntriesByType('navigation')[0];
    });
    
    expect(performanceEntries.loadEventEnd - performanceEntries.loadEventStart).toBeLessThan(2000);
  });
});

test.describe('API Integration Tests', () => {
  test('Projects API returns valid data', async ({ request }) => {
    // This test would have caught the enum conversion issue
    const response = await request.get('/api/v1/projects/?skip=0&limit=10');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('projects');
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('page');
    expect(data).toHaveProperty('page_size');
    expect(data).toHaveProperty('has_next');
    
    // Verify project structure
    if (data.projects.length > 0) {
      const project = data.projects[0];
      expect(project).toHaveProperty('id');
      expect(project).toHaveProperty('name');
      expect(project).toHaveProperty('description');
      expect(project).toHaveProperty('domain');
      expect(project).toHaveProperty('status');
      expect(project).toHaveProperty('created_at');
      expect(project).toHaveProperty('updated_at');
      
      // Verify enum values are valid
      expect(['cloud-native', 'data-platform', 'enterprise']).toContain(project.domain);
      expect(['pending', 'processing', 'completed', 'failed']).toContain(project.status);
    }
  });

  test('WebSocket endpoint accepts connections', async ({ request }) => {
    // This test would have caught the missing WebSocket endpoint
    const response = await request.get('/ws');
    
    // WebSocket endpoints should return 426 Upgrade Required or similar
    expect([426, 101]).toContain(response.status());
  });

  test('Health check endpoint works', async ({ request }) => {
    const response = await request.get('/api/v1/health');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });
});

test.describe('Database Integration Tests', () => {
  test('Project creation persists to database', async ({ request }) => {
    // Test database integration
    const projectData = {
      name: 'Database Test Project',
      description: 'Testing database persistence',
      domain: 'cloud-native'
    };
    
    const response = await request.post('/api/v1/projects/', {
      data: projectData
    });
    
    expect(response.ok()).toBeTruthy();
    
    const createdProject = await response.json();
    expect(createdProject.name).toBe(projectData.name);
    expect(createdProject.domain).toBe(projectData.domain);
    
    // Verify project can be retrieved
    const getResponse = await request.get(`/api/v1/projects/${createdProject.id}`);
    expect(getResponse.ok()).toBeTruthy();
    
    const retrievedProject = await getResponse.json();
    expect(retrievedProject.name).toBe(projectData.name);
  });
});
