/**
 * Service Detail Panel Component.
 * 
 * Displays comprehensive information about a selected service including
 * metadata, dependencies, health status, and configuration details.
 */

import React, { useCallback, useMemo } from 'react';
import { 
  X, 
  Edit, 
  Trash2, 
  ExternalLink, 
  Activity, 
  Clock, 
  Users, 
  Database, 
  Globe, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle,
  GitBranch,
  Calendar,
  BarChart3,
  Link,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';
import { 
  ServiceDetailPanelProps, 
  Service, 
  Dependency, 
  ServiceStatus,
  ServiceType 
} from '../../types/architecture';

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

const TYPE_COLORS = {
  service: 'bg-blue-100 text-blue-800',
  database: 'bg-purple-100 text-purple-800',
  queue: 'bg-yellow-100 text-yellow-800',
  gateway: 'bg-green-100 text-green-800',
  cache: 'bg-cyan-100 text-cyan-800',
  monitoring: 'bg-red-100 text-red-800',
  api: 'bg-lime-100 text-lime-800',
  frontend: 'bg-orange-100 text-orange-800',
  backend: 'bg-indigo-100 text-indigo-800',
};

export const ServiceDetailPanel: React.FC<ServiceDetailPanelProps> = ({
  service,
  dependencies,
  onClose,
  onEdit,
  onDelete,
  className = '',
}) => {
  const StatusIcon = STATUS_ICONS[service.status];
  const TypeIcon = TYPE_ICONS[service.type];

  // Separate incoming and outgoing dependencies
  const { incomingDependencies, outgoingDependencies } = useMemo(() => {
    const incoming = dependencies.filter(dep => dep.target === service.id);
    const outgoing = dependencies.filter(dep => dep.source === service.id);
    return { incomingDependencies: incoming, outgoingDependencies: outgoing };
  }, [dependencies, service.id]);

  // Handle edit
  const handleEdit = useCallback(() => {
    onEdit?.(service);
  }, [onEdit, service]);

  // Handle delete
  const handleDelete = useCallback(() => {
    if (window.confirm(`Are you sure you want to delete ${service.name}?`)) {
      onDelete?.(service.id);
    }
  }, [onDelete, service.id]);

  // Format uptime
  const formatUptime = useCallback((uptime?: number) => {
    if (!uptime) return 'N/A';
    const days = Math.floor(uptime / (24 * 60 * 60));
    const hours = Math.floor((uptime % (24 * 60 * 60)) / (60 * 60));
    return `${days}d ${hours}h`;
  }, []);

  // Format response time
  const formatResponseTime = useCallback((time?: number) => {
    if (!time) return 'N/A';
    return `${time}ms`;
  }, []);

  // Format error rate
  const formatErrorRate = useCallback((rate?: number) => {
    if (!rate) return 'N/A';
    return `${(rate * 100).toFixed(2)}%`;
  }, []);

  return (
    <div className={`bg-white rounded-lg shadow-xl border border-gray-200 w-96 max-h-[80vh] overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${TYPE_COLORS[service.type]}`}>
            <TypeIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{service.name}</h3>
            <div className="flex items-center space-x-2">
              <StatusIcon className={`w-4 h-4 ${STATUS_COLORS[service.status]}`} />
              <span className={`text-sm font-medium ${STATUS_COLORS[service.status]}`}>
                {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {onEdit && (
            <button
              onClick={handleEdit}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Edit service"
            >
              <Edit className="w-4 h-4" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={handleDelete}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Delete service"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Close panel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="overflow-y-auto max-h-[calc(80vh-80px)]">
        {/* Basic Information */}
        <div className="p-4 border-b border-gray-200">
          <h4 className="font-medium text-gray-900 mb-3">Basic Information</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Type</span>
              <span className="text-sm font-medium">{service.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Technology</span>
              <span className="text-sm font-medium">{service.technology}</span>
            </div>
            {service.version && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Version</span>
                <span className="text-sm font-medium">{service.version}</span>
              </div>
            )}
            {service.environment && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Environment</span>
                <span className="text-sm font-medium">{service.environment}</span>
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        {service.description && (
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Description</h4>
            <p className="text-sm text-gray-600">{service.description}</p>
          </div>
        )}

        {/* Team Information */}
        {(service.owner || service.team) && (
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Team</h4>
            <div className="space-y-2">
              {service.owner && (
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Owner: {service.owner}</span>
                </div>
              )}
              {service.team && (
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Team: {service.team}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {service.metadata && (
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Performance</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {formatUptime(service.metadata.uptime)}
                </div>
                <div className="text-xs text-gray-500">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {formatResponseTime(service.metadata.responseTime)}
                </div>
                <div className="text-xs text-gray-500">Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {formatErrorRate(service.metadata.errorRate)}
                </div>
                <div className="text-xs text-gray-500">Error Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {service.metadata.lastDeployed ? 'Recent' : 'N/A'}
                </div>
                <div className="text-xs text-gray-500">Last Deployed</div>
              </div>
            </div>
          </div>
        )}

        {/* Endpoints */}
        {service.metadata?.endpoints && service.metadata.endpoints.length > 0 && (
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Endpoints</h4>
            <div className="space-y-2">
              {service.metadata.endpoints.map((endpoint, index) => (
                <div key={index} className="flex items-center justify-between">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">{endpoint}</code>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dependencies */}
        <div className="p-4 border-b border-gray-200">
          <h4 className="font-medium text-gray-900 mb-3">Dependencies</h4>
          
          {/* Outgoing Dependencies */}
          {outgoingDependencies.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <ArrowRight className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">Depends On</span>
                <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                  {outgoingDependencies.length}
                </span>
              </div>
              <div className="space-y-1">
                {outgoingDependencies.map((dep) => (
                  <div key={dep.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">{dep.target}</span>
                    <span className="text-xs text-gray-500">{dep.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Incoming Dependencies */}
          {incomingDependencies.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <ArrowLeft className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">Used By</span>
                <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                  {incomingDependencies.length}
                </span>
              </div>
              <div className="space-y-1">
                {incomingDependencies.map((dep) => (
                  <div key={dep.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">{dep.source}</span>
                    <span className="text-xs text-gray-500">{dep.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {dependencies.length === 0 && (
            <div className="text-sm text-gray-500 text-center py-4">
              No dependencies found
            </div>
          )}
        </div>

        {/* Links */}
        <div className="p-4">
          <h4 className="font-medium text-gray-900 mb-3">Links</h4>
          <div className="space-y-2">
            {service.metadata?.documentation && (
              <a
                href={service.metadata.documentation}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Documentation</span>
              </a>
            )}
            {service.metadata?.repository && (
              <a
                href={service.metadata.repository}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
              >
                <GitBranch className="w-4 h-4" />
                <span>Repository</span>
              </a>
            )}
            {service.metadata?.healthCheck && (
              <a
                href={service.metadata.healthCheck}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
              >
                <Activity className="w-4 h-4" />
                <span>Health Check</span>
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetailPanel;
