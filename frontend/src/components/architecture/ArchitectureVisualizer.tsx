/**
 * Interactive Architecture Visualizer Component.
 * 
 * Enterprise-grade architecture visualization with multiple zoom levels,
 * interactive features, and comprehensive controls similar to Sparx EA or LeanIX.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  EdgeChange,
  NodeChange,
  ReactFlowProvider,
  ReactFlowInstance,
  NodeTypes,
  EdgeTypes,
  MarkerType,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { 
  Service, 
  Dependency, 
  ArchitectureVisualizerProps,
  CustomNodeData,
  CustomEdgeData,
  ZoomLevel,
  ServiceType,
  ServiceStatus
} from '../../types/architecture';
import { useArchitectureGraph } from '../../hooks/useArchitectureGraph';
import { CustomServiceNode } from './nodes/CustomServiceNode';
import { CustomDependencyEdge } from './edges/CustomDependencyEdge';
import { ArchitectureControls } from './ArchitectureControls';
import { ServiceDetailPanel } from './ServiceDetailPanel';
import { ArchitectureLegend } from './ArchitectureLegend';
import { ErrorBoundary } from '../common/ErrorBoundary';

// Node and edge types
const nodeTypes: NodeTypes = {
  service: CustomServiceNode,
  database: CustomServiceNode,
  queue: CustomServiceNode,
  gateway: CustomServiceNode,
  cache: CustomServiceNode,
  monitoring: CustomServiceNode,
  api: CustomServiceNode,
  frontend: CustomServiceNode,
  backend: CustomServiceNode,
};

const edgeTypes: EdgeTypes = {
  custom: CustomDependencyEdge,
};

// Color schemes for different statuses and types
const STATUS_COLORS = {
  healthy: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
  unknown: '#6b7280',
};

const TYPE_COLORS = {
  service: '#3b82f6',
  database: '#8b5cf6',
  queue: '#f59e0b',
  gateway: '#10b981',
  cache: '#06b6d4',
  monitoring: '#ef4444',
  api: '#84cc16',
  frontend: '#f97316',
  backend: '#6366f1',
};

const ArchitectureVisualizerInner: React.FC<ArchitectureVisualizerProps> = ({
  services,
  dependencies,
  onNodeClick,
  onNodeDoubleClick,
  onZoomLevelChange,
  onDependencyClick,
  initialZoomLevel = 1,
  selectedNodeId,
  searchQuery,
  showMinimap = true,
  showControls = true,
  showLegend = true,
  enableExport = true,
  enableSearch = true,
  className = '',
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [selectedService, setSelectedService] = useState<Service | undefined>();
  const [showDetailPanel, setShowDetailPanel] = useState(false);

  // Zustand store
  const {
    filteredServices,
    filteredDependencies,
    zoomLevel,
    selectedNodeId: storeSelectedNodeId,
    searchQuery: storeSearchQuery,
    searchResults,
    viewport,
    showMinimap: storeShowMinimap,
    showLegend: storeShowLegend,
    setServices,
    setDependencies,
    setZoomLevel,
    setSelectedNode,
    setSearchQuery,
    setViewport,
    toggleMinimap,
    toggleLegend,
    resetView,
    zoomIn,
    zoomOut,
    exportGraph,
  } = useArchitectureGraph();

  // Initialize data
  useEffect(() => {
    setServices(services);
    setDependencies(dependencies);
  }, [services, dependencies, setServices, setDependencies]);

  // Set initial zoom level
  useEffect(() => {
    if (initialZoomLevel !== zoomLevel) {
      setZoomLevel(initialZoomLevel);
    }
  }, [initialZoomLevel, zoomLevel, setZoomLevel]);

  // Handle external search query
  useEffect(() => {
    if (searchQuery !== storeSearchQuery) {
      setSearchQuery(searchQuery);
    }
  }, [searchQuery, storeSearchQuery, setSearchQuery]);

  // Handle external selected node
  useEffect(() => {
    if (selectedNodeId !== storeSelectedNodeId) {
      setSelectedNode(selectedNodeId);
    }
  }, [selectedNodeId, storeSelectedNodeId, setSelectedNode]);

  // Convert services to React Flow nodes
  const nodes: Node<CustomNodeData>[] = useMemo(() => {
    return filteredServices.map((service) => {
      const isSelected = service.id === storeSelectedNodeId;
      const isHighlighted = searchResults.some(result => result.service.id === service.id);
      const isFiltered = true; // All visible services are filtered

      return {
        id: service.id,
        type: service.type,
        position: service.position,
        data: {
          service,
          isSelected,
          isHighlighted,
          isFiltered,
        },
        style: {
          backgroundColor: STATUS_COLORS[service.status],
          borderColor: TYPE_COLORS[service.type],
          borderWidth: isSelected ? 3 : 1,
          opacity: isHighlighted ? 1 : 0.8,
        },
        selected: isSelected,
      };
    });
  }, [filteredServices, storeSelectedNodeId, searchResults]);

  // Convert dependencies to React Flow edges
  const edges: Edge<CustomEdgeData>[] = useMemo(() => {
    return filteredDependencies.map((dependency) => {
      const isSelected = false; // Could be enhanced to support edge selection
      const isHighlighted = false; // Could be enhanced for search highlighting
      const isFiltered = true;

      return {
        id: dependency.id,
        source: dependency.source,
        target: dependency.target,
        type: 'custom',
        data: {
          dependency,
          isSelected,
          isHighlighted,
          isFiltered,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#6b7280',
        },
        style: {
          stroke: '#6b7280',
          strokeWidth: 2,
        },
        animated: dependency.type === 'event' || dependency.type === 'message',
      };
    });
  }, [filteredDependencies]);

  // Handle node click
  const onNodeClickHandler = useCallback((event: React.MouseEvent, node: Node<CustomNodeData>) => {
    const service = node.data.service;
    setSelectedNode(service.id);
    setSelectedService(service);
    setShowDetailPanel(true);
    onNodeClick?.(service);
  }, [setSelectedNode, onNodeClick]);

  // Handle node double click (zoom in)
  const onNodeDoubleClickHandler = useCallback((event: React.MouseEvent, node: Node<CustomNodeData>) => {
    const service = node.data.service;
    if (zoomLevel < 4 && service.children && service.children.length > 0) {
      zoomIn();
      onZoomLevelChange?.(zoomLevel + 1 as ZoomLevel);
    }
    onNodeDoubleClick?.(service);
  }, [zoomLevel, zoomIn, onZoomLevelChange, onNodeDoubleClick]);

  // Handle edge click
  const onEdgeClickHandler = useCallback((event: React.MouseEvent, edge: Edge<CustomEdgeData>) => {
    const dependency = edge.data.dependency;
    onDependencyClick?.(dependency);
  }, [onDependencyClick]);

  // Handle viewport change
  const onViewportChange = useCallback((viewport: any) => {
    setViewport(viewport);
  }, [setViewport]);

  // Handle zoom level change
  const handleZoomLevelChange = useCallback((level: ZoomLevel) => {
    setZoomLevel(level);
    onZoomLevelChange?.(level);
  }, [setZoomLevel, onZoomLevelChange]);

  // Handle export
  const handleExport = useCallback((format: 'png' | 'svg' | 'json') => {
    if (format === 'png' || format === 'svg') {
      // For image exports, we need to use the React Flow instance
      if (reactFlowInstance) {
        const exportOptions = {
          includeBackground: true,
          backgroundColor: '#ffffff',
        };
        
        if (format === 'png') {
          reactFlowInstance.getViewport();
          // PNG export logic would go here
          console.log('PNG export requested');
        } else if (format === 'svg') {
          // SVG export logic would go here
          console.log('SVG export requested');
        }
      }
    } else {
      exportGraph(format);
    }
  }, [reactFlowInstance, exportGraph]);

  // Handle search
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, [setSearchQuery]);

  // Handle detail panel close
  const handleDetailPanelClose = useCallback(() => {
    setShowDetailPanel(false);
    setSelectedService(undefined);
    setSelectedNode(undefined);
  }, [setSelectedNode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case '=':
          case '+':
            event.preventDefault();
            zoomIn();
            break;
          case '-':
            event.preventDefault();
            zoomOut();
            break;
          case '0':
            event.preventDefault();
            resetView();
            break;
          case 'f':
            event.preventDefault();
            // Focus search input
            const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
            searchInput?.focus();
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [zoomIn, zoomOut, resetView]);

  return (
    <div className={`relative w-full h-full ${className}`}>
      <ReactFlow
        ref={reactFlowWrapper}
        nodes={nodes}
        edges={edges}
        onInit={setReactFlowInstance}
        onNodeClick={onNodeClickHandler}
        onNodeDoubleClick={onNodeDoubleClickHandler}
        onEdgeClick={onEdgeClickHandler}
        onViewportChange={onViewportChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{
          padding: 0.1,
          includeHiddenNodes: false,
        }}
        defaultViewport={viewport}
        minZoom={0.1}
        maxZoom={4}
        attributionPosition="bottom-left"
        className="bg-gray-50"
      >
        <Background 
          color="#e5e7eb" 
          gap={20} 
          size={1}
          variant="dots"
        />
        
        {showControls && (
          <Controls 
            className="bg-white shadow-lg border border-gray-200 rounded-lg"
            showInteractive={false}
          />
        )}
        
        {showMinimap && storeShowMinimap && (
          <MiniMap
            nodeColor={(node) => {
              const service = (node.data as CustomNodeData).service;
              return STATUS_COLORS[service.status];
            }}
            nodeStrokeColor={(node) => {
              const service = (node.data as CustomNodeData).service;
              return TYPE_COLORS[service.type];
            }}
            nodeStrokeWidth={2}
            className="bg-white border border-gray-200 rounded-lg shadow-lg"
            maskColor="rgba(0, 0, 0, 0.1)"
            pannable
            zoomable
          />
        )}
      </ReactFlow>

      {/* Architecture Controls */}
      {showControls && (
        <ArchitectureControls
          zoomLevel={zoomLevel}
          onZoomLevelChange={handleZoomLevelChange}
          onZoomIn={zoomIn}
          onZoomOut={zoomOut}
          onReset={resetView}
          onExport={handleExport}
          onSearch={handleSearch}
          onToggleLayer={(layer) => {
            // Layer toggle logic would go here
            console.log('Toggle layer:', layer);
          }}
          searchQuery={storeSearchQuery}
          searchResults={searchResults}
          selectedNodeId={storeSelectedNodeId}
          showMinimap={storeShowMinimap}
          onToggleMinimap={toggleMinimap}
          showLegend={storeShowLegend}
          onToggleLegend={toggleLegend}
          className="absolute top-4 left-4 z-10"
        />
      )}

      {/* Architecture Legend */}
      {showLegend && storeShowLegend && (
        <ArchitectureLegend
          className="absolute bottom-4 right-4 z-10"
        />
      )}

      {/* Service Detail Panel */}
      {showDetailPanel && selectedService && (
        <ServiceDetailPanel
          service={selectedService}
          dependencies={dependencies.filter(dep => 
            dep.source === selectedService.id || dep.target === selectedService.id
          )}
          onClose={handleDetailPanelClose}
          className="absolute top-4 right-4 z-20"
        />
      )}

      {/* Search Results Indicator */}
      {searchResults.length > 0 && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
            {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
          </div>
        </div>
      )}
    </div>
  );
};

// Wrapper component with ReactFlowProvider
export const ArchitectureVisualizer: React.FC<ArchitectureVisualizerProps> = (props) => {
  return (
    <ErrorBoundary fallback={<div className="p-4 text-red-600">Error loading architecture visualizer</div>}>
      <ReactFlowProvider>
        <ArchitectureVisualizerInner {...props} />
      </ReactFlowProvider>
    </ErrorBoundary>
  );
};

export default ArchitectureVisualizer;
