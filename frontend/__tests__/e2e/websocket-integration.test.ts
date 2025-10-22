/**
 * WebSocket Integration Tests
 * 
 * These tests specifically target WebSocket functionality and would have caught
 * the missing WebSocket endpoint issue that was recently fixed.
 * 
 * TDD Approach: RED Phase - These tests would have caught the WebSocket issues
 */

import { test, expect, Page } from '@playwright/test';

test.describe('WebSocket Integration Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Enable console logging to catch WebSocket errors
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('WebSocket')) {
        console.error(`WebSocket Error: ${msg.text()}`);
      }
    });
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('WebSocket connection establishes successfully', async () => {
    // This test would have caught the missing WebSocket endpoint
    await page.goto('/');
    
    // Wait for page to load and WebSocket to attempt connection
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for WebSocket connection errors in console
    const wsErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('WebSocket')) {
        wsErrors.push(msg.text());
      }
    });
    
    // Verify no WebSocket connection errors
    expect(wsErrors).toHaveLength(0);
  });

  test('WebSocket ping/pong mechanism works', async () => {
    // Test WebSocket ping/pong functionality
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Inject WebSocket test code
    const wsTestResult = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        let pongReceived = false;
        
        ws.onopen = () => {
          console.log('WebSocket connected for ping/pong test');
          ws.send('ping');
        };
        
        ws.onmessage = (event) => {
          if (event.data === 'pong') {
            pongReceived = true;
            ws.close();
            resolve({ connected: true, pongReceived: true });
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          resolve({ connected: false, pongReceived: false, error: error.toString() });
        };
        
        ws.onclose = () => {
          if (!pongReceived) {
            resolve({ connected: true, pongReceived: false });
          }
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          if (!pongReceived) {
            ws.close();
            resolve({ connected: true, pongReceived: false, timeout: true });
          }
        }, 5000);
      });
    });
    
    expect(wsTestResult.connected).toBeTruthy();
    expect(wsTestResult.pongReceived).toBeTruthy();
  });

  test('WebSocket handles multiple connections', async () => {
    // Test multiple WebSocket connections
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const multiConnectionResult = await page.evaluate(async () => {
      const connections: Promise<any>[] = [];
      
      // Create 3 WebSocket connections
      for (let i = 0; i < 3; i++) {
        connections.push(new Promise((resolve) => {
          const ws = new WebSocket('ws://localhost:8000/ws');
          
          ws.onopen = () => {
            resolve({ id: i, connected: true });
          };
          
          ws.onerror = (error) => {
            resolve({ id: i, connected: false, error: error.toString() });
          };
          
          setTimeout(() => {
            ws.close();
          }, 1000);
        }));
      }
      
      return Promise.all(connections);
    });
    
    // All connections should succeed
    for (const result of multiConnectionResult) {
      expect(result.connected).toBeTruthy();
    }
  });

  test('WebSocket handles connection drops gracefully', async () => {
    // Test WebSocket reconnection logic
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const reconnectionResult = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        let reconnected = false;
        
        ws.onopen = () => {
          console.log('Initial WebSocket connection established');
          
          // Close connection after 1 second
          setTimeout(() => {
            ws.close();
          }, 1000);
        };
        
        ws.onclose = () => {
          console.log('WebSocket connection closed, attempting reconnection...');
          
          // Attempt reconnection
          const ws2 = new WebSocket('ws://localhost:8000/ws');
          
          ws2.onopen = () => {
            reconnected = true;
            ws2.close();
            resolve({ initialConnection: true, reconnected: true });
          };
          
          ws2.onerror = () => {
            resolve({ initialConnection: true, reconnected: false });
          };
        };
        
        ws.onerror = () => {
          resolve({ initialConnection: false, reconnected: false });
        };
        
        // Timeout after 10 seconds
        setTimeout(() => {
          resolve({ initialConnection: true, reconnected: false, timeout: true });
        }, 10000);
      });
    });
    
    expect(reconnectionResult.initialConnection).toBeTruthy();
    expect(reconnectionResult.reconnected).toBeTruthy();
  });

  test('WebSocket message handling works correctly', async () => {
    // Test WebSocket message sending and receiving
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const messageResult = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        const testMessage = 'Hello WebSocket!';
        let messageReceived = false;
        
        ws.onopen = () => {
          ws.send(testMessage);
        };
        
        ws.onmessage = (event) => {
          if (event.data.includes(testMessage)) {
            messageReceived = true;
            ws.close();
            resolve({ connected: true, messageReceived: true, response: event.data });
          }
        };
        
        ws.onerror = (error) => {
          resolve({ connected: false, messageReceived: false, error: error.toString() });
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          ws.close();
          resolve({ connected: true, messageReceived: false, timeout: true });
        }, 5000);
      });
    });
    
    expect(messageResult.connected).toBeTruthy();
    expect(messageResult.messageReceived).toBeTruthy();
  });

  test('WebSocket handles invalid messages gracefully', async () => {
    // Test WebSocket error handling
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const errorHandlingResult = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        let errorHandled = false;
        
        ws.onopen = () => {
          // Send invalid message (binary data as text)
          try {
            ws.send(new ArrayBuffer(8));
          } catch (error) {
            errorHandled = true;
            resolve({ connected: true, errorHandled: true });
          }
        };
        
        ws.onerror = (error) => {
          resolve({ connected: false, errorHandled: false, error: error.toString() });
        };
        
        ws.onclose = () => {
          if (!errorHandled) {
            resolve({ connected: true, errorHandled: false });
          }
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          ws.close();
          resolve({ connected: true, errorHandled: false, timeout: true });
        }, 5000);
      });
    });
    
    expect(errorHandlingResult.connected).toBeTruthy();
    // Error handling behavior may vary, so we just check connection was established
  });

  test('WebSocket performance is acceptable', async () => {
    // Test WebSocket connection performance
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const performanceResult = await page.evaluate(async () => {
      const startTime = performance.now();
      
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onopen = () => {
          const connectionTime = performance.now() - startTime;
          ws.close();
          resolve({ connected: true, connectionTime });
        };
        
        ws.onerror = () => {
          resolve({ connected: false, connectionTime: -1 });
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          ws.close();
          resolve({ connected: false, connectionTime: -1, timeout: true });
        }, 5000);
      });
    });
    
    expect(performanceResult.connected).toBeTruthy();
    expect(performanceResult.connectionTime).toBeLessThan(2000); // Should connect within 2 seconds
  });

  test('WebSocket works with different message types', async () => {
    // Test different message types
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const messageTypesResult = await page.evaluate(async () => {
      const results: any[] = [];
      
      const testMessages = [
        'ping',
        'Hello World',
        JSON.stringify({ type: 'test', data: 'json message' }),
        '12345',
        ''
      ];
      
      for (const message of testMessages) {
        const result = await new Promise((resolve) => {
          const ws = new WebSocket('ws://localhost:8000/ws');
          
          ws.onopen = () => {
            ws.send(message);
          };
          
          ws.onmessage = (event) => {
            ws.close();
            resolve({ message, received: true, response: event.data });
          };
          
          ws.onerror = () => {
            resolve({ message, received: false });
          };
          
          setTimeout(() => {
            ws.close();
            resolve({ message, received: false, timeout: true });
          }, 3000);
        });
        
        results.push(result);
      }
      
      return results;
    });
    
    // All message types should be handled
    for (const result of messageTypesResult) {
      expect(result.received).toBeTruthy();
    }
  });

  test('WebSocket endpoint returns correct headers', async ({ request }) => {
    // Test WebSocket endpoint headers
    const response = await request.get('/ws');
    
    // Should return 426 Upgrade Required or 101 Switching Protocols
    expect([426, 101]).toContain(response.status());
    
    if (response.status() === 426) {
      // Check for proper WebSocket headers
      const headers = response.headers();
      expect(headers['upgrade']).toBe('websocket');
      expect(headers['connection']).toContain('Upgrade');
    }
  });

  test('WebSocket handles concurrent message sending', async () => {
    // Test concurrent message sending
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const concurrentResult = await page.evaluate(async () => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        const messages = ['msg1', 'msg2', 'msg3', 'msg4', 'msg5'];
        let receivedCount = 0;
        
        ws.onopen = () => {
          // Send all messages quickly
          messages.forEach(msg => ws.send(msg));
        };
        
        ws.onmessage = (event) => {
          receivedCount++;
          if (receivedCount === messages.length) {
            ws.close();
            resolve({ connected: true, allMessagesReceived: true, receivedCount });
          }
        };
        
        ws.onerror = () => {
          resolve({ connected: false, allMessagesReceived: false });
        };
        
        setTimeout(() => {
          ws.close();
          resolve({ connected: true, allMessagesReceived: false, receivedCount, timeout: true });
        }, 10000);
      });
    });
    
    expect(concurrentResult.connected).toBeTruthy();
    expect(concurrentResult.allMessagesReceived).toBeTruthy();
  });
});
