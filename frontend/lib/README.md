# API Client Documentation

This directory contains the API client and utility functions for communicating with the ArchMesh backend.

## Files

- `api-client.ts` - Main API client with full TypeScript support
- `utils.ts` - Utility functions (from shadcn/ui)
- `test-api.ts` - API testing utilities

## API Client Usage

### Basic Setup

```typescript
import { apiClient } from '@/lib/api-client';

// The client is pre-configured with the API URL from environment variables
// NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Project Operations

```typescript
// Create a new project
const project = await apiClient.createProject({
  name: "My Project",
  description: "Project description",
  domain: "cloud-native"
});

// Get project by ID
const project = await apiClient.getProject("project-id");

// List all projects
const projects = await apiClient.listProjects(0, 100);

// Update project
const updatedProject = await apiClient.updateProject("project-id", {
  name: "Updated Name"
});

// Delete project
await apiClient.deleteProject("project-id");
```

### Workflow Operations

```typescript
// Start a new workflow
const workflow = await apiClient.startWorkflow(
  "project-id",
  file, // File object
  "cloud-native",
  "Additional context"
);

// Get workflow status
const status = await apiClient.getWorkflowStatus("session-id");

// Submit human review
const result = await apiClient.submitReview("session-id", {
  decision: "approved",
  comments: "Looks good!",
  constraints: [],
  preferences: []
});

// Get requirements
const requirements = await apiClient.getRequirements("session-id");

// Get architecture
const architecture = await apiClient.getArchitecture("session-id");

// Cancel workflow
await apiClient.cancelWorkflow("session-id");
```

### Error Handling

The API client includes comprehensive error handling:

```typescript
try {
  const project = await apiClient.createProject(projectData);
  console.log('Project created:', project);
} catch (error) {
  console.error('Failed to create project:', error.message);
  // Handle error appropriately
}
```

### File Upload

The client handles file uploads with proper FormData:

```typescript
const file = document.getElementById('file-input').files[0];
const workflow = await apiClient.startWorkflow(
  projectId,
  file,
  'cloud-native',
  'Additional context'
);
```

## TypeScript Support

All API methods are fully typed with TypeScript interfaces:

- `Project` - Project data structure
- `ProjectCreate` - Project creation payload
- `WorkflowSession` - Workflow session data
- `WorkflowStatus` - Workflow status response
- `Requirements` - Extracted requirements
- `Architecture` - Generated architecture
- `HumanFeedback` - Review feedback payload

## Environment Configuration

Set the API URL in your `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

Use the test utilities to verify API connectivity:

```typescript
import { testApiConnection, testProjectOperations } from '@/lib/test-api';

// Test API connection
const isConnected = await testApiConnection();

// Test project operations
const projectsWork = await testProjectOperations();
```

Or in the browser console:

```javascript
// Test API connection
await window.testApi.testApiConnection();

// Test project operations
await window.testApi.testProjectOperations();
```

## Error Types

The API client throws errors for:

- Network connectivity issues
- HTTP error responses (4xx, 5xx)
- Invalid request data
- File upload failures
- Authentication issues (if implemented)

All errors include descriptive messages and can be caught with try/catch blocks.
