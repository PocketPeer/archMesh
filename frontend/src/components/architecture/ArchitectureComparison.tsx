"use client";

/**
 * Architecture Comparison Component.
 * 
 * Shows "before and after" architecture comparison with detailed change tracking,
 * impact analysis, and approval workflow for brownfield changes.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { 
  ToggleLeft, 
  ToggleRight, 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Eye,
  EyeOff,
  BarChart3,
  FileText,
  Users,
  Clock,
  TrendingUp
} from 'lucide-react';
import { 
  ArchitectureComparisonProps, 
  ViewMode, 
  ChangeType, 
  EntityType, 
  ImpactLevel,
  CHANGE_COLORS,
  IMPACT_COLORS
} from '../../types/architecture-comparison';
import { ArchitectureVisualizer } from './ArchitectureVisualizer';
import { ChangesPanel } from './comparison/ChangesPanel';
import { ImpactAnalysisPanel } from './comparison/ImpactAnalysisPanel';
import { ApprovalWorkflow } from './comparison/ApprovalWorkflow';
import { ComparisonLegend } from './comparison/ComparisonLegend';
import { DiffVisualization } from './comparison/DiffVisualization';

export const ArchitectureComparison: React.FC<ArchitectureComparisonProps> = ({
  currentArchitecture,
  proposedArchitecture,
  changes,
  impactAnalysis,
  onApprove,
  onReject,
  onExport,
  viewMode: initialViewMode = 'side-by-side',
  showImpactAnalysis = true,
  showApprovalWorkflow = true,
  className = '',
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>(initialViewMode);
  const [selectedChangeId, setSelectedChangeId] = useState<string | undefined>();
  const [showLegend, setShowLegend] = useState(true);
  const [showChangesPanel, setShowChangesPanel] = useState(true);
  const [showImpactPanel, setShowImpactPanel] = useState(showImpactAnalysis);
  const [showApprovalPanel, setShowApprovalPanel] = useState(showApprovalWorkflow);

  // Memoized change statistics
  const changeStats = useMemo(() => {
    const stats = {
      total: changes.length,
      additions: changes.filter(c => c.type === 'add').length,
      modifications: changes.filter(c => c.type === 'modify').length,
      removals: changes.filter(c => c.type === 'remove').length,
      deprecations: changes.filter(c => c.type === 'deprecate').length,
      breakingChanges: changes.filter(c => c.breakingChange).length,
      highImpact: changes.filter(c => c.impact === 'high' || c.impact === 'critical').length,
    };
    return stats;
  }, [changes]);

  // Handle view mode toggle
  const handleViewModeToggle = useCallback(() => {
    setViewMode(prev => prev === 'side-by-side' ? 'overlay' : 'side-by-side');
  }, []);

  // Handle change selection
  const handleChangeClick = useCallback((changeId: string) => {
    setSelectedChangeId(prev => prev === changeId ? undefined : changeId);
  }, []);

  // Handle service click
  const handleServiceClick = useCallback((service: any, isCurrent: boolean) => {
    // Find related changes for this service
    const relatedChanges = changes.filter(change => 
      change.affectedServices.includes(service.id)
    );
    if (relatedChanges.length > 0) {
      setSelectedChangeId(relatedChanges[0].id);
    }
  }, [changes]);

  // Handle dependency click
  const handleDependencyClick = useCallback((dependency: any, isCurrent: boolean) => {
    // Find related changes for this dependency
    const relatedChanges = changes.filter(change => 
      change.entity === 'dependency' && 
      (change.name === dependency.id || change.affectedServices.includes(dependency.source) || change.affectedServices.includes(dependency.target))
    );
    if (relatedChanges.length > 0) {
      setSelectedChangeId(relatedChanges[0].id);
    }
  }, [changes]);

  // Handle export
  const handleExport = useCallback((format: 'pdf' | 'json' | 'html') => {
    onExport(format);
  }, [onExport]);

  // Render side-by-side view
  const renderSideBySideView = () => (
    <div className="grid grid-cols-2 gap-4 h-full">
      {/* Current Architecture */}
      <div className="relative">
        <div className="absolute top-2 left-2 z-10 bg-white px-3 py-1 rounded-lg shadow-sm border">
          <h3 className="text-sm font-semibold text-gray-700">Current Architecture</h3>
        </div>
        <ArchitectureVisualizer
          services={currentArchitecture.services}
          dependencies={currentArchitecture.dependencies}
          onNodeClick={(service) => handleServiceClick(service, true)}
          onDependencyClick={(dependency) => handleDependencyClick(dependency, true)}
          showMinimap={false}
          showControls={false}
          showLegend={false}
          className="border border-gray-200 rounded-lg"
        />
      </div>

      {/* Proposed Architecture */}
      <div className="relative">
        <div className="absolute top-2 left-2 z-10 bg-white px-3 py-1 rounded-lg shadow-sm border">
          <h3 className="text-sm font-semibold text-gray-700">Proposed Architecture</h3>
        </div>
        <ArchitectureVisualizer
          services={proposedArchitecture.services}
          dependencies={proposedArchitecture.dependencies}
          onNodeClick={(service) => handleServiceClick(service, false)}
          onDependencyClick={(dependency) => handleDependencyClick(dependency, false)}
          showMinimap={false}
          showControls={false}
          showLegend={false}
          className="border border-gray-200 rounded-lg"
        />
      </div>
    </div>
  );

  // Render overlay view
  const renderOverlayView = () => (
    <div className="relative h-full">
      <DiffVisualization
        currentServices={currentArchitecture.services}
        proposedServices={proposedArchitecture.services}
        currentDependencies={currentArchitecture.dependencies}
        proposedDependencies={proposedArchitecture.dependencies}
        changes={changes}
        onElementClick={(element, change) => {
          if (change) {
            setSelectedChangeId(change.id);
          }
        }}
        className="h-full"
      />
    </div>
  );

  return (
    <div className={`flex flex-col h-full bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Architecture Comparison</h1>
            <p className="text-sm text-gray-600 mt-1">
              {changeStats.total} changes • {changeStats.breakingChanges} breaking changes • {changeStats.highImpact} high impact
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Side-by-side</span>
              <button
                onClick={handleViewModeToggle}
                className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    viewMode === 'overlay' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className="text-sm text-gray-600">Overlay</span>
            </div>

            {/* Export Button */}
            <div className="relative">
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>

        {/* Change Statistics */}
        <div className="flex items-center space-x-6 mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-sm text-gray-600">{changeStats.additions} additions</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-sm text-gray-600">{changeStats.modifications} modifications</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-sm text-gray-600">{changeStats.removals} removals</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-sm text-gray-600">{changeStats.deprecations} deprecations</span>
          </div>
          {changeStats.breakingChanges > 0 && (
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-600 font-medium">{changeStats.breakingChanges} breaking changes</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Visualization */}
        <div className="flex-1 flex flex-col">
          {/* Visualization Controls */}
          <div className="bg-white border-b border-gray-200 p-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowLegend(!showLegend)}
                  className={`flex items-center space-x-2 px-3 py-1 rounded-md text-sm transition-colors ${
                    showLegend ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {showLegend ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  <span>Legend</span>
                </button>
              </div>
              
              <div className="text-sm text-gray-500">
                {viewMode === 'side-by-side' ? 'Side-by-side comparison' : 'Overlay with changes highlighted'}
              </div>
            </div>
          </div>

          {/* Visualization Area */}
          <div className="flex-1 relative">
            {viewMode === 'side-by-side' ? renderSideBySideView() : renderOverlayView()}
            
            {/* Legend Overlay */}
            {showLegend && (
              <div className="absolute top-4 right-4 z-20">
                <ComparisonLegend />
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Details */}
        <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
          {/* Panel Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => {
                  setShowChangesPanel(true);
                  setShowImpactPanel(false);
                  setShowApprovalPanel(false);
                }}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  showChangesPanel ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Changes</span>
                  <span className="bg-gray-200 text-gray-600 text-xs px-2 py-1 rounded-full">
                    {changeStats.total}
                  </span>
                </div>
              </button>
              
              {showImpactAnalysis && (
                <button
                  onClick={() => {
                    setShowChangesPanel(false);
                    setShowImpactPanel(true);
                    setShowApprovalPanel(false);
                  }}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    showImpactPanel ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-2">
                    <BarChart3 className="w-4 h-4" />
                    <span>Impact</span>
                  </div>
                </button>
              )}
              
              {showApprovalWorkflow && (
                <button
                  onClick={() => {
                    setShowChangesPanel(false);
                    setShowImpactPanel(false);
                    setShowApprovalPanel(true);
                  }}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    showApprovalPanel ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-2">
                    <Users className="w-4 h-4" />
                    <span>Approval</span>
                  </div>
                </button>
              )}
            </div>
          </div>

          {/* Panel Content */}
          <div className="flex-1 overflow-y-auto">
            {showChangesPanel && (
              <ChangesPanel
                changes={changes}
                impactAnalysis={impactAnalysis}
                onChangeClick={handleChangeClick}
                onFilterChange={(filter) => {
                  // Handle filter changes
                  console.log('Filter changed:', filter);
                }}
                selectedChangeId={selectedChangeId}
              />
            )}
            
            {showImpactPanel && (
              <ImpactAnalysisPanel
                impactAnalysis={impactAnalysis}
                changes={changes}
                onRecommendationClick={(recommendation) => {
                  console.log('Recommendation clicked:', recommendation);
                }}
              />
            )}
            
            {showApprovalPanel && (
              <ApprovalWorkflow
                onApprove={onApprove}
                onReject={onReject}
                onRequestChanges={(feedback) => {
                  console.log('Changes requested:', feedback);
                }}
                approvalHistory={[]}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureComparison;
