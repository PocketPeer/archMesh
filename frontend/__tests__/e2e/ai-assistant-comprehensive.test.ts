/**
 * AI ASSISTANT COMPREHENSIVE TESTS - TDD Test Suite
 * 
 * Tests comprehensive AI Assistant functionality:
 * 1. Response Quality (Template vs Real Answers)
 * 2. Provider Switching and Fallbacks
 * 3. Conversation History and Context
 * 4. Guidance Best Practices
 * 5. Error Handling and Recovery
 * 6. Performance and Rate Limiting
 * 7. User Experience and Accessibility
 * 8. Integration with Workflow Context
 */

import { test, expect } from '@playwright/test';

test.describe('AI Assistant Comprehensive Tests - TDD', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `aiassistanttest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'AI Assistant Test User'
    };

    // Register and login with retry logic
    await page.goto('http://localhost:3000/register');
    await page.fill('input[id="name"]', testUser.name);
    await page.fill('input[id="email"]', testUser.email);
    await page.fill('input[id="password"]', testUser.password);
    await page.fill('input[id="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');

    // Wait for registration to complete and check for redirect
    await page.waitForLoadState('networkidle');
    
    // If still on register page, try to navigate to projects directly
    if (page.url().includes('/register')) {
      await page.goto('http://localhost:3000/projects');
    }
    
    // Wait for projects page to load
    await expect(page).toHaveURL('http://localhost:3000/projects', { timeout: 30000 });
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });

  test.describe('Response Quality (Template vs Real Answers)', () => {
    test('should provide real AI responses, not template fallbacks', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Response Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing AI response quality');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for any toast notifications to disappear and dismiss them
      await page.waitForTimeout(3000);
      
      // Dismiss any toast notifications that might be blocking clicks
      const toastCloseButtons = page.locator('[data-sonner-toast] button[aria-label="Close"]');
      const toastCount = await toastCloseButtons.count();
      for (let i = 0; i < toastCount; i++) {
        try {
          await toastCloseButtons.nth(i).click({ timeout: 1000 });
        } catch (e) {
          // Ignore if toast is already dismissed
        }
      }
      
      // Wait a bit more for toasts to fully disappear
      await page.waitForTimeout(1000);
      
      // Click on the expand button of the AI Assistant widget with force
      await page.click('div[class*="fixed bottom-4 right-4"] button:has-text("+")', { force: true });
      
      // Wait for AI Assistant widget to be visible and expanded
      await page.waitForSelector('input[placeholder*="Ask AI anything..."]', { timeout: 10000 });

      // Ask a specific technical question
      await page.fill('input[placeholder*="Ask AI anything..."]', 'What are the key architectural patterns for building scalable microservices?');
      await page.click('button[aria-label="Send message"]');

      // Wait for AI response
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Should receive a real, detailed response (not template)
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toBeTruthy();
      expect(response?.length).toBeGreaterThan(100); // Real responses are longer
      expect(response).toContain('microservices'); // Should reference the topic
      expect(response).not.toContain('template'); // Should not be a template response
    });

    test('should detect and handle template fallback responses', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Template Fallback Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing template fallbacks');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for any toast notifications to disappear and dismiss them
      await page.waitForTimeout(3000);
      
      // Dismiss any toast notifications that might be blocking clicks
      const toastCloseButtons = page.locator('[data-sonner-toast] button[aria-label="Close"]');
      const toastCount = await toastCloseButtons.count();
      for (let i = 0; i < toastCount; i++) {
        try {
          await toastCloseButtons.nth(i).click({ timeout: 1000 });
        } catch (e) {
          // Ignore if toast is already dismissed
        }
      }
      
      // Wait a bit more for toasts to fully disappear
      await page.waitForTimeout(1000);
      
      // Click on the expand button of the AI Assistant widget with force
      await page.click('div[class*="fixed bottom-4 right-4"] button:has-text("+")', { force: true });
      
      // Wait for AI Assistant widget to be visible and expanded
      await page.waitForSelector('input[placeholder*="Ask AI anything..."]', { timeout: 10000 });

      // Simulate network issues to trigger fallback
      await page.route('**/api/v1/ai/chat', route => route.abort());

      // Ask a question
      await page.fill('input[placeholder*="Ask AI anything..."]', 'What is the best database for microservices?');
      await page.click('button[aria-label="Send message"]');

      // Should show AI response (even with network issues, it should handle gracefully)
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toBeTruthy();
      expect(response?.length).toBeGreaterThan(10);
    });

    test('should provide contextual responses based on project type', async ({ page }) => {
      // Create cloud-native project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Contextual Response Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'E-commerce platform for online shopping');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Ask a general question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What technologies should I use?');
      await page.click('button[aria-label="Send message"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should be contextual to e-commerce and cloud-native
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('e-commerce');
      expect(response).toContain('cloud-native');
    });

    test('should provide different response qualities based on model', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Model Quality Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing model quality');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Test with different models
      const models = ['DeepSeek R1', 'OpenAI GPT-4', 'Anthropic Claude'];
      
      for (const model of models) {
        // Switch to model
        await page.click('text=Change Model');
        await page.click(`text=${model}`);
        await expect(page.locator(`text=${model}`)).toBeVisible();

        // Ask same question
        await page.fill('input[placeholder*="Ask AI anything"]', 'Explain microservices architecture patterns');
        await page.click('button[aria-label="Send message"]');
        await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

        // Response should be model-specific
        const response = await page.locator('[data-testid="ai-response"]').textContent();
        expect(response).toBeTruthy();
        expect(response?.length).toBeGreaterThan(50);
      }
    });
  });

  test.describe('Provider Switching and Fallbacks', () => {
    test('should switch between AI providers seamlessly', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Provider Switch Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing provider switching');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Test provider switching
      const providers = [
        { name: 'DeepSeek R1', expected: 'DeepSeek' },
        { name: 'OpenAI GPT-4', expected: 'OpenAI' },
        { name: 'Anthropic Claude', expected: 'Anthropic' }
      ];

      for (const provider of providers) {
        // Switch provider
        await page.click('text=Change Model');
        await page.click(`text=${provider.name}`);
        await expect(page.locator(`text=${provider.expected}`)).toBeVisible();

        // Ask question
        await page.fill('input[placeholder*="Ask AI anything"]', 'What is the best approach for microservices?');
        await page.click('button[type="submit"]');
        await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

        // Should receive response from selected provider
        await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
      }
    });

    test('should handle provider failures with automatic fallback', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Provider Fallback Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing provider fallback');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Simulate provider failure
      await page.route('**/api/v1/ai/chat', route => route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Provider unavailable' })
      }));

      // Ask question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are microservices best practices?');
      await page.click('button[aria-label="Send message"]');

      // Should show fallback mechanism
      await expect(page.locator('text=Provider unavailable')).toBeVisible();
      await expect(page.locator('text=Switching to fallback')).toBeVisible();
    });

    test('should maintain conversation context across provider switches', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Context Switch Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing context across switches');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Start conversation with DeepSeek
      await page.fill('input[placeholder*="Ask AI anything"]', 'I am building a microservices application. What should I consider?');
      await page.click('button[aria-label="Send message"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Switch to OpenAI
      await page.click('text=Change Model');
      await page.click('text=OpenAI GPT-4');

      // Reference previous conversation
      await page.fill('input[placeholder*="Ask AI anything"]', 'Based on our previous discussion about microservices, what database should I use?');
      await page.click('button[aria-label="Send message"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Should maintain context
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('microservices');
      expect(response).toContain('database');
    });
  });

  test.describe('Conversation History and Context', () => {
    test('should maintain conversation history across page navigation', async ({ page }) => {
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
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Start conversation
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are the key components of microservices architecture?');
      await page.click('button[aria-label="Send message"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Navigate away and back
      await page.goto('http://localhost:3000/projects');
      await page.goto(`http://localhost:3000/projects/${testProject.id}`);
      await page.click('text=Start Workflow');
      await page.click('text=AI Assistant');

      // Should see conversation history
      await expect(page.locator('text=What are the key components of microservices architecture?')).toBeVisible();
    });

    test('should provide context-aware responses based on project state', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Context Aware Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'E-commerce platform for online shopping');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Upload requirements
      await page.click('text=Start Workflow');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('The system shall handle e-commerce transactions securely.')
      });

      // Open AI Assistant
      await page.click('text=AI Assistant');

      // Ask context-aware question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What should I consider for my e-commerce platform?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should be context-aware
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('e-commerce');
      expect(response).toContain('transactions');
      expect(response).toContain('security');
    });

    test('should handle long conversation threads efficiently', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Long Conversation Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing long conversations');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Have a long conversation
      const questions = [
        'What are microservices?',
        'How do I design microservices architecture?',
        'What databases work best with microservices?',
        'How do I handle data consistency?',
        'What about security in microservices?'
      ];

      for (const question of questions) {
        await page.fill('input[placeholder*="Ask AI anything"]', question);
        await page.click('button[type="submit"]');
        await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
      }

      // Should maintain context throughout
      await expect(page.locator('text=What are microservices?')).toBeVisible();
      await expect(page.locator('text=How do I design microservices architecture?')).toBeVisible();
      await expect(page.locator('text=What databases work best with microservices?')).toBeVisible();
    });
  });

  test.describe('Guidance Best Practices', () => {
    test('should provide helpful, actionable guidance', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Guidance Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing guidance quality');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Ask for specific guidance
      await page.fill('input[placeholder*="Ask AI anything"]', 'I am new to microservices. What are the first steps I should take?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should be helpful and actionable
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('steps');
      expect(response).toContain('first');
      expect(response?.length).toBeGreaterThan(200); // Detailed guidance
    });

    test('should provide step-by-step instructions', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Step by Step Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing step-by-step guidance');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Ask for step-by-step guidance
      await page.fill('input[placeholder*="Ask AI anything"]', 'How do I implement microservices step by step?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should include numbered steps or clear structure
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('1.');
      expect(response).toContain('2.');
      expect(response).toContain('step');
    });

    test('should provide relevant examples and use cases', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Examples Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'E-commerce platform for online shopping');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Ask for examples
      await page.fill('input[placeholder*="Ask AI anything"]', 'Can you give me examples of microservices for e-commerce?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should include relevant examples
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('e-commerce');
      expect(response).toContain('example');
      expect(response).toContain('service');
    });

    test('should ask clarifying questions when needed', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Clarifying Questions Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing clarifying questions');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Ask vague question
      await page.fill('input[placeholder*="Ask AI anything"]', 'I need help with my system');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Response should ask clarifying questions
      const response = await page.locator('[data-testid="ai-response"]').textContent();
      expect(response).toContain('?');
      expect(response).toContain('what');
      expect(response).toContain('help');
    });
  });

  test.describe('Error Handling and Recovery', () => {
    test('should handle network timeouts gracefully', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Timeout Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing timeouts');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Simulate timeout
      await page.route('**/api/v1/ai/chat', route => route.abort());

      // Ask question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are microservices?');
      await page.click('button[type="submit"]');

      // Should handle timeout gracefully
      await expect(page.locator('text=Request timeout')).toBeVisible();
      await expect(page.locator('text=Please try again')).toBeVisible();
    });

    test('should handle model failures with fallback', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Model Failure Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing model failures');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Simulate model failure
      await page.route('**/api/v1/ai/chat', route => route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Model unavailable' })
      }));

      // Ask question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are microservices?');
      await page.click('button[type="submit"]');

      // Should show fallback
      await expect(page.locator('text=Model unavailable')).toBeVisible();
      await expect(page.locator('text=Using fallback model')).toBeVisible();
    });

    test('should allow retry after errors', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Retry Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing retry functionality');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Simulate temporary error
      let errorCount = 0;
      await page.route('**/api/v1/ai/chat', route => {
        if (errorCount < 1) {
          errorCount++;
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Temporary error' })
          });
        } else {
          route.continue();
        }
      });

      // Ask question
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are microservices?');
      await page.click('button[type="submit"]');

      // Should show error first
      await expect(page.locator('text=Temporary error')).toBeVisible();

      // Should allow retry
      await page.click('text=Retry');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
      await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
    });
  });

  test.describe('Performance and Rate Limiting', () => {
    test('should handle concurrent requests efficiently', async ({ page, context }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Concurrent Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing concurrent requests');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Open multiple tabs
      const tabs = [];
      for (let i = 0; i < 3; i++) {
        const newPage = await context.newPage();
        await newPage.goto(`http://localhost:3000/projects/${testProject.id}`);
        await newPage.click('text=Start Workflow');
        await newPage.click('text=AI Assistant');
        tabs.push(newPage);
      }

      // Send requests from all tabs
      for (let i = 0; i < tabs.length; i++) {
        await tabs[i].fill('input[placeholder*="Ask AI anything"]', `Question ${i + 1}: What are microservices?`);
        await tabs[i].click('button[type="submit"]');
      }

      // All should handle requests properly
      for (const tab of tabs) {
        await tab.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
        await expect(tab.locator('[data-testid="ai-response"]')).toBeVisible();
      }
    });

    test('should respect rate limiting', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Rate Limit Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing rate limiting');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Send multiple rapid requests
      for (let i = 0; i < 5; i++) {
        await page.fill('input[placeholder*="Ask AI anything"]', `Rapid request ${i + 1}`);
        await page.click('button[type="submit"]');
        await page.waitForTimeout(100); // Small delay
      }

      // Should handle rate limiting gracefully
      await expect(page.locator('text=Rate limit exceeded')).toBeVisible();
      await expect(page.locator('text=Please wait')).toBeVisible();
    });

    test('should measure and display response times', async ({ page }) => {
      // Create project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Response Time Test Project ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Project for testing response times');
      await page.selectOption('[role="dialog"] select', 'cloud-native');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Navigate to upload page and open AI Assistant
      await page.click('text=Start Workflow');
      
      // Wait for page to stabilize
      await page.waitForTimeout(2000);
      
      // Try to interact with AI Assistant directly - it might already be expanded
      // Wait for AI Assistant input field to be available
      await page.waitForSelector('input[placeholder*="Ask AI anything"]', { timeout: 10000 });

      // Measure response time
      const startTime = Date.now();
      await page.fill('input[placeholder*="Ask AI anything"]', 'What are microservices?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });
      const responseTime = Date.now() - startTime;

      // Should show response time
      await expect(page.locator('text=Response time')).toBeVisible();
      await expect(page.locator('text=' + responseTime + 'ms')).toBeVisible();

      // Response time should be reasonable
      expect(responseTime).toBeLessThan(30000); // 30 seconds max
    });
  });
});
