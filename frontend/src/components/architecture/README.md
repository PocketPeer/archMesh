# Architecture Visualization Components

Enterprise-grade interactive architecture visualization components similar to Sparx EA or LeanIX, built with React Flow, TypeScript, and Tailwind CSS.

## Overview

The Architecture Visualization system provides comprehensive tools for visualizing, analyzing, and interacting with enterprise architecture diagrams. It supports multiple zoom levels, interactive features, and real-time updates.

## Features

### 🎯 **Multiple Zoom Levels**
- **L1: Enterprise** - All systems and high-level components
- **L2: System** - Services within a system
- **L3: Service** - Components within a service
- **L4: Component** - Code structure and internal components

### 🖱️ **Interactive Features**
- **Click** - Select and view service details
- **Double-click** - Zoom into service components
- **Drag** - Pan around the diagram
- **Scroll** - Zoom in/out
- **Search** - Find services by name, technology, or type
- **Filter** - Show/hide specific service types or statuses

### 🎨 **Visual Elements**
- **Nodes** - Services, databases, queues, gateways with status indicators
- **Edges** - Dependencies with type indicators and protocols
- **Color Coding** - Health status, service type, technology stack
- **Labels** - Service names, technologies, versions
- **Tooltips** - Detailed information on hover

### 🎛️ **Controls**
- **Zoom Controls** - In/out buttons and level selector
- **Reset View** - Return to default view
- **Export** - PNG, SVG, and JSON formats
- **Layer Toggle** - Show/hide specific elements
- **Search Box** - Find and highlight services
- **Minimap** - Navigation overview
- **Legend** - Visual guide to symbols and colors

## Components

### ArchitectureVisualizer
Main visualization component that renders the interactive architecture diagram.

```tsx
import { ArchitectureVisualizer } from './components/architecture';

<ArchitectureVisualizer
  services={services}
  dependencies={dependencies}
  onNodeClick={handleNodeClick}
  onZoomLevelChange={handleZoomLevelChange}
  showMinimap={true}
  showControls={true}
  showLegend={true}
/>
```

### ArchitectureControls
Comprehensive control panel with zoom, search, export, and layer management.

```tsx
import { ArchitectureControls } from './components/architecture';

<ArchitectureControls
  zoomLevel={zoomLevel}
  onZoomLevelChange={handleZoomLevelChange}
  onExport={handleExport}
  onSearch={handleSearch}
  searchResults={searchResults}
/>
```

### ServiceDetailPanel
Detailed information panel for selected services.

```tsx
import { ServiceDetailPanel } from './components/architecture';

<ServiceDetailPanel
  service={selectedService}
  dependencies={serviceDependencies}
  onClose={handleClose}
  onEdit={handleEdit}
/>
```

### ArchitectureLegend
Visual guide showing the meaning of colors, icons, and symbols.

```tsx
import { ArchitectureLegend } from './components/architecture';

<ArchitectureLegend />
```

## Data Models

### Service
```typescript
interface Service {
  id: string;
  name: string;
  type: ServiceType;
  technology: string;
  status: ServiceStatus;
  description?: string;
  version?: string;
  owner?: string;
  team?: string;
  environment?: string;
  position: { x: number; y: number };
  metadata?: {
    endpoints?: string[];
    healthCheck?: string;
    repository?: string;
    uptime?: number;
    responseTime?: number;
    errorRate?: number;
  };
}
```

### Dependency
```typescript
interface Dependency {
  id: string;
  source: string;
  target: string;
  type: DependencyType;
  protocol?: string;
  description?: string;
  frequency?: 'high' | 'medium' | 'low';
  criticality?: 'critical' | 'important' | 'normal';
}
```

## State Management

The architecture visualization uses Zustand for state management with the `useArchitectureGraph` hook:

```tsx
import { useArchitectureGraph } from './hooks/useArchitectureGraph';

const {
  services,
  dependencies,
  zoomLevel,
  selectedNodeId,
  searchQuery,
  searchResults,
  setServices,
  setZoomLevel,
  search,
  exportGraph,
} = useArchitectureGraph();
```

### Key State Actions
- `setServices(services)` - Update service data
- `setZoomLevel(level)` - Change zoom level
- `search(query)` - Search for services
- `exportGraph(format)` - Export diagram
- `resetView()` - Reset to default view

## Usage Examples

### Basic Usage
```tsx
import React from 'react';
import { ArchitectureVisualizer } from './components/architecture';

const MyArchitectureView = () => {
  const services = [
    {
      id: 'user-service',
      name: 'User Service',
      type: 'service',
      technology: 'Node.js',
      status: 'healthy',
      position: { x: 100, y: 100 },
    },
    // ... more services
  ];

  const dependencies = [
    {
      id: 'user-to-db',
      source: 'user-service',
      target: 'user-database',
      type: 'data',
    },
    // ... more dependencies
  ];

  return (
    <div className="w-full h-screen">
      <ArchitectureVisualizer
        services={services}
        dependencies={dependencies}
        onNodeClick={(service) => console.log('Clicked:', service)}
        showMinimap={true}
        showControls={true}
      />
    </div>
  );
};
```

