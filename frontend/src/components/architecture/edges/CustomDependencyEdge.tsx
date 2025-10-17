/**
 * Custom Dependency Edge Component.
 * 
 * Custom React Flow edge component for displaying dependencies with
 * type indicators, protocol information, and interactive features.
 */

import React, { memo } from 'react';
import { EdgeProps, getBezierPath, EdgeLabelRenderer, BaseEdge } from 'reactflow';
import { CustomEdgeData, DependencyType } from '../../../types/architecture';

const DEPENDENCY_COLORS = {
  api: '#3b82f6',
  event: '#8b5cf6',
  data: '#10b981',
  message: '#f59e0b',
  sync: '#ef4444',
  async: '#06b6d4',
};

const DEPENDENCY_STYLES = {
  api: { strokeDasharray: 'none', strokeWidth: 2 },
  event: { strokeDasharray: '5,5', strokeWidth: 2 },
  data: { strokeDasharray: '10,5', strokeWidth: 2 },
  message: { strokeDasharray: '2,2', strokeWidth: 2 },
  sync: { strokeDasharray: 'none', strokeWidth: 3 },
  async: { strokeDasharray: '15,5', strokeWidth: 2 },
};

export const CustomDependencyEdge: React.FC<EdgeProps<CustomEdgeData>> = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  data,
  markerEnd,
}) => {
  const { dependency, isSelected, isHighlighted, isFiltered } = data || {};

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const edgeColor = DEPENDENCY_COLORS[dependency?.type || 'api'];
  const edgeStyle = DEPENDENCY_STYLES[dependency?.type || 'api'];

  const finalStyle = {
    ...style,
    ...edgeStyle,
    stroke: edgeColor,
    opacity: isFiltered ? 1 : 0.3,
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={finalStyle}
        className={`
          transition-all duration-200
          ${isSelected ? 'stroke-blue-500 stroke-2' : ''}
          ${isHighlighted ? 'stroke-yellow-500' : ''}
        `}
      />
      
      {/* Edge Label */}
      {dependency && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              fontSize: 12,
              pointerEvents: 'all',
            }}
            className="bg-white px-2 py-1 rounded shadow-sm border border-gray-200"
          >
            <div className="flex items-center space-x-1">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: edgeColor }}
              />
              <span className="text-xs font-medium text-gray-700">
                {dependency.type.toUpperCase()}
              </span>
            </div>
            
            {/* Protocol Information */}
            {dependency.protocol && (
              <div className="text-xs text-gray-500 mt-1">
                {dependency.protocol}
              </div>
            )}
            
            {/* Frequency Indicator */}
            {dependency.frequency && (
              <div className={`
                text-xs px-1 py-0.5 rounded mt-1
                ${dependency.frequency === 'high' ? 'bg-red-100 text-red-800' :
                  dependency.frequency === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'}
              `}>
                {dependency.frequency}
              </div>
            )}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
});

CustomDependencyEdge.displayName = 'CustomDependencyEdge';
