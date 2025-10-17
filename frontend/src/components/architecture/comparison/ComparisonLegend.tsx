/**
 * Comparison Legend Component.
 * 
 * Displays a legend showing the meaning of different colors and symbols
 * used in the architecture comparison visualization.
 */

import React from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle
} from 'lucide-react';
import { 
  ComparisonLegendProps,
  CHANGE_COLORS,
  IMPACT_COLORS,
  CHANGE_ICONS,
  IMPACT_ICONS
} from '../../../types/architecture-comparison';

export const ComparisonLegend: React.FC<ComparisonLegendProps> = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-xs ${className}`}>
      <h3 className="font-semibold text-gray-900 mb-4">Comparison Legend</h3>
      
      {/* Change Types */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Change Types</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: CHANGE_COLORS.add }}
            >
              <Plus className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">New/Added</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: CHANGE_COLORS.modify }}
            >
              <Edit className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Modified/Changed</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: CHANGE_COLORS.remove }}
            >
              <Trash2 className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Removed/Deleted</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: CHANGE_COLORS.deprecate }}
            >
              <AlertTriangle className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Deprecated</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: CHANGE_COLORS.unchanged }}
            />
            <span className="text-sm text-gray-600">Unchanged</span>
          </div>
        </div>
      </div>

      {/* Impact Levels */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Impact Levels</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: IMPACT_COLORS.low }}
            >
              <CheckCircle className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Low Impact</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: IMPACT_COLORS.medium }}
            >
              <AlertTriangle className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Medium Impact</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: IMPACT_COLORS.high }}
            >
              <XCircle className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">High Impact</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded-full flex items-center justify-center text-white text-xs"
              style={{ backgroundColor: IMPACT_COLORS.critical }}
            >
              <XCircle className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-600">Critical Impact</span>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Status Indicators</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-sm text-gray-600">Healthy</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <span className="text-sm text-gray-600">Warning</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <XCircle className="w-4 h-4 text-red-600" />
            <span className="text-sm text-gray-600">Critical</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-gray-600" />
            <span className="text-sm text-gray-600">Unknown</span>
          </div>
        </div>
      </div>

      {/* View Modes */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">View Modes</h4>
        <div className="space-y-2 text-xs text-gray-600">
          <div>• <strong>Side-by-side:</strong> Compare current vs proposed</div>
          <div>• <strong>Overlay:</strong> Highlight changes on single view</div>
          <div>• <strong>Diff:</strong> Show detailed differences</div>
        </div>
      </div>

      {/* Interactions */}
      <div className="pt-2 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Interactions</h4>
        <div className="space-y-1 text-xs text-gray-500">
          <div>• Click element to see details</div>
          <div>• Hover for quick info</div>
          <div>• Use filters to focus on specific changes</div>
          <div>• Export comparison report</div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonLegend;
