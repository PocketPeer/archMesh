# Frontend-Backend API Integration Test Concept

## Problem Statement
The frontend startup page shows loading skeletons but never loads actual project data, despite:
- Backend API working correctly (returns 6 projects)
- CORS configured properly
- API client code updated with correct base URL

## Test Concept Overview

### 1. Environment Verification Tests

#### 1.1 Port Configuration Test
```bash
# Check if frontend is running on expected port
curl -s http://localhost:3000 | head -5
curl -s http://localhost:3001 | head -5

# Check backend port
curl -s http://localhost:8000/api/v1/health
```

#### 1.2 Service Status Test
```bash
# Backend health check
curl -v http://localhost:8000/api/v1/health

# Frontend accessibility
curl -v http://localhost:3001
```

### 2. API Client Configuration Tests

#### 2.1 Base URL Verification
- [ ] Verify API client uses correct base URL (`http://localhost:8000/api/v1`)
- [ ] Check if port mismatch (3000 vs 3001) affects API calls
- [ ] Validate CORS configuration includes correct frontend port

#### 2.2 API Client Method Tests
```javascript
// Test individual API client methods
const testApiClient = async () => {
  try {
    // Test 1: Direct fetch to backend
    const directResponse = await fetch('http://localhost:8000/api/v1/projects/?skip=0&limit=6');
    console.log('Direct fetch status:', directResponse.status);
    const directData = await directResponse.json();
    console.log('Direct fetch data:', directData);

    // Test 2: API client method
    const apiResponse = await apiClient.getProjects(0, 6);
    console.log('API client response:', apiResponse);

    // Test 3: Compare results
    console.log('Data matches:', JSON.stringify(directData.projects) === JSON.stringify(apiResponse.items));
  } catch (error) {
    console.error('API test error:', error);
  }
};
```

### 3. Network Layer Tests

#### 3.1 CORS Preflight Test
```bash
# Test CORS preflight request
curl -X OPTIONS \
  -H "Origin: http://localhost:3001" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v http://localhost:8000/api/v1/projects/
```

#### 3.2 Actual Request Test
```bash
# Test actual request with CORS headers
curl -X GET \
  -H "Origin: http://localhost:3001" \
  -H "Content-Type: application/json" \
  -v http://localhost:8000/api/v1/projects/?skip=0&limit=6
```

### 4. Frontend Integration Tests

#### 4.1 Browser Console Debug Test
```javascript
// Add to browser console on http://localhost:3001
const debugApiCall = async () => {
  console.log('=== API Debug Test ===');
  
  // Test 1: Check if apiClient is available
  console.log('apiClient available:', typeof apiClient !== 'undefined');
  
  // Test 2: Check base URL
  console.log('API base URL:', apiClient.baseUrl);
  
  // Test 3: Make API call
  try {
    const result = await apiClient.getProjects(0, 6);
    console.log('API call successful:', result);
  } catch (error) {
    console.error('API call failed:', error);
  }
  
  // Test 4: Direct fetch test
  try {
    const response = await fetch('http://localhost:8000/api/v1/projects/?skip=0&limit=6');
    console.log('Direct fetch status:', response.status);
    const data = await response.json();
    console.log('Direct fetch data:', data);
  } catch (error) {
    console.error('Direct fetch failed:', error);
  }
};

debugApiCall();
```

#### 4.2 Network Tab Analysis
- [ ] Open browser DevTools → Network tab
- [ ] Reload page at http://localhost:3001
- [ ] Look for requests to `localhost:8000`
- [ ] Check request status codes
- [ ] Verify response data
- [ ] Check for CORS errors

### 5. Component-Level Tests

#### 5.1 Page Component Test
```javascript
// Test the main page component
const testPageComponent = () => {
  // Check if loadProjects function is called
  // Verify projects state is updated
  // Check if loading state changes correctly
};
```

#### 5.2 API Client Integration Test
```javascript
// Test API client integration in page component
const testApiIntegration = async () => {
  // Mock the API client
  // Test error handling
  // Test success scenarios
  // Test loading states
};
```

### 6. Configuration Tests

