/**
 * Impact Analysis Panel Component.
 * 
 * Displays comprehensive impact analysis including risk factors,
 * recommendations, timeline, and affected systems.
 */

import React, { useCallback, useMemo } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Users, 
  TrendingUp, 
  Shield, 
  FileText,
  Play,
  Pause,
  RotateCcw,
  Target,
  Zap,
  Database,
  Globe,
  BarChart3
} from 'lucide-react';
import { 
  ImpactAnalysisPanelProps, 
  ImpactLevel,
  IMPACT_COLORS,
  IMPACT_ICONS
} from '../../../types/architecture-comparison';

export const ImpactAnalysisPanel: React.FC<ImpactAnalysisPanelProps> = ({
  impactAnalysis,
  changes,
  onRecommendationClick,
  className = '',
}) => {
  // Calculate risk score
  const riskScore = useMemo(() => {
    const factors = impactAnalysis.riskFactors;
    let score = 0;
    
    score += factors.breakingChanges * 20;
    score += factors.dataMigrationRequired ? 15 : 0;
    score += factors.downtimeRequired ? 25 : 0;
    score += factors.rollbackComplexity === 'high' ? 20 : factors.rollbackComplexity === 'medium' ? 10 : 0;
    score += factors.testingComplexity === 'high' ? 15 : factors.testingComplexity === 'medium' ? 8 : 0;
    
    return Math.min(score, 100);
  }, [impactAnalysis.riskFactors]);

  // Get risk level based on score
  const riskLevel: ImpactLevel = useMemo(() => {
    if (riskScore >= 80) return 'critical';
    if (riskScore >= 60) return 'high';
    if (riskScore >= 40) return 'medium';
    return 'low';
  }, [riskScore]);

  // Calculate total effort
  const totalEffort = useMemo(() => {
    return changes.reduce((sum, change) => sum + change.estimatedEffort, 0);
  }, [changes]);

  // Group changes by impact
  const changesByImpact = useMemo(() => {
    const groups: Record<ImpactLevel, typeof changes> = {
      low: [],
      medium: [],
      high: [],
      critical: [],
    };

    changes.forEach(change => {
      groups[change.impact].push(change);
    });

    return groups;
  }, [changes]);

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Impact Analysis</h2>
        <p className="text-sm text-gray-600 mt-1">
          Comprehensive analysis of architecture changes
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Overall Impact */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900">Overall Impact</h3>
            <div
              className="flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium"
              style={{
                backgroundColor: `${IMPACT_COLORS[impactAnalysis.overallImpact]}20`,
                color: IMPACT_COLORS[impactAnalysis.overallImpact]
              }}
            >
              <span>{IMPACT_ICONS[impactAnalysis.overallImpact]}</span>
              <span className="capitalize">{impactAnalysis.overallImpact}</span>
            </div>
          </div>

          {/* Risk Score */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Risk Score</span>
              <span className="text-sm text-gray-600">{riskScore}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${riskScore}%`,
                  backgroundColor: IMPACT_COLORS[riskLevel]
                }}
              />
            </div>
          </div>

          {/* Affected Systems */}
          <div>
            <span className="text-sm font-medium text-gray-700">Affected Systems:</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {impactAnalysis.affectedSystems.map((system) => (
                <span
                  key={system}
                  className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full"
                >
                  {system}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Risk Factors */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Risk Factors</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-gray-700">Breaking Changes</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.riskFactors.breakingChanges}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-orange-500" />
                <span className="text-sm text-gray-700">Data Migration</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.riskFactors.dataMigrationRequired ? 'Required' : 'Not Required'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Pause className="w-4 h-4 text-red-500" />
                <span className="text-sm text-gray-700">Downtime Required</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.riskFactors.downtimeRequired ? 'Yes' : 'No'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <RotateCcw className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-gray-700">Rollback Complexity</span>
              </div>
              <span
                className="text-sm font-medium"
                style={{ color: IMPACT_COLORS[impactAnalysis.riskFactors.rollbackComplexity] }}
              >
                {impactAnalysis.riskFactors.rollbackComplexity}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-700">Testing Complexity</span>
              </div>
              <span
                className="text-sm font-medium"
                style={{ color: IMPACT_COLORS[impactAnalysis.riskFactors.testingComplexity] }}
              >
                {impactAnalysis.riskFactors.testingComplexity}
              </span>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Implementation Timeline</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-700">Planning</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.timeline.planning} days
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Play className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-700">Development</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.timeline.development} days
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-gray-700">Testing</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.timeline.testing} days
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-purple-500" />
                <span className="text-sm text-gray-700">Deployment</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {impactAnalysis.timeline.deployment} days
              </span>
            </div>

            <div className="border-t border-gray-200 pt-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="font-medium text-gray-900">Total</span>
                </div>
                <span className="font-medium text-gray-900">
                  {impactAnalysis.timeline.total} days
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Effort Summary */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Effort Summary</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Total Estimated Effort</span>
              <span className="text-sm font-medium text-gray-900">{totalEffort} hours</span>
            </div>

            <div className="space-y-2">
              {Object.entries(changesByImpact).map(([impact, impactChanges]) => {
                if (impactChanges.length === 0) return null;
                
                const impactEffort = impactChanges.reduce((sum, change) => sum + change.estimatedEffort, 0);
                
                return (
                  <div key={impact} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span>{IMPACT_ICONS[impact as ImpactLevel]}</span>
                      <span className="text-sm text-gray-700 capitalize">{impact} Impact</span>
                      <span className="text-xs text-gray-500">({impactChanges.length})</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{impactEffort}h</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Recommendations</h3>
          
          {/* Implementation */}
          {impactAnalysis.recommendations.implementation.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <Play className="w-4 h-4 text-green-500" />
                <span>Implementation</span>
              </h4>
              <ul className="space-y-1">
                {impactAnalysis.recommendations.implementation.map((rec, index) => (
                  <li
                    key={index}
                    className="text-sm text-gray-600 cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={() => onRecommendationClick(rec)}
                  >
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Testing */}
          {impactAnalysis.recommendations.testing.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <Target className="w-4 h-4 text-yellow-500" />
                <span>Testing</span>
              </h4>
              <ul className="space-y-1">
                {impactAnalysis.recommendations.testing.map((rec, index) => (
                  <li
                    key={index}
                    className="text-sm text-gray-600 cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={() => onRecommendationClick(rec)}
                  >
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Deployment */}
          {impactAnalysis.recommendations.deployment.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <Globe className="w-4 h-4 text-purple-500" />
                <span>Deployment</span>
              </h4>
              <ul className="space-y-1">
                {impactAnalysis.recommendations.deployment.map((rec, index) => (
                  <li
                    key={index}
                    className="text-sm text-gray-600 cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={() => onRecommendationClick(rec)}
                  >
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Monitoring */}
          {impactAnalysis.recommendations.monitoring.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-blue-500" />
                <span>Monitoring</span>
              </h4>
              <ul className="space-y-1">
                {impactAnalysis.recommendations.monitoring.map((rec, index) => (
                  <li
                    key={index}
                    className="text-sm text-gray-600 cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={() => onRecommendationClick(rec)}
                  >
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImpactAnalysisPanel;
