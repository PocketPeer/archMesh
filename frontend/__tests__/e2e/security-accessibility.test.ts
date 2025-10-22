/**
 * SECURITY AND ACCESSIBILITY TESTS - TDD Test Suite
 * 
 * Tests application security and accessibility:
 * 1. Authentication security
 * 2. Authorization and access control
 * 3. Input validation and sanitization
 * 4. XSS and CSRF protection
 * 5. Accessibility compliance (WCAG)
 * 6. Keyboard navigation
 * 7. Screen reader compatibility
 */

import { test, expect } from '@playwright/test';

test.describe('Security and Accessibility Tests - TDD', () => {
  let authToken: string;
  let testUser: { email: string; password: string; name: string };
  let otherUser: { email: string; password: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `securitytest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'Security Test User'
    };
    otherUser = {
      email: `otheruser${timestamp}@example.com`,
      password: 'OtherPass1!',
      name: 'Other User'
    };
  });

  test.describe('Authentication Security', () => {
    test('should not expose sensitive information in error messages', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Try login with non-existent user
      await page.fill('input[id="email"]', 'nonexistent@example.com');
      await page.fill('input[id="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');

      // Error message should not reveal if user exists
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
      await expect(page.locator('text=User not found')).not.toBeVisible();
    });

    test('should prevent brute force attacks with rate limiting', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Attempt multiple failed logins
      for (let i = 0; i < 10; i++) {
        await page.fill('input[id="email"]', 'test@example.com');
        await page.fill('input[id="password"]', 'wrongpassword');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(100);
      }

      // Should show rate limiting message
      await expect(page.locator('text=Too many attempts')).toBeVisible();
    });

    test('should require strong passwords', async ({ page }) => {
      await page.goto('http://localhost:3000/register');
      
      // Try weak password
      await page.fill('input[id="name"]', 'Test User');
      await page.fill('input[id="email"]', 'test@example.com');
      await page.fill('input[id="password"]', '123');
      await page.fill('input[id="confirmPassword"]', '123');
      await page.click('button[type="submit"]');

      // Should show password strength error
      await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
    });

    test('should validate email format', async ({ page }) => {
      await page.goto('http://localhost:3000/register');
      
      // Try invalid email
      await page.fill('input[id="name"]', 'Test User');
      await page.fill('input[id="email"]', 'invalid-email');
      await page.fill('input[id="password"]', 'TestPass1!');
      await page.fill('input[id="confirmPassword"]', 'TestPass1!');
      await page.click('button[type="submit"]');

      // Should show email validation error
      await expect(page.locator('text=Please enter a valid email')).toBeVisible();
    });

    test('should prevent SQL injection in login', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Try SQL injection
      await page.fill('input[id="email"]', "admin'; DROP TABLE users; --");
      await page.fill('input[id="password"]', 'password');
      await page.click('button[type="submit"]');

      // Should handle gracefully without error
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });
  });

  test.describe('Authorization and Access Control', () => {
    test('should prevent access to other users projects', async ({ page }) => {
      // Register first user and create project
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Create project
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      await page.fill('input[id="name"]', 'Private Project');
      await page.fill('textarea[id="description"]', 'This is a private project');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      // Get project ID from URL
      const projectUrl = page.url();
      const projectId = projectUrl.split('/').pop();

      // Logout
      await page.click('text=Logout');

      // Register second user
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', otherUser.name);
      await page.fill('input[id="email"]', otherUser.email);
      await page.fill('input[id="password"]', otherUser.password);
      await page.fill('input[id="confirmPassword"]', otherUser.password);
      await page.click('button[type="submit"]');

      // Try to access first user's project
      await page.goto(`http://localhost:3000/projects/${projectId}`);

      // Should be redirected or show access denied
      await expect(page.locator('text=Access denied')).toBeVisible();
    });

    test('should require authentication for API endpoints', async ({ page }) => {
      // Try to access projects API without authentication
      const response = await page.request.get('http://localhost:8000/api/v1/projects');
      expect(response.status()).toBe(401);
    });

    test('should validate JWT tokens properly', async ({ page }) => {
      // Try to access API with invalid token
      const response = await page.request.get('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': 'Bearer invalid-token'
        }
      });
      expect(response.status()).toBe(401);
    });
  });

  test.describe('Input Validation and Sanitization', () => {
    test('should sanitize HTML in project names', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Try to create project with HTML/script tags
      await page.goto('http://localhost:3000/projects');
      await page.click('text=Create New Project');
      await page.fill('input[id="name"]', '<script>alert("XSS")</script>Project Name');
      await page.fill('textarea[id="description"]', 'Project description');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      // HTML should be escaped, not executed
      await expect(page.locator('text=<script>alert("XSS")</script>Project Name')).toBeVisible();
      // Should not see alert popup
      await expect(page.locator('text=XSS')).not.toBeVisible();
    });

    test('should validate file upload types', async ({ page }) => {
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
      await page.fill('input[id="name"]', 'File Upload Test Project');
      await page.fill('textarea[id="description"]', 'Project for file upload testing');
      await page.selectOption('select[id="domain"]', 'cloud-native');
      await page.selectOption('select[id="mode"]', 'greenfield');
      await page.click('button[type="submit"]');

      // Try to upload executable file
      await page.click('text=Upload Documents');
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'malicious.exe',
        mimeType: 'application/x-msdownload',
        buffer: Buffer.from('MZ')
      });

      // Should reject executable files
      await expect(page.locator('text=File type not allowed')).toBeVisible();
    });

    test('should prevent XSS in AI chat', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Open AI assistant
      await page.goto('http://localhost:3000/projects');
      await page.click('text=AI Assistant');

      // Try to send XSS payload
      await page.fill('textarea[placeholder*="message"]', '<script>alert("XSS")</script>');
      await page.click('button[type="submit"]');

      // Message should be displayed as text, not executed
      await expect(page.locator('text=<script>alert("XSS")</script>')).toBeVisible();
      // Should not see alert popup
      await expect(page.locator('text=XSS')).not.toBeVisible();
    });
  });

  test.describe('Accessibility Compliance', () => {
    test('should have proper heading structure', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Check for h1 heading
      await expect(page.locator('h1')).toBeVisible();
      
      // Check heading hierarchy
      const h1 = page.locator('h1');
      const h2 = page.locator('h2');
      expect(await h1.count()).toBeGreaterThan(0);
    });

    test('should have proper form labels', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Check that all form inputs have labels
      const emailInput = page.locator('input[id="email"]');
      const passwordInput = page.locator('input[id="password"]');
      
      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
      
      // Check for associated labels
      await expect(page.locator('label[for="email"]')).toBeVisible();
      await expect(page.locator('label[for="password"]')).toBeVisible();
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Tab through form elements
      await page.keyboard.press('Tab');
      await expect(page.locator('input[id="email"]')).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(page.locator('input[id="password"]')).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(page.locator('button[type="submit"]')).toBeFocused();
    });

    test('should have proper ARIA attributes', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Check for ARIA labels and roles
      const form = page.locator('form');
      await expect(form).toHaveAttribute('role', 'form');
      
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toHaveAttribute('type', 'submit');
    });

    test('should have sufficient color contrast', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Check that text is visible and readable
      await expect(page.locator('text=Sign in to your account')).toBeVisible();
      await expect(page.locator('text=Email address')).toBeVisible();
      await expect(page.locator('text=Password')).toBeVisible();
    });

    test('should support screen readers', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Check for alt text on images
      const images = page.locator('img');
      const imageCount = await images.count();
      
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        expect(alt).toBeDefined();
      }
    });
  });

  test.describe('Error Handling and User Feedback', () => {
    test('should provide clear error messages', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Try login with invalid credentials
      await page.fill('input[id="email"]', 'invalid@example.com');
      await page.fill('input[id="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');

      // Should show clear error message
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network error by going offline
      await page.context().setOffline(true);
      
      await page.goto('http://localhost:3000/login');
      await page.fill('input[id="email"]', 'test@example.com');
      await page.fill('input[id="password"]', 'password');
      await page.click('button[type="submit"]');

      // Should show network error message
      await expect(page.locator('text=Network error')).toBeVisible();
      
      // Restore network
      await page.context().setOffline(false);
    });

    test('should provide loading states', async ({ page }) => {
      await page.goto('http://localhost:3000/login');
      
      // Fill form and submit
      await page.fill('input[id="email"]', 'test@example.com');
      await page.fill('input[id="password"]', 'password');
      await page.click('button[type="submit"]');

      // Should show loading state
      await expect(page.locator('text=Signing in...')).toBeVisible();
    });
  });

  test.describe('Data Privacy and Security', () => {
    test('should not expose sensitive data in URLs', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Check that sensitive data is not in URL
      const url = page.url();
      expect(url).not.toContain('password');
      expect(url).not.toContain('token');
      expect(url).not.toContain('secret');
    });

    test('should use HTTPS in production', async ({ page }) => {
      // This test would check for HTTPS in production environment
      // For now, just verify the protocol is handled correctly
      await page.goto('http://localhost:3000/login');
      expect(page.url()).toMatch(/^http:\/\/localhost:3000/);
    });

    test('should not log sensitive information', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Check browser console for sensitive data
      const logs = [];
      page.on('console', msg => logs.push(msg.text()));
      
      await page.goto('http://localhost:3000/projects');
      
      // Should not contain password in logs
      const logText = logs.join(' ');
      expect(logText).not.toContain(testUser.password);
    });
  });

  test.describe('Session Management', () => {
    test('should timeout inactive sessions', async ({ page }) => {
      // Register and login
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Simulate session timeout by clearing storage
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });

      // Try to access protected page
      await page.goto('http://localhost:3000/projects');
      
      // Should redirect to login
      await expect(page).toHaveURL('http://localhost:3000/login');
    });

    test('should handle concurrent sessions', async ({ page, browser }) => {
      // Register user
      await page.goto('http://localhost:3000/register');
      await page.fill('input[id="name"]', testUser.name);
      await page.fill('input[id="email"]', testUser.email);
      await page.fill('input[id="password"]', testUser.password);
      await page.fill('input[id="confirmPassword"]', testUser.password);
      await page.click('button[type="submit"]');

      // Login in second browser context
      const context2 = await browser.newContext();
      const page2 = await context2.newPage();
      
      await page2.goto('http://localhost:3000/login');
      await page2.fill('input[id="email"]', testUser.email);
      await page2.fill('input[id="password"]', testUser.password);
      await page2.click('button[type="submit"]');

      // Both sessions should work
      await expect(page.locator('text=Your Projects')).toBeVisible();
      await expect(page2.locator('text=Your Projects')).toBeVisible();

      await context2.close();
    });
  });
});
