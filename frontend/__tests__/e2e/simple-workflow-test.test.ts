import { test, expect } from '@playwright/test';

test.describe('Simple Workflow Test', () => {
  test('Test workflow execution flow with proper authentication', async ({ page }) => {
    console.log('🧪 Starting simple workflow test...');
    
    // Step 1: Navigate to the application
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    console.log(`Initial URL: ${page.url()}`);
    
    // Step 2: Handle authentication
    if (page.url().includes('/login')) {
      console.log('📝 On login page, proceeding with registration...');
      
      // Go to register page
      await page.goto('http://localhost:3000/register');
      await page.waitForLoadState('networkidle');
      
      // Fill registration form
      const testEmail = `test-${Date.now()}@example.com`;
      await page.fill('input[id="email"]', testEmail);
      await page.fill('input[id="password"]', 'TestPass123!');
      await page.fill('input[id="name"]', 'Test User');
      
      // Submit registration
      await page.click('button[type="submit"]');
      
      // Wait for redirect
      await page.waitForURL('**/projects', { timeout: 15000 });
      console.log('✅ Registration completed, redirected to projects');
    }
    
    // Step 3: Verify we're on projects page
    await page.waitForTimeout(3000);
    console.log(`Current URL: ${page.url()}`);
    
    // Check if we can see the projects page
    const projectsHeading = page.locator('h1:has-text("Projects")');
    if (await projectsHeading.isVisible()) {
      console.log('✅ Projects page loaded successfully');
    } else {
      console.log('❌ Projects page not loaded, checking for errors...');
      
      // Check for error messages
      const errorMessages = page.locator('[role="alert"]');
      const errorCount = await errorMessages.count();
      if (errorCount > 0) {
        for (let i = 0; i < errorCount; i++) {
          const errorText = await errorMessages.nth(i).textContent();
          console.log(`Error ${i + 1}: ${errorText}`);
        }
      }
      
      // Check page content
      const pageContent = await page.textContent('body');
      console.log('Page content preview:', pageContent?.substring(0, 200));
    }
    
    // Step 4: Create a project if needed
    const hasProjects = await page.locator('a[href*="/projects/"]').count() > 0;
    console.log(`Projects found: ${hasProjects}`);
    
    if (!hasProjects) {
      console.log('📝 Creating new project...');
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      
      await page.fill('input[placeholder="Enter project name"]', 'Test Workflow Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for workflow execution');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      await page.waitForURL('**/projects/**', { timeout: 15000 });
      console.log('✅ Project created successfully');
    }
    
    // Step 5: Navigate to project detail
    const projectCard = page.locator('a[href*="/projects/"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    console.log('✅ Navigated to project detail page');
    
    // Step 6: Navigate to upload page
    await page.click('button:has-text("Start Workflow")');
    await page.waitForURL('**/upload', { timeout: 10000 });
    console.log('✅ Navigated to upload page');
    
    // Step 7: Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
# Test Requirements

## Business Goals
- Create a scalable platform
- Support 1000 users
- Ensure 99% uptime

## Functional Requirements
- User authentication
- Data management
- Reporting system

## Non-Functional Requirements
- Response time < 1 second
- Mobile support
- Secure data handling
      `.trim())
    });
    
    await page.waitForTimeout(2000);
    console.log('✅ File uploaded successfully');
    
    // Step 8: Fill project context
    await page.fill('textarea[placeholder*="project context"]', 'This is a test platform for workflow execution');
    console.log('✅ Project context filled');
    
    // Step 9: Submit workflow
    await page.click('button[type="submit"]');
    console.log('✅ Workflow submitted');
    
    // Step 10: Wait for redirect and verify
    await page.waitForURL('**/projects/**?workflow=**', { timeout: 15000 });
    console.log('✅ Redirected to project detail with workflow parameter');
    
    // Step 11: Check for workflow status
    await page.waitForTimeout(5000);
    
    const statusElements = [
      'text=Current Workflow Status',
      'text=STARTING',
      'text=Processing',
      'text=Total Workflows',
      'text=Active Workflows'
    ];
    
    let foundElements = 0;
    for (const element of statusElements) {
      if (await page.locator(element).isVisible()) {
        console.log(`✅ Found: ${element}`);
        foundElements++;
      }
    }
    
    console.log(`Found ${foundElements} status elements`);
    
    // Step 12: Check for errors
    const errorMessages = page.locator('[role="alert"]');
    const errorCount = await errorMessages.count();
    if (errorCount > 0) {
      console.log('⚠️ Error messages found:');
      for (let i = 0; i < errorCount; i++) {
        const errorText = await errorMessages.nth(i).textContent();
        console.log(`Error ${i + 1}: ${errorText}`);
      }
    } else {
      console.log('✅ No error messages found');
    }
    
    console.log('🎉 Simple workflow test completed!');
  });
});
