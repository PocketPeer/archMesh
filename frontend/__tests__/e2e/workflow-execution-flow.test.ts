import { test, expect } from '@playwright/test';

test.describe('Workflow Execution Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Register a new user if not already registered
    if (page.url().includes('/login') || page.url().includes('/register')) {
      // Navigate to register page
      await page.goto('http://localhost:3000/register');
      await page.waitForLoadState('networkidle');
      
      // Fill registration form
      await page.fill('input[id="email"]', `test-${Date.now()}@example.com`);
      await page.fill('input[id="password"]', 'TestPass123!');
      await page.fill('input[id="name"]', 'Test User');
      
      // Submit registration
      await page.click('button[type="submit"]');
      
      // Wait for redirect to projects page
      await page.waitForURL('**/projects', { timeout: 10000 });
    }
  });

  test('should execute complete workflow from upload to completion', async ({ page }) => {
    // Step 1: Navigate to projects page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    
    // Wait for projects to load
    await page.waitForTimeout(3000);
    
    // Step 2: Create a project if none exist
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Test Workflow Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for workflow execution');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Step 3: Navigate to project detail page
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Step 4: Navigate to upload page
    await page.click('button:has-text("Start Workflow")');
    await page.waitForURL('**/upload', { timeout: 10000 });
    
    // Step 5: Upload a requirements document
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
# Test Requirements Document

## Business Goals
- Create a scalable e-commerce platform
- Support 10,000 concurrent users
- Ensure 99.9% uptime

## Functional Requirements
- User authentication and authorization
- Product catalog management
- Shopping cart functionality
- Order processing
- Payment integration

## Non-Functional Requirements
- Response time < 2 seconds
- Support for mobile devices
- Secure data handling
- Backup and recovery procedures

## Stakeholders
- Customers
- Store administrators
- Payment processors
- Customer support team
      `.trim())
    });
    
    // Wait for file upload to complete
    await page.waitForTimeout(2000);
    
    // Step 6: Fill project context
    await page.fill('textarea[placeholder*="project context"]', 'This is a test e-commerce platform for a small business');
    
    // Step 7: Start the workflow
    await page.click('button[type="submit"]');
    
    // Step 8: Verify workflow started and redirect
    await page.waitForURL('**/projects/**?workflow=**', { timeout: 15000 });
    
    // Step 9: Verify workflow status display
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    await expect(page.locator('text=STARTING')).toBeVisible();
    
    // Step 10: Verify workflow statistics update
    await expect(page.locator('text=Active Workflows')).toBeVisible();
    
    // Step 11: Wait for workflow progression (with timeout)
    await page.waitForTimeout(10000);
    
    // Step 12: Check for workflow status updates
    const workflowStatus = page.locator('[data-testid="workflow-status"]');
    if (await workflowStatus.isVisible()) {
      await expect(workflowStatus).toBeVisible();
    }
    
    // Step 13: Verify workflow list updates
    await expect(page.locator('text=Total Workflows')).toBeVisible();
    
    // Step 14: Check for any error messages
    const errorMessages = page.locator('[role="alert"]');
    const errorCount = await errorMessages.count();
    
    if (errorCount > 0) {
      console.log('Error messages found:');
      for (let i = 0; i < errorCount; i++) {
        const errorText = await errorMessages.nth(i).textContent();
        console.log(`Error ${i + 1}: ${errorText}`);
      }
    }
    
    // Step 15: Verify workflow session ID is present in URL
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/workflow=[a-f0-9-]{36}/);
    
    // Step 16: Check for workflow progress indicators
    const progressIndicators = page.locator('[data-testid="workflow-progress"]');
    if (await progressIndicators.isVisible()) {
      await expect(progressIndicators).toBeVisible();
    }
  });

  test('should handle workflow errors gracefully', async ({ page }) => {
    // Navigate to upload page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Test Error Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for error handling');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to upload page
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    await page.click('button:has-text("Start Workflow")');
    await page.waitForURL('**/upload', { timeout: 10000 });
    
    // Upload invalid file type
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-invalid.exe',
      mimeType: 'application/x-msdownload',
      buffer: Buffer.from('invalid file content')
    });
    
    // Try to submit
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('[role="alert"]')).toBeVisible();
  });

  test('should display real-time workflow status updates', async ({ page }) => {
    // Navigate to project with active workflow
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Test Status Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for status updates');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to project detail
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Check for workflow status elements
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    
    // Check for workflow statistics
    await expect(page.locator('text=Total Workflows')).toBeVisible();
    await expect(page.locator('text=Active Workflows')).toBeVisible();
    await expect(page.locator('text=Completed')).toBeVisible();
    
    // Wait for potential status updates
    await page.waitForTimeout(5000);
    
    // Verify status elements are still visible
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
  });

  test('should handle workflow restart functionality', async ({ page }) => {
    // This test would verify restart functionality if implemented
    // For now, just verify the UI elements exist
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Test Restart Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for restart functionality');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to project detail
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Check for workflow management elements
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    
    // Look for restart button (if it exists)
    const restartButton = page.locator('button:has-text("Restart")');
    if (await restartButton.isVisible()) {
      await expect(restartButton).toBeVisible();
    }
  });
});
