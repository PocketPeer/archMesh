/**
 * AI ASSISTANT WORKFLOW INTEGRATION TESTS - TDD Test Suite
 * 
 * Tests AI Assistant integration within the core workflow:
 * 1. AI Assistant during Requirements Processing
 * 2. AI Assistant during Architecture Generation
 * 3. AI Assistant Context and History
 * 4. Model Selection and Switching
 * 5. Real-time AI Assistance
 * 6. AI Assistant Error Handling
 */

import { test, expect } from '@playwright/test';

test.describe('AI Assistant Workflow Integration - TDD', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `aiworkflowtest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'AI Workflow Test User'
    };

    // Register and login
    await page.goto('http://localhost:3000/register');
    await page.fill('input[id="name"]', testUser.name);
    await page.fill('input[id="email"]', testUser.email);
    await page.fill('input[id="password"]', testUser.password);
    await page.fill('input[id="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to projects page (with longer timeout for auto-login)
    await expect(page).toHaveURL('http://localhost:3000/projects', { timeout: 30000 });
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });

  test.describe('AI Assistant during Requirements Processing', () => {
    test('should provide AI assistance during requirements upload', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Requirements Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI assistance during requirements');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page
      await page.click('text=Start Workflow');
      await expect(page.locator('[data-slot="card-title"]:has-text("Upload Requirements Document")').first()).toBeVisible();

      // Step 1: Open AI Assistant
      await page.click('text=AI Assistant');
      await expect(page.locator('text=AI Assistant')).toBeVisible();

      // Step 2: Ask AI for requirements guidance
      await page.fill('textarea[placeholder*="message"]', 'What are the key requirements I should include for a scalable microservices application?');
      await page.click('button[type="submit"]');

      // Step 3: Should receive AI response
      await expect(page.locator('text=What are the key requirements I should include for a scalable microservices application?')).toBeVisible();
      // Wait for AI response
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: Upload requirements document
      const requirementsContent = `
# System Requirements

## Functional Requirements
- The system shall process user requests within 2 seconds
- The system shall support 1000 concurrent users
- The system shall provide real-time notifications

## Non-Functional Requirements
- The system shall be available 99.9% of the time
- The system shall be secure and compliant with GDPR
- The system shall be scalable to handle growth
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(requirementsContent)
      });

      // Step 5: Ask AI to review the uploaded requirements
      await page.fill('textarea[placeholder*="message"]', 'Can you review my uploaded requirements and suggest improvements?');
      await page.click('button[type="submit"]');

      // Step 6: Should receive AI feedback on requirements
      await expect(page.locator('text=Can you review my uploaded requirements and suggest improvements?')).toBeVisible();
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });

    test('should maintain context during requirements processing workflow', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Context Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI context during requirements');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Step 1: Establish context with AI
      await page.fill('textarea[placeholder*="message"]', 'I am working on a cloud-native microservices application for e-commerce. What should I consider?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 2: Upload requirements
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall handle e-commerce transactions securely.')
      });

      // Step 3: Start workflow
      await page.click('text=Start Workflow');

      // Step 4: Ask AI about the processing status
      await page.fill('textarea[placeholder*="message"]', 'What is happening with my requirements processing?');
      await page.click('button[type="submit"]');

      // Step 5: AI should understand the context and provide relevant assistance
      await expect(page.locator('text=What is happening with my requirements processing?')).toBeVisible();
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 6: AI should reference the e-commerce context
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('e-commerce');
    });
  });

  test.describe('AI Assistant during Architecture Generation', () => {
    test('should provide AI assistance during architecture design', async ({ page }) => {
      // Complete requirements processing first
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Architecture Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI assistance during architecture');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Upload requirements and process
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall use microservices architecture and be deployed on cloud infrastructure.')
      });
      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Requirements Processed', { timeout: 300000 });

      // Step 1: Navigate to architecture generation
      await page.click('text=Generate Architecture');

      // Step 2: Open AI Assistant for architecture guidance
      await page.click('text=AI Assistant');
      await expect(page.locator('text=AI Assistant')).toBeVisible();

      // Step 3: Ask AI for architecture recommendations
      await page.fill('textarea[placeholder*="message"]', 'What architecture patterns would work best for a cloud-native microservices application?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: Start architecture generation
      await page.click('text=Generate Architecture');

      // Step 5: Ask AI about the generation process
      await page.fill('textarea[placeholder*="message"]', 'What technologies should I consider for my microservices architecture?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 6: Wait for architecture generation to complete
      await page.waitForSelector('text=Architecture Generated', { timeout: 300000 });

      // Step 7: Ask AI to review the generated architecture
      await page.fill('textarea[placeholder*="message"]', 'Can you review the generated architecture and suggest improvements?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });

    test('should provide real-time assistance during architecture customization', async ({ page }) => {
      // Complete full workflow first
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Customization Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI assistance during customization');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Complete workflow
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall use microservices architecture.')
      });
      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Requirements Processed', { timeout: 300000 });
      await page.click('text=Generate Architecture');
      await page.click('text=Generate Architecture');
      await page.waitForSelector('text=Architecture Generated', { timeout: 300000 });

      // Step 1: Open architecture editor
      await page.click('text=Edit Architecture');
      await expect(page.locator('text=Architecture Editor')).toBeVisible();

      // Step 2: Open AI Assistant for customization help
      await page.click('text=AI Assistant');

      // Step 3: Ask AI about specific technology choices
      await page.fill('textarea[placeholder*="message"]', 'Should I use Kubernetes or Docker Swarm for container orchestration?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: Ask AI about database choices
      await page.fill('textarea[placeholder*="message"]', 'What database should I use for my microservices?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });
  });

  test.describe('Model Selection and Switching', () => {
    test('should allow switching between AI models during workflow', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Model Switch Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing model switching');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Step 1: Check current model
      await expect(page.locator('text=Current Model')).toBeVisible();
      await expect(page.locator('text=DeepSeek R1')).toBeVisible();

      // Step 2: Switch to OpenAI
      await page.click('text=Change Model');
      await page.click('text=OpenAI GPT-4');
      await expect(page.locator('text=OpenAI GPT-4')).toBeVisible();

      // Step 3: Ask a question with OpenAI
      await page.fill('textarea[placeholder*="message"]', 'What are the benefits of microservices architecture?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: Switch to Anthropic
      await page.click('text=Change Model');
      await page.click('text=Anthropic Claude');
      await expect(page.locator('text=Anthropic Claude')).toBeVisible();

      // Step 5: Ask a question with Claude
      await page.fill('textarea[placeholder*="message"]', 'How should I structure my microservices for scalability?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });

    test('should maintain conversation history across model switches', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'History Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing conversation history');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Step 1: Start conversation with DeepSeek
      await page.fill('textarea[placeholder*="message"]', 'I am building a microservices application. What should I consider?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 2: Switch to OpenAI
      await page.click('text=Change Model');
      await page.click('text=OpenAI GPT-4');

      // Step 3: Reference previous conversation
      await page.fill('textarea[placeholder*="message"]', 'Based on our previous discussion about microservices, what database should I use?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: Should see conversation history
      await expect(page.locator('text=I am building a microservices application. What should I consider?')).toBeVisible();
      await expect(page.locator('text=Based on our previous discussion about microservices, what database should I use?')).toBeVisible();
    });
  });

  test.describe('AI Assistant Error Handling', () => {
    test('should handle AI model failures gracefully', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Error Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI error handling');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Step 1: Simulate model failure by asking a question that might timeout
      await page.fill('textarea[placeholder*="message"]', 'Generate a very complex architecture diagram with detailed explanations');
      await page.click('button[type="submit"]');

      // Step 2: Should handle timeout gracefully
      await page.waitForSelector('text=Model timeout', { timeout: 30000 });
      await expect(page.locator('text=Switching to fallback model')).toBeVisible();

      // Step 3: Should retry with fallback model
      await expect(page.locator('text=Retrying with faster model')).toBeVisible();
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });

    test('should handle network errors during AI communication', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Network Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI network errors');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Step 1: Go offline to simulate network error
      await page.context().setOffline(true);

      // Step 2: Try to send message
      await page.fill('textarea[placeholder*="message"]', 'What are the best practices for microservices?');
      await page.click('button[type="submit"]');

      // Step 3: Should show network error
      await expect(page.locator('text=Network error')).toBeVisible();
      await expect(page.locator('text=Please check your connection')).toBeVisible();

      // Step 4: Restore network
      await page.context().setOffline(false);

      // Step 5: Should be able to retry
      await page.click('text=Retry');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
    });
  });

  test.describe('Real-time AI Assistance', () => {
    test('should provide contextual help during workflow steps', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Contextual Help Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing contextual AI help');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Step 1: Open AI Assistant
      await page.click('text=AI Assistant');

      // Step 2: Navigate to upload page
      await page.click('text=Start Workflow');

      // Step 3: AI should provide contextual help
      await expect(page.locator('text=AI Suggestions')).toBeVisible();
      await expect(page.locator('text=Requirements Tips')).toBeVisible();

      // Step 4: Ask for specific help
      await page.fill('textarea[placeholder*="message"]', 'What should I include in my requirements document?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 5: Upload requirements
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall be scalable and secure.')
      });

      // Step 6: AI should provide next step guidance
      await expect(page.locator('text=Next Steps')).toBeVisible();
      await expect(page.locator('text=Ready to process')).toBeVisible();
    });

    test('should provide intelligent suggestions based on project context', async ({ page }) => {
      // Create project with specific domain
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Intelligent Suggestions Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'E-commerce platform for online shopping');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Step 1: Open AI Assistant
      await page.click('text=AI Assistant');

      // Step 2: AI should provide domain-specific suggestions
      await expect(page.locator('text=E-commerce Recommendations')).toBeVisible();
      await expect(page.locator('text=Payment Processing')).toBeVisible();
      await expect(page.locator('text=Inventory Management')).toBeVisible();

      // Step 3: Ask for specific e-commerce guidance
      await page.fill('textarea[placeholder*="message"]', 'What are the key requirements for an e-commerce platform?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Step 4: AI response should be e-commerce specific
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('e-commerce');
    });
  });
});
