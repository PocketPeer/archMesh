"use client";

/**
 * Custom Service Node Component.
 * 
 * Custom React Flow node component for displaying services with
 * status indicators, technology badges, and interactive features.
 */

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { 
  Database, 
  Globe, 
  Activity, 
  BarChart3, 
  Link, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle
} from 'lucide-react';
import { CustomNodeData, ServiceType, ServiceStatus } from '../../../types/architecture';

const TYPE_ICONS = {
  service: Globe,
  database: Database,
  queue: Activity,
  gateway: Globe,
  cache: Database,
  monitoring: BarChart3,
  api: Link,
  frontend: Globe,
  backend: Globe,
};

const STATUS_ICONS = {
  healthy: CheckCircle,
  warning: AlertTriangle,
  critical: XCircle,
  unknown: HelpCircle,
};

const STATUS_COLORS = {
  healthy: 'text-green-600',
  warning: 'text-yellow-600',
  critical: 'text-red-600',
  unknown: 'text-gray-600',
};

const TYPE_COLORS = {
  service: 'bg-blue-500',
  database: 'bg-purple-500',
  queue: 'bg-yellow-500',
  gateway: 'bg-green-500',
  cache: 'bg-cyan-500',
  monitoring: 'bg-red-500',
  api: 'bg-lime-500',
  frontend: 'bg-orange-500',
  backend: 'bg-indigo-500',
};

export const CustomServiceNode: React.FC<NodeProps<CustomNodeData>> = memo(({ data, selected }) => {
  const { service, isSelected, isHighlighted, isFiltered } = data;
  const TypeIcon = TYPE_ICONS[service.type];
  const StatusIcon = STATUS_ICONS[service.status];

  // Determine node size based on type and status
  const getNodeSize = () => {
    const baseSize = 120;
    const statusMultiplier = service.status === 'critical' ? 1.2 : 1;
    const typeMultiplier = service.type === 'gateway' ? 1.3 : 1;
    return baseSize * statusMultiplier * typeMultiplier;
  };

  const nodeSize = getNodeSize();

  return (
    <div
      className={`
        relative bg-white rounded-lg shadow-lg border-2 transition-all duration-200
        ${isSelected ? 'border-blue-500 shadow-xl' : 'border-gray-200'}
        ${isHighlighted ? 'ring-2 ring-blue-300' : ''}
        ${!isFiltered ? 'opacity-50' : ''}
        hover:shadow-xl hover:scale-105
      `}
      style={{ width: nodeSize, height: nodeSize }}
    >
      {/* Connection Handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-gray-400 border-2 border-white"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-gray-400 border-2 border-white"
      />
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-gray-400 border-2 border-white"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-gray-400 border-2 border-white"
      />

      {/* Status Indicator */}
      <div className="absolute -top-2 -right-2 z-10">
        <div className={`
          p-1 rounded-full bg-white shadow-md
          ${STATUS_COLORS[service.status]}
        `}>
          <StatusIcon className="w-4 h-4" />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center h-full p-3">
        {/* Type Icon */}
        <div className={`
          p-3 rounded-full mb-2
          ${TYPE_COLORS[service.type]}
        `}>
          <TypeIcon className="w-6 h-6 text-white" />
        </div>

        {/* Service Name */}
        <div className="text-center">
          <div className="font-semibold text-sm text-gray-900 mb-1 leading-tight">
            {service.name}
          </div>
          <div className="text-xs text-gray-500 mb-1">
            {service.technology}
          </div>
          <div className="text-xs text-gray-400">
            {service.type}
          </div>
        </div>
      </div>

      {/* Technology Badge */}
      {service.technology && (
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
          <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded-full whitespace-nowrap">
            {service.technology}
          </div>
        </div>
      )}

      {/* Version Badge */}
      {service.version && (
        <div className="absolute -top-2 -left-2">
          <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
            v{service.version}
          </div>
        </div>
      )}

      {/* Environment Badge */}
      {service.environment && (
        <div className="absolute top-1 left-1">
          <div className={`
            text-xs px-2 py-1 rounded-full
            ${service.environment === 'production' ? 'bg-red-100 text-red-800' : 
              service.environment === 'staging' ? 'bg-yellow-100 text-yellow-800' : 
              'bg-green-100 text-green-800'}
          `}>
            {service.environment}
          </div>
        </div>
      )}

      {/* Metrics Overlay */}
      {service.metadata && (
        <div className="absolute bottom-1 right-1 flex space-x-1">
          {service.metadata.responseTime && (
            <div className="bg-white text-gray-600 text-xs px-1 py-0.5 rounded shadow-sm">
              {service.metadata.responseTime}ms
            </div>
          )}
          {service.metadata.errorRate && (
            <div className={`
              text-xs px-1 py-0.5 rounded shadow-sm
              ${service.metadata.errorRate > 0.05 ? 'bg-red-100 text-red-800' : 
                service.metadata.errorRate > 0.01 ? 'bg-yellow-100 text-yellow-800' : 
                'bg-green-100 text-green-800'}
            `}>
              {(service.metadata.errorRate * 100).toFixed(1)}%
            </div>
          )}
        </div>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute inset-0 rounded-lg border-2 border-blue-500 pointer-events-none" />
      )}

      {/* Highlight Ring */}
      {isHighlighted && (
        <div className="absolute inset-0 rounded-lg ring-2 ring-blue-300 pointer-events-none" />
      )}
    </div>
  );
});

CustomServiceNode.displayName = 'CustomServiceNode';
