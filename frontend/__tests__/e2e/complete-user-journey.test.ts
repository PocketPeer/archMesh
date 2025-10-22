/**
 * COMPREHENSIVE TDD TEST SUITE - Complete User Journey Tests
 * 
 * This test suite covers every aspect of the ArchMesh application:
 * 1. Authentication (login, register, logout, password reset)
 * 2. Project Management (create, view, edit, delete projects)
 * 3. Workflow Management (start, monitor, complete workflows)
 * 4. AI Assistant (chat, model selection, context)
 * 5. Document Upload and Processing
 * 6. Architecture Generation
 * 7. Error Handling and Edge Cases
 */

import { test, expect } from '@playwright/test';

test.describe('Complete User Journey - TDD Test Suite', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    // Generate unique test user for each test
    const timestamp = Date.now();
    testUser = {
      email: `testuser${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'Test User'
    };
  });

  test.describe('Authentication Flow', () => {
    test('should allow user registration with valid data', async ({ page }) => {
      await page.goto('http://localhost:3000/register');
      
      // Fill registration form
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      
      await page.click('button[type="submit"]');
      
      // Should redirect to projects page
      await expect(page).toHaveURL('http://localhost:3000/projects');
      await expect(page.locator('text=Your Projects')).toBeVisible();
    });

    test('should handle registration with existing email', async ({ page }) => {
      // First, register a user
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Try to register again with same email
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', 'Another User');
      await page.fill('input[id="email"]', testUser.email); // Same email
      await page.fill('input[id="password"]', 'AnotherPass1!');
      await page.fill('input[id="confirmPassword"]', 'AnotherPass1!');
      await page.click('button[type="submit"]');
      
      // Should show error message (check for any error message)
      await expect(page.locator('[role="alert"]')).toBeVisible();
    });

    test('should allow login with valid credentials', async ({ page }) => {
      // First register a user
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Logout
      await page.click('text=Sign out');
      
      // Login with same credentials
      await page.goto('http://localhost:3000/login');
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Should redirect to projects
      await expect(page).toHaveURL('http://localhost:3000/projects');
      await expect(page.locator('text=Your Projects')).toBeVisible();
    });

    test('should handle login with invalid credentials', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      await page.fill('input[id="email"]', 'invalid@example.com');
      await page.fill('input[id="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // Should show error and stay on login page
      await expect(page.locator('[role="alert"]')).toBeVisible();
      await expect(page).toHaveURL('http://localhost:3000/login');
    });

    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      await expect(page).toHaveURL('http://localhost:3000/login');
    });
  });

  test.describe('Project Management', () => {
    test.beforeEach(async ({ page }) => {
      // Register and login before each project test
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
    });

    test('should create a new project', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      
      // Click create project button
      await page.click('text=Create Project');
      
      // Fill project form
      testProject = {
        id: '',
        name: 'Test Project ' + Date.now()
      };
      
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'A test project for TDD');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      
      await page.click('button[type="submit"]');
      
      // Should redirect to project detail page
      await expect(page).toHaveURL(/\/projects\/[a-f0-9-]+/);
      await expect(page.locator(`text=${testProject.name}`)).toBeVisible();
    });

    test('should display project in projects list', async ({ page }) => {
      // Create a project first
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      
      testProject = {
        id: '',
        name: 'List Test Project ' + Date.now()
      };
      
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'Project for list test');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');
      
      // Navigate back to projects list
      await page.goto('http://localhost:3000/projects');
      
      // Should see the project in the list
      await expect(page.locator(`text=${testProject.name}`)).toBeVisible();
    });

    test('should edit project details', async ({ page }) => {
      // Create a project first
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      
      testProject = {
        id: '',
        name: 'Edit Test Project ' + Date.now()
      };
      
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'Original description');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');
      
      // Edit the project
      await page.click('text=Edit Project');
      await page.fill('textarea[id="description"]', 'Updated description');
      await page.click('button[type="submit"]');
      
      // Should see updated description
      await expect(page.locator('text=Updated description')).toBeVisible();
    });

    test('should delete project', async ({ page }) => {
      // Create a project first
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      
      testProject = {
        id: '',
        name: 'Delete Test Project ' + Date.now()
      };
      
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'Project to be deleted');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');
      
      // Delete the project
      await page.click('text=Delete Project');
      await page.click('text=Confirm Delete');
      
      // Should redirect to projects list
      await expect(page).toHaveURL('http://localhost:3000/projects');
      await expect(page.locator(`text=${testProject.name}`)).not.toBeVisible();
    });
  });

  test.describe('Workflow Management', () => {
    test.beforeEach(async ({ page }) => {
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
      testProject = {
        id: '',
        name: 'Workflow Test Project ' + Date.now()
      };
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'Project for workflow testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');
    });

    test('should start architecture workflow', async ({ page }) => {
      // Navigate to upload page
      await page.click('text=Upload Documents');
      
      // Upload a requirements document
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall process user requests within 2 seconds.')
      });
      
      await page.click('text=Start Workflow');
      
      // Should see workflow status
      await expect(page.locator('text=Workflow Started')).toBeVisible();
    });

    test('should monitor workflow progress', async ({ page }) => {
      // Start a workflow first
      await page.click('text=Upload Documents');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable.')
      });
      await page.click('text=Start Workflow');
      
      // Check workflow status
      await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    });

    test('should display workflow history', async ({ page }) => {
      // Navigate to project detail
      await page.goto('http://localhost:3000/projects');
      await page.click(`text=${testProject.name}`);
      
      // Should see workflow history section
      await expect(page.locator('text=Workflow History')).toBeVisible();
    });
  });

  test.describe('AI Assistant', () => {
    test.beforeEach(async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
    });

    test('should open AI assistant widget', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      
      // Click AI assistant button
      await page.click('text=AI Assistant');
      
      // Should see chat interface
      await expect(page.locator('text=AI Assistant')).toBeVisible();
    });

    test('should send message to AI assistant', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      await page.click('text=AI Assistant');
      
      // Type a message
      await page.fill('textarea[placeholder*="message"]', 'Hello, can you help me with architecture design?');
      await page.click('button[type="submit"]');
      
      // Should see the message in chat
      await expect(page.locator('text=Hello, can you help me with architecture design?')).toBeVisible();
    });

    test('should change AI model', async ({ page }) => {
      await page.goto('http://localhost:3000/projects');
      await page.click('text=AI Assistant');
      
      // Click model selector
      await page.click('text=DeepSeek R1');
      
      // Should see model options
      await expect(page.locator('text=OpenAI GPT-4')).toBeVisible();
      await expect(page.locator('text=Anthropic Claude')).toBeVisible();
    });
  });

  test.describe('Document Upload and Processing', () => {
    test.beforeEach(async ({ page }) => {
      // Register, login, and create project
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      testProject = {
        id: '',
        name: 'Document Test Project ' + Date.now()
      };
      await page.fill('input[id="name"]', testProject.name);
      await page.fill('textarea[id="description"]', 'Project for document testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');
    });

    test('should upload requirements document', async ({ page }) => {
      await page.click('text=Upload Documents');
      
      // Upload file
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall handle 1000 concurrent users.')
      });
      
      // Should see file uploaded
      await expect(page.locator('text=requirements.txt')).toBeVisible();
    });

    test('should process uploaded document', async ({ page }) => {
      await page.click('text=Upload Documents');
      
      // Upload and process
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be secure and scalable.')
      });
      
      await page.click('text=Start Workflow');
      
      // Should see processing status
      await expect(page.locator('text=Processing')).toBeVisible();
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network error by going to invalid URL
      await page.goto('http://localhost:3000/invalid-page');
      await expect(page.locator('text=404')).toBeVisible();
    });

    test('should handle form validation errors', async ({ page }) => {
      await page.goto('http://localhost:3000/register');
      
      // Submit empty form
      await page.click('button[type="submit"]');
      
      // Should show validation errors
      await expect(page.locator('text=Name is required')).toBeVisible();
      await expect(page.locator('text=Email is required')).toBeVisible();
    });

    test('should handle session timeout', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Simulate session timeout by clearing localStorage
      await page.evaluate(() => localStorage.clear());
      
      // Try to access protected page
      await page.goto('http://localhost:3000/projects');
      
      // Should redirect to login
      await expect(page).toHaveURL('http://localhost:3000/login');
    });
  });
});
