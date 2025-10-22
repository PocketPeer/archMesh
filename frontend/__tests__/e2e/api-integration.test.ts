/**
 * API INTEGRATION TESTS - TDD Test Suite
 * 
 * Tests all API endpoints and integrations:
 * 1. Authentication API (login, register, refresh, logout)
 * 2. Project API (CRUD operations)
 * 3. Workflow API (start, status, history)
 * 4. AI Chat API (models, messages, context)
 * 5. File Upload API
 * 6. Error handling and status codes
 */

import { test, expect } from '@playwright/test';

test.describe('API Integration Tests - TDD', () => {
  let authToken: string;
  let testUser: { email: string; password: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `apitest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'API Test User'
    };
  });

  test.describe('Authentication API', () => {
    test('POST /api/v1/auth/register - should register new user', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data.email).toBe(testUser.email);
    });

    test('POST /api/v1/auth/login - should login with valid credentials', async ({ request }) => {
      // First register
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      // Then login
      const response = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data.access_token).toBeDefined();
      authToken = data.data.access_token;
    });

    test('POST /api/v1/auth/login - should reject invalid credentials', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: 'invalid@example.com',
          password: 'wrongpassword'
        }
      });

      expect(response.status()).toBe(401);
      const data = await response.json();
      expect(data.success).toBe(false);
    });

    test('POST /api/v1/auth/refresh - should refresh token', async ({ request }) => {
      // Register and login first
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      const refreshToken = loginData.data.refresh_token;

      // Refresh token
      const response = await request.post('http://localhost:8000/api/v1/auth/refresh', {
        data: {
          refresh_token: refreshToken
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data.access_token).toBeDefined();
    });
  });

  test.describe('Project API', () => {
    test.beforeEach(async ({ request }) => {
      // Register, login, and get token
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;
    });

    test('GET /api/v1/projects - should list user projects', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data.projects)).toBe(true);
    });

    test('POST /api/v1/projects - should create new project', async ({ request }) => {
      const projectData = {
        name: 'API Test Project',
        description: 'Project created via API test',
        domain: 'cloud-native',
        mode: 'greenfield'
      };

      const response = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: projectData
      });

      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data.name).toBe(projectData.name);
      expect(data.domain).toBe(projectData.domain);
    });

    test('GET /api/v1/projects/{id} - should get project details', async ({ request }) => {
      // First create a project
      const createResponse = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Detail Test Project',
          description: 'Project for detail test',
          domain: 'cloud-native',
          mode: 'greenfield'
        }
      });

      const project = await createResponse.json();

      // Get project details
      const response = await request.get(`http://localhost:8000/api/v1/projects/${project.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.id).toBe(project.id);
      expect(data.name).toBe('Detail Test Project');
    });

    test('PUT /api/v1/projects/{id} - should update project', async ({ request }) => {
      // Create project
      const createResponse = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Update Test Project',
          description: 'Original description',
          domain: 'cloud-native',
          mode: 'greenfield'
        }
      });

      const project = await createResponse.json();

      // Update project
      const response = await request.put(`http://localhost:8000/api/v1/projects/${project.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Updated Project Name',
          description: 'Updated description'
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.name).toBe('Updated Project Name');
      expect(data.description).toBe('Updated description');
    });

    test('DELETE /api/v1/projects/{id} - should delete project', async ({ request }) => {
      // Create project
      const createResponse = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Delete Test Project',
          description: 'Project to be deleted',
          domain: 'cloud-native',
          mode: 'greenfield'
        }
      });

      const project = await createResponse.json();

      // Delete project
      const response = await request.delete(`http://localhost:8000/api/v1/projects/${project.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(204);

      // Verify project is deleted
      const getResponse = await request.get(`http://localhost:8000/api/v1/projects/${project.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(getResponse.status()).toBe(404);
    });
  });

  test.describe('Workflow API', () => {
    let projectId: string;

    test.beforeEach(async ({ request }) => {
      // Register, login, and create project
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;

      // Create project
      const projectResponse = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Workflow Test Project',
          description: 'Project for workflow testing',
          domain: 'cloud-native',
          mode: 'greenfield'
        }
      });

      const project = await projectResponse.json();
      projectId = project.id;
    });

    test('POST /api/v1/workflows - should start workflow', async ({ request }) => {
      const workflowData = {
        project_id: projectId,
        workflow_type: 'architecture',
        documents: [
          {
            name: 'requirements.txt',
            content: 'The system shall be scalable and secure.'
          }
        ]
      };

      const response = await request.post('http://localhost:8000/api/v1/workflows', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: workflowData
      });

      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data.workflow_id).toBeDefined();
      expect(data.status).toBe('started');
    });

    test('GET /api/v1/workflows - should list workflows', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/workflows', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data.workflows)).toBe(true);
    });

    test('GET /api/v1/workflows/{id} - should get workflow details', async ({ request }) => {
      // Start a workflow first
      const startResponse = await request.post('http://localhost:8000/api/v1/workflows', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          project_id: projectId,
          workflow_type: 'architecture',
          documents: [
            {
              name: 'requirements.txt',
              content: 'The system shall be reliable.'
            }
          ]
        }
      });

      const workflow = await startResponse.json();

      // Get workflow details
      const response = await request.get(`http://localhost:8000/api/v1/workflows/${workflow.workflow_id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.workflow_id).toBe(workflow.workflow_id);
    });
  });

  test.describe('AI Chat API', () => {
    test.beforeEach(async ({ request }) => {
      // Register and login
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;
    });

    test('GET /api/v1/ai/models - should get available models', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/ai/models', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data.models)).toBe(true);
      expect(data.models.length).toBeGreaterThan(0);
    });

    test('POST /api/v1/ai/chat - should send message to AI', async ({ request }) => {
      const messageData = {
        message: 'Hello, can you help me with architecture design?',
        model: 'deepseek-r1',
        session_id: 'test-session-123'
      };

      const response = await request.post('http://localhost:8000/api/v1/ai/chat', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: messageData
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.response).toBeDefined();
      expect(data.session_id).toBe(messageData.session_id);
    });
  });

  test.describe('File Upload API', () => {
    test.beforeEach(async ({ request }) => {
      // Register and login
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;
    });

    test('POST /api/v1/upload - should upload file', async ({ request }) => {
      const formData = new FormData();
      formData.append('file', new Blob(['Test file content'], { type: 'text/plain' }), 'test.txt');
      formData.append('project_id', 'test-project-id');

      const response = await request.post('http://localhost:8000/api/v1/upload', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        multipart: formData
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.file_id).toBeDefined();
      expect(data.filename).toBe('test.txt');
    });
  });

  test.describe('Error Handling', () => {
    test('should return 401 for unauthorized requests', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/projects');
      expect(response.status()).toBe(401);
    });

    test('should return 404 for non-existent resources', async ({ request }) => {
      // Register and login first
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;

      // Try to get non-existent project
      const response = await request.get('http://localhost:8000/api/v1/projects/non-existent-id', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      expect(response.status()).toBe(404);
    });

    test('should return 400 for invalid data', async ({ request }) => {
      // Register and login first
      await request.post('http://localhost:8000/api/v1/auth/register', {
        data: {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password
        }
      });

      const loginData = await loginResponse.json();
      authToken = loginData.data.access_token;

      // Try to create project with invalid data
      const response = await request.post('http://localhost:8000/api/v1/projects', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: '', // Invalid: empty name
          domain: 'invalid-domain' // Invalid: not a valid enum value
        }
      });

      expect(response.status()).toBe(400);
    });
  });
});