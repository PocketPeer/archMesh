/**
 * Architecture Legend Component.
 * 
 * Displays a legend showing the meaning of different colors, icons,
 * and symbols used in the architecture visualization.
 */

import React from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  HelpCircle,
  Globe,
  Database,
  Activity,
  BarChart3,
  Link
} from 'lucide-react';
import { ServiceType, ServiceStatus } from '../../types/architecture';

const STATUS_ITEMS: { status: ServiceStatus; icon: React.ComponentType<any>; label: string; color: string }[] = [
  { status: 'healthy', icon: CheckCircle, label: 'Healthy', color: 'text-green-600' },
  { status: 'warning', icon: AlertTriangle, label: 'Warning', color: 'text-yellow-600' },
  { status: 'critical', icon: XCircle, label: 'Critical', color: 'text-red-600' },
  { status: 'unknown', icon: HelpCircle, label: 'Unknown', color: 'text-gray-600' },
];

const TYPE_ITEMS: { type: ServiceType; icon: React.ComponentType<any>; label: string; color: string }[] = [
  { type: 'service', icon: Globe, label: 'Service', color: 'bg-blue-500' },
  { type: 'database', icon: Database, label: 'Database', color: 'bg-purple-500' },
  { type: 'queue', icon: Activity, label: 'Queue', color: 'bg-yellow-500' },
  { type: 'gateway', icon: Globe, label: 'Gateway', color: 'bg-green-500' },
  { type: 'cache', icon: Database, label: 'Cache', color: 'bg-cyan-500' },
  { type: 'monitoring', icon: BarChart3, label: 'Monitoring', color: 'bg-red-500' },
  { type: 'api', icon: Link, label: 'API', color: 'bg-lime-500' },
  { type: 'frontend', icon: Globe, label: 'Frontend', color: 'bg-orange-500' },
  { type: 'backend', icon: Globe, label: 'Backend', color: 'bg-indigo-500' },
];

const DEPENDENCY_ITEMS = [
  { type: 'api', label: 'API Call', color: '#3b82f6', style: 'solid' },
  { type: 'event', label: 'Event', color: '#8b5cf6', style: 'dashed' },
  { type: 'data', label: 'Data Flow', color: '#10b981', style: 'dotted' },
  { type: 'message', label: 'Message', color: '#f59e0b', style: 'dashed' },
  { type: 'sync', label: 'Synchronous', color: '#ef4444', style: 'solid' },
  { type: 'async', label: 'Asynchronous', color: '#06b6d4', style: 'dashed' },
];

interface ArchitectureLegendProps {
  className?: string;
}

export const ArchitectureLegend: React.FC<ArchitectureLegendProps> = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-xs ${className}`}>
      <h3 className="font-semibold text-gray-900 mb-4">Legend</h3>
      
      {/* Status Legend */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Status</h4>
        <div className="space-y-1">
          {STATUS_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.status} className="flex items-center space-x-2">
                <Icon className={`w-4 h-4 ${item.color}`} />
                <span className="text-sm text-gray-600">{item.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Type Legend */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Service Types</h4>
        <div className="space-y-1">
          {TYPE_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.type} className="flex items-center space-x-2">
                <div className={`p-1 rounded ${item.color}`}>
                  <Icon className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm text-gray-600">{item.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dependency Legend */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Dependencies</h4>
        <div className="space-y-1">
          {DEPENDENCY_ITEMS.map((item) => (
            <div key={item.type} className="flex items-center space-x-2">
              <div
                className="w-4 h-0.5"
                style={{
                  backgroundColor: item.color,
                  borderStyle: item.style === 'dashed' ? 'dashed' : 
                              item.style === 'dotted' ? 'dotted' : 'solid',
                  borderWidth: '1px 0 0 0',
                  borderColor: item.color,
                }}
              />
              <span className="text-sm text-gray-600">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Zoom Levels */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Zoom Levels</h4>
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-300 rounded"></div>
            <span className="text-sm text-gray-600">L1: Enterprise</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-400 rounded"></div>
            <span className="text-sm text-gray-600">L2: System</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-500 rounded"></div>
            <span className="text-sm text-gray-600">L3: Service</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-600 rounded"></div>
            <span className="text-sm text-gray-600">L4: Component</span>
          </div>
        </div>
      </div>

      {/* Interaction Hints */}
      <div className="pt-2 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Interactions</h4>
        <div className="space-y-1 text-xs text-gray-500">
          <div>• Click: Select service</div>
          <div>• Double-click: Zoom in</div>
          <div>• Drag: Pan view</div>
          <div>• Scroll: Zoom</div>
          <div>• Ctrl+F: Search</div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureLegend;
