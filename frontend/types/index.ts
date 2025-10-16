// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  domain: 'cloud-native' | 'data-platform' | 'enterprise';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  domain: 'cloud-native' | 'data-platform' | 'enterprise';
}

// Requirements types
export interface StructuredRequirements {
  business_goals: string[];
  functional_requirements: string[];
  non_functional_requirements: {
    performance: string[];
    security: string[];
    scalability: string[];
    reliability: string[];
    maintainability: string[];
  };
  constraints: string[];
  stakeholders: Array<{
    name: string;
    role: string;
    concerns: string[];
  }>;
}

export interface ClarificationQuestion {
  question: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Requirements {
  id: string;
  project_id: string;
  structured_requirements: StructuredRequirements;
  clarification_questions: ClarificationQuestion[];
  identified_gaps: string[];
  confidence_score: number;
  status: string;
  created_at: string;
}

// Architecture types
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

// Workflow types
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

export interface WorkflowStatus {
  session_id: string;
  project_id: string;
  current_stage: string;
  requirements?: Requirements;
  architecture?: Architecture;
  errors: string[];
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// File upload types
export interface FileUpload {
  file: File;
  project_id: string;
  domain: string;
  project_context?: string;
}

// Human feedback types
export interface HumanFeedback {
  decision: 'approved' | 'rejected' | 'needs_info';
  comments?: string;
  constraints?: string[];
  preferences?: string[];
}
