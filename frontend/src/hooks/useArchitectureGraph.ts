/**
 * Custom hook for architecture graph state management.
 * 
 * Provides centralized state management for the architecture visualization
 * with Zustand for efficient updates and persistence.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { 
  Service, 
  Dependency, 
  ZoomLevel, 
  SearchResult, 
  ArchitectureGraphState, 
  ArchitectureGraphActions,
  ServiceType,
  ServiceStatus,
  ExportFormat,
  FilterOptions
} from '../types/architecture';

interface ArchitectureGraphStore extends ArchitectureGraphState, ArchitectureGraphActions {}

// Zoom level configurations
const ZOOM_LEVEL_CONFIGS = {
  1: {
    name: 'Enterprise',
    description: 'All systems and high-level components',
    nodeFilter: (service: Service) => service.type === 'service' || service.type === 'gateway',
    showDependencies: true,
  },
  2: {
    name: 'System',
    description: 'Services within a system',
    nodeFilter: (service: Service) => true, // Show all services
    showDependencies: true,
  },
  3: {
    name: 'Service',
    description: 'Components within a service',
    nodeFilter: (service: Service) => service.children && service.children.length > 0,
    showDependencies: true,
  },
  4: {
    name: 'Component',
    description: 'Code structure and internal components',
    nodeFilter: (service: Service) => true, // Show all components
    showDependencies: false,
  },
};

// Default state
const defaultState: ArchitectureGraphState = {
  services: [],
  dependencies: [],
  zoomLevel: 1,
  selectedNodeId: undefined,
  searchQuery: '',
  searchResults: [],
  filteredServices: [],
  filteredDependencies: [],
  viewport: { x: 0, y: 0, zoom: 1 },
  showMinimap: true,
  showLegend: true,
  visibleLayers: new Set(['services', 'dependencies', 'labels']),
  loading: false,
  error: undefined,
};

export const useArchitectureGraph = create<ArchitectureGraphStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...defaultState,

        // Service management
        setServices: (services: Service[]) => {
          set((state) => {
            const filteredServices = filterServicesByZoomLevel(services, state.zoomLevel);
            return {
              services,
              filteredServices,
              loading: false,
              error: undefined,
            };
          });
        },

        setDependencies: (dependencies: Dependency[]) => {
          set((state) => {
            const filteredDependencies = filterDependenciesByZoomLevel(
              dependencies, 
              state.zoomLevel, 
              state.filteredServices
            );
            return {
              dependencies,
              filteredDependencies,
            };
          });
        },

        // Zoom level management
        setZoomLevel: (level: ZoomLevel) => {
          set((state) => {
            const previousLevel = state.zoomLevel;
            const filteredServices = filterServicesByZoomLevel(state.services, level);
            const filteredDependencies = filterDependenciesByZoomLevel(
              state.dependencies, 
              level, 
              filteredServices
            );
            
            return {
              zoomLevel: level,
              filteredServices,
              filteredDependencies,
              selectedNodeId: undefined, // Clear selection on zoom change
            };
          });
        },

        // Node selection
        setSelectedNode: (nodeId?: string) => {
          set({ selectedNodeId: nodeId });
        },

        // Search functionality
        setSearchQuery: (query: string) => {
          set((state) => {
            const searchResults = query ? performSearch(query, state.services) : [];
            return {
              searchQuery: query,
              searchResults,
            };
          });
        },

        // Viewport management
        setViewport: (viewport) => {
          set({ viewport });
        },

        // UI toggles
        toggleMinimap: () => {
          set((state) => ({ showMinimap: !state.showMinimap }));
        },

        toggleLegend: () => {
          set((state) => ({ showLegend: !state.showLegend }));
        },

        toggleLayer: (layer: string) => {
          set((state) => {
            const newVisibleLayers = new Set(state.visibleLayers);
            if (newVisibleLayers.has(layer)) {
              newVisibleLayers.delete(layer);
            } else {
              newVisibleLayers.add(layer);
            }
            return { visibleLayers: newVisibleLayers };
          });
        },

        // Navigation controls
        resetView: () => {
          set({
            viewport: { x: 0, y: 0, zoom: 1 },
            selectedNodeId: undefined,
            searchQuery: '',
            searchResults: [],
          });
        },

        zoomIn: () => {
          const state = get();
          const currentLevel = state.zoomLevel;
          if (currentLevel < 4) {
            state.setZoomLevel((currentLevel + 1) as ZoomLevel);
          }
        },

        zoomOut: () => {
          const state = get();
          const currentLevel = state.zoomLevel;
          if (currentLevel > 1) {
            state.setZoomLevel((currentLevel - 1) as ZoomLevel);
          }
        },

        // Search functionality
        search: (query: string): SearchResult[] => {
          const state = get();
          return performSearch(query, state.services);
        },

        // Filtering
        filterByType: (type: ServiceType) => {
          set((state) => {
            const filteredServices = state.services.filter(service => service.type === type);
            const filteredDependencies = state.dependencies.filter(dep => 
              filteredServices.some(s => s.id === dep.source || s.id === dep.target)
            );
            return {
              filteredServices,
              filteredDependencies,
            };
          });
        },

        filterByStatus: (status: ServiceStatus) => {
          set((state) => {
            const filteredServices = state.services.filter(service => service.status === status);
            const filteredDependencies = state.dependencies.filter(dep => 
              filteredServices.some(s => s.id === dep.source || s.id === dep.target)
            );
            return {
              filteredServices,
              filteredDependencies,
            };
          });
        },

        clearFilters: () => {
          set((state) => {
            const filteredServices = filterServicesByZoomLevel(state.services, state.zoomLevel);
            const filteredDependencies = filterDependenciesByZoomLevel(
              state.dependencies, 
              state.zoomLevel, 
              filteredServices
            );
            return {
              filteredServices,
              filteredDependencies,
              searchQuery: '',
              searchResults: [],
            };
          });
        },

        // Export functionality
        exportGraph: (format: ExportFormat) => {
          const state = get();
          exportGraphData(state, format);
        },
      }),
      {
        name: 'architecture-graph-store',
        partialize: (state) => ({
          showMinimap: state.showMinimap,
          showLegend: state.showLegend,
          visibleLayers: Array.from(state.visibleLayers),
          viewport: state.viewport,
        }),
      }
    ),
    {
      name: 'architecture-graph',
    }
  )
);

// Helper functions

function filterServicesByZoomLevel(services: Service[], zoomLevel: ZoomLevel): Service[] {
  const config = ZOOM_LEVEL_CONFIGS[zoomLevel];
  return services.filter(config.nodeFilter);
}

function filterDependenciesByZoomLevel(
  dependencies: Dependency[], 
  zoomLevel: ZoomLevel, 
  filteredServices: Service[]
): Dependency[] {
  const config = ZOOM_LEVEL_CONFIGS[zoomLevel];
  if (!config.showDependencies) {
    return [];
  }
  
  const serviceIds = new Set(filteredServices.map(s => s.id));
  return dependencies.filter(dep => 
    serviceIds.has(dep.source) && serviceIds.has(dep.target)
  );
}

function performSearch(query: string, services: Service[]): SearchResult[] {
  const lowercaseQuery = query.toLowerCase();
  const results: SearchResult[] = [];

  services.forEach(service => {
    let score = 0;
    let matchType: 'name' | 'technology' | 'type' | 'description' = 'name';

    // Search in service name
    if (service.name.toLowerCase().includes(lowercaseQuery)) {
      score += 10;
      matchType = 'name';
    }

    // Search in technology
    if (service.technology.toLowerCase().includes(lowercaseQuery)) {
      score += 8;
      matchType = 'technology';
    }

    // Search in type
    if (service.type.toLowerCase().includes(lowercaseQuery)) {
      score += 6;
      matchType = 'type';
    }

    // Search in description
    if (service.description?.toLowerCase().includes(lowercaseQuery)) {
      score += 4;
      matchType = 'description';
    }

    if (score > 0) {
      results.push({
        service,
        matchType,
        score,
      });
    }
  });

  // Sort by score (highest first)
  return results.sort((a, b) => b.score - a.score);
}

function exportGraphData(state: ArchitectureGraphState, format: ExportFormat) {
  const data = {
    services: state.filteredServices,
    dependencies: state.filteredDependencies,
    metadata: {
      exportedAt: new Date().toISOString(),
      zoomLevel: state.zoomLevel,
      totalServices: state.filteredServices.length,
      totalDependencies: state.filteredDependencies.length,
    },
  };

  switch (format) {
    case 'json':
      const jsonData = JSON.stringify(data, null, 2);
      downloadFile(jsonData, 'architecture-graph.json', 'application/json');
      break;
    case 'svg':
      // SVG export would be handled by the visualization component
      console.log('SVG export requested');
      break;
    case 'png':
      // PNG export would be handled by the visualization component
      console.log('PNG export requested');
      break;
  }
}

function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Selector hooks for optimized re-renders
export const useServices = () => useArchitectureGraph((state) => state.services);
export const useFilteredServices = () => useArchitectureGraph((state) => state.filteredServices);
export const useDependencies = () => useArchitectureGraph((state) => state.dependencies);
export const useFilteredDependencies = () => useArchitectureGraph((state) => state.filteredDependencies);
export const useZoomLevel = () => useArchitectureGraph((state) => state.zoomLevel);
export const useSelectedNode = () => useArchitectureGraph((state) => state.selectedNodeId);
export const useSearchQuery = () => useArchitectureGraph((state) => state.searchQuery);
export const useSearchResults = () => useArchitectureGraph((state) => state.searchResults);
export const useViewport = () => useArchitectureGraph((state) => state.viewport);
export const useUIState = () => useArchitectureGraph((state) => ({
  showMinimap: state.showMinimap,
  showLegend: state.showLegend,
  visibleLayers: state.visibleLayers,
}));

// Action hooks
export const useArchitectureActions = () => useArchitectureGraph((state) => ({
  setServices: state.setServices,
  setDependencies: state.setDependencies,
  setZoomLevel: state.setZoomLevel,
  setSelectedNode: state.setSelectedNode,
  setSearchQuery: state.setSearchQuery,
  setViewport: state.setViewport,
  toggleMinimap: state.toggleMinimap,
  toggleLegend: state.toggleLegend,
  toggleLayer: state.toggleLayer,
  resetView: state.resetView,
  zoomIn: state.zoomIn,
  zoomOut: state.zoomOut,
  search: state.search,
  filterByType: state.filterByType,
  filterByStatus: state.filterByStatus,
  clearFilters: state.clearFilters,
  exportGraph: state.exportGraph,
}));
