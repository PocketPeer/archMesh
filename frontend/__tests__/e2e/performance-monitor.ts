/**
 * E2E Test Performance Monitor
 * 
 * Tracks test execution performance and identifies bottlenecks.
 */

import { Page } from '@playwright/test';

export interface PerformanceMetrics {
  testName: string;
  startTime: number;
  endTime: number;
  duration: number;
  memoryUsage?: number;
  networkRequests: number;
  errors: string[];
  retries: number;
}

export class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private currentTest?: PerformanceMetrics;
  private networkRequestCount = 0;

  constructor(private page: Page) {
    this.setupNetworkMonitoring();
  }

  startTest(testName: string): void {
    this.currentTest = {
      testName,
      startTime: Date.now(),
      endTime: 0,
      duration: 0,
      networkRequests: 0,
      errors: [],
      retries: 0
    };
    this.networkRequestCount = 0;
  }

  endTest(): PerformanceMetrics | undefined {
    if (!this.currentTest) return undefined;

    this.currentTest.endTime = Date.now();
    this.currentTest.duration = this.currentTest.endTime - this.currentTest.startTime;
    this.currentTest.networkRequests = this.networkRequestCount;

    // Get memory usage if available
    if (typeof process !== 'undefined' && process.memoryUsage) {
      this.currentTest.memoryUsage = process.memoryUsage().heapUsed;
    }

    this.metrics.push(this.currentTest);
    const result = this.currentTest;
    this.currentTest = undefined;
    return result;
  }

  recordError(error: string): void {
    if (this.currentTest) {
      this.currentTest.errors.push(error);
    }
  }

  recordRetry(): void {
    if (this.currentTest) {
      this.currentTest.retries++;
    }
  }

  private setupNetworkMonitoring(): void {
    this.page.on('request', () => {
      this.networkRequestCount++;
    });
  }

  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  getAverageDuration(): number {
    if (this.metrics.length === 0) return 0;
    const totalDuration = this.metrics.reduce((sum, metric) => sum + metric.duration, 0);
    return totalDuration / this.metrics.length;
  }

  getSlowestTests(limit: number = 5): PerformanceMetrics[] {
    return this.metrics
      .sort((a, b) => b.duration - a.duration)
      .slice(0, limit);
  }

  getFlakyTests(): PerformanceMetrics[] {
    return this.metrics.filter(metric => metric.retries > 0 || metric.errors.length > 0);
  }

  generateReport(): string {
    const report = [
      '# E2E Test Performance Report',
      '',
      `## Summary`,
      `- Total Tests: ${this.metrics.length}`,
      `- Average Duration: ${this.getAverageDuration().toFixed(2)}ms`,
      `- Total Duration: ${this.metrics.reduce((sum, m) => sum + m.duration, 0).toFixed(2)}ms`,
      '',
      '## Slowest Tests',
      ''
    ];

    this.getSlowestTests().forEach((metric, index) => {
      report.push(`${index + 1}. ${metric.testName}: ${metric.duration}ms`);
    });

    report.push('', '## Flaky Tests', '');
    this.getFlakyTests().forEach(metric => {
      report.push(`- ${metric.testName}: ${metric.retries} retries, ${metric.errors.length} errors`);
    });

    report.push('', '## Detailed Metrics', '');
    this.metrics.forEach(metric => {
      report.push(`### ${metric.testName}`);
      report.push(`- Duration: ${metric.duration}ms`);
      report.push(`- Network Requests: ${metric.networkRequests}`);
      report.push(`- Retries: ${metric.retries}`);
      report.push(`- Errors: ${metric.errors.length}`);
      if (metric.memoryUsage) {
        report.push(`- Memory Usage: ${(metric.memoryUsage / 1024 / 1024).toFixed(2)}MB`);
      }
      report.push('');
    });

    return report.join('\n');
  }

  saveReport(filename: string = 'test-performance-report.md'): void {
    const fs = require('fs');
    const path = require('path');
    const reportPath = path.join(process.cwd(), 'test-results', filename);
    
    // Ensure directory exists
    const dir = path.dirname(reportPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(reportPath, this.generateReport());
    console.log(`Performance report saved to: ${reportPath}`);
  }
}

/**
 * Decorator for automatic performance monitoring
 */
export function monitorPerformance(monitor: PerformanceMonitor) {
  return function(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;
    
    descriptor.value = async function(...args: any[]) {
      monitor.startTest(propertyName);
      
      try {
        const result = await method.apply(this, args);
        monitor.endTest();
        return result;
      } catch (error) {
        monitor.recordError(error.message);
        monitor.endTest();
        throw error;
      }
    };
  };
}

/**
 * Helper function to measure operation performance
 */
export async function measurePerformance<T>(
  operation: () => Promise<T>,
  operationName: string
): Promise<{ result: T; duration: number }> {
  const startTime = Date.now();
  
  try {
    const result = await operation();
    const duration = Date.now() - startTime;
    
    console.log(`${operationName} completed in ${duration}ms`);
    return { result, duration };
  } catch (error) {
    const duration = Date.now() - startTime;
    console.log(`${operationName} failed after ${duration}ms: ${error.message}`);
    throw error;
  }
}
