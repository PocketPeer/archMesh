// Browser Console Test Script
// Copy and paste this into the browser console on http://localhost:3000

console.log('🔍 Starting Frontend API Test...');

// Test 1: Check if apiClient is available
console.log('apiClient available:', typeof apiClient !== 'undefined');

if (typeof apiClient !== 'undefined') {
  console.log('apiClient baseUrl:', apiClient.baseUrl);
  
  // Test 2: Make API call
  apiClient.getProjects(0, 6)
    .then(result => {
      console.log('✅ API call successful:', result);
      console.log('Projects found:', result.items.length);
    })
    .catch(error => {
      console.error('❌ API call failed:', error);
    });
} else {
  console.error('❌ apiClient not found - check imports');
}

// Test 3: Direct fetch test
fetch('http://localhost:8000/api/v1/projects/?skip=0&limit=6')
  .then(response => {
    console.log('Direct fetch status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('✅ Direct fetch successful:', data);
    console.log('Projects found:', data.projects.length);
  })
  .catch(error => {
    console.error('❌ Direct fetch failed:', error);
  });

console.log('🔍 Test completed - check results above');
