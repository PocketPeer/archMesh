/**
 * Changes Panel Component.
 * 
 * Displays detailed list of architecture changes with filtering,
 * search, and impact analysis capabilities.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  ChevronDown, 
  ChevronRight, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  FileText,
  ExternalLink,
  Plus,
  Minus,
  Edit,
  Trash2
} from 'lucide-react';
import { 
  ChangesPanelProps, 
  ChangeFilter, 
  ChangeType, 
  EntityType, 
  ImpactLevel,
  CHANGE_COLORS,
  IMPACT_COLORS,
  CHANGE_ICONS,
  IMPACT_ICONS
} from '../../../types/architecture-comparison';

export const ChangesPanel: React.FC<ChangesPanelProps> = ({
  changes,
  impactAnalysis,
  onChangeClick,
  onFilterChange,
  selectedChangeId,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [expandedChanges, setExpandedChanges] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<ChangeFilter>({
    types: [],
    entities: [],
    impacts: [],
    breakingChangesOnly: false,
    searchQuery: '',
  });

  // Filter changes based on current filter
  const filteredChanges = useMemo(() => {
    return changes.filter(change => {
      // Search query filter
      if (searchQuery && !change.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !change.description.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // Type filter
      if (filter.types.length > 0 && !filter.types.includes(change.type)) {
        return false;
      }

      // Entity filter
      if (filter.entities.length > 0 && !filter.entities.includes(change.entity)) {
        return false;
      }

      // Impact filter
      if (filter.impacts.length > 0 && !filter.impacts.includes(change.impact)) {
        return false;
      }

      // Breaking changes filter
      if (filter.breakingChangesOnly && !change.breakingChange) {
        return false;
      }

      return true;
    });
  }, [changes, searchQuery, filter]);

  // Group changes by type
  const groupedChanges = useMemo(() => {
    const groups: Record<ChangeType, typeof filteredChanges> = {
      add: [],
      modify: [],
      remove: [],
      deprecate: [],
    };

    filteredChanges.forEach(change => {
      groups[change.type].push(change);
    });

    return groups;
  }, [filteredChanges]);

  // Handle change expansion
  const handleChangeExpansion = useCallback((changeId: string) => {
    setExpandedChanges(prev => {
      const newSet = new Set(prev);
      if (newSet.has(changeId)) {
        newSet.delete(changeId);
      } else {
        newSet.add(changeId);
      }
      return newSet;
    });
  }, []);

  // Handle filter update
  const handleFilterUpdate = useCallback((newFilter: Partial<ChangeFilter>) => {
    const updatedFilter = { ...filter, ...newFilter };
    setFilter(updatedFilter);
    onFilterChange(updatedFilter);
  }, [filter, onFilterChange]);

  // Handle type filter toggle
  const handleTypeFilterToggle = useCallback((type: ChangeType) => {
    const newTypes = filter.types.includes(type)
      ? filter.types.filter(t => t !== type)
      : [...filter.types, type];
    handleFilterUpdate({ types: newTypes });
  }, [filter.types, handleFilterUpdate]);

  // Handle impact filter toggle
  const handleImpactFilterToggle = useCallback((impact: ImpactLevel) => {
    const newImpacts = filter.impacts.includes(impact)
      ? filter.impacts.filter(i => i !== impact)
      : [...filter.impacts, impact];
    handleFilterUpdate({ impacts: newImpacts });
  }, [filter.impacts, handleFilterUpdate]);

  // Render change item
  const renderChangeItem = (change: any) => {
    const isExpanded = expandedChanges.has(change.id);
    const isSelected = selectedChangeId === change.id;

    return (
      <div
        key={change.id}
        className={`border border-gray-200 rounded-lg mb-2 transition-all ${
          isSelected ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
        }`}
      >
        {/* Change Header */}
        <div
          className="p-3 cursor-pointer"
          onClick={() => onChangeClick(change.id)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                style={{ backgroundColor: CHANGE_COLORS[change.type] }}
              >
                {CHANGE_ICONS[change.type]}
              </div>
              
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="font-medium text-gray-900">{change.name}</h4>
                  {change.breakingChange && (
                    <AlertTriangle className="w-4 h-4 text-red-500" title="Breaking Change" />
                  )}
                </div>
                <p className="text-sm text-gray-600">{change.description}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div
                className="flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium"
                style={{ 
                  backgroundColor: `${IMPACT_COLORS[change.impact]}20`,
                  color: IMPACT_COLORS[change.impact]
                }}
              >
                <span>{IMPACT_ICONS[change.impact]}</span>
                <span>{change.impact}</span>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleChangeExpansion(change.id);
                }}
                className="p-1 hover:bg-gray-100 rounded"
              >
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="px-3 pb-3 border-t border-gray-100">
            <div className="pt-3 space-y-3">
              {/* Change Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Type:</span>
                  <span className="ml-2 text-gray-600">{change.type}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Entity:</span>
                  <span className="ml-2 text-gray-600">{change.entity}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Impact:</span>
                  <span className="ml-2 text-gray-600">{change.impact}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Effort:</span>
                  <span className="ml-2 text-gray-600">{change.estimatedEffort}h</span>
                </div>
              </div>

              {/* Affected Services */}
              {change.affectedServices.length > 0 && (
                <div>
                  <span className="font-medium text-gray-700 text-sm">Affected Services:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {change.affectedServices.map((serviceId: string) => (
                      <span
                        key={serviceId}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                      >
                        {serviceId}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Dependencies */}
              {change.dependencies.length > 0 && (
                <div>
                  <span className="font-medium text-gray-700 text-sm">Dependencies:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {change.dependencies.map((dep: string) => (
                      <span
                        key={dep}
                        className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                      >
                        {dep}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <span className="font-medium text-gray-700">Risk:</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    change.riskLevel === 'low' ? 'bg-green-100 text-green-700' :
                    change.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {change.riskLevel}
                  </span>
                </div>
                
                {change.migrationRequired && (
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4 text-orange-500" />
                    <span className="text-orange-600 text-xs">Migration Required</span>
                  </div>
                )}
              </div>

              {/* Metadata */}
              {change.metadata && (
                <div className="space-y-2">
                  {change.metadata.reason && (
                    <div>
                      <span className="font-medium text-gray-700 text-sm">Reason:</span>
                      <p className="text-sm text-gray-600 mt-1">{change.metadata.reason}</p>
                    </div>
                  )}
                  
                  {change.metadata.alternatives && change.metadata.alternatives.length > 0 && (
                    <div>
                      <span className="font-medium text-gray-700 text-sm">Alternatives:</span>
                      <ul className="text-sm text-gray-600 mt-1 list-disc list-inside">
                        {change.metadata.alternatives.map((alt: string, index: number) => (
                          <li key={index}>{alt}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Search and Filters */}
      <div className="p-4 border-b border-gray-200">
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search changes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Filter Options */}
        {showFilters && (
          <div className="mt-3 space-y-3">
            {/* Type Filters */}
            <div>
              <span className="text-sm font-medium text-gray-700">Types:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {(['add', 'modify', 'remove', 'deprecate'] as ChangeType[]).map(type => (
                  <button
                    key={type}
                    onClick={() => handleTypeFilterToggle(type)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filter.types.includes(type)
                        ? 'text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    style={{
                      backgroundColor: filter.types.includes(type) ? CHANGE_COLORS[type] : undefined
                    }}
                  >
                    {CHANGE_ICONS[type]} {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Impact Filters */}
            <div>
              <span className="text-sm font-medium text-gray-700">Impact:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {(['low', 'medium', 'high', 'critical'] as ImpactLevel[]).map(impact => (
                  <button
                    key={impact}
                    onClick={() => handleImpactFilterToggle(impact)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filter.impacts.includes(impact)
                        ? 'text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    style={{
                      backgroundColor: filter.impacts.includes(impact) ? IMPACT_COLORS[impact] : undefined
                    }}
                  >
                    {IMPACT_ICONS[impact]} {impact}
                  </button>
                ))}
              </div>
            </div>

            {/* Breaking Changes Filter */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="breaking-changes"
                checked={filter.breakingChangesOnly}
                onChange={(e) => handleFilterUpdate({ breakingChangesOnly: e.target.checked })}
                className="rounded border-gray-300"
              />
              <label htmlFor="breaking-changes" className="text-sm text-gray-700">
                Breaking changes only
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Changes List */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredChanges.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No changes found</p>
            {searchQuery && (
              <p className="text-sm text-gray-400 mt-1">Try adjusting your search or filters</p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {/* Group by type */}
            {Object.entries(groupedChanges).map(([type, typeChanges]) => {
              if (typeChanges.length === 0) return null;
              
              return (
                <div key={type}>
                  <div className="flex items-center space-x-2 mb-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: CHANGE_COLORS[type as ChangeType] }}
                    />
                    <h3 className="font-medium text-gray-700 capitalize">
                      {type} ({typeChanges.length})
                    </h3>
                  </div>
                  
                  {typeChanges.map(renderChangeItem)}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-sm text-gray-600">
          Showing {filteredChanges.length} of {changes.length} changes
        </div>
      </div>
    </div>
  );
};

export default ChangesPanel;
