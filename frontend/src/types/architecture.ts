/**
 * Architecture visualization types and interfaces.
 * 
 * Defines the data structures for enterprise architecture visualization
 * with multiple zoom levels and interactive features.
 */

export type ServiceType = 'service' | 'database' | 'queue' | 'gateway' | 'cache' | 'monitoring' | 'api' | 'frontend' | 'backend';
export type ServiceStatus = 'healthy' | 'warning' | 'critical' | 'unknown';
export type DependencyType = 'api' | 'event' | 'data' | 'message' | 'sync' | 'async';
export type ZoomLevel = 1 | 2 | 3 | 4;
export type ExportFormat = 'png' | 'svg' | 'json';

export interface Position {
  x: number;
  y: number;
}

export interface Service {
  id: string;
  name: string;
  type: ServiceType;
  technology: string;
  status: ServiceStatus;
  description?: string;
  version?: string;
  owner?: string;
  team?: string;
  environment?: string;
  children?: Service[];  // For drill-down functionality
  position: Position;
  metadata?: {
    endpoints?: string[];
    dependencies?: string[];
    healthCheck?: string;
    documentation?: string;
    repository?: string;
    lastDeployed?: string;
    uptime?: number;
    responseTime?: number;
    errorRate?: number;
  };
}

export interface Dependency {
  id: string;
  source: string;  // service id
  target: string;  // service id
  type: DependencyType;
  protocol?: string;
  description?: string;
  frequency?: 'high' | 'medium' | 'low';
  criticality?: 'critical' | 'important' | 'normal';
  metadata?: {
    endpoint?: string;
    method?: string;
    payload?: string;
    responseTime?: number;
    errorRate?: number;
    lastUsed?: string;
  };
}

export interface ArchitectureGraph {
  services: Service[];
  dependencies: Dependency[];
  metadata?: {
    lastUpdated?: string;
    version?: string;
    totalServices?: number;
    totalDependencies?: number;
    architectureStyle?: string;
  };
}

export interface ZoomLevelConfig {
  level: ZoomLevel;
  name: string;
  description: string;
  nodeFilter: (service: Service) => boolean;
  showDependencies: boolean;
  layout: 'hierarchical' | 'force' | 'circular' | 'grid';
}

export interface VisualConfig {
  nodeSize: {
    min: number;
    max: number;
    default: number;
  };
  colors: {
    healthy: string;
    warning: string;
    critical: string;
    unknown: string;
    background: string;
    grid: string;
    text: string;
  };
  fonts: {
    nodeLabel: string;
    edgeLabel: string;
    tooltip: string;
  };
  animations: {
    enabled: boolean;
    duration: number;
    easing: string;
  };
}

export interface SearchResult {
  service: Service;
  matchType: 'name' | 'technology' | 'type' | 'description';
  score: number;
}

export interface ExportOptions {
  format: ExportFormat;
  includeMetadata: boolean;
  includeDependencies: boolean;
  backgroundColor?: string;
  watermark?: string;
}

export interface ArchitectureVisualizerProps {
  services: Service[];
  dependencies: Dependency[];
  onNodeClick?: (service: Service) => void;
  onNodeDoubleClick?: (service: Service) => void;
  onZoomLevelChange?: (level: ZoomLevel) => void;
  onDependencyClick?: (dependency: Dependency) => void;
  initialZoomLevel?: ZoomLevel;
  selectedNodeId?: string;
  searchQuery?: string;
  showMinimap?: boolean;
  showControls?: boolean;
  showLegend?: boolean;
  enableExport?: boolean;
  enableSearch?: boolean;
  className?: string;
}

export interface ArchitectureControlsProps {
  zoomLevel: ZoomLevel;
  onZoomLevelChange: (level: ZoomLevel) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  onExport: (format: ExportFormat) => void;
  onSearch: (query: string) => void;
  onToggleLayer: (layer: string) => void;
  searchQuery: string;
  searchResults: SearchResult[];
  selectedNodeId?: string;
  showMinimap: boolean;
  onToggleMinimap: () => void;
  showLegend: boolean;
  onToggleLegend: () => void;
  className?: string;
}

export interface ServiceDetailPanelProps {
  service?: Service;
  dependencies: Dependency[];
  onClose: () => void;
  onEdit?: (service: Service) => void;
  onDelete?: (serviceId: string) => void;
  className?: string;
}

export interface ArchitectureGraphState {
  services: Service[];
  dependencies: Dependency[];
  zoomLevel: ZoomLevel;
  selectedNodeId?: string;
  searchQuery: string;
  searchResults: SearchResult[];
  filteredServices: Service[];
  filteredDependencies: Dependency[];
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
  showMinimap: boolean;
  showLegend: boolean;
  visibleLayers: Set<string>;
  loading: boolean;
  error?: string;
}

export interface ArchitectureGraphActions {
  setServices: (services: Service[]) => void;
  setDependencies: (dependencies: Dependency[]) => void;
  setZoomLevel: (level: ZoomLevel) => void;
  setSelectedNode: (nodeId?: string) => void;
  setSearchQuery: (query: string) => void;
  setViewport: (viewport: { x: number; y: number; zoom: number }) => void;
  toggleMinimap: () => void;
  toggleLegend: () => void;
  toggleLayer: (layer: string) => void;
  resetView: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
  search: (query: string) => SearchResult[];
  filterByType: (type: ServiceType) => void;
  filterByStatus: (status: ServiceStatus) => void;
  clearFilters: () => void;
  exportGraph: (format: ExportFormat) => void;
}

// React Flow specific types
export interface CustomNodeData {
  service: Service;
  isSelected: boolean;
  isHighlighted: boolean;
  isFiltered: boolean;
}

export interface CustomEdgeData {
  dependency: Dependency;
  isSelected: boolean;
  isHighlighted: boolean;
  isFiltered: boolean;
}

// Event types
export interface NodeClickEvent {
  service: Service;
  event: React.MouseEvent;
}

export interface NodeDoubleClickEvent {
  service: Service;
  event: React.MouseEvent;
}

export interface DependencyClickEvent {
  dependency: Dependency;
  event: React.MouseEvent;
}

export interface ZoomChangeEvent {
  level: ZoomLevel;
  previousLevel: ZoomLevel;
}

// Utility types
export type ServiceFilter = (service: Service) => boolean;
export type DependencyFilter = (dependency: Dependency) => boolean;

export interface FilterOptions {
  types?: ServiceType[];
  statuses?: ServiceStatus[];
  technologies?: string[];
  teams?: string[];
  environments?: string[];
}

// Layout algorithms
export interface LayoutAlgorithm {
  name: string;
  apply: (services: Service[], dependencies: Dependency[]) => Service[];
}

export interface LayoutOptions {
  algorithm: 'dagre' | 'force' | 'circular' | 'grid' | 'hierarchical';
  direction: 'TB' | 'BT' | 'LR' | 'RL';
  spacing: {
    node: number;
    level: number;
  };
  alignment: 'UL' | 'UR' | 'DL' | 'DR';
}
