/**
 * E2E Test Utilities
 * 
 * Optimized utilities for E2E testing with better performance
 * and reduced flakiness.
 */

import { Page, expect } from '@playwright/test';
import { E2E_CONFIG } from './test-config';

/**
 * Smart wait for element to be visible with retry logic
 */
export async function waitForElement(
  page: Page, 
  selector: string, 
  options: { timeout?: number; retries?: number } = {}
): Promise<void> {
  const { timeout = E2E_CONFIG.timeouts.element, retries = 3 } = options;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      await page.waitForSelector(selector, { 
        state: 'visible', 
        timeout: timeout / retries 
      });
      return;
    } catch (error) {
      if (attempt === retries - 1) throw error;
      console.log(`Attempt ${attempt + 1} failed, retrying...`);
      await page.waitForTimeout(1000);
    }
  }
}

/**
 * Wait for workflow status to reach a final state
 */
export async function waitForWorkflowStatus(
  page: Page,
  expectedStates: string[] = ['completed', 'failed'],
  timeout: number = E2E_CONFIG.timeouts.workflow
): Promise<string> {
  const startTime = Date.now();
  const pollInterval = E2E_CONFIG.polling.workflow;
  
  while (Date.now() - startTime < timeout) {
    try {
      const statusElement = page.locator(E2E_CONFIG.selectors.workflowStatus);
      const statusText = await statusElement.textContent();
      
      if (statusText && expectedStates.includes(statusText.toLowerCase())) {
        return statusText;
      }
      
      await page.waitForTimeout(pollInterval);
    } catch (error) {
      console.log('Error checking workflow status:', error);
      await page.waitForTimeout(pollInterval);
    }
  }
  
  throw new Error(`Workflow did not reach final state within ${timeout / 1000} seconds`);
}

/**
 * Wait for navigation with proper error handling
 */
export async function waitForNavigation(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = E2E_CONFIG.timeouts.navigation
): Promise<void> {
  try {
    await page.waitForURL(urlPattern, { timeout });
  } catch (error) {
    const currentUrl = page.url();
    console.log(`Navigation timeout. Current URL: ${currentUrl}`);
    throw new Error(`Failed to navigate to ${urlPattern}. Current URL: ${currentUrl}`);
  }
}

/**
 * Fill form with retry logic
 */
export async function fillFormField(
  page: Page,
  selector: string,
  value: string,
  options: { timeout?: number; retries?: number } = {}
): Promise<void> {
  const { timeout = E2E_CONFIG.timeouts.form, retries = 3 } = options;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      await page.fill(selector, value, { timeout: timeout / retries });
      return;
    } catch (error) {
      if (attempt === retries - 1) throw error;
      console.log(`Form fill attempt ${attempt + 1} failed, retrying...`);
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Click element with retry logic
 */
export async function clickElement(
  page: Page,
  selector: string,
  options: { timeout?: number; retries?: number } = {}
): Promise<void> {
  const { timeout = E2E_CONFIG.timeouts.element, retries = 3 } = options;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      await page.click(selector, { timeout: timeout / retries });
      return;
    } catch (error) {
      if (attempt === retries - 1) throw error;
      console.log(`Click attempt ${attempt + 1} failed, retrying...`);
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Wait for API response with timeout
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = E2E_CONFIG.timeouts.api
): Promise<void> {
  try {
    await page.waitForResponse(response => 
      response.url().match(urlPattern) && response.status() < 400,
      { timeout }
    );
  } catch (error) {
    throw new Error(`API request to ${urlPattern} failed or timed out`);
  }
}

/**
 * Create test user with unique data
 */
export function createTestUser(prefix: string = 'test'): {
  email: string;
  password: string;
  name: string;
} {
  const timestamp = Date.now();
  return {
    email: `${prefix}-${timestamp}@example.com`,
    password: 'TestPassword123!',
    name: `E2E Test User ${timestamp}`
  };
}

/**
 * Create test project with unique data
 */
export function createTestProject(prefix: string = 'test'): {
  name: string;
  description: string;
  domain: string;
} {
  const timestamp = Date.now();
  return {
    name: `${prefix} Project ${timestamp}`,
    description: `Test project created at ${new Date().toISOString()}`,
    domain: 'cloud-native'
  };
}

/**
 * Wait for page to be fully loaded
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Take screenshot on failure for debugging
 */
export async function takeFailureScreenshot(page: Page, testName: string): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `failure-${testName}-${timestamp}.png`;
  await page.screenshot({ path: `test-results/${filename}`, fullPage: true });
  console.log(`Screenshot saved: ${filename}`);
}

/**
 * Retry mechanism for flaky operations
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  options: { retries?: number; delay?: number } = {}
): Promise<T> {
  const { retries = 3, delay = 1000 } = options;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === retries - 1) throw error;
      console.log(`Operation failed (attempt ${attempt + 1}/${retries}), retrying...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw new Error('All retry attempts failed');
}

/**
 * Wait for element to be stable (not moving/changing)
 */
export async function waitForElementStable(
  page: Page,
  selector: string,
  timeout: number = 5000
): Promise<void> {
  let previousBoundingBox = await page.locator(selector).boundingBox();
  let stableCount = 0;
  const requiredStableCount = 3;
  
  while (stableCount < requiredStableCount) {
    await page.waitForTimeout(100);
    const currentBoundingBox = await page.locator(selector).boundingBox();
    
    if (previousBoundingBox && currentBoundingBox &&
        previousBoundingBox.x === currentBoundingBox.x &&
        previousBoundingBox.y === currentBoundingBox.y) {
      stableCount++;
    } else {
      stableCount = 0;
    }
    
    previousBoundingBox = currentBoundingBox;
  }
}

/**
 * Assert element is visible with better error messages
 */
export async function assertElementVisible(
  page: Page,
  selector: string,
  description: string = 'element'
): Promise<void> {
  try {
    await expect(page.locator(selector)).toBeVisible();
  } catch (error) {
    const currentUrl = page.url();
    const pageContent = await page.content();
    throw new Error(
      `${description} (${selector}) is not visible on page ${currentUrl}. ` +
      `Page content preview: ${pageContent.substring(0, 200)}...`
    );
  }
}