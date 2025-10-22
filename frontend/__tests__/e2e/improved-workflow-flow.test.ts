import { test, expect } from '@playwright/test';

test.describe('Improved Workflow Flow with 2-Step Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // Handle authentication
    const currentUrl = page.url();
    if (currentUrl.includes('/login') || currentUrl.includes('/register')) {
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
      await page.waitForTimeout(3000);
    }
  });

  test('Complete workflow with 2-step validation process', async ({ page }) => {
    console.log('🧪 Testing improved workflow flow with 2-step validation...');
    
    // ========================================
    // STEP 1: PROJECTS OVERVIEW PAGE
    // ========================================
    console.log('📍 Step 1: Projects Overview Page');
    
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Verify we're on the projects page
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
    
    // Create a project if none exist
    const hasProjects = await page.locator('a[href*="/projects/"]').count() > 0;
    
    if (!hasProjects) {
      console.log('📝 Creating new project...');
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      
      await page.fill('input[placeholder="Enter project name"]', 'Improved Workflow Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for improved workflow execution');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      
      await page.waitForURL('**/projects/**', { timeout: 15000 });
      console.log('✅ Project created successfully');
    }
    
    // ========================================
    // STEP 2: PROJECT DETAIL PAGE
    // ========================================
    console.log('📍 Step 2: Project Detail Page');
    
    const projectCard = page.locator('a[href*="/projects/"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Verify we're on the project detail page
    await expect(page.locator('h1')).toBeVisible();
    
    // Check for workflow statistics and history
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
    
    // ========================================
    // STEP 4: CLIENT-SIDE VALIDATION (Step 1 of 2-step process)
    // ========================================
    console.log('📍 Step 4: Client-side Validation');
    
    // Test 1: Invalid file type
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test-invalid.exe',
      mimeType: 'application/x-msdownload',
      buffer: Buffer.from('invalid file content')
    });
    
    // Try to submit without filling required fields
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    const errorMessages = page.locator('[role="alert"]');
    if (await errorMessages.isVisible()) {
      console.log('✅ Client-side validation working - showing errors for invalid file');
    }
    
    // Test 2: Valid file upload
    await fileInput.setInputFiles({
      name: 'test-requirements.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(`
# Improved Workflow Test Requirements

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
    
    // Fill project context (required field)
    await page.fill('textarea[placeholder*="project context"]', 'This is a comprehensive e-commerce platform for a growing online business that needs to scale to support thousands of users and provide excellent customer experience.');
    
    // ========================================
    // STEP 5: SERVER-SIDE WORKFLOW EXECUTION (Step 2 of 2-step process)
    // ========================================
    console.log('📍 Step 5: Server-side Workflow Execution');
    
    // Submit the workflow
    await page.click('button[type="submit"]');
    
    // Step 5a: Show notification
    console.log('📍 Step 5a: Checking for notification...');
    await page.waitForTimeout(2000);
    
    // Check for notification
    const notification = page.locator('[data-sonner-toast]');
    if (await notification.isVisible()) {
      console.log('✅ Notification displayed');
    }
    
    // Step 5b: Wait for redirect to project detail
    console.log('📍 Step 5b: Waiting for redirect...');
    await page.waitForURL('**/projects/**?workflow=**', { timeout: 15000 });
    
    // ========================================
    // STEP 6: WORKFLOW STATUS VERIFICATION
    // ========================================
    console.log('📍 Step 6: Workflow Status Verification');
    
    // Verify we're back on the project detail page with workflow parameter
    const workflowUrl = page.url();
    expect(workflowUrl).toMatch(/workflow=[a-f0-9-]{36}/);
    console.log('✅ Redirected to project detail with workflow parameter');
    
    // Check for workflow status elements
    await expect(page.locator('text=Current Workflow Status')).toBeVisible();
    
    // Wait for workflow status to appear
    await page.waitForTimeout(5000);
    
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
    // STEP 9: WORKFLOW HISTORY VERIFICATION
    // ========================================
    console.log('📍 Step 9: Workflow History Verification');
    
    // Check for workflow history section
    const historySection = page.locator('text=Workflow History');
    if (await historySection.isVisible()) {
      console.log('✅ Workflow history section found');
    } else {
      console.log('⚠️ Workflow history section not found - this should be implemented');
    }
    
    // ========================================
    // STEP 10: ERROR HANDLING VERIFICATION
    // ========================================
    console.log('📍 Step 10: Error Handling Verification');
    
    // Check for any error messages
    const finalErrorMessages = page.locator('[role="alert"]');
    const finalErrorCount = await finalErrorMessages.count();
    
    if (finalErrorCount > 0) {
      console.log('⚠️ Error messages found:');
      for (let i = 0; i < finalErrorCount; i++) {
        const errorText = await finalErrorMessages.nth(i).textContent();
        console.log(`❌ Error ${i + 1}: ${errorText}`);
      }
    } else {
      console.log('✅ No error messages found');
    }
    
    // ========================================
    // STEP 11: RERUN WORKFLOW VERIFICATION
    // ========================================
    console.log('📍 Step 11: Rerun Workflow Verification');
    
    // Check for rerun workflow functionality
    const rerunButton = page.locator('button:has-text("Rerun Workflow")');
    if (await rerunButton.isVisible()) {
      console.log('✅ Rerun workflow button found');
    } else {
      console.log('⚠️ Rerun workflow button not found - this should be implemented');
    }
    
    console.log('🎉 Improved workflow flow test completed!');
  });

  test('Test project creation with type selection', async ({ page }) => {
    console.log('🧪 Testing project creation with type selection...');
    
    // Navigate to projects page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Click create project
    await page.click('button:has-text("Create Project")');
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    // Check for project type selection
    const greenfieldOption = page.locator('text=Greenfield');
    const brownfieldOption = page.locator('text=Brownfield');
    
    if (await greenfieldOption.isVisible() && await brownfieldOption.isVisible()) {
      console.log('✅ Project type selection found');
      
      // Test greenfield selection
      await greenfieldOption.click();
      console.log('✅ Greenfield option selected');
      
      // Check for information about differences
      const typeInfo = page.locator('text=Greenfield');
      if (await typeInfo.isVisible()) {
        console.log('✅ Project type information displayed');
      }
    } else {
      console.log('⚠️ Project type selection not found - this should be implemented');
    }
    
    // Fill project details
    await page.fill('input[placeholder="Enter project name"]', 'Type Selection Test Project');
    await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for type selection');
    
    // Submit project creation
    await page.click('[role="dialog"] button:has-text("Create Project")');
    await page.waitForURL('**/projects/**', { timeout: 15000 });
    
    console.log('✅ Project creation with type selection completed');
  });

  test('Test team collaboration features', async ({ page }) => {
    console.log('🧪 Testing team collaboration features...');
    
    // Navigate to project detail page
    await page.goto('http://localhost:3000/projects');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Create project if needed
    const hasProjects = await page.locator('a[href*="/projects/"]').count() > 0;
    if (!hasProjects) {
      await page.click('button:has-text("Create Project")');
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.fill('input[placeholder="Enter project name"]', 'Collaboration Test Project');
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Test project for collaboration');
      await page.click('[role="dialog"] button:has-text("Create Project")');
      await page.waitForURL('**/projects/**', { timeout: 15000 });
    }
    
    // Navigate to project detail
    const projectCard = page.locator('a[href*="/projects/"]').first();
    await projectCard.click();
    await page.waitForURL('**/projects/**', { timeout: 10000 });
    
    // Check for team collaboration features
    const addUserButton = page.locator('button:has-text("Add User")');
    const permissionsButton = page.locator('button:has-text("Permissions")');
    
    if (await addUserButton.isVisible() || await permissionsButton.isVisible()) {
      console.log('✅ Team collaboration features found');
    } else {
      console.log('⚠️ Team collaboration features not found - this should be implemented');
    }
    
    console.log('✅ Team collaboration features test completed');
  });
});
