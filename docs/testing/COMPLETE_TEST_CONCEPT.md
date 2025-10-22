# Complete Test Concept for ArchMesh PoC

## 🎯 **Current Status Summary**

### ✅ **What's Working:**
1. **Backend API**: Running correctly on port 8000
2. **Frontend**: Running on port 3000, API client configured
3. **CORS**: Properly configured between frontend and backend
4. **Project Creation**: Successfully creates projects via API
5. **Workflow Start**: Successfully starts workflow with file upload
6. **Database**: PostgreSQL working, 6 sample projects available

### ❌ **What's Not Working:**
1. **LLM Integration**: DeepSeek API calls failing - "All connection attempts failed"
2. **Workflow Execution**: Stuck in "starting" state due to LLM failures
3. **Requirements Processing**: Cannot parse sample requirements without LLM

## 🔍 **Root Cause Analysis**

The workflow execution fails because:
- **No API keys configured** for DeepSeek or other LLM providers
- **DeepSeek base URL** points to `http://localhost:11434` (Ollama) instead of DeepSeek API
- **LLM calls fail** during requirements parsing stage

## 🚀 **Complete Test Concept**

### **Phase 1: Environment Setup & Verification**

#### 1.1 Service Status Check
```bash
# Backend health
curl -s http://localhost:8000/api/v1/health | jq '.'

# Frontend accessibility  
curl -s http://localhost:3000 | head -5

# Database connectivity
curl -s http://localhost:8000/api/v1/projects/?skip=0&limit=1 | jq '.projects[0].id'
```

#### 1.2 API Integration Test
```bash
# Test project creation
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Test project for validation",
    "domain": "cloud-native",
    "mode": "greenfield"
  }' | jq '.id'

# Test project listing
curl -s "http://localhost:8000/api/v1/projects/?skip=0&limit=6" | jq '.projects | length'
```

### **Phase 2: LLM Configuration & Testing**

#### 2.1 Configure DeepSeek API
```bash
# Set environment variables
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# Or create .env file
echo "DEEPSEEK_API_KEY=your-deepseek-api-key" >> backend/.env
echo "DEEPSEEK_BASE_URL=https://api.deepseek.com" >> backend/.env
```

#### 2.2 Test LLM Connection
```bash
# Test direct LLM call
curl -X POST "http://localhost:8000/api/v1/test-llm" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you respond?"}'
```

#### 2.3 Alternative: Mock LLM for Testing
```python
# Create mock LLM service for testing
# This allows testing the workflow without API costs
```

### **Phase 3: Workflow Execution Testing**

#### 3.1 Upload Sample Requirements
```bash
# Upload sample requirements file
curl -X POST "http://localhost:8000/api/v1/workflows/start-architecture" \
  -H "Origin: http://localhost:3000" \
  -F "file=@/Users/schwipee/dev/archMesh/archmesh-poc/sample-docs/sample-requirements.txt" \
  -F "project_id=YOUR_PROJECT_ID" \
  -F "domain=cloud-native" \
  -F "project_context=E-commerce platform for handmade crafts" \
  -F "llm_provider=deepseek"
```

#### 3.2 Monitor Workflow Progress
```bash
# Check workflow status
curl -s "http://localhost:8000/api/v1/workflows/SESSION_ID/status" | jq '.'

# Monitor progress
watch -n 5 'curl -s "http://localhost:8000/api/v1/workflows/SESSION_ID/status" | jq ".current_stage, .state_data.stage_progress"'
```

#### 3.3 Expected Workflow Stages
1. **starting** → **parse_requirements** (Requirements Agent)
2. **requirements_review** → **design_architecture** (Architecture Agent)  
3. **architecture_review** → **completed**

### **Phase 4: Frontend Integration Testing**

#### 4.1 Browser Console Testing
```javascript
// Test API client in browser console
await apiClient.getProjects(0, 6)
await apiClient.createProject({
  name: "Test Project",
  description: "Test description", 
  domain: "cloud-native",
  mode: "greenfield"
})
```

#### 4.2 End-to-End User Journey
1. **Navigate to** http://localhost:3000
2. **Verify projects load** (should show 6+ projects)
3. **Create new project** using sample requirements
4. **Start workflow** and monitor progress
5. **Review results** (requirements, architecture)

### **Phase 5: Error Handling & Recovery**

#### 5.1 LLM Failure Scenarios
```bash
# Test with invalid API key
export DEEPSEEK_API_KEY="invalid-key"
# Start workflow and verify error handling

# Test with network issues
# Disconnect network and verify graceful degradation
```

#### 5.2 Workflow Error Recovery
```bash
# Check error logs
tail -f backend/logs/error.log

# Test workflow restart
curl -X POST "http://localhost:8000/api/v1/workflows/SESSION_ID/restart"
```

## 🛠️ **Quick Fix Implementation**

### **Option 1: Configure Real DeepSeek API**
```bash
# 1. Get DeepSeek API key from https://platform.deepseek.com
# 2. Set environment variables
export DEEPSEEK_API_KEY="sk-your-key-here"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# 3. Restart backend
cd backend && python -m uvicorn app.main:app --reload
```

### **Option 2: Use Mock LLM for Testing**
```python
# Create mock LLM service that returns sample responses
# This allows testing workflow logic without API costs
```

### **Option 3: Use Alternative LLM Provider**
```bash
# Configure OpenAI or Anthropic as fallback
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-your-anthropic-key"
```

## 📊 **Test Results Validation**

### **Success Criteria:**
- [ ] Projects load in frontend within 5 seconds
- [ ] New project creation works via API and frontend
- [ ] Workflow starts successfully with file upload
- [ ] Requirements parsing completes (with LLM)
- [ ] Architecture design completes (with LLM)
- [ ] Results display in frontend
- [ ] Error handling works gracefully

### **Performance Benchmarks:**
- **API Response Time**: < 500ms for simple operations
- **Workflow Execution**: < 2 minutes for sample requirements
- **Frontend Load Time**: < 3 seconds
- **LLM Response Time**: < 30 seconds per call

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions:**

1. **"All connection attempts failed"**
   - **Cause**: No API key configured
   - **Solution**: Set `DEEPSEEK_API_KEY` environment variable

2. **"Workflow stuck in starting state"**
   - **Cause**: LLM call failing
   - **Solution**: Check API key and network connectivity

3. **"CORS errors in browser"**
   - **Cause**: Frontend port not in CORS origins
   - **Solution**: Add port to `cors_origins` in config

4. **"Projects not loading"**
   - **Cause**: API client base URL incorrect
   - **Solution**: Verify `apiClient.baseUrl` in frontend

## 📋 **Next Steps**

1. **Configure LLM Provider** (DeepSeek API key)
2. **Test Workflow Execution** with sample requirements
3. **Validate End-to-End Flow** from frontend to backend
4. **Performance Testing** with larger requirements files
5. **Error Handling Testing** with various failure scenarios

## 🎯 **Expected Outcome**

After implementing the LLM configuration:
- ✅ Complete workflow execution from requirements to architecture
- ✅ Frontend displays parsed requirements and generated architecture
- ✅ All API endpoints working correctly
- ✅ Error handling and recovery mechanisms functional
- ✅ Ready for production deployment with proper API keys

This test concept provides a comprehensive approach to validate the entire ArchMesh PoC system, with particular focus on resolving the LLM integration issue that's currently blocking workflow execution.