#### 6.1 CORS Configuration Test
```python
# Backend CORS test
# Check if frontend port 3001 is in CORS origins
# Verify CORS headers in response
```

#### 6.2 Environment Variables Test
```bash
# Check environment variables
echo $NEXT_PUBLIC_API_URL
echo $API_BASE_URL
```

### 7. End-to-End Test Scenarios

#### 7.1 Happy Path Test
1. Start backend on port 8000
2. Start frontend on port 3001
3. Navigate to http://localhost:3001
4. Verify projects load within 5 seconds
5. Check that loading skeletons disappear
6. Verify project cards are displayed

#### 7.2 Error Handling Test
1. Stop backend
2. Navigate to frontend
3. Verify error handling (toast message, fallback UI)
4. Restart backend
5. Verify recovery

#### 7.3 Network Failure Test
1. Block network requests to localhost:8000
2. Test frontend behavior
3. Restore network
4. Test recovery

### 8. Debugging Tools

#### 8.1 API Client Debug Wrapper
```javascript
// Enhanced API client with debugging
class DebugApiClient extends ApiClient {
  async getProjects(skip = 0, limit = 10) {
    console.log('🔍 API Debug: getProjects called with', { skip, limit });
    console.log('🔍 API Debug: baseUrl =', this.baseUrl);
    
    const url = `${this.baseUrl}/projects/?skip=${skip}&limit=${limit}`;
    console.log('🔍 API Debug: full URL =', url);
    
    try {
      const response = await fetch(url);
      console.log('🔍 API Debug: response status =', response.status);
      console.log('🔍 API Debug: response headers =', [...response.headers.entries()]);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('🔍 API Debug: response data =', data);
      
      const result = { items: data.projects || [] };
      console.log('🔍 API Debug: transformed result =', result);
      
      return result;
    } catch (error) {
      console.error('🔍 API Debug: error =', error);
      throw error;
    }
  }
}
```

#### 8.2 Network Monitoring
```javascript
// Network request interceptor
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('🌐 Network: Request to', args[0]);
  return originalFetch.apply(this, args)
    .then(response => {
      console.log('🌐 Network: Response from', args[0], response.status);
      return response;
    })
    .catch(error => {
      console.error('🌐 Network: Error for', args[0], error);
      throw error;
    });
};
```

### 9. Test Execution Plan

#### Phase 1: Environment Setup (5 minutes)
1. Verify backend running on port 8000
2. Verify frontend running on port 3001
3. Check CORS configuration includes port 3001

#### Phase 2: API Client Testing (10 minutes)
1. Test API client base URL configuration
2. Test individual API methods
3. Compare with direct fetch calls

#### Phase 3: Network Layer Testing (10 minutes)
1. Test CORS preflight requests
2. Test actual API requests
3. Verify response headers

#### Phase 4: Frontend Integration Testing (15 minutes)
1. Browser console debugging
2. Network tab analysis
3. Component state verification

#### Phase 5: End-to-End Validation (10 minutes)
1. Complete user journey test
2. Error scenario testing
3. Recovery testing

### 10. Expected Results

#### Success Criteria
- [ ] Frontend loads projects within 5 seconds
- [ ] No CORS errors in browser console
- [ ] No network errors in DevTools
- [ ] Loading skeletons disappear
- [ ] Project cards display correctly
- [ ] Error handling works for failures

#### Failure Indicators
- [ ] Loading skeletons persist indefinitely
- [ ] CORS errors in console
- [ ] Network requests fail
- [ ] API client throws errors
- [ ] No requests to backend visible

### 11. Quick Fix Checklist

If issues are found:
1. **Port Mismatch**: Update API client base URL if frontend port changed
2. **CORS Issues**: Add frontend port to backend CORS origins
3. **API Client Issues**: Verify method signatures and response handling
4. **Network Issues**: Check firewall, proxy, or network configuration
5. **Component Issues**: Verify React state management and useEffect hooks

## Implementation Priority

1. **High Priority**: Environment verification and CORS testing
2. **Medium Priority**: API client debugging and network analysis
3. **Low Priority**: Advanced error handling and edge cases

This test concept provides a systematic approach to identify and resolve the frontend-backend integration issue.
