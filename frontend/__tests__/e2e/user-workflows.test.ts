/**
 * User Workflow E2E Tests
 * 
 * These tests focus on real user workflows and scenarios
 * rather than edge cases or technical implementation details.
 */

import { test, expect, Page } from '@playwright/test';
import { E2E_CONFIG } from './test-config';
import { 
  waitForElement, 
  waitForNavigation, 
  fillFormField, 
  clickElement,
  createTestUser,
  createTestProject,
  waitForPageLoad,
  retryOperation,
  waitForWorkflowStatus
} from './test-utils';

test.describe('Real User Workflows', () => {
  let page: Page;
  let testUser: ReturnType<typeof createTestUser>;
  let testProject: ReturnType<typeof createTestProject>;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    testUser = createTestUser();
    testProject = createTestProject();
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('New User Onboarding Journey', async () => {
    // Scenario: A new user discovers ArchMesh and wants to create their first architecture
    
    // Step 1: User visits the homepage
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User sees the value proposition
    await expect(page.locator('text=ArchMesh')).toBeVisible();
    await expect(page.locator('text=architecture')).toBeVisible();
    
    // Step 2: User decides to sign up
    await clickElement(page, 'text=Sign Up');
    await waitForNavigation(page, '**/register');
    
    // User fills out registration form
    await fillFormField(page, 'input[name="email"]', testUser.email);
    await fillFormField(page, 'input[name="password"]', testUser.password);
    await fillFormField(page, 'input[name="name"]', testUser.name);
    
    await clickElement(page, 'button[type="submit"]');
    
    // User sees successful registration
    await waitForElement(page, 'text=Registration successful');
    
    // Step 3: User is guided to create their first project
    await clickElement(page, 'text=Get Started');
    await waitForNavigation(page, '**/projects');
    
    // User sees the project creation interface
    await expect(page.locator('text=Create Your First Project')).toBeVisible();
    
    // Step 4: User creates a project for their startup
    await clickElement(page, 'text=Create New Project');
    await waitForElement(page, 'form');
    
    await fillFormField(page, 'input[name="name"]', 'My Startup Platform');
    await fillFormField(page, 'textarea[name="description"]', 'A modern web platform for our startup');
    await page.selectOption('select[name="domain"]', 'cloud-native');
    
    await clickElement(page, 'button[type="submit"]');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // Step 5: User sees their project dashboard
    await expect(page.locator('text=My Startup Platform')).toBeVisible();
    await expect(page.locator('text=Project created successfully')).toBeVisible();
  });

  test('Architect Creates System Architecture', async () => {
    // Scenario: An experienced architect wants to design a microservices architecture
    
    // Setup: User is already registered and logged in
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User logs in (assuming they have an account)
    await clickElement(page, 'text=Sign In');
    await waitForNavigation(page, '**/login');
    
    await fillFormField(page, 'input[name="email"]', 'architect@example.com');
    await fillFormField(page, 'input[name="password"]', 'TestPassword123!');
    await clickElement(page, 'button[type="submit"]');
    
    // User navigates to their projects
    await waitForNavigation(page, '**/projects');
    
    // User creates a new project for microservices architecture
    await clickElement(page, 'text=Create New Project');
    await waitForElement(page, 'form');
    
    await fillFormField(page, 'input[name="name"]', 'E-commerce Microservices');
    await fillFormField(page, 'textarea[name="description"]', 'Scalable e-commerce platform with microservices architecture');
    await page.selectOption('select[name="domain"]', 'cloud-native');
    
    await clickElement(page, 'button[type="submit"]');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User starts the architecture workflow
    await clickElement(page, 'text=Start Workflow');
    await waitForNavigation(page, '**/upload');
    
    // User uploads their requirements document
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
        E-commerce Platform Requirements
        
        Functional Requirements:
        - User registration and authentication
        - Product catalog browsing
        - Shopping cart management
        - Order processing
        - Payment integration
        - Inventory management
        
        Non-functional Requirements:
        - Handle 10,000 concurrent users
        - 99.9% uptime
        - Sub-second response times
        - Secure payment processing
        - Scalable architecture
      `)
    });
    
    await fillFormField(page, 'textarea[placeholder*="context"]', 'Modern e-commerce platform with microservices architecture, supporting high traffic and real-time inventory updates');
    
    await clickElement(page, 'button[type="submit"]');
    
    // User is redirected to project detail page to monitor progress
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User sees workflow status
    await waitForElement(page, '[data-testid="workflow-status"]');
    
    // User waits for architecture generation (realistic timing)
    const finalStatus = await waitForWorkflowStatus(page, ['completed', 'failed']);
    
    // User sees the generated architecture
    if (finalStatus.toLowerCase().includes('completed')) {
      await expect(page.locator('text=Architecture')).toBeVisible();
      await expect(page.locator('text=Components')).toBeVisible();
    }
  });

  test('Team Collaboration Workflow', async () => {
    // Scenario: A project manager wants to collaborate with their team on architecture review
    
    // Setup: User has a project with completed architecture
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User navigates to an existing project
    await clickElement(page, 'text=Projects');
    await waitForNavigation(page, '**/projects');
    
    // User selects a project (assuming one exists)
    await clickElement(page, '[data-testid="project-card"]:first-child');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User wants to invite team members
    await expect(page.locator('text=Team Members')).toBeVisible();
    
    // User adds a team member
    await clickElement(page, 'text=Add Member');
    await waitForElement(page, 'form');
    
    await fillFormField(page, 'input[type="email"]', 'developer@example.com');
    await page.selectOption('select', 'collaborator');
    
    await clickElement(page, 'button:has-text("Add Member")');
    
    // User sees confirmation
    await expect(page.locator('text=Team member invitation sent')).toBeVisible();
    
    // User checks workflow history
    await expect(page.locator('text=Workflow History')).toBeVisible();
    
    // User can see previous workflow runs
    const workflowCards = page.locator('[data-testid="workflow-card"]');
    if (await workflowCards.count() > 0) {
      await expect(workflowCards.first()).toBeVisible();
    }
  });

  test('Architecture Review and Iteration', async () => {
    // Scenario: An architect wants to review and improve an existing architecture
    
    // Setup: User has a project with generated architecture
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User navigates to project with architecture
    await clickElement(page, 'text=Projects');
    await waitForNavigation(page, '**/projects');
    
    // User selects a project
    await clickElement(page, '[data-testid="project-card"]:first-child');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User reviews the generated architecture
    await expect(page.locator('text=Architecture')).toBeVisible();
    
    // User can see architecture components
    await expect(page.locator('text=Components')).toBeVisible();
    
    // User can see technology stack
    await expect(page.locator('text=Technology Stack')).toBeVisible();
    
    // User wants to start a new workflow with updated requirements
    await clickElement(page, 'text=Start New Workflow');
    await waitForNavigation(page, '**/upload');
    
    // User uploads updated requirements
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'updated-requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
        Updated E-commerce Platform Requirements
        
        New Requirements:
        - Real-time notifications
        - Mobile app support
        - Advanced analytics
        - AI-powered recommendations
        
        Updated Constraints:
        - Must support mobile-first design
        - Integration with existing CRM system
        - Compliance with GDPR regulations
      `)
    });
    
    await fillFormField(page, 'textarea[placeholder*="context"]', 'Updated requirements for mobile-first e-commerce platform with AI recommendations and real-time features');
    
    await clickElement(page, 'button[type="submit"]');
    
    // User monitors the updated workflow
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    await waitForElement(page, '[data-testid="workflow-status"]');
    
    // User can see both old and new workflows in history
    await expect(page.locator('text=Workflow History')).toBeVisible();
  });

  test('Error Recovery and Support', async () => {
    // Scenario: A user encounters an error and needs to recover
    
    // Setup: User has a project with a failed workflow
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User navigates to project with failed workflow
    await clickElement(page, 'text=Projects');
    await waitForNavigation(page, '**/projects');
    
    // User selects a project
    await clickElement(page, '[data-testid="project-card"]:first-child');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User sees failed workflow in history
    const failedWorkflow = page.locator('[data-testid="workflow-card"]').filter({ hasText: 'Failed' });
    if (await failedWorkflow.count() > 0) {
      await expect(failedWorkflow.first()).toBeVisible();
      
      // User can see error details
      await expect(page.locator('text=Error')).toBeVisible();
      
      // User can retry the workflow
      await clickElement(page, 'text=Retry');
      
      // User is taken to upload page with pre-filled data
      await waitForNavigation(page, '**/upload');
      
      // User can modify the input and retry
      await fillFormField(page, 'textarea[placeholder*="context"]', 'Updated context for retry');
      
      await clickElement(page, 'button[type="submit"]');
      
      // User is redirected back to monitor progress
      await waitForNavigation(page, /\/projects\/[^\/]+/);
    }
  });

  test('Project Export and Sharing', async () => {
    // Scenario: A user wants to export and share their architecture
    
    // Setup: User has a completed project
    await page.goto(E2E_CONFIG.baseUrl);
    await waitForPageLoad(page);
    
    // User navigates to completed project
    await clickElement(page, 'text=Projects');
    await waitForNavigation(page, '**/projects');
    
    // User selects a project
    await clickElement(page, '[data-testid="project-card"]:first-child');
    await waitForNavigation(page, /\/projects\/[^\/]+/);
    
    // User wants to export the architecture
    await expect(page.locator('text=Export')).toBeVisible();
    
    // User clicks export button
    await clickElement(page, 'text=Export');
    
    // User sees export options
    await expect(page.locator('text=Export Format')).toBeVisible();
    
    // User selects PDF export
    await clickElement(page, 'text=PDF');
    
    // User sees download link or file download starts
    await expect(page.locator('text=Download')).toBeVisible();
  });
});
