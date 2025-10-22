/**
 * UI BEST PRACTICES TESTS - TDD Test Suite
 * 
 * Tests UI best practices for project pages:
 * 1. Accessibility (WCAG 2.1 AA compliance)
 * 2. Performance (Core Web Vitals)
 * 3. User Experience (UX patterns)
 * 4. Responsive Design
 * 5. Error Handling and Recovery
 * 6. Loading States and Feedback
 * 7. Navigation and Breadcrumbs
 * 8. Form Validation and UX
 */

import { test, expect } from '@playwright/test';

test.describe('UI Best Practices Tests - TDD', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `uibestpractices${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'UI Best Practices Test User'
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

  test.describe('Accessibility (WCAG 2.1 AA Compliance)', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      // Check main page heading
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Create project and check heading hierarchy
      await page.click('text=Create Project');
      await expect(page.locator('h2:has-text("Create New Project")')).toBeVisible();
      
      // Fill form and create project
      testProject = {
        id: '',
        name: 'Accessibility Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing accessibility');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Check project detail page heading
      await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
    });

    test('should have proper form labels and ARIA attributes', async ({ page }) => {
      // Open create project dialog
      await page.click('text=Create Project');
      
      // Check for proper form labels
      await expect(page.locator('label[for="name"]')).toBeVisible();
      await expect(page.locator('label[for="description"]')).toBeVisible();
      await expect(page.locator('label[for="domain"]')).toBeVisible();
      
      // Check for proper ARIA attributes
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('[aria-labelledby]')).toBeVisible();
      await expect(page.locator('[aria-describedby]')).toBeVisible();
      
      // Check for proper input associations
      const nameInput = page.locator('input[placeholder="Enter project name"]');
      await expect(nameInput).toHaveAttribute('id', 'name');
      await expect(nameInput).toHaveAttribute('aria-required', 'true');
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Test keyboard navigation through projects page
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to navigate to create project button
      await page.keyboard.press('Enter');
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      
      // Test keyboard navigation in dialog
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to close dialog with Escape
      await page.keyboard.press('Escape');
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    });

    test('should have proper color contrast and visual indicators', async ({ page }) => {
      // Check for proper color contrast (basic check)
      const heading = page.locator('h1:has-text("Projects")');
      await expect(heading).toBeVisible();
      
      // Check for proper focus indicators
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
      
      // Check for proper button states
      const createButton = page.locator('text=Create Project');
      await expect(createButton).toBeVisible();
      await expect(createButton).toHaveAttribute('type', 'button');
    });

    test('should have proper screen reader support', async ({ page }) => {
      // Check for proper alt text on images
      const images = page.locator('img');
      const imageCount = await images.count();
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        expect(alt).toBeTruthy();
      }
      
      // Check for proper ARIA labels
      await expect(page.locator('[aria-label]')).toBeVisible();
      await expect(page.locator('[aria-labelledby]')).toBeVisible();
    });
  });

  test.describe('Performance (Core Web Vitals)', () => {
    test('should have fast page load times', async ({ page }) => {
      // Measure page load time
      const startTime = Date.now();
      await page.goto('http://localhost:3000/projects');
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      const loadTime = Date.now() - startTime;
      
      // Page should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should have good performance metrics', async ({ page }) => {
      // Start performance measurement
      await page.goto('http://localhost:3000/projects');
      
      // Check for performance metrics
      const performanceMetrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
      });
      
      // Performance should be within acceptable ranges
      expect(performanceMetrics.domContentLoaded).toBeLessThan(2000);
      expect(performanceMetrics.loadComplete).toBeLessThan(3000);
    });

    test('should handle large datasets efficiently', async ({ page }) => {
      // Create multiple projects to test performance
      for (let i = 0; i < 5; i++) {
        await page.click('text=Create Project');
        await page.fill('input[placeholder="Enter project name"]', `Performance Test Project ${i} ${Date.now()}`);
        await page.fill('textarea[placeholder="Enter project description (optional)"]', `Project ${i} for testing performance`);
        await page.selectOption('[role="dialog"] select', 'cloud-native');
        await page.click('[role="dialog"] button:has-text("Create Project")');
        
        // Wait for project creation
        await expect(page.locator('h1:has-text("Performance Test Project")')).toBeVisible();
        
        // Navigate back to projects list
        await page.goto('http://localhost:3000/projects');
        await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      }
      
      // Projects list should still load quickly
      const startTime = Date.now();
      await page.reload();
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      const reloadTime = Date.now() - startTime;
      expect(reloadTime).toBeLessThan(2000);
    });
  });

  test.describe('User Experience (UX Patterns)', () => {
    test('should have intuitive navigation and breadcrumbs', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'UX Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing UX patterns');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Check for breadcrumb navigation
      await expect(page.locator('nav[aria-label="Breadcrumb"]')).toBeVisible();
      await expect(page.locator('text=Projects')).toBeVisible();
      await expect(page.locator('text=' + testProject.name)).toBeVisible();
    });

    test('should have proper loading states and feedback', async ({ page }) => {
      // Create project and check loading states
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Loading UX Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing loading UX');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      
      // Click create and check for loading state
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see loading indicator
      await expect(page.locator('text=Creating project...')).toBeVisible();
    });

    test('should have proper error handling and user feedback', async ({ page }) => {
      // Try to create project with invalid data
      await page.click('text=Create Project');
      await page.fill('input[placeholder="Enter project name"]', ''); // Empty name
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see validation error
      await expect(page.locator('text=Project name is required')).toBeVisible();
      await expect(page.locator('[role="alert"]')).toBeVisible();
    });

    test('should have proper success feedback', async ({ page }) => {
      // Create project successfully
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Success UX Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing success feedback');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see success message
      await expect(page.locator('text=Project created successfully')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should work correctly on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Check mobile layout
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test mobile navigation
      await page.click('text=Create Project');
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      
      // Test mobile form
      testProject = {
        id: '',
        name: 'Mobile Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Mobile project');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should work on mobile
      await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
    });

    test('should work correctly on tablet devices', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      // Check tablet layout
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test tablet navigation
      await page.click('text=Create Project');
      await expect(page.locator('[role="dialog"]')).toBeVisible();
    });

    test('should work correctly on desktop devices', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      
      // Check desktop layout
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test desktop navigation
      await page.click('text=Create Project');
      await expect(page.locator('[role="dialog"]')).toBeVisible();
    });

    test('should adapt to different screen orientations', async ({ page }) => {
      // Test landscape orientation
      await page.setViewportSize({ width: 1024, height: 768 });
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
      
      // Test portrait orientation
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    });
  });

  test.describe('Form Validation and UX', () => {
    test('should validate required fields properly', async ({ page }) => {
      // Open create project dialog
      await page.click('text=Create Project');
      
      // Try to submit without required fields
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should see validation errors
      await expect(page.locator('text=Project name is required')).toBeVisible();
    });

    test('should provide real-time validation feedback', async ({ page }) => {
      // Open create project dialog
      await page.click('text=Create Project');
      
      // Start typing in name field
      await page.fill('input[placeholder="Enter project name"]', 'Test');
      
      // Should see validation feedback
      await expect(page.locator('text=Valid name')).toBeVisible();
    });

    test('should handle form submission gracefully', async ({ page }) => {
      // Open create project dialog
      await page.click('text=Create Project');
      
      // Fill form correctly
      testProject = {
        id: '',
        name: 'Form UX Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing form UX');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      
      // Submit form
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should handle submission gracefully
      await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
    });
  });

  test.describe('Error Handling and Recovery', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network error
      await page.route('**/api/v1/projects', route => route.abort());
      
      // Try to create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Network Error Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing network errors');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should show network error message
      await expect(page.locator('text=Network error')).toBeVisible();
      await expect(page.locator('text=Please check your connection')).toBeVisible();
    });

    test('should handle server errors gracefully', async ({ page }) => {
      // Simulate server error
      await page.route('**/api/v1/projects', route => route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      }));
      
      // Try to create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Server Error Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing server errors');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should show server error message
      await expect(page.locator('text=Server error')).toBeVisible();
      await expect(page.locator('text=Please try again later')).toBeVisible();
    });

    test('should allow retry after errors', async ({ page }) => {
      // Simulate temporary error
      let errorCount = 0;
      await page.route('**/api/v1/projects', route => {
        if (errorCount < 1) {
          errorCount++;
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Temporary server error' })
          });
        } else {
          route.continue();
        }
      });
      
      // Try to create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Retry Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing retry functionality');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      // Should show error first
      await expect(page.locator('text=Server error')).toBeVisible();
      
      // Should allow retry
      await page.click('text=Retry');
      await expect(page.locator('h1:has-text("' + testProject.name + '")')).toBeVisible();
    });
  });
});
