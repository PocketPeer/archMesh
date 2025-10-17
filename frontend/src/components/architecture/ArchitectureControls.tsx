/**
 * Architecture Controls Component.
 * 
 * Provides comprehensive controls for the architecture visualizer including
 * zoom controls, export functionality, search, and layer toggles.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Download, 
  Search, 
  Eye, 
  EyeOff, 
  Map, 
  MapPin,
  Filter,
  Settings,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { 
  ArchitectureControlsProps, 
  ZoomLevel, 
  ExportFormat,
  SearchResult 
} from '../../types/architecture';

const ZOOM_LEVELS = [
  { level: 1, name: 'Enterprise', description: 'All systems' },
  { level: 2, name: 'System', description: 'Services within system' },
  { level: 3, name: 'Service', description: 'Components within service' },
  { level: 4, name: 'Component', description: 'Code structure' },
];

const EXPORT_FORMATS: { format: ExportFormat; label: string; description: string }[] = [
  { format: 'png', label: 'PNG', description: 'High-quality image' },
  { format: 'svg', label: 'SVG', description: 'Scalable vector' },
  { format: 'json', label: 'JSON', description: 'Data export' },
];

const LAYERS = [
  { id: 'services', label: 'Services', icon: '🔧' },
  { id: 'dependencies', label: 'Dependencies', icon: '🔗' },
  { id: 'labels', label: 'Labels', icon: '🏷️' },
  { id: 'metrics', label: 'Metrics', icon: '📊' },
];

export const ArchitectureControls: React.FC<ArchitectureControlsProps> = ({
  zoomLevel,
  onZoomLevelChange,
  onZoomIn,
  onZoomOut,
  onReset,
  onExport,
  onSearch,
  onToggleLayer,
  searchQuery,
  searchResults,
  selectedNodeId,
  showMinimap,
  onToggleMinimap,
  showLegend,
  onToggleLegend,
  className = '',
}) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isLayersOpen, setIsLayersOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [localSearchQuery, setLocalSearchQuery] = useState(searchQuery);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Sync local search query with prop
  useEffect(() => {
    setLocalSearchQuery(searchQuery);
  }, [searchQuery]);

  // Handle search input change
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setLocalSearchQuery(query);
    onSearch(query);
  }, [onSearch]);

  // Handle search result click
  const handleSearchResultClick = useCallback((result: SearchResult) => {
    // This would typically trigger node selection
    console.log('Search result clicked:', result);
  }, []);

  // Handle export format selection
  const handleExportFormat = useCallback((format: ExportFormat) => {
    onExport(format);
    setIsExportOpen(false);
  }, [onExport]);

  // Handle layer toggle
  const handleLayerToggle = useCallback((layerId: string) => {
    onToggleLayer(layerId);
  }, [onToggleLayer]);

  // Focus search input when search is opened
  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 p-4 space-y-4 ${className}`}>
      {/* Zoom Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onZoomOut}
          disabled={zoomLevel <= 1}
          className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        
        <select
          value={zoomLevel}
          onChange={(e) => onZoomLevelChange(parseInt(e.target.value) as ZoomLevel)}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {ZOOM_LEVELS.map((level) => (
            <option key={level.level} value={level.level}>
              L{level.level}: {level.name}
            </option>
          ))}
        </select>
        
        <button
          onClick={onZoomIn}
          disabled={zoomLevel >= 4}
          className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        
        <button
          onClick={onReset}
          className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <button
          onClick={() => setIsSearchOpen(!isSearchOpen)}
          className="w-full flex items-center justify-between p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4" />
            <span className="text-sm">Search</span>
            {searchResults.length > 0 && (
              <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                {searchResults.length}
              </span>
            )}
          </div>
          {isSearchOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {isSearchOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-md shadow-lg z-50">
            <div className="p-3">
              <input
                ref={searchInputRef}
                type="text"
                value={localSearchQuery}
                onChange={handleSearchChange}
                placeholder="Search services, technologies..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              {searchResults.length > 0 && (
                <div className="mt-2 max-h-48 overflow-y-auto">
                  {searchResults.map((result, index) => (
                    <div
                      key={index}
                      onClick={() => handleSearchResultClick(result)}
                      className="p-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-sm">{result.service.name}</div>
                          <div className="text-xs text-gray-500">
                            {result.service.type} • {result.service.technology}
                          </div>
                        </div>
                        <div className="text-xs text-gray-400">
                          {result.matchType}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Export */}
      <div className="relative">
        <button
          onClick={() => setIsExportOpen(!isExportOpen)}
          className="w-full flex items-center justify-between p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span className="text-sm">Export</span>
          </div>
          {isExportOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {isExportOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-md shadow-lg z-50">
            <div className="p-2">
              {EXPORT_FORMATS.map((format) => (
                <button
                  key={format.format}
                  onClick={() => handleExportFormat(format.format)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded-md text-sm"
                >
                  <div className="font-medium">{format.label}</div>
                  <div className="text-xs text-gray-500">{format.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Layers */}
      <div className="relative">
        <button
          onClick={() => setIsLayersOpen(!isLayersOpen)}
          className="w-full flex items-center justify-between p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <Eye className="w-4 h-4" />
            <span className="text-sm">Layers</span>
          </div>
          {isLayersOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {isLayersOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-md shadow-lg z-50">
            <div className="p-2">
              {LAYERS.map((layer) => (
                <button
                  key={layer.id}
                  onClick={() => handleLayerToggle(layer.id)}
                  className="w-full flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-md text-sm"
                >
                  <span>{layer.icon}</span>
                  <span>{layer.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* View Options */}
      <div className="space-y-2">
        <button
          onClick={onToggleMinimap}
          className={`w-full flex items-center space-x-2 p-2 rounded-md transition-colors ${
            showMinimap ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          <Map className="w-4 h-4" />
          <span className="text-sm">Minimap</span>
        </button>
        
        <button
          onClick={onToggleLegend}
          className={`w-full flex items-center space-x-2 p-2 rounded-md transition-colors ${
            showLegend ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          <MapPin className="w-4 h-4" />
          <span className="text-sm">Legend</span>
        </button>
      </div>

      {/* Status Info */}
      {selectedNodeId && (
        <div className="pt-2 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Selected: {selectedNodeId}
          </div>
        </div>
      )}
    </div>
  );
};

export default ArchitectureControls;
