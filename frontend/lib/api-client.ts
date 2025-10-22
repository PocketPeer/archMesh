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
  state_data: {
    current_stage: string;
    stage_progress: number;
    completed_stages: string[];
    stage_results: Record<string, any>;
    pending_tasks: string[];
    errors: string[];
    metadata: Record<string, any>;
  };
  is_active: boolean;
  started_at: string;
  last_activity_at: string;
  completed_at?: string;
  agent_executions: any[];
  human_feedback: any[];
  estimated_completion?: string;
}

export interface WorkflowStatus {
  session_id: string;
  project_id: string;
  current_stage: string;
  requirements?: Requirements;
  architecture?: Architecture;
  errors: string[];
}

// Simple Modular Architecture Types
export interface SimpleArchitectureRequest {
  input_text: string;
  domain?: string;
  complexity?: string;
}

export interface SimpleArchitectureResponse {
  success: boolean;
  message: string;
  data: {
    requirements: {
      business_goals: any[];
      functional_requirements: any[];
      non_functional_requirements: any[];
      constraints: any[];
      stakeholders: any[];
      validation_score: number;
      validation_status: string;
    };
    architecture: {
      name: string;
      style: string;
      description: string;
      components: any[];
      technology_stack: Record<string, string[]>;
      quality_score: number;
    };
    diagrams: Array<{
      title: string;
      description: string;
      type: string;
      code: string;
    }>;
    recommendations: Array<{
      id: string;
      priority: string;
      title: string;
      description: string;
      impact: string;
      effort: string;
      cost: string;
    }>;
    metadata: {
      input_confidence: number;
      total_requirements: number;
      diagram_count: number;
      recommendation_count: number;
    };
  };
}

export interface WorkflowStartResponse {
  session_id: string;
  project_id: string;
  file_info: {
    file_id: string;
    original_filename: string;
    file_size: number;
  };
  workflow_status: {
    current_stage: string;
    started_at: string;
    is_active: boolean;
  };
  message: string;
}

export interface Requirements {
  id: string;
  project_id: string;
  structured_requirements: any;
  clarification_questions: any[];
  identified_gaps: string[];
  confidence_score: number;
  status: string;
  created_at: string;
}

