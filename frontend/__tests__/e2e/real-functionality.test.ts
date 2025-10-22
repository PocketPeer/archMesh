/**
 * Real Functionality E2E Tests
 * 
 * These tests verify the complete application functionality
 * using real backend services without any mocks.
 * 
 * Prerequisites:
 * - Backend server running on localhost:8000
 * - Database initialized
 * - All services available
 */

import { test, expect, Page } from '@playwright/test';
import { E2E_CONFIG } from './test-config';
import { 
  waitForElement, 
  waitForWorkflowStatus, 
  waitForNavigation, 
  fillFormField, 
  clickElement,
  createTestUser,
  createTestProject,
  waitForPageLoad,
  retryOperation
} from './test-utils';

// Use dynamic test data
const testUser = createTestUser();
const testProject = createTestProject();

test.describe('Real Functionality E2E Tests', () => {
  let page: Page;
  let projectId: string;
  let workflowId: string;

  test.beforeAll(async ({ browser }) => {
    // Verify backend is running
    try {
      const response = await fetch(`${E2E_CONFIG.apiBaseUrl}/api/v1/health`);
      if (!response.ok) {
        throw new Error('Backend is not running');
      }
    } catch (error) {
      throw new Error(`Backend not available at ${E2E_CONFIG.apiBaseUrl}. Please start the backend server.`);
    }
  });

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Enable detailed logging
    page.on('console', msg => {
      console.log(`[${msg.type()}] ${msg.text()}`);
    });
    
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`[REQUEST] ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/') && !response.ok()) {
        console.error(`[ERROR] ${response.status()} ${response.url()}`);
      }
    });
  });

  test.afterEach(async () => {
    // Cleanup: Delete test project if it exists
    if (projectId) {
      try {
        await fetch(`${E2E_CONFIG.apiBaseUrl}/api/v1/projects/${projectId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.warn('Failed to cleanup test project:', error);
      }
    }
    
    await page.close();
  });

  test('Complete User Journey: Registration to Workflow Execution', async () => {
    // Step 1: Navigate to homepage
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // Verify homepage loads
    await expect(page).toHaveTitle(/ArchMesh/);
    
    // Step 2: Register new user
    await clickElement(page, 'text=Sign Up');
    await waitForNavigation(page, '**/register');
    
    await fillFormField(page, 'input[name="email"]', testUser.email);
    await fillFormField(page, 'input[name="password"]', testUser.password);
    await fillFormField(page, 'input[name="name"]', testUser.name);
    
    await clickElement(page, 'button[type="submit"]');
    
    // Wait for registration to complete
    await waitForElement(page, 'text=Registration successful');
    
    // Step 3: Navigate to projects page
    await clickElement(page, 'text=Projects');
    await waitForNavigation(page, '**/projects');
    
    // Step 4: Create new project
    await clickElement(page, 'text=Create New Project');
    await waitForElement(page, 'form');
    
    await fillFormField(page, 'input[name="name"]', testProject.name);
    await fillFormField(page, 'textarea[name="description"]', testProject.description);
    await page.selectOption('select[name="domain"]', testProject.domain);
    
    await clickElement(page, 'button[type="submit"]');
    
    // Wait for project creation and redirect
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // Extract project ID from URL
    const url = page.url();
    const match = url.match(/\/projects\/([^\/]+)/);
    if (match) {
      projectId = match[1];
    }
    
    // Verify project detail page loads
    await expect(page.locator('h1')).toContainText(testProject.name);
    
    // Step 5: Start workflow
    await page.click('text=Start Workflow');
    await page.waitForURL(`**/projects/${projectId}/upload`);
    
    // Upload test document
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
    
    // Create and upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testContent)
    });
    
    // Fill additional context
    await page.fill('textarea[name="projectContext"]', 'E-commerce platform for online retail business');
    
    // Select LLM provider
    await page.selectOption('select[name="llmProvider"]', 'deepseek');
    
    // Submit workflow
    await page.click('button[type="submit"]');
    
    // Wait for workflow to start
    await page.waitForSelector('text=Workflow started successfully', { timeout: 10000 });
    
    // Step 6: Verify workflow status tracking
    // Should redirect back to project detail page with workflow parameter
    await page.waitForURL(/\/projects\/[^\/]+\?workflow=/, { timeout: 10000 });
    
    // Extract workflow ID from URL
    const workflowMatch = page.url().match(/workflow=([^&]+)/);
    if (workflowMatch) {
      workflowId = workflowMatch[1];
    }
    
    // Verify workflow status is displayed
    await page.waitForSelector('[data-testid="workflow-status"]', { timeout: 10000 });
    
    // Step 7: Monitor workflow progress using optimized helper function
    const finalStatus = await waitForWorkflowStatus(page, ['completed', 'failed']);
    
    // Step 8: Verify workflow completion or failure handling
    expect(finalStatus).toBeDefined();
    
    if (finalStatus?.toLowerCase().includes('failed')) {
      // If failed, should show error details and restart option
      await expect(page.locator('text=Restart')).toBeVisible();
    } else if (finalStatus?.toLowerCase().includes('completed')) {
      // If completed, should show results
      await expect(page.locator('text=Architecture')).toBeVisible();
    }
    
  });

  test('Workflow History and Error Handling', async () => {
    // This test verifies workflow history display and error handling
    
    // Navigate to projects page
    await page.goto(`${E2E_CONFIG.baseUrl}/projects`);
    await page.waitForLoadState('networkidle');
    
    // Create a project for testing
    await page.click('text=Create New Project');
    await page.fill('input[name="name"]', `Error Test Project ${Date.now()}`);
    await page.fill('textarea[name="description"]', 'Testing error handling');
    await page.selectOption('select[name="domain"]', 'cloud-native');
    await page.click('button[type="submit"]');
    
    // Wait for project creation
    await page.waitForURL(/\/projects\/[^\/]+/, { timeout: 10000 });
    
    // Navigate to workflows tab
    await page.click('text=Workflows');
    
    // Should show workflow history (even if empty)
    await expect(page.locator('text=Workflow Sessions')).toBeVisible();
    
    // Test error handling by trying to start workflow with invalid data
    await page.click('text=Start Workflow');
    await page.waitForURL(/\/upload/);
    
    // Try to submit without file
    await page.click('button[type="submit"]');
    
    // Should show validation error
    await expect(page.locator('text=Please upload a file first')).toBeVisible();
  });

  test('AI Chat Integration', async () => {
    // Test AI chat functionality with real backend
    
    await page.goto(E2E_CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    
    // Look for AI chat widget
    const aiChatButton = page.locator('[data-testid="ai-chat-toggle"]');
    if (await aiChatButton.isVisible()) {
      await aiChatButton.click();
      
      // Wait for chat interface to open
      await page.waitForSelector('[data-testid="ai-chat-interface"]', { timeout: 5000 });
      
      // Test sending a message
      const messageInput = page.locator('[data-testid="ai-chat-input"]');
      await messageInput.fill('Hello, can you help me with architecture design?');
      
      const sendButton = page.locator('[data-testid="ai-chat-send"]');
      await sendButton.click();
      
      // Wait for response (or timeout)
      await page.waitForTimeout(10000);
      
      // Chat should handle the interaction gracefully
      await expect(page.locator('[data-testid="ai-chat-interface"]')).toBeVisible();
    }
  });

  test('Real-time Updates and Notifications', async () => {
    // Test real-time functionality
    
    await page.goto(`${E2E_CONFIG.baseUrl}/projects`);
    await page.waitForLoadState('networkidle');
    
    // Create a project
    await page.click('text=Create New Project');
    await page.fill('input[name="name"]', `Real-time Test ${Date.now()}`);
    await page.fill('textarea[name="description"]', 'Testing real-time updates');
    await page.selectOption('select[name="domain"]', 'cloud-native');
    await page.click('button[type="submit"]');
    
    // Wait for project creation
    await page.waitForURL(/\/projects\/[^\/]+/, { timeout: 10000 });
    
    // Should show success notification
    await expect(page.locator('text=Project created successfully')).toBeVisible();
    
    // Test workflow status updates
    await page.click('text=Start Workflow');
    await page.waitForURL(/\/upload/);
    
    // Upload a small test file
    const testContent = '# Test Requirements\n- Simple test requirement';
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testContent)
    });
    
    await page.click('button[type="submit"]');
    
    // Should show workflow started notification
    await expect(page.locator('text=Workflow started successfully')).toBeVisible();
  });

  test('Performance and Responsiveness', async () => {
    // Test application performance
    
    const startTime = Date.now();
    await page.goto(E2E_CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Should load within reasonable time
    expect(loadTime).toBeLessThan(5000); // 5 seconds max
    
    // Test responsive design
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Should still be functional on mobile
    await expect(page.locator('h1')).toBeVisible();
    
    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Should work on desktop
    await expect(page.locator('h1')).toBeVisible();
  });
});
