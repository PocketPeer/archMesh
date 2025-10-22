import { test, expect } from '@playwright/test';

test.describe('Project Navigation', () => {
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

  test('should navigate from projects overview to project details', async ({ page }) => {
    // Ensure we're on the projects page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    
    // Wait for projects to load (or show empty state)
    await page.waitForTimeout(3000);
    
    // Check if we have projects or need to create one
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    
    if (!hasProjects) {
      // Create a new project
      await page.click('button:has-text("Create Project")');
      
      // Wait for dialog to open
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      
      // Fill project creation form
      await page.fill('input[placeholder="Enter project name"]', 'Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project description');
      
      // Submit project creation
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Wait for project to be created and redirect
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Now we should have at least one project
    const projectCard = page.locator('[data-slot="card"]').first();
    await expect(projectCard).toBeVisible();
    
    // Click on the first project card
    await projectCard.click();
    
    // Should navigate to project detail page
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Verify we're on the project detail page
    await expect(page.locator('h1')).toBeVisible();
    
    // Check for project details elements
    await expect(page.locator('[data-slot="card"]')).toBeVisible();
  });

  test('should handle authentication redirects properly', async ({ page }) => {
    // Test unauthenticated access to projects page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    
    // Should redirect to login page
    await page.waitForURL('**/login', { timeout: 10000 });
    
    // Test unauthenticated access to project detail page
    await page.goto('http://localhost:3000/projects/test-project-id');
    await page.waitForLoadState('networkidle');
    
    // Should redirect to login page
    await page.waitForURL('**/login', { timeout: 10000 });
  });

  test('should display project details correctly', async ({ page }) => {
    // First, ensure we're authenticated and have a project
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    
    // Wait for projects to load
    await page.waitForTimeout(3000);
    
    // Create a project if none exist
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project description');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to project details
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Verify project details page elements
    await expect(page.locator('h1')).toBeVisible();
    
    // Check for tabs
    await expect(page.locator('[role="tablist"]')).toBeVisible();
    
    // Check for project information
    await expect(page.locator('[data-slot="card"]')).toBeVisible();
    
    // Check for navigation elements
    await expect(page.locator('button:has-text("Back to Projects")')).toBeVisible();
  });

  test('should handle project not found gracefully', async ({ page }) => {
    // Navigate to a non-existent project
    await page.goto('http://localhost:3000/projects/non-existent-project-id');
    await page.waitForLoadState('networkidle');
    
    // Should either redirect to login or show error
    const currentUrl = page.url();
    const isLoginPage = currentUrl.includes('/login');
    const isErrorPage = await page.locator('text=404').isVisible();
    
    expect(isLoginPage || isErrorPage).toBeTruthy();
  });

  test('should maintain project state during navigation', async ({ page }) => {
    // Navigate to projects page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    
    // Wait for projects to load
    await page.waitForTimeout(2000);
    
    // Create a project if none exist
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.fill('input[placeholder="Enter project name"]', 'Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project description');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 10000 });
    }
    
    // Navigate to project details
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Navigate back to projects
    await page.click('button:has-text("Back to Projects")');
    await page.waitForURL('**/projects', { timeout: 10000 });
    
    // Verify we're back on projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });
});
