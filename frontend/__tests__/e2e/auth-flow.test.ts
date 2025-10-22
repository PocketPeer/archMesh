/**
 * TDD Test: Complete Authentication Flow
 * 
 * This test defines the expected behavior for the complete user journey:
 * 1. User can access login page
 * 2. User can register a new account
 * 3. User can login with valid credentials
 * 4. User is redirected to projects page after login
 * 5. User can see projects page (empty for new user)
 * 6. User can create a new project
 * 7. User can see the created project in the list
 */

import { test, expect } from '@playwright/test';

test.describe('Complete Authentication Flow', () => {
  test('should allow user to register, login, and create project', async ({ page }) => {
    // Step 1: Navigate directly to register page
    await page.goto('http://localhost:3000/register');
    await expect(page.locator('text=Create your account')).toBeVisible();
    
    // Step 2: Register a new user
    const timestamp = Date.now();
    const testEmail = `testuser${timestamp}@example.com`;
    const testPassword = 'TestPass1!';
    const testName = 'Test User';
    
    await page.fill('input[id="name"]', testName);
    await page.fill('input[id="email"]', testEmail);
    await page.fill('input[id="password"]', testPassword);
    await page.fill('input[id="confirmPassword"]', testPassword);
    
    await page.click('button[type="submit"]');
    
    // Step 4: Should be redirected to projects page after successful registration
    await expect(page).toHaveURL('http://localhost:3000/projects');
    
    // Step 5: Should see projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    
    // Step 6: Create a new project
    await page.click('text=Create Project');
    
    await page.fill('input[placeholder="Enter project name"]', 'Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'A test project created via TDD');
    await page.selectOption('[role="dialog"] select', 'cloud-native');
    
    await page.click('[role="dialog"] button:has-text("Create Project")');
    
    // Step 7: Should be redirected to project detail page
    await expect(page).toHaveURL(/\/projects\/[a-f0-9-]+/);
    
    // Step 8: Should see project details
    await expect(page.locator('h1:has-text("Test Project")')).toBeVisible();
    await expect(page.locator('text=A test project created via TDD')).toBeVisible();
    
    // Step 9: Navigate back to projects list
    await page.goto('http://localhost:3000/projects');
    
    // Step 10: Should see the created project in the list
    await expect(page.locator('[data-slot="card-title"]:has-text("Test Project")')).toBeVisible();
  });
  
  test('should handle login with existing user', async ({ page }) => {
    // Step 1: Navigate to login page
    await page.goto('http://localhost:3000/login');
    
    // Step 2: Login with existing user (we'll use the user from previous test)
    await page.fill('input[id="email"]', 'newuser@example.com');
    await page.fill('input[id="password"]', 'TestPass1!');
    
    await page.click('button[type="submit"]');
    
    // Step 3: Should be redirected to projects page
    await expect(page).toHaveURL('http://localhost:3000/projects');
    
    // Step 4: Should see projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });
  
  test('should handle invalid login credentials', async ({ page }) => {
    // Step 1: Navigate to login page
    await page.goto('http://localhost:3000/login');
    
    // Step 2: Try to login with invalid credentials
    await page.fill('input[id="email"]', 'invalid@example.com');
    await page.fill('input[id="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Step 3: Should show error message and stay on login page
    await expect(page.locator('[role="alert"]').filter({ hasText: 'Invalid credentials' })).toBeVisible();
    await expect(page).toHaveURL('http://localhost:3000/login');
  });
  
  test('should redirect unauthenticated users to login', async ({ page }) => {
    // Step 1: Try to access projects page without authentication
    await page.goto('http://localhost:3000/projects');
    
    // Step 2: Should be redirected to login page
    await expect(page).toHaveURL('http://localhost:3000/login');
  });
});
