import { 
  Project, 
  ProjectCreate, 
  WorkflowSession, 
  WorkflowStartResponse, 
  WorkflowStatus,
  Requirements, 
  Architecture, 
  HumanFeedback,
  ApiResponse,
  PaginatedResponse 
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Generic request method with error handling
   */
  async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  /**
   * Upload file with FormData
   */
  async uploadFile<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`File upload failed: ${endpoint}`, error);
      throw error;
    }
  }

  // ==================== PROJECT ENDPOINTS ====================

  /**
   * Create a new project
   */
  async createProject(data: ProjectCreate): Promise<Project> {
    return this.request<Project>('/api/v1/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get project by ID
   */
  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`);
  }

  /**
   * List all projects with pagination
   */
  async listProjects(skip: number = 0, limit: number = 100): Promise<PaginatedResponse<Project>> {
    return this.request<PaginatedResponse<Project>>(
      `/api/v1/projects/?skip=${skip}&limit=${limit}`
    );
  }

  /**
   * Update project
   */
  async updateProject(id: string, data: Partial<ProjectCreate>): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    return this.request<void>(`/api/v1/projects/${id}`, {
      method: 'DELETE',
    });
  }

  // ==================== WORKFLOW ENDPOINTS ====================

  /**
   * Start a new architecture workflow
   */
  async startWorkflow(
    projectId: string, 
    file: File, 
    domain: string = 'cloud-native',
    projectContext?: string,
    llmProvider?: string
  ): Promise<WorkflowStartResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    formData.append('domain', domain);
    if (projectContext) {
      formData.append('project_context', projectContext);
    }
    if (llmProvider) {
      formData.append('llm_provider', llmProvider);
    }

    return this.uploadFile<WorkflowStartResponse>(
      '/api/v1/workflows/start-architecture',
      formData
    );
  }

  /**
   * Get workflow status
   */
  async getWorkflowStatus(sessionId: string): Promise<WorkflowStatus> {
    return this.request<WorkflowStatus>(`/api/v1/workflows/${sessionId}/status`);
  }

  /**
   * List workflows with optional filtering
   */
  async listWorkflows(
    skip: number = 0,
    limit: number = 100,
    projectId?: string,
    isActive?: boolean
  ): Promise<PaginatedResponse<WorkflowSession>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    if (projectId) params.append('project_id', projectId);
    if (isActive !== undefined) params.append('is_active', isActive.toString());

    return this.request<PaginatedResponse<WorkflowSession>>(
      `/api/v1/workflows/?${params.toString()}`
    );
  }

  /**
   * Submit human review feedback
   */
  async submitReview(sessionId: string, feedback: HumanFeedback): Promise<WorkflowStatus> {
    return this.request<WorkflowStatus>(`/api/v1/workflows/${sessionId}/review`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  /**
   * Get requirements from workflow
   */
  async getRequirements(sessionId: string): Promise<Requirements> {
    return this.request<Requirements>(`/api/v1/workflows/${sessionId}/requirements`);
  }

  /**
   * Get architecture from workflow
   */
  async getArchitecture(sessionId: string): Promise<Architecture> {
    return this.request<Architecture>(`/api/v1/workflows/${sessionId}/architecture`);
  }

  /**
   * Cancel workflow
   */
  async cancelWorkflow(sessionId: string): Promise<void> {
    return this.request<void>(`/api/v1/workflows/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // ==================== UTILITY ENDPOINTS ====================

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request<{ status: string; version: string }>('/api/v1/health');
  }

  // ==================== ALIASES FOR BACKWARD COMPATIBILITY ====================

  /**
   * Alias for startWorkflow
   */
  async startArchitectureWorkflow(
    file: File,
    projectId: string,
    domain: string = 'cloud-native',
    projectContext?: string,
    llmProvider?: string
  ): Promise<WorkflowStartResponse> {
    return this.startWorkflow(projectId, file, domain, projectContext, llmProvider);
  }

  /**
   * Alias for submitReview
   */
  async submitWorkflowReview(
    sessionId: string,
    feedback: HumanFeedback
  ): Promise<WorkflowStatus> {
    return this.submitReview(sessionId, feedback);
  }

  /**
   * Alias for getRequirements
   */
  async getWorkflowRequirements(sessionId: string): Promise<Requirements> {
    return this.getRequirements(sessionId);
  }

  /**
   * Alias for getArchitecture
   */
  async getWorkflowArchitecture(sessionId: string): Promise<Architecture> {
    return this.getArchitecture(sessionId);
  }
}

// Create and export singleton instance
export const apiClient = new APIClient();
export default apiClient;