/**
 * Architecture Comparison types and interfaces.
 * 
 * Defines data structures for comparing current and proposed architectures
 * with detailed change tracking and impact analysis.
 */

import { Service, Dependency, ArchitectureGraph } from './architecture';

export type ChangeType = 'add' | 'modify' | 'remove' | 'deprecate';
export type EntityType = 'service' | 'component' | 'dependency' | 'interface' | 'data_model';
export type ImpactLevel = 'low' | 'medium' | 'high' | 'critical';
export type ViewMode = 'side-by-side' | 'overlay' | 'diff';

export interface ArchitectureChange {
  id: string;
  type: ChangeType;
  entity: EntityType;
  name: string;
  description: string;
  impact: ImpactLevel;
  affectedServices: string[];
  breakingChange: boolean;
  migrationRequired: boolean;
  estimatedEffort: number; // in hours
  riskLevel: 'low' | 'medium' | 'high';
  dependencies: string[];
  metadata?: {
    reason?: string;
    alternatives?: string[];
    rollbackPlan?: string;
    testingRequired?: boolean;
    documentationRequired?: boolean;
  };
}

export interface ArchitectureComparison {
  currentArchitecture: ArchitectureGraph;
  proposedArchitecture: ArchitectureGraph;
  changes: ArchitectureChange[];
  summary: {
    totalChanges: number;
    additions: number;
    modifications: number;
    removals: number;
    deprecations: number;
    breakingChanges: number;
    estimatedEffort: number;
    riskLevel: ImpactLevel;
  };
  metadata: {
    comparedAt: string;
    comparedBy: string;
    version: string;
    description: string;
  };
}

export interface ServiceChange {
  serviceId: string;
  changeType: ChangeType;
  currentService?: Service;
  proposedService?: Service;
  changes: {
    name?: { from: string; to: string };
    technology?: { from: string; to: string };
    status?: { from: string; to: string };
    endpoints?: { added: string[]; removed: string[]; modified: string[] };
    dependencies?: { added: string[]; removed: string[]; modified: string[] };
    metadata?: Record<string, { from: any; to: any }>;
  };
  impact: ImpactLevel;
  affectedDependencies: string[];
}

export interface DependencyChange {
  dependencyId: string;
  changeType: ChangeType;
  currentDependency?: Dependency;
  proposedDependency?: Dependency;
  changes: {
    source?: { from: string; to: string };
    target?: { from: string; to: string };
    type?: { from: string; to: string };
    protocol?: { from: string; to: string };
    frequency?: { from: string; to: string };
  };
  impact: ImpactLevel;
  affectedServices: string[];
}

export interface ImpactAnalysis {
  overallImpact: ImpactLevel;
  affectedSystems: string[];
  riskFactors: {
    breakingChanges: number;
    dataMigrationRequired: boolean;
    downtimeRequired: boolean;
    rollbackComplexity: ImpactLevel;
    testingComplexity: ImpactLevel;
  };
  recommendations: {
    implementation: string[];
    testing: string[];
    deployment: string[];
    monitoring: string[];
  };
  timeline: {
    planning: number; // days
    development: number; // days
    testing: number; // days
    deployment: number; // days
    total: number; // days
  };
}

export interface ArchitectureComparisonProps {
  currentArchitecture: ArchitectureGraph;
  proposedArchitecture: ArchitectureGraph;
  changes: ArchitectureChange[];
  impactAnalysis: ImpactAnalysis;
  onApprove: (approval: ApprovalDecision) => void;
  onReject: (reason: string) => void;
  onExport: (format: 'pdf' | 'json' | 'html') => void;
  viewMode?: ViewMode;
  showImpactAnalysis?: boolean;
  showApprovalWorkflow?: boolean;
  className?: string;
}

export interface ApprovalDecision {
  approved: boolean;
  approver: string;
  comments: string;
  conditions?: string[];
  timeline?: {
    startDate: string;
    endDate: string;
  };
}

export interface ComparisonViewProps {
  currentServices: Service[];
  proposedServices: Service[];
  currentDependencies: Dependency[];
  proposedDependencies: Dependency[];
  changes: ArchitectureChange[];
  viewMode: ViewMode;
  onServiceClick: (service: Service, isCurrent: boolean) => void;
  onDependencyClick: (dependency: Dependency, isCurrent: boolean) => void;
  className?: string;
}

export interface ChangesPanelProps {
  changes: ArchitectureChange[];
  impactAnalysis: ImpactAnalysis;
  onChangeClick: (change: ArchitectureChange) => void;
  onFilterChange: (filter: ChangeFilter) => void;
  selectedChangeId?: string;
  className?: string;
}

export interface ChangeFilter {
  types: ChangeType[];
  entities: EntityType[];
  impacts: ImpactLevel[];
  breakingChangesOnly: boolean;
  searchQuery: string;
}

export interface ImpactAnalysisPanelProps {
  impactAnalysis: ImpactAnalysis;
  changes: ArchitectureChange[];
  onRecommendationClick: (recommendation: string) => void;
  className?: string;
}

export interface ApprovalWorkflowProps {
  onApprove: (decision: ApprovalDecision) => void;
  onReject: (reason: string) => void;
  onRequestChanges: (feedback: string) => void;
  currentApprover?: string;
  approvalHistory: ApprovalHistory[];
  className?: string;
}

export interface ApprovalHistory {
  id: string;
  approver: string;
  decision: 'approved' | 'rejected' | 'changes_requested';
  comments: string;
  timestamp: string;
  version: string;
}

export interface ComparisonLegendProps {
  className?: string;
}

export interface ExportOptions {
  format: 'pdf' | 'json' | 'html';
  includeCharts: boolean;
  includeDetails: boolean;
  includeImpactAnalysis: boolean;
  includeApprovalHistory: boolean;
}

// Utility types for change detection
export interface ChangeDetectionResult {
  serviceChanges: ServiceChange[];
  dependencyChanges: DependencyChange[];
  newServices: Service[];
  removedServices: Service[];
  newDependencies: Dependency[];
  removedDependencies: Dependency[];
}

export interface DiffVisualizationProps {
  currentServices: Service[];
  proposedServices: Service[];
  currentDependencies: Dependency[];
  proposedDependencies: Dependency[];
  changes: ArchitectureChange[];
  onElementClick: (element: Service | Dependency, change?: ArchitectureChange) => void;
  className?: string;
}

// Color schemes for different change types
export const CHANGE_COLORS = {
  add: '#10b981',      // Green
  modify: '#f59e0b',   // Yellow
  remove: '#ef4444',   // Red
  deprecate: '#8b5cf6', // Purple
  unchanged: '#6b7280', // Gray
} as const;

export const IMPACT_COLORS = {
  low: '#10b981',      // Green
  medium: '#f59e0b',   // Yellow
  high: '#ef4444',     // Red
  critical: '#dc2626', // Dark Red
} as const;

// Change type icons
export const CHANGE_ICONS = {
  add: '➕',
  modify: '🔄',
  remove: '❌',
  deprecate: '⚠️',
} as const;

// Impact level icons
export const IMPACT_ICONS = {
  low: '🟢',
  medium: '🟡',
  high: '🟠',
  critical: '🔴',
} as const;
