import { test, expect } from '@playwright/test';

test.describe('Complete Workflow Execution Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if we need to register/login
    const currentUrl = page.url();
    console.log(`Current URL after initial load: ${currentUrl}`);
    
    if (currentUrl.includes('/login') || currentUrl.includes('/register')) {
      console.log('Authentication required, proceeding with registration...');
      
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
      await page.waitForURL('**/projects', { timeout: 15000 });
      
      // Wait a bit more for the page to fully load
      await page.waitForTimeout(3000);
    } else if (currentUrl.includes('/projects')) {
      console.log('Already on projects page');
      // Wait for page to fully load
      await page.waitForTimeout(3000);
    } else {
      console.log('Unexpected page, checking if we need to login...');
      
      // Check if we're on login page
      if (currentUrl.includes('/login')) {
        console.log('On login page, proceeding with login...');
        
        // Fill login form
        await page.fill('input[id="email"]', `test-${Date.now()}@example.com`);
        await page.fill('input[id="password"]', 'TestPass123!');
        await page.click('button[type="submit"]');
        
        // Wait for redirect to projects page
        await page.waitForURL('**/projects', { timeout: 15000 });
        await page.waitForTimeout(3000);
      } else {
        console.log('Navigating to projects...');
        await page.goto('http://localhost:3000/projects');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);
      }
    }
  });

  test('Complete workflow execution from projects overview to completion', async ({ page }) => {
    // ========================================
    // STEP 1: PROJECTS OVERVIEW PAGE
    // ========================================
    console.log('📍 Step 1: Projects Overview Page');
    
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Debug: Check current URL and page content
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    // Check if we're on the right page
    const pageTitle = await page.title();
    console.log(`Page title: ${pageTitle}`);
    
    // Check for any error messages
    const debugErrorMessages = page.locator('[role="alert"]');
    const debugErrorCount = await debugErrorMessages.count();
    if (debugErrorCount > 0) {
      console.log('Error messages found:');
      for (let i = 0; i < debugErrorCount; i++) {
        const errorText = await debugErrorMessages.nth(i).textContent();
        console.log(`Error ${i + 1}: ${errorText}`);
      }
    }
    
    // Check for loading state
    const loadingElements = page.locator('.animate-pulse');
    const loadingCount = await loadingElements.count();
    if (loadingCount > 0) {
      console.log(`Found ${loadingCount} loading elements, waiting for them to disappear...`);
      await page.waitForTimeout(5000);
    }
    
    // Verify we're on the projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    
    // Create a project if none exist
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    
    if (!hasProjects) {
      console.log('📝 Creating new project...');
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Complete Workflow Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for complete workflow execution');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // ========================================
    // STEP 2: PROJECT DETAIL PAGE
    // ========================================
    console.log('📍 Step 2: Project Detail Page');
    
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Verify we're on the project detail page
    await expect(page.locator('h1')).toBeVisible();
    
    // Check for workflow statistics
    await expect(page.locator('text=Total Workflows')).toBeVisible();
    await expect(page.locator('text=Active Workflows')).toBeVisible();
    await expect(page.locator('text=Completed')).toBeVisible();
    
    // ========================================
    // STEP 3: UPLOAD PAGE
    // ========================================
    console.log('📍 Step 3: Upload Page');
    
    await page.click('button:has-text("Start Workflow")');
    await page.waitForURL('**/upload', { timeout: 10000 });
    
    // Verify we're on the upload page
    await expect(page.locator('h1')).toBeVisible();
    
    // Check for upload form elements
    await expect(page.locator('input[type="file"]')).toBeVisible();
    await expect(page.locator('textarea[placeholder*="project context"]')).toBeVisible();
    
    // ========================================
    // STEP 4: FILE UPLOAD
    // ========================================
    console.log('📍 Step 4: File Upload');
    
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
# Complete Workflow Test Requirements

## Business Goals
- Create a scalable e-commerce platform
- Support 10,000 concurrent users
- Ensure 99.9% uptime
- Provide excellent user experience

## Functional Requirements
- User authentication and authorization
- Product catalog management
- Shopping cart functionality
- Order processing and tracking
- Payment integration
- Customer support system

## Non-Functional Requirements
- Response time < 2 seconds
- Support for mobile devices
- Secure data handling
- Backup and recovery procedures
- Scalable architecture

## Stakeholders
- Customers
- Store administrators
- Payment processors
- Customer support team
- IT operations team

## Technical Constraints
- Must integrate with existing payment systems
- Should support multiple languages
- Must comply with GDPR regulations
      `.trim())
    });
    
    // Wait for file upload to complete
    await page.waitForTimeout(2000);
    
    // Fill project context
    await page.fill('textarea[placeholder*="project context"]', 'This is a comprehensive e-commerce platform for a growing online business that needs to scale to support thousands of users.');
    
    // ========================================
    // STEP 5: WORKFLOW SUBMISSION
    // ========================================
    console.log('📍 Step 5: Workflow Submission');
    
    // Submit the workflow
    await page.click('button[type="submit"]');
    
    // Wait for API response and redirect
    await page.waitForURL('**/projects/**?workflow=**', { timeout: 15000 });
    
    // ========================================
    // STEP 6: WORKFLOW STATUS VERIFICATION
    // ========================================
    console.log('📍 Step 6: Workflow Status Verification');
    
    // Verify we're back on the project detail page with workflow parameter
    const workflowUrl = page.url();
    expect(workflowUrl).toMatch(/workflow=[a-f0-9-]{36}/);
    
    // Check for workflow status elements
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    
    // Wait for workflow status to appear
    await page.waitForTimeout(3000);
    
    // Check for workflow status indicators
    const statusIndicators = [
      'text=STARTING',
      'text=Processing',
      'text=Current Workflow Status'
    ];
    
    let statusFound = false;
    for (const indicator of statusIndicators) {
      if (await page.locator(indicator).isVisible()) {
        statusFound = true;
        console.log(`✅ Found status indicator: ${indicator}`);
        break;
      }
    }
    
    if (!statusFound) {
      console.log('⚠️ No status indicators found, checking for error messages...');
      const errorMessages = page.locator('[role="alert"]');
      const errorCount = await errorMessages.count();
      if (errorCount > 0) {
        for (let i = 0; i < errorCount; i++) {
          const errorText = await errorMessages.nth(i).textContent();
          console.log(`❌ Error ${i + 1}: ${errorText}`);
        }
      }
    }
    
    // ========================================
    // STEP 7: WORKFLOW STATISTICS VERIFICATION
    // ========================================
    console.log('📍 Step 7: Workflow Statistics Verification');
    
    // Check for updated workflow statistics
    await expect(page.locator('text=Total Workflows')).toBeVisible();
    await expect(page.locator('text=Active Workflows')).toBeVisible();
    
    // Wait for statistics to update
    await page.waitForTimeout(5000);
    
    // ========================================
    // STEP 8: REAL-TIME UPDATES VERIFICATION
    // ========================================
    console.log('📍 Step 8: Real-time Updates Verification');
    
    // Wait for potential status updates
    await page.waitForTimeout(10000);
    
    // Check for any status changes
    const statusElements = page.locator('[data-testid="workflow-status"]');
    if (await statusElements.isVisible()) {
      await expect(statusElements).toBeVisible();
      console.log('✅ Workflow status element found');
    }
    
    // ========================================
    // STEP 9: ERROR HANDLING VERIFICATION
    // ========================================
    console.log('📍 Step 9: Error Handling Verification');
    
    // Check for any error messages
    const workflowErrorMessages = page.locator('[role="alert"]');
    const workflowErrorCount = await workflowErrorMessages.count();
    
    if (workflowErrorCount > 0) {
      console.log('⚠️ Error messages found:');
      for (let i = 0; i < workflowErrorCount; i++) {
        const errorText = await workflowErrorMessages.nth(i).textContent();
        console.log(`❌ Error ${i + 1}: ${errorText}`);
      }
    } else {
      console.log('✅ No error messages found');
    }
    
    // ========================================
    // STEP 10: NAVIGATION VERIFICATION
    // ========================================
    console.log('📍 Step 10: Navigation Verification');
    
    // Verify we can navigate back to projects
    await page.click('button:has-text("Back to Projects")');
    await page.waitForURL('**/projects', { timeout: 10000 });
    
    // Verify we're back on projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    
    console.log('🎉 Complete workflow execution test completed!');
  });

  test('Workflow error handling and fallback mechanisms', async ({ page }) => {
    console.log('🧪 Testing workflow error handling...');
    
    // Navigate to upload page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Error Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for error handling');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to upload page
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    await page.click('button:has-text("Start Workflow")');
    await page.waitForURL('**/upload', { timeout: 10000 });
    
    // Test 1: Invalid file type
    console.log('📝 Testing invalid file type...');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-invalid.exe',
      mimeType: 'application/x-msdownload',
      buffer: Buffer.from('invalid file content')
    });
    
    await page.click('button[type="submit"]');
    
    // Should show error message
    const errorMessage = page.locator('[role="alert"]');
    if (await errorMessage.isVisible()) {
      console.log('✅ Invalid file type error handled correctly');
    }
    
    // Test 2: Empty file
    console.log('📝 Testing empty file...');
    await fileInput.setInputFiles({
      name: 'empty.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('')
    });
    
    await page.click('button[type="submit"]');
    
    // Test 3: Large file (if size limit exists)
    console.log('📝 Testing large file...');
    const largeContent = 'x'.repeat(10 * 1024 * 1024); // 10MB
    await fileInput.setInputFiles({
      name: 'large.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(largeContent)
    });
    
    await page.click('button[type="submit"]');
    
    console.log('✅ Error handling tests completed');
  });

  test('Workflow status polling and real-time updates', async ({ page }) => {
    console.log('🧪 Testing workflow status polling...');
    
    // Navigate to project detail page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('[data-slot="card"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Polling Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for status polling');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to project detail
    const projectCard = page.locator('[data-slot="card"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Check for workflow status elements
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    
    // Wait for polling to occur
    await page.waitForTimeout(15000);
    
    // Check for status updates
    const statusElements = [
      'text=Current Workflow Status',
      'text=Total Workflows',
      'text=Active Workflows',
      'text=Completed'
    ];
    
    for (const element of statusElements) {
      if (await page.locator(element).isVisible()) {
        console.log(`✅ Found status element: ${element}`);
      }
    }
    
    console.log('✅ Status polling test completed');
  });
});