### With State Management
```tsx
import React, { useEffect } from 'react';
import { ArchitectureVisualizer } from './components/architecture';
import { useArchitectureGraph } from './hooks/useArchitectureGraph';

const ArchitectureView = () => {
  const {
    services,
    dependencies,
    setServices,
    setDependencies,
    search,
  } = useArchitectureGraph();

  useEffect(() => {
    // Load data from API
    fetchArchitectureData().then((data) => {
      setServices(data.services);
      setDependencies(data.dependencies);
    });
  }, [setServices, setDependencies]);

  const handleSearch = (query: string) => {
    const results = search(query);
    console.log('Search results:', results);
  };

  return (
    <ArchitectureVisualizer
      services={services}
      dependencies={dependencies}
      onSearch={handleSearch}
    />
  );
};
```

### Custom Styling
```tsx
<ArchitectureVisualizer
  services={services}
  dependencies={dependencies}
  className="custom-architecture-view"
  showMinimap={true}
  showLegend={true}
/>
```

## Customization

### Custom Node Types
```tsx
import { CustomServiceNode } from './components/architecture';

const nodeTypes = {
  custom: CustomServiceNode,
  // Add more custom node types
};
```

### Custom Edge Types
```tsx
import { CustomDependencyEdge } from './components/architecture';

const edgeTypes = {
  custom: CustomDependencyEdge,
  // Add more custom edge types
};
```

### Color Schemes
```typescript
const customColors = {
  healthy: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
  unknown: '#6b7280',
};
```

## Performance Optimization

### Large Datasets
- **Virtualization** - Only render visible nodes
- **Lazy Loading** - Load data on demand
- **Debounced Search** - Reduce search frequency
- **Memoization** - Cache expensive calculations

### Memory Management
- **Cleanup** - Remove unused event listeners
- **Garbage Collection** - Clear old data
- **Efficient Updates** - Minimize re-renders

## Accessibility

### Keyboard Navigation
- **Tab** - Navigate between controls
- **Enter** - Activate buttons and links
- **Escape** - Close panels and dialogs
- **Arrow Keys** - Navigate diagram
- **Ctrl+F** - Focus search

### Screen Reader Support
- **ARIA Labels** - Descriptive labels for all elements
- **Role Attributes** - Proper semantic roles
- **Live Regions** - Announce dynamic changes

## Browser Support

- **Chrome** 90+
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

## Dependencies

### Core Dependencies
- **React** 18+ - UI framework
- **React Flow** 11+ - Graph visualization
- **TypeScript** 4.9+ - Type safety
- **Tailwind CSS** 3+ - Styling
- **Zustand** 4+ - State management

### Development Dependencies
- **Lucide React** - Icons
- **React Testing Library** - Testing
- **Jest** - Test runner

## Installation

```bash
npm install react react-flow-renderer zustand lucide-react
npm install -D @types/react @types/react-dom typescript tailwindcss
```

## Configuration

### Tailwind CSS
Add to your `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    './src/components/architecture/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      // Custom theme extensions
    },
  },
};
```

### TypeScript
Ensure your `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  }
}
```

## Testing

### Unit Tests
```tsx
import { render, screen } from '@testing-library/react';
import { ArchitectureVisualizer } from './ArchitectureVisualizer';

test('renders architecture visualizer', () => {
  render(<ArchitectureVisualizer services={[]} dependencies={[]} />);
  expect(screen.getByRole('main')).toBeInTheDocument();
});
```

### Integration Tests
```tsx
import { render, fireEvent } from '@testing-library/react';
import { ArchitectureDemo } from './ArchitectureDemo';

test('handles node click', () => {
  const { getByTestId } = render(<ArchitectureDemo />);
  const node = getByTestId('user-service');
  fireEvent.click(node);
  // Assert expected behavior
});
```

## Troubleshooting

### Common Issues

1. **Performance with Large Datasets**
   - Use virtualization for 100+ nodes
   - Implement data pagination
   - Optimize rendering with React.memo

2. **Memory Leaks**
   - Clean up event listeners
   - Remove unused subscriptions
   - Clear intervals and timeouts

3. **Layout Issues**
   - Check CSS conflicts
   - Verify container dimensions
   - Ensure proper z-index values

### Debug Mode
Enable debug logging:

```tsx
<ArchitectureVisualizer
  services={services}
  dependencies={dependencies}
  debug={true}
/>
```

## Contributing

1. Follow TypeScript best practices
2. Write comprehensive tests
3. Update documentation
4. Ensure accessibility compliance
5. Test with large datasets

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issues
- Check documentation
- Review examples
- Test with sample data
