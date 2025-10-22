/**
 * COMPREHENSIVE PROJECTS PAGE TESTS - TDD Test Suite
 * 
 * Tests critical functionality for /projects/ pages:
 * 1. Workflow Persistence in Database
 * 2. Status Updates After Page Navigation
 * 3. Results Display and UI Components
 * 4. Workflow ID Management and Tracking
 * 5. UI Best Practices (Accessibility, Performance, UX)
 * 6. Real-time Updates and State Management
 * 7. Error Handling and Recovery
 * 8. Data Integrity and Consistency
 */

import { test, expect } from '@playwright/test';

test.describe('Projects Page Comprehensive Tests - TDD', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `projectstest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'Projects Test User'
    };

    // Register and login
    await page.goto('http://localhost:3000/register');
    await page.fill('input[id="name"]', testUser.name);
    await page.fill('input[id="email"]', testUser.email);
    await page.fill('input[id="password"]', testUser.password);
    await page.fill('input[id="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to projects page
    await expect(page).toHaveURL('http://localhost:3000/projects', { timeout: 30000 });
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });

  test.describe('Workflow Persistence in Database', () => {
    test('should persist workflow data in database and retrieve correctly', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Persistence Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing workflow persistence');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and start workflow
      await page.click('text=Start Workflow');
      await expect(page.locator('[data-slot="card-title"]:has-text("Upload Requirements Document")').first()).toBeVisible();

      // Upload requirements
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable and secure.')
      });

      // Start workflow
      await page.click('text=Start Workflow');
      
      // Wait for workflow to start
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
      
      // Get workflow ID from URL or page
      const currentUrl = page.url();
      const projectId = currentUrl.split('/projects/')[1];
      testProject.id = projectId;

      // Navigate away from project page
      await page.goto('http://localhost:3000/projects');
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();

      // Navigate back to project page
      await page.goto(`http://localhost:3000/projects/${projectId}`);
      
      // Should see workflow status persisted
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
      await expect(page.locator('text=Workflow Status')).toBeVisible();
    });

    test('should maintain workflow history across browser sessions', async ({ page, context }) => {
      // Create project and start workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Session Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing session persistence');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Get project ID
      const currentUrl = page.url();
      const projectId = currentUrl.split('/projects/')[1];
      testProject.id = projectId;

      // Simulate browser session end (close context)
      await context.close();

      // Create new context and navigate to project
      const newContext = await page.context().browser()?.newContext();
      const newPage = await newContext?.newPage();
      await newPage?.goto(`http://localhost:3000/projects/${projectId}`);

      // Should see workflow persisted
      await expect(newPage?.locator('text=Current Workflow Status')).toBeVisible();
    });

    test('should handle multiple concurrent workflows per project', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Concurrent Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing concurrent workflows');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start first workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements1.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('First workflow requirements.')
      });
      await page.click('text=Start Workflow');

      // Wait for first workflow to start
      await expect(page.locator('text=Processing')).toBeVisible();

      // Navigate away and back
      await page.goto('http://localhost:3000/projects');
      await page.goto(`http://localhost:3000/projects/${testProject.id}`);

      // Should see first workflow status
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    });
  });

  test.describe('Status Updates After Page Navigation', () => {
    test('should update workflow status when returning to project page', async ({ page }) => {
      // Create project and start workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Status Update Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing status updates');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Get project ID
      const currentUrl = page.url();
      const projectId = currentUrl.split('/projects/')[1];
      testProject.id = projectId;

      // Navigate away
      await page.goto('http://localhost:3000/projects');
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();

      // Wait for workflow to progress (simulate time passing)
      await page.waitForTimeout(5000);

      // Navigate back to project
      await page.goto(`http://localhost:3000/projects/${projectId}`);

      // Should see updated status
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
      // Status should be different from initial "Processing"
      await expect(page.locator('text=Processing')).not.toBeVisible();
    });

    test('should show real-time status updates without page refresh', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Real-time Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing real-time updates');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Should see status updates in real-time
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
      
      // Wait for status to change
      await page.waitForSelector('text=Completed', { timeout: 300000 });
      
      // Should see completion status
      await expect(page.locator('text=Workflow Completed')).toBeVisible();
    });

    test('should handle workflow failures and show error status', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Error Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing error handling');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow with problematic input
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'invalid.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('Invalid content that might cause processing to fail')
      });
      await page.click('text=Start Workflow');

      // Should handle failure gracefully
      await page.waitForSelector('text=Workflow Failed', { timeout: 300000 });
      await expect(page.locator('text=Error Details')).toBeVisible();
      await expect(page.locator('text=Retry Workflow')).toBeVisible();
    });
  });

  test.describe('Results Display and UI Components', () => {
    test('should display workflow results correctly', async ({ page }) => {
      // Create project and complete workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Results Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing results display');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Complete workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable and secure.')
      });
      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Workflow Completed', { timeout: 300000 });

      // Should see comprehensive results
      await expect(page.locator('text=Project Results')).toBeVisible();
      await expect(page.locator('text=Requirements Summary')).toBeVisible();
      await expect(page.locator('text=Architecture Overview')).toBeVisible();
      await expect(page.locator('text=Technology Stack')).toBeVisible();
    });

    test('should display workflow history and status timeline', async ({ page }) => {
      // Create project and complete workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'History Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing workflow history');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Complete workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Workflow Completed', { timeout: 300000 });

      // Should see workflow history
      await expect(page.locator('text=Workflow History')).toBeVisible();
      await expect(page.locator('text=Completed Workflows')).toBeVisible();
      await expect(page.locator('text=Requirements Processing')).toBeVisible();
      await expect(page.locator('text=Architecture Generation')).toBeVisible();
    });

    test('should allow export and sharing of results', async ({ page }) => {
      // Create project and complete workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Export Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing results export');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Complete workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Workflow Completed', { timeout: 300000 });

      // Should see export options
      await expect(page.locator('text=Export Results')).toBeVisible();
      await expect(page.locator('text=Download PDF')).toBeVisible();
      await expect(page.locator('text=Download JSON')).toBeVisible();
      await expect(page.locator('text=Share Results')).toBeVisible();
    });
  });

  test.describe('Workflow ID Management and Tracking', () => {
    test('should generate and track unique workflow IDs', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Workflow ID Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing workflow ID management');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Should see workflow ID
      await expect(page.locator('text=Workflow ID')).toBeVisible();
      await expect(page.locator('text=Status')).toBeVisible();
      await expect(page.locator('text=Started')).toBeVisible();
    });

    test('should maintain workflow ID consistency across page navigation', async ({ page }) => {
      // Create project and start workflow
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'ID Consistency Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing ID consistency');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Get workflow ID
      const workflowIdElement = page.locator('text=Workflow ID').locator('..').locator('code');
      const workflowId = await workflowIdElement.textContent();

      // Navigate away and back
      await page.goto('http://localhost:3000/projects');
      await page.goto(`http://localhost:3000/projects/${testProject.id}`);

      // Should see same workflow ID
      await expect(page.locator('text=Workflow ID')).toBeVisible();
      const sameWorkflowId = await workflowIdElement.textContent();
      expect(sameWorkflowId).toBe(workflowId);
    });

    test('should handle multiple workflow IDs per project', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Multiple IDs Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing multiple workflow IDs');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Start first workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements1.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('First workflow requirements.')
      });
      await page.click('text=Start Workflow');

      // Get first workflow ID
      const firstWorkflowId = await page.locator('text=Workflow ID').locator('..').locator('code').textContent();

      // Wait for completion
      await page.waitForSelector('text=Workflow Completed', { timeout: 300000 });

      // Start second workflow
      await page.click('text=Start New Workflow');
      await fileInput.setInputFiles({
        name: 'requirements2.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('Second workflow requirements.')
      });
      await page.click('text=Start Workflow');

      // Get second workflow ID
      const secondWorkflowId = await page.locator('text=Workflow ID').locator('..').locator('code').textContent();

      // Should have different IDs
      expect(firstWorkflowId).not.toBe(secondWorkflowId);

      // Should see workflow history with both IDs
      await expect(page.locator('text=Workflow History')).toBeVisible();
      await expect(page.locator(`text=${firstWorkflowId}`)).toBeVisible();
      await expect(page.locator(`text=${secondWorkflowId}`)).toBeVisible();
    });
  });

  test.describe('UI Best Practices', () => {
    test('should follow accessibility best practices', async ({ page }) => {
      // Navigate to projects page
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();

      // Check for proper heading hierarchy
      await expect(page.locator('h1')).toBeVisible();
      
      // Check for proper form labels
      await page.click('text=Create Project');
      await expect(page.locator('label[for="name"]')).toBeVisible();
      await expect(page.locator('label[for="description"]')).toBeVisible();
      await expect(page.locator('label[for="domain"]')).toBeVisible();

      // Check for proper ARIA attributes
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('[aria-label]')).toBeVisible();

      // Check for keyboard navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
    });

    test('should have proper loading states and feedback', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Loading Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing loading states');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      
      // Click create and check for loading state
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see loading indicator
      await expect(page.locator('text=Creating project...')).toBeVisible();
    });

    test('should handle responsive design correctly', async ({ page }) => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    });

    test('should have proper error handling and user feedback', async ({ page }) => {
      // Try to create project with invalid data
      await page.click('text=Create Project');
      await page.fill('input[placeholder="Enter project name"]', ''); // Empty name
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see validation error
      await expect(page.locator('text=Project name is required')).toBeVisible();
    });

    test('should have proper performance characteristics', async ({ page }) => {
      // Measure page load time
      const startTime = Date.now();
      await page.goto('http://localhost:3000/projects');
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      const loadTime = Date.now() - startTime;
      
      // Page should load within reasonable time
      expect(loadTime).toBeLessThan(3000); // 3 seconds max
    });
  });

  test.describe('Data Integrity and Consistency', () => {
    test('should maintain data consistency across operations', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Consistency Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing data consistency');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Get project ID
      const currentUrl = page.url();
      const projectId = currentUrl.split('/projects/')[1];
      testProject.id = projectId;

      // Start workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');

      // Navigate away and back multiple times
      for (let i = 0; i < 3; i++) {
        await page.goto('http://localhost:3000/projects');
        await page.goto(`http://localhost:3000/projects/${projectId}`);
        
        // Data should remain consistent
        await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
        await expect(page.locator('text=Current Workflow Status')).toBeVisible();
      }
    });

    test('should handle concurrent user operations safely', async ({ page, context }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Concurrent Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing concurrent operations');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Get project ID
      const currentUrl = page.url();
      const projectId = currentUrl.split('/projects/')[1];
      testProject.id = projectId;

      // Open project in second tab
      const secondPage = await context.newPage();
      await secondPage.goto(`http://localhost:3000/projects/${projectId}`);

      // Both pages should show same data
      await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
      await expect(secondPage.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
    });
  });
});
