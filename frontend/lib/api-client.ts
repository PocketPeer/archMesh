/**
 * API Client for communicating with the backend
 */

export interface Project {
  id: string;
  name: string;
  description?: string;
  domain: 'cloud-native' | 'data-platform' | 'enterprise';
  mode: 'greenfield' | 'brownfield';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  repository_url?: string;
  existing_architecture?: any;
  proposed_architecture?: any;
  changes?: any[];
}

export interface WorkflowSession {
  session_id: string;
  project_id: string;
  current_stage: string;
  status: string;
  created_at: string;
  updated_at: string;
  context: any;
}

export interface Requirements {
  id: string;
  project_id: string;
  structured_requirements: any;
  created_at: string;
  updated_at: string;
}

export interface Architecture {
  id: string;
  project_id: string;
  architecture_design: any;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  async getProject(projectId: string): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch project: ${response.statusText}`);
    }
    return response.json();
  }

  async listProjects(): Promise<Project[]> {
    const response = await fetch(`${this.baseUrl}/projects`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    return response.json();
  }

  async createProject(project: Partial<Project>): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(project),
    });
    if (!response.ok) {
      throw new Error(`Failed to create project: ${response.statusText}`);
    }
    return response.json();
  }

  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    if (!response.ok) {
      throw new Error(`Failed to update project: ${response.statusText}`);
    }
    return response.json();
  }

  async deleteProject(projectId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete project: ${response.statusText}`);
    }
  }

  async listWorkflows(skip: number = 0, limit: number = 10, projectId?: string): Promise<{ items: WorkflowSession[] }> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (projectId) {
      params.append('project_id', projectId);
    }
    const response = await fetch(`${this.baseUrl}/workflows/?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflows: ${response.statusText}`);
    }
    return response.json();
  }

  async getWorkflowStatus(sessionId: string): Promise<WorkflowSession> {
    const response = await fetch(`${this.baseUrl}/workflows/${sessionId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow status: ${response.statusText}`);
    }
    return response.json();
  }

  async getRequirements(sessionId: string): Promise<Requirements> {
    const response = await fetch(`${this.baseUrl}/workflows/${sessionId}/requirements`);
    if (!response.ok) {
      throw new Error(`Failed to fetch requirements: ${response.statusText}`);
    }
    return response.json();
  }

  async getArchitecture(sessionId: string): Promise<Architecture> {
    const response = await fetch(`${this.baseUrl}/workflows/${sessionId}/architecture`);
    if (!response.ok) {
      throw new Error(`Failed to fetch architecture: ${response.statusText}`);
    }
    return response.json();
  }

  async approveIntegration(projectId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}/approve-integration`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to approve integration: ${response.statusText}`);
    }
  }

  async rejectIntegration(projectId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}/reject-integration`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to reject integration: ${response.statusText}`);
    }
  }

  async getProjects(skip: number = 0, limit: number = 10): Promise<{ items: Project[] }> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    const response = await fetch(`${this.baseUrl}/projects/?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    return response.json();
  }

  async startArchitectureWorkflow(file: File, projectId: string, domain: string): Promise<{ session_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    formData.append('domain', domain);

    const response = await fetch(`${this.baseUrl}/workflows/start`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error(`Failed to start workflow: ${response.statusText}`);
    }
    return response.json();
  }

  async submitReview(sessionId: string, review: any): Promise<void> {
    const response = await fetch(`${this.baseUrl}/workflows/${sessionId}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(review),
    });
    if (!response.ok) {
      throw new Error(`Failed to submit review: ${response.statusText}`);
    }
  }

  async getHealth(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Failed to fetch health: ${response.statusText}`);
    }
    return response.json();
  }

  async analyzeRepository(repositoryUrl: string, branch: string = 'main', token?: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/analyze-repository`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repository_url: repositoryUrl,
        branch,
        github_token: token,
      }),
    });
    if (!response.ok) {
      throw new Error(`Failed to analyze repository: ${response.statusText}`);
    }
    return response.json();
  }

  async updateProjectMode(projectId: string, mode: 'greenfield' | 'brownfield'): Promise<Project> {
    return this.updateProject(projectId, { mode });
  }
}

export const apiClient = new ApiClient();