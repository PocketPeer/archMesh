/**
 * Diff Visualization Component.
 * 
 * Shows a single architecture view with changes highlighted using
 * color coding and visual indicators for additions, modifications, and removals.
 */

import React, { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  useNodesState,
  useEdgesState,
  NodeTypes,
  EdgeTypes,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { 
  DiffVisualizationProps, 
  Service, 
  Dependency, 
  ArchitectureChange,
  CHANGE_COLORS,
  IMPACT_COLORS
} from '../../../types/architecture-comparison';
import { CustomServiceNode } from '../nodes/CustomServiceNode';
import { CustomDependencyEdge } from '../edges/CustomDependencyEdge';

// Custom node types for diff visualization
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

export const DiffVisualization: React.FC<DiffVisualizationProps> = ({
  currentServices,
  proposedServices,
  currentDependencies,
  proposedDependencies,
  changes,
  onElementClick,
  className = '',
}) => {
  // Create change lookup maps
  const serviceChanges = useMemo(() => {
    const changeMap = new Map<string, ArchitectureChange>();
    changes.forEach(change => {
      if (change.entity === 'service' || change.entity === 'component') {
        changeMap.set(change.name, change);
      }
    });
    return changeMap;
  }, [changes]);

  const dependencyChanges = useMemo(() => {
    const changeMap = new Map<string, ArchitectureChange>();
    changes.forEach(change => {
      if (change.entity === 'dependency') {
        changeMap.set(change.name, change);
      }
    });
    return changeMap;
  }, [changes]);

  // Merge services and apply change indicators
  const mergedServices = useMemo(() => {
    const serviceMap = new Map<string, Service>();
    
    // Add current services
    currentServices.forEach(service => {
      serviceMap.set(service.id, { ...service });
    });
    
    // Add or update with proposed services
    proposedServices.forEach(service => {
      const existingService = serviceMap.get(service.id);
      if (existingService) {
        // Service exists in both - check for modifications
        const change = serviceChanges.get(service.id);
        if (change && change.type === 'modify') {
          serviceMap.set(service.id, {
            ...service,
            // Add change indicator to metadata
            metadata: {
              ...service.metadata,
              changeType: 'modify',
              change: change,
            }
          });
        } else {
          // No changes detected, keep as unchanged
          serviceMap.set(service.id, {
            ...existingService,
            metadata: {
              ...existingService.metadata,
              changeType: 'unchanged',
            }
          });
        }
      } else {
        // New service
        const change = serviceChanges.get(service.id);
        serviceMap.set(service.id, {
          ...service,
          metadata: {
            ...service.metadata,
            changeType: 'add',
            change: change,
          }
        });
      }
    });
    
    // Mark removed services
    currentServices.forEach(service => {
      if (!proposedServices.find(s => s.id === service.id)) {
        const change = serviceChanges.get(service.id);
        serviceMap.set(service.id, {
          ...service,
          metadata: {
            ...service.metadata,
            changeType: 'remove',
            change: change,
          }
        });
      }
    });
    
    return Array.from(serviceMap.values());
  }, [currentServices, proposedServices, serviceChanges]);

  // Merge dependencies and apply change indicators
  const mergedDependencies = useMemo(() => {
    const dependencyMap = new Map<string, Dependency>();
    
    // Add current dependencies
    currentDependencies.forEach(dep => {
      dependencyMap.set(dep.id, { ...dep });
    });
    
    // Add or update with proposed dependencies
    proposedDependencies.forEach(dep => {
      const existingDep = dependencyMap.get(dep.id);
      if (existingDep) {
        // Dependency exists in both - check for modifications
        const change = dependencyChanges.get(dep.id);
        if (change && change.type === 'modify') {
          dependencyMap.set(dep.id, {
            ...dep,
            metadata: {
              ...dep.metadata,
              changeType: 'modify',
              change: change,
            }
          });
        } else {
          // No changes detected, keep as unchanged
          dependencyMap.set(dep.id, {
            ...existingDep,
            metadata: {
              ...existingDep.metadata,
              changeType: 'unchanged',
            }
          });
        }
      } else {
        // New dependency
        const change = dependencyChanges.get(dep.id);
        dependencyMap.set(dep.id, {
          ...dep,
          metadata: {
            ...dep.metadata,
            changeType: 'add',
            change: change,
          }
        });
      }
    });
    
    // Mark removed dependencies
    currentDependencies.forEach(dep => {
      if (!proposedDependencies.find(d => d.id === dep.id)) {
        const change = dependencyChanges.get(dep.id);
        dependencyMap.set(dep.id, {
          ...dep,
          metadata: {
            ...dep.metadata,
            changeType: 'remove',
            change: change,
          }
        });
      }
    });
    
    return Array.from(dependencyMap.values());
  }, [currentDependencies, proposedDependencies, dependencyChanges]);

  // Convert to React Flow nodes
  const nodes: Node[] = useMemo(() => {
    return mergedServices.map((service) => {
      const changeType = service.metadata?.changeType || 'unchanged';
      const change = service.metadata?.change as ArchitectureChange;
      
      // Determine node styling based on change type
      let nodeStyle = {};
      let borderColor = '#e5e7eb'; // default gray
      let borderWidth = 1;
      
      switch (changeType) {
        case 'add':
          borderColor = CHANGE_COLORS.add;
          borderWidth = 3;
          break;
        case 'modify':
          borderColor = CHANGE_COLORS.modify;
          borderWidth = 3;
          break;
        case 'remove':
          borderColor = CHANGE_COLORS.remove;
          borderWidth = 3;
          break;
        case 'deprecate':
          borderColor = CHANGE_COLORS.deprecate;
          borderWidth = 3;
          break;
        default:
          borderColor = CHANGE_COLORS.unchanged;
          borderWidth = 1;
      }
      
      return {
        id: service.id,
        type: service.type,
        position: service.position,
        data: {
          service,
          isSelected: false,
          isHighlighted: false,
          isFiltered: true,
          changeType,
          change,
        },
        style: {
          borderColor,
          borderWidth,
          opacity: changeType === 'remove' ? 0.5 : 1,
        },
      };
    });
  }, [mergedServices]);

  // Convert to React Flow edges
  const edges: Edge[] = useMemo(() => {
    return mergedDependencies.map((dependency) => {
      const changeType = dependency.metadata?.changeType || 'unchanged';
      const change = dependency.metadata?.change as ArchitectureChange;
      
      // Determine edge styling based on change type
      let strokeColor = '#6b7280'; // default gray
      let strokeWidth = 2;
      let strokeDasharray = 'none';
      
      switch (changeType) {
        case 'add':
          strokeColor = CHANGE_COLORS.add;
          strokeWidth = 3;
          break;
        case 'modify':
          strokeColor = CHANGE_COLORS.modify;
          strokeWidth = 3;
          break;
        case 'remove':
          strokeColor = CHANGE_COLORS.remove;
          strokeWidth = 2;
          strokeDasharray = '5,5';
          break;
        case 'deprecate':
          strokeColor = CHANGE_COLORS.deprecate;
          strokeWidth = 2;
          strokeDasharray = '10,5';
          break;
        default:
          strokeColor = CHANGE_COLORS.unchanged;
          strokeWidth = 1;
      }
      
      return {
        id: dependency.id,
        source: dependency.source,
        target: dependency.target,
        type: 'custom',
        data: {
          dependency,
          isSelected: false,
          isHighlighted: false,
          isFiltered: true,
          changeType,
          change,
        },
        style: {
          stroke: strokeColor,
          strokeWidth,
          strokeDasharray,
          opacity: changeType === 'remove' ? 0.5 : 1,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
        },
        animated: changeType === 'add' || changeType === 'modify',
      };
    });
  }, [mergedDependencies]);

  // Handle node click
  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const service = node.data.service as Service;
    const change = node.data.change as ArchitectureChange;
    onElementClick(service, change);
  }, [onElementClick]);

  // Handle edge click
  const handleEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    const dependency = edge.data.dependency as Dependency;
    const change = edge.data.change as ArchitectureChange;
    onElementClick(dependency, change);
  }, [onElementClick]);

  return (
    <div className={`w-full h-full ${className}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{
          padding: 0.1,
          includeHiddenNodes: false,
        }}
        attributionPosition="bottom-left"
        className="bg-gray-50"
      >
        <Background 
          color="#e5e7eb" 
          gap={20} 
          size={1}
          variant="dots"
        />
      </ReactFlow>
      
      {/* Change Summary Overlay */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg border border-gray-200 p-3">
        <h4 className="font-medium text-gray-900 mb-2">Changes Summary</h4>
        <div className="space-y-1 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-600">
              {changes.filter(c => c.type === 'add').length} additions
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-600">
              {changes.filter(c => c.type === 'modify').length} modifications
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-600">
              {changes.filter(c => c.type === 'remove').length} removals
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-gray-600">
              {changes.filter(c => c.type === 'deprecate').length} deprecations
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiffVisualization;