export interface Architecture {
  id: string;
  project_id: string;
  architecture_style: string;
  components: any[];
  c4_diagram_context?: string;
  technology_stack: Record<string, any>;
  alternatives: any[];
  status: string;
  created_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    const envBase = typeof process !== 'undefined' ? (process.env.NEXT_PUBLIC_API_BASE as string | undefined) : undefined;
    this.baseUrl = envBase || baseUrl;
  }

  private getAuthTokens(): { accessToken?: string; refreshToken?: string } {
    try {
      const accessToken = typeof window !== 'undefined' ? localStorage.getItem('accessToken') || undefined : undefined;
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refreshToken') || undefined : undefined;
      return { accessToken, refreshToken };
    } catch {
      return {};
    }
  }

  private setAuthTokens(accessToken: string, refreshToken?: string): void {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('accessToken', accessToken);
        if (refreshToken) {
          localStorage.setItem('refreshToken', refreshToken);
        }
      }
    } catch {
      // Ignore localStorage errors
    }
  }

  private clearAuthTokens(): void {
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      }
    } catch {
      // Ignore localStorage errors
    }
  }

  getHeaders(extra?: Record<string, string>, skipContentType?: boolean): HeadersInit {
    const headers: Record<string, string> = {
      ...(skipContentType ? {} : { 'Content-Type': 'application/json' }),
      ...(extra || {}),
    };
    const { accessToken } = this.getAuthTokens();
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return headers;
  }

  async refreshToken(): Promise<boolean> {
    try {
      const { refreshToken } = this.getAuthTokens();
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        // Try to parse error response
        try {
          const errorData = await response.json();
          console.warn('Token refresh failed:', errorData);
        } catch {
          console.warn('Token refresh failed with status:', response.status);
        }
        return false;
      }

      const data = await response.json();
      if (data.success && data.access_token) {
        this.setAuthTokens(data.access_token, data.refresh_token);
        return true;
      }
      return false;
    } catch (error) {
      console.warn('Token refresh error:', error);
      return false;
    }
  }

  async makeRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      redirect: 'follow',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || errorData.message || response.statusText;
      throw new Error(`Request failed: ${errorMessage}`);
    }

    return response;
  }

  async makeAuthenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    let response = await fetch(url, {
      ...options,
      redirect: 'follow',
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    // If token expired, try to refresh and retry once
    if (response.status === 401) {
      console.log('Token expired, attempting refresh...');
      const refreshed = await this.refreshToken();
      if (refreshed) {
        console.log('Token refreshed successfully, retrying request...');
        response = await fetch(url, {
          ...options,
          redirect: 'follow',
          headers: {
            ...this.getHeaders(),
            ...options.headers,
          },
        });
      } else {
        console.warn('Token refresh failed, clearing auth tokens');
        this.clearAuthTokens();
        // Dispatch event to notify auth context
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:logout'));
        }
      }
    }

    return response;
  }

  async getProject(projectId: string): Promise<Project> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/projects/${projectId}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({} as any));
      const detail = (err && (err.detail || err.error || err.message)) || response.statusText;
      throw new Error(`Failed to fetch project: ${detail}`);
    }
    return response.json();
  }

  async listProjects(): Promise<Project[]> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/projects`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    const data = await response.json();
    return data.projects || [];
  }

  async createProject(project: Partial<Project>): Promise<Project> {
    // Backend route expects trailing slash and fields: name, description?, domain
    const payload = {
      name: project.name,
      description: project.description ?? undefined,
      domain: project.domain,
    } as Record<string, any>;
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/projects/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({} as any));
      const detail = (err && (err.detail || err.error || err.message)) || response.statusText;
      throw new Error(`Failed to create project: ${detail}`);
    }
    return response.json();
  }

  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
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
      headers: this.getHeaders(),
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
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflows: ${response.statusText}`);
    }
    const data = await response.json();
    // Backend returns { workflows: [...] } but frontend expects { items: [...] }
    return {
      items: data.workflows || []
    };
  }

  async getWorkflowStatus(sessionId: string): Promise<WorkflowStatus> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/${sessionId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow status: ${response.statusText}`);
    }
    return response.json();
  }

  async getWorkflow(sessionId: string): Promise<WorkflowSession> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/${sessionId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow: ${response.statusText}`);
    }
    return response.json();
  }

  async getRequirements(sessionId: string): Promise<Requirements> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/${sessionId}/requirements`);
    if (!response.ok) {
      throw new Error(`Failed to fetch requirements: ${response.statusText}`);
    }
    return response.json();
  }

  async getArchitecture(sessionId: string): Promise<Architecture> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/${sessionId}/architecture`);
    if (!response.ok) {
      throw new Error(`Failed to fetch architecture: ${response.statusText}`);
    }
    return response.json();
  }

  async approveIntegration(projectId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}/approve-integration`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Failed to approve integration: ${response.statusText}`);
    }
  }

  async rejectIntegration(projectId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/projects/${projectId}/reject-integration`, {
      method: 'POST',
      headers: this.getHeaders(),
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
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/projects?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      throw new Error('Unexpected response type when fetching projects');
    }
    const data = await response.json();
    return { items: data.projects || [] };
  }

  async startArchitectureWorkflow(file: File, projectId: string, domain: string, projectContext?: string, llmProvider?: string): Promise<WorkflowStartResponse> {
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

    const response = await fetch(`${this.baseUrl}/workflows/start-architecture`, {
      method: 'POST',
      headers: this.getHeaders({}, true), // Skip Content-Type for FormData, include Authorization
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({} as any));
      const detail = (err && (err.detail || err.error || err.message)) || response.statusText;
      throw new Error(`Failed to start workflow: ${detail}`);
    }
    return response.json();
  }

  async submitReview(sessionId: string, review: any): Promise<WorkflowStatus> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/workflows/${sessionId}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(review),
    });
    if (!response.ok) {
      throw new Error(`Failed to submit review: ${response.statusText}`);
    }
    return response.json();
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

  // Vibe Coding Tool API methods
  async generateCode(request: {
    user_input: string;
    project_id: string;
    session_id?: string;
    context_sources?: string[];
    language?: string;
    framework?: string;
  }): Promise<{
    success: boolean;
    session_id: string;
    generated_code?: {
      code: string;
      language: string;
      framework?: string;
      quality_score?: number;
    };
    execution_result?: {
      success: boolean;
      stdout: string;
      stderr: string;
      execution_time: number;
      memory_usage_mb?: number;
      cpu_usage_percent?: number;
    };
    error_message?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/vibe-coding/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getSessionStatus(sessionId: string): Promise<{
    session_id: string;
    status: string;
    progress: number;
    current_stage: string;
    result?: any;
  }> {
    const response = await fetch(`${this.baseUrl}/vibe-coding/session/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async submitFeedback(request: {
    session_id: string;
    rating: number;
    comments?: string;
    suggested_changes?: string[];
  }): Promise<{
    session_id: string;
    success: boolean;
    message: string;
  }> {
    const response = await fetch(`${this.baseUrl}/vibe-coding/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Authentication API methods
  async login(email: string, password: string): Promise<{
    success: boolean;
    access_token?: string;
    refresh_token?: string;
    user?: {
      id: string;
      email: string;
      name: string;
      is_verified: boolean;
    };
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    // Parse JSON once
    const json = await response.json().catch(() => ({}));

    if (!response.ok) {
      const err = (json && (json.error || json.detail?.error || json.detail)) || 'Login failed';
      throw new Error(err);
    }

    // Backend may wrap payload in `data`
    const data = (json as any).data || json;

    return {
      success: Boolean(json.success ?? true),
      access_token: data?.access_token,
      refresh_token: data?.refresh_token,
      user: data?.user,
      error: json.error,
    };
  }

  // AI Chat API methods
  async getAIChatModels(): Promise<{
    models: Array<{
      name: string;
      provider: string;
      description: string;
      capabilities: string[];
      cost_per_token: number;
      max_tokens: number;
    }>;
    current_model: string;
    default_model: string;
  }> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/ai-chat/models`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get AI models');
    }

    return response.json();
  }

  async createAIChatSession(title: string = 'New Chat Session'): Promise<{
    id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
    messages: any[];
    current_model: string;
    context: Record<string, any>;
  }> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/ai-chat/sessions`, {
      method: 'POST',
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create chat session');
    }

    return response.json();
  }

  async getAIChatSessions(): Promise<Array<{
    id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
    messages: any[];
    current_model: string;
    context: Record<string, any>;
  }>> {
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/ai-chat/sessions`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get chat sessions');
    }

    return response.json();
  }

  async getAIChatSession(sessionId: string): Promise<{
    id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
    messages: any[];
    current_model: string;
    context: Record<string, any>;
  }> {
    const response = await fetch(`${this.baseUrl}/ai-chat/sessions/${sessionId}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get chat session');
    }

    return response.json();
  }

  async sendAIChatMessage(
    sessionId: string,
    content: string,
    model?: string,
    context?: Record<string, any>
  ): Promise<{
    success: boolean;
    message: {
      id: string;
      content: string;
      role: string;
      timestamp: string;
      model_used?: string;
      metadata?: Record<string, any>;
    };
    session_id: string;
    model_used: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/ai-chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ content, model, context }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
  }

  async switchAIChatModel(sessionId: string, model: string): Promise<{
    success: boolean;
    model: string;
  }> {
    const response = await fetch(`${this.baseUrl}/ai-chat/sessions/${sessionId}/model`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify({ model }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to switch model');
    }

    return response.json();
  }

  async deleteAIChatSession(sessionId: string): Promise<{
    success: boolean;
  }> {
    const response = await fetch(`${this.baseUrl}/ai-chat/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete session');
    }

    return response.json();
  }

  async register(email: string, password: string, name: string): Promise<{
    success: boolean;
    access_token?: string;
    refresh_token?: string;
    user?: {
      id: string;
      email: string;
      name: string;
      is_verified: boolean;
    };
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Registration failed');
    }

    return response.json();
  }


  async logout(accessToken: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ access_token: accessToken }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Logout failed');
    }

    return response.json();
  }

  async changePassword(oldPassword: string, newPassword: string, accessToken: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Password change failed');
    }

    return response.json();
  }

  async requestPasswordReset(email: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/request-password-reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Password reset request failed');
    }

    return response.json();
  }

  async resetPassword(token: string, newPassword: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token, new_password: newPassword }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Password reset failed');
    }

    return response.json();
  }

  async verifyEmail(token: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/auth/verify-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || 'Email verification failed');
    }

    return response.json();
  }

  // Architecture Proposal Methods
  async getArchitectureProposal(projectId: string) {
    return this.makeAuthenticatedRequest(`/projects/${projectId}/architecture/proposal`);
  }

  async generateArchitectureProposal(projectId: string) {
    return this.makeAuthenticatedRequest(`/projects/${projectId}/architecture/proposal`, {
      method: 'POST'
    });
  }

  async updateArchitectureProposal(projectId: string, proposal: any) {
    return this.makeAuthenticatedRequest(`/projects/${projectId}/architecture/proposal`, {
      method: 'PUT',
      body: JSON.stringify(proposal)
    });
  }

  // Diagram Methods
  async generateDiagram(request: {
    project_id: string;
    diagram_type: string;
    output_format: string;
    context?: any;
  }) {
    return this.makeAuthenticatedRequest('/diagrams/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async updateDiagram(diagramId: string, updates: { content: string }) {
    return this.makeAuthenticatedRequest(`/diagrams/${diagramId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteDiagram(diagramId: string) {
    return this.makeAuthenticatedRequest(`/diagrams/${diagramId}`, {
      method: 'DELETE'
    });
  }

  // Knowledge Base Methods
  async saveArchitectureToKnowledgeBase(projectId: string, data: any) {
    return this.makeAuthenticatedRequest(`/projects/${projectId}/architecture/knowledge-base`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async searchKnowledgeBase(query: string, projectId?: string) {
    return this.makeAuthenticatedRequest('/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({ query, project_id: projectId })
    });
  }

  // Project Diagrams Methods
  async getProjectDiagrams(projectId: string) {
    const response = await this.makeAuthenticatedRequest(`/workflow-diagrams/project/${projectId}/diagrams`);
    const data = await response.json();
    return { data: data.diagrams || [] };
  }

  async generateProjectDiagram(request: {
    project_id: string;
    workflow_id: string;
    stage: string;
    workflow_data: any;
    diagram_type: string;
    output_format?: string;
  }) {
    return this.makeAuthenticatedRequest('/workflow-diagrams/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async regenerateDiagram(diagramId: string, request: any) {
    return this.makeAuthenticatedRequest(`/workflow-diagrams/regenerate/${diagramId}`, {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getDiagramStatus(diagramId: string) {
    return this.makeAuthenticatedRequest(`/workflow-diagrams/${diagramId}/status`);
  }

  // Simple Modular Architecture Methods
  async analyzeArchitecture(request: SimpleArchitectureRequest): Promise<SimpleArchitectureResponse> {
    const response = await this.makeRequest('/simple-architecture/analyze', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    return response.json();
  }

  async generateSimpleCode(request: SimpleArchitectureRequest): Promise<SimpleArchitectureResponse> {
    const response = await this.makeRequest('/simple-architecture/generate-code', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    return response.json();
  }

  async getSimpleArchitectureHealth() {
    const response = await this.makeRequest('/simple-architecture/health');
    return response.json();
  }

  // Admin: LLM Interactions
  async listLLMInteractions(params: { stage?: string; provider?: string; model?: string; limit?: number } = {}) {
    const query = new URLSearchParams();
    if (params.stage) query.set('stage', params.stage);
    if (params.provider) query.set('provider', params.provider);
    if (params.model) query.set('model', params.model);
    if (params.limit) query.set('limit', String(params.limit));
    const qs = query.toString();
    // Backend mounts admin router at /api/v1; use baseUrl prefix
    const response = await this.makeAuthenticatedRequest(`${this.baseUrl}/llm/interactions${qs ? `?${qs}` : ''}`);
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to fetch LLM interactions');
    }
    return response.json();
  }
}

// Prefer NEXT_PUBLIC_API_BASE; otherwise use relative '/api/v1' which can be proxied in dev.
export const apiClient = new ApiClient();