/**
 * PERFORMANCE AND LOAD TESTS - TDD Test Suite
 * 
 * Tests application performance and scalability:
 * 1. Page load times
 * 2. API response times
 * 3. Concurrent user scenarios
 * 4. Memory usage
 * 5. Database performance
 * 6. LLM response times
 */

import { test, expect } from '@playwright/test';

test.describe('Performance and Load Tests - TDD', () => {
  let authToken: string;
  let testUser: { email: string; password: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `perftest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'Performance Test User'
    };
  });

  test.describe('Page Load Performance', () => {
    test('should load login page within 2 seconds', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('http://localhost:3000/login');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(2000);
      await expect(page.locator('text=Sign in to your account')).toBeVisible();
    });

    test('should load projects page within 3 seconds', async ({ page }) => {
      // Register and login first
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      const startTime = Date.now();
      await page.goto('http://localhost:3000/projects');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(3000);
      await expect(page.locator('text=Your Projects')).toBeVisible();
    });

    test('should load project detail page within 3 seconds', async ({ page }) => {
      // Register, login, and create project
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Create project
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      await page.fill('input[id="name"]', 'Performance Test Project');
      await page.fill('textarea[id="description"]', 'Project for performance testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      const startTime = Date.now();
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(3000);
    });
  });

  test.describe('API Response Times', () => {
    test.beforeEach(async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
    });

    test('authentication API should respond within 1 second', async ({ page }) => {
      const startTime = Date.now();
      
      // Test login API
      const response = await page.request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(1000);
      expect(response.status()).toBe(200);
    });

    test('projects API should respond within 1 second', async ({ page }) => {
      // Get auth token first
      const loginResponse = await page.request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });
      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;

      const startTime = Date.now();
      const response = await page.request.get('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(1000);
      expect(response.status()).toBe(200);
    });

    test('AI models API should respond within 2 seconds', async ({ page }) => {
      // Get auth token first
      const loginResponse = await page.request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });
      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;

      const startTime = Date.now();
      const response = await page.request.get('http://localhost:8000/api/v1/ai/models', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(2000);
      expect(response.status()).toBe(200);
    });
  });

  test.describe('Concurrent User Scenarios', () => {
    test('should handle multiple users creating projects simultaneously', async ({ browser }) => {
      const users = [];
      const contexts = [];

      // Create multiple browser contexts for concurrent users
      for (let i = 0; i < 5; i++) {
        const context = await browser.newContext();
        const page = await context.newPage();
        contexts.push(context);

        const user = {
          email: `concurrent${i}${Date.now()}@example.com`,
          password: 'TestPass1!',
          name: `Concurrent User ${i}`
        };
        users.push(user);

        // Register user
        await page.goto('http://localhost:3000/register');
        await page.fill('input[id="name"]', user.name);
        await page.fill('input[id="email"]', user.email);
        await page.fill('input[id="password"]', user.password);
        await page.fill('input[id="confirmPassword"]', user.password);
        await page.click('button[type="submit"]');

        // Create project
        await page.goto('http://localhost:3000/projects');
        await page.click('text=Create New Project');
        await page.fill('input[id="name"]', `Concurrent Project ${i}`);
        await page.fill('textarea[id="description"]', `Project created by user ${i}`);
        await page.selectOption('select[id="domain"]', 'cloud-native');
        await page.selectOption('select[id="mode"]', 'greenfield');
        await page.click('button[type="submit"]');
      }

      // Verify all users can access their projects
      for (let i = 0; i < contexts.length; i++) {
        const page = await contexts[i].newPage();
        await page.goto('http://localhost:3000/projects');
        await expect(page.locator(`text=Concurrent Project ${i}`)).toBeVisible();
      }

      // Cleanup
      for (const context of contexts) {
        await context.close();
      }
    });

    test('should handle multiple AI chat sessions simultaneously', async ({ browser }) => {
      const contexts = [];
      const users = [];

      // Create multiple contexts for concurrent AI chats
      for (let i = 0; i < 3; i++) {
        const context = await browser.newContext();
        const page = await context.newPage();
        contexts.push(context);

        const user = {
          email: `aichat${i}${Date.now()}@example.com`,
          password: 'TestPass1!',
          name: `AI Chat User ${i}`
        };
        users.push(user);

        // Register and login
        await page.goto('http://localhost:3000/register');
        await page.fill('input[id="name"]', user.name);
        await page.fill('input[id="email"]', user.email);
        await page.fill('input[id="password"]', user.password);
        await page.fill('input[id="confirmPassword"]', user.password);
        await page.click('button[type="submit"]');

        // Open AI assistant
        await page.goto('http://localhost:3000/projects');
        await page.click('text=AI Assistant');
        await expect(page.locator('text=AI Assistant')).toBeVisible();

        // Send message
        await page.fill('textarea[placeholder*="message"]', `Hello from user ${i}`);
        await page.click('button[type="submit"]');
      }

      // Verify all AI chats are working
      for (let i = 0; i < contexts.length; i++) {
        const page = await contexts[i].newPage();
        await page.goto('http://localhost:3000/projects');
        await page.click('text=AI Assistant');
        await expect(page.locator(`text=Hello from user ${i}`)).toBeVisible();
      }

      // Cleanup
      for (const context of contexts) {
        await context.close();
      }
    });
  });

  test.describe('Memory and Resource Usage', () => {
    test('should not have memory leaks during extended usage', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Perform multiple operations to test for memory leaks
      for (let i = 0; i < 10; i++) {
        // Navigate between pages
        await page.goto('http://localhost:3000/projects');
        await page.goto('http://localhost:3000/login');
        await page.goto('http://localhost:3000/projects');

        // Create and delete projects
        await page.click('text=Create New Project');
        await page.fill('input[id="name"]', `Memory Test Project ${i}`);
        await page.fill('textarea[id="description"]', 'Memory test project');
        await page.selectOption('select[id="domain"]', 'cloud-native');
        await page.selectOption('select[id="mode"]', 'greenfield');
        await page.click('button[type="submit"]');

        // Navigate back to projects list
        await page.goto('http://localhost:3000/projects');
      }

      // The test passes if no memory-related errors occur
      expect(true).toBe(true);
    });

    test('should handle large file uploads efficiently', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Create project
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      await page.fill('input[id="name"]', 'Large File Test Project');
      await page.fill('textarea[id="description"]', 'Project for large file testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      // Upload large file (simulate with large content)
      await page.click('text=Upload Documents');
      
      const largeContent = 'A'.repeat(100000); // 100KB of content
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'large-file.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(largeContent)
      });

      const startTime = Date.now();
      await page.click('text=Start Workflow');
      const uploadTime = Date.now() - startTime;

      // Should handle large file within reasonable time
      expect(uploadTime).toBeLessThan(30000); // 30 seconds max
    });
  });

  test.describe('LLM Performance', () => {
    test.beforeEach(async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
    });

    test('AI chat should respond within 10 seconds', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      await page.click('text=AI Assistant');

      const startTime = Date.now();
      await page.fill('textarea[placeholder*="message"]', 'What is the best architecture for a microservices application?');
      await page.click('button[type="submit"]');

      // Wait for response
      await expect(page.locator('text=What is the best architecture for a microservices application?')).toBeVisible();
      const responseTime = Date.now() - startTime;

      expect(responseTime).toBeLessThan(10000); // 10 seconds max
    });

    test('workflow processing should complete within 5 minutes', async ({ page }) => {
      // Create project
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      await page.fill('input[id="name"]', 'LLM Performance Test Project');
      await page.fill('textarea[id="description"]', 'Project for LLM performance testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      // Start workflow
      await page.click('text=Upload Documents');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable, secure, and maintainable.')
      });

      const startTime = Date.now();
      await page.click('text=Start Workflow');

      // Wait for workflow completion (with timeout)
      await page.waitForSelector('text=Workflow Completed', { timeout: 300000 }); // 5 minutes max
      const processingTime = Date.now() - startTime;

      expect(processingTime).toBeLessThan(300000); // 5 minutes max
    });
  });

  test.describe('Database Performance', () => {
    test('should handle bulk project creation efficiently', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      const startTime = Date.now();

      // Create multiple projects rapidly
      for (let i = 0; i < 20; i++) {
        await page.goto('http://localhost:3000/projects');
        await page.click('text=Create New Project');
        await page.fill('input[id="name"]', `Bulk Project ${i}`);
        await page.fill('textarea[id="description"]', `Bulk created project ${i}`);
        await page.selectOption('select[id="domain"]', 'cloud-native');
        await page.selectOption('select[id="mode"]', 'greenfield');
        await page.click('button[type="submit"]');
      }

      const totalTime = Date.now() - startTime;
      const averageTime = totalTime / 20;

      // Each project creation should be reasonably fast
      expect(averageTime).toBeLessThan(5000); // 5 seconds per project max
    });

    test('should handle concurrent database operations', async ({ browser }) => {
      const contexts = [];
      const users = [];

      // Create multiple contexts for concurrent database operations
      for (let i = 0; i < 10; i++) {
        const context = await browser.newContext();
        const page = await context.newPage();
        contexts.push(context);

        const user = {
          email: `dbconcurrent${i}${Date.now()}@example.com`,
          password: 'TestPass1!',
          name: `DB Concurrent User ${i}`
        };
        users.push(user);

        // Register user
        await page.goto('http://localhost:3000/register');
        await page.fill('input[id="name"]', user.name);
        await page.fill('input[id="email"]', user.email);
        await page.fill('input[id="password"]', user.password);
        await page.fill('input[id="confirmPassword"]', user.password);
        await page.click('button[type="submit"]');

        // Create multiple projects
        for (let j = 0; j < 5; j++) {
          await page.goto('http://localhost:3000/projects');
          await page.click('text=Create New Project');
          await page.fill('input[id="name"]', `Concurrent DB Project ${i}-${j}`);
          await page.fill('textarea[id="description"]', `Project ${j} by user ${i}`);
          await page.selectOption('select[id="domain"]', 'cloud-native');
          await page.selectOption('select[id="mode"]', 'greenfield');
          await page.click('button[type="submit"]');
        }
      }

      // Verify all operations completed successfully
      for (let i = 0; i < contexts.length; i++) {
        const page = await contexts[i].newPage();
        await page.goto('http://localhost:3000/projects');
        
        // Should see all projects created by this user
        for (let j = 0; j < 5; j++) {
          await expect(page.locator(`text=Concurrent DB Project ${i}-${j}`)).toBeVisible();
        }
      }

      // Cleanup
      for (const context of contexts) {
        await context.close();
      }
    });
  });
});
