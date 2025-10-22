import { test, expect } from '@playwright/test';

test.describe('Team Collaboration Features', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to register page
    await page.goto('http://localhost:3000/register');
    await page.waitForLoadState('networkidle');

    // Register a new user
    await page.fill('input[id="email"]', `test-${Date.now()}@example.com`);
    await page.fill('input[id="password"]', 'TestPassword123');
    await page.fill('input[id="confirmPassword"]', 'TestPassword123');
    
    // Wait for button to be enabled
    await page.waitForSelector('button[type="submit"]:not([disabled])', { timeout: 15000 });
    await page.click('button[type="submit"]');

    // Wait for redirect to projects page or handle any errors
    try {
      await page.waitForURL('**/projects', { timeout: 15000 });
    } catch (error) {
      // If redirect fails, check current URL and try to navigate manually
      const currentUrl = page.url();
      console.log('Current URL after registration:', currentUrl);
      
      if (currentUrl.includes('/register')) {
        // Still on register page, try to navigate to projects
        await page.goto('http://localhost:3000/projects');
      }
    }
    
    await page.waitForLoadState('networkidle');
  });

  test('should display team collaboration section', async ({ page }) => {
    // Create a project first
    await page.click('button:has-text("Create Project")');
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    await page.fill('input[placeholder="Enter project name"]', 'Team Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for team collaboration');
    await page.click('[role="dialog"] button:has-text("Create Project")');
    
    // Wait for project to be created and navigate to detail page
    await page.waitForURL('**/projects/**', { timeout: 15000 });
    
    // Check if team collaboration section is visible
    await expect(page.locator('text=Team Members')).toBeVisible();
    await expect(page.locator('text=Add Member')).toBeVisible();
  });

  test('should add team member', async ({ page }) => {
    // Create a project first
    await page.click('button:has-text("Create Project")');
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    await page.fill('input[placeholder="Enter project name"]', 'Team Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for team collaboration');
    await page.click('[role="dialog"] button:has-text("Create Project")');
    
    // Wait for project to be created and navigate to detail page
    await page.waitForURL('**/projects/**', { timeout: 15000 });
    
    // Click Add Member button
    await page.click('button:has-text("Add Member")');
    
    // Fill in member details
    await page.fill('input[type="email"]', 'collaborator@example.com');
    await page.selectOption('select', 'collaborator');
    
    // Submit the form
    await page.click('button:has-text("Add Member")');
    
    // Check for success message
    await expect(page.locator('text=Team member invitation sent')).toBeVisible();
  });

  test('should display notification center', async ({ page }) => {
    // Create a project first
    await page.click('button:has-text("Create Project")');
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    await page.fill('input[placeholder="Enter project name"]', 'Notification Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for notifications');
    await page.click('[role="dialog"] button:has-text("Create Project")');
    
    // Wait for project to be created and navigate to detail page
    await page.waitForURL('**/projects/**', { timeout: 15000 });
    
    // Check if notification center is visible
    await expect(page.locator('button[aria-label*="notification"]')).toBeVisible();
  });

  test('should display workflow history', async ({ page }) => {
    // Create a project first
    await page.click('button:has-text("Create Project")');
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    await page.fill('input[placeholder="Enter project name"]', 'History Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for workflow history');
    await page.click('[role="dialog"] button:has-text("Create Project")');
    
    // Wait for project to be created and navigate to detail page
    await page.waitForURL('**/projects/**', { timeout: 15000 });
    
    // Check if workflow history section is visible (should show "No workflows yet" initially)
    await expect(page.locator('text=Workflow History')).toBeVisible();
  });
});
