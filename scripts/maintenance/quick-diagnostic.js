#!/usr/bin/env node

/**
 * Quick Diagnostic Script for Frontend-Backend API Integration
 * 
 * This script performs immediate checks to identify the root cause
 * of the frontend API integration issue.
 */

const https = require('https');
const http = require('http');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(color, message) {
  console.log(`${color}${message}${colors.reset}`);
}

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data, headers: res.headers }));
    });
    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function runDiagnostics() {
  log(colors.bold + colors.blue, '🔍 Frontend-Backend API Integration Diagnostic');
  log(colors.blue, '=' .repeat(60));
  
  const results = {
    backend: { status: 'unknown', projects: 0, cors: false },
    frontend: { status: 'unknown', port: null },
    api: { working: false, cors: false }
  };

  // Test 1: Backend Health Check
  log(colors.yellow, '\n1. Testing Backend Health...');
  try {
    const response = await makeRequest('http://localhost:8000/api/v1/health');
    if (response.status === 200) {
      log(colors.green, '✅ Backend is running on port 8000');
      results.backend.status = 'running';
    } else {
      log(colors.red, `❌ Backend returned status ${response.status}`);
    }
  } catch (error) {
    log(colors.red, `❌ Backend not accessible: ${error.message}`);
  }

  // Test 2: Backend Projects API
  log(colors.yellow, '\n2. Testing Backend Projects API...');
  try {
    const response = await makeRequest('http://localhost:8000/api/v1/projects/?skip=0&limit=6');
    if (response.status === 200) {
      const data = JSON.parse(response.data);
      const projectCount = data.projects ? data.projects.length : 0;
      log(colors.green, `✅ Backend API returns ${projectCount} projects`);
      results.backend.projects = projectCount;
    } else {
      log(colors.red, `❌ Backend API returned status ${response.status}`);
    }
  } catch (error) {
    log(colors.red, `❌ Backend API error: ${error.message}`);
  }

  // Test 3: CORS Configuration
  log(colors.yellow, '\n3. Testing CORS Configuration...');
  try {
    const response = await makeRequest('http://localhost:8000/api/v1/projects/?skip=0&limit=6');
    const corsOrigin = response.headers['access-control-allow-origin'];
    if (corsOrigin) {
      log(colors.green, `✅ CORS configured: ${corsOrigin}`);
      results.backend.cors = true;
      
      // Check if it includes the frontend port
      if (corsOrigin.includes('3000') || corsOrigin.includes('3001')) {
        log(colors.green, '✅ CORS includes frontend port');
        results.api.cors = true;
      } else {
        log(colors.yellow, `⚠️  CORS origin ${corsOrigin} may not match frontend port`);
      }
    } else {
      log(colors.red, '❌ No CORS headers found');
    }
  } catch (error) {
    log(colors.red, `❌ CORS test failed: ${error.message}`);
  }

  // Test 4: Frontend Accessibility
  log(colors.yellow, '\n4. Testing Frontend Accessibility...');
  const frontendPorts = [3000, 3001];
  let frontendFound = false;
  
  for (const port of frontendPorts) {
    try {
      const response = await makeRequest(`http://localhost:${port}`);
      if (response.status === 200) {
        log(colors.green, `✅ Frontend is running on port ${port}`);
        results.frontend.status = 'running';
        results.frontend.port = port;
        frontendFound = true;
        break;
      }
    } catch (error) {
      // Port not accessible, continue to next
    }
  }
  
  if (!frontendFound) {
    log(colors.red, '❌ Frontend not accessible on ports 3000 or 3001');
  }

  // Test 5: API Client Configuration Test
  log(colors.yellow, '\n5. Testing API Client Configuration...');
  if (results.frontend.port && results.backend.status === 'running') {
    try {
      // Test with CORS headers
      const response = await makeRequest('http://localhost:8000/api/v1/projects/?skip=0&limit=6');
      if (response.status === 200) {
        log(colors.green, '✅ API endpoint accessible from frontend context');
        results.api.working = true;
      }
    } catch (error) {
      log(colors.red, `❌ API endpoint not accessible: ${error.message}`);
    }
  }

  // Summary and Recommendations
  log(colors.bold + colors.blue, '\n📊 DIAGNOSTIC SUMMARY');
  log(colors.blue, '=' .repeat(60));
  
  log(colors.blue, `Backend Status: ${results.backend.status}`);
  log(colors.blue, `Backend Projects: ${results.backend.projects}`);
  log(colors.blue, `CORS Configured: ${results.backend.cors}`);
  log(colors.blue, `Frontend Port: ${results.frontend.port || 'Not found'}`);
  log(colors.blue, `API Working: ${results.api.working}`);

  // Recommendations
  log(colors.bold + colors.yellow, '\n💡 RECOMMENDATIONS');
  log(colors.yellow, '=' .repeat(60));

  if (!results.backend.status === 'running') {
    log(colors.red, '🔧 Start the backend: cd backend && python -m uvicorn app.main:app --reload');
  }

  if (!results.frontend.port) {
    log(colors.red, '🔧 Start the frontend: cd frontend && npm run dev');
  }

  if (results.frontend.port && results.frontend.port !== 3000) {
    log(colors.yellow, `🔧 Frontend is on port ${results.frontend.port}, update API client base URL if needed`);
  }

  if (!results.api.cors) {
    log(colors.yellow, '🔧 Check CORS configuration in backend/app/config.py');
    log(colors.yellow, '   Ensure cors_origins includes the frontend port');
  }

  if (results.backend.projects === 0) {
    log(colors.yellow, '🔧 No projects found in database, create some test projects');
  }

  // Quick Fix Commands
  log(colors.bold + colors.green, '\n🚀 QUICK FIX COMMANDS');
  log(colors.green, '=' .repeat(60));
  
  if (results.frontend.port === 3001) {
    log(colors.green, '# Update API client base URL:');
    log(colors.green, 'sed -i "s/localhost:8000/localhost:8000/g" frontend/lib/api-client.ts');
  }
  
  log(colors.green, '# Test API client in browser console:');
  log(colors.green, 'await apiClient.getProjects(0, 6)');
  
  log(colors.green, '# Check browser network tab for failed requests');
  log(colors.green, '# Look for CORS errors in console');
}

// Run diagnostics
runDiagnostics().catch(console.error);
