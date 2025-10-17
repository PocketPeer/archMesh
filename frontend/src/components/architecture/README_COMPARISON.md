# Architecture Comparison Components

Enterprise-grade "before and after" architecture comparison components for brownfield changes, featuring detailed change tracking, impact analysis, and approval workflows.

## Overview

The Architecture Comparison system provides comprehensive tools for comparing current and proposed architectures, tracking changes, analyzing impact, and managing approval workflows for brownfield development projects.

## Features

### 🔍 **Multiple View Modes**
- **Side-by-side**: Compare current vs proposed architectures
- **Overlay**: Highlight changes on a single view
- **Diff**: Show detailed differences with color coding

### 🎨 **Visual Change Indicators**
- **Green**: New services/components (additions)
- **Yellow**: Modified services (changes)
- **Red**: Removed/deprecated elements
- **Gray**: Unchanged elements
- **Purple**: Deprecated elements

### 📊 **Comprehensive Change Tracking**
- **Service Changes**: Additions, modifications, removals
- **Dependency Changes**: New connections, protocol changes
- **Impact Analysis**: Risk assessment and effort estimation
- **Breaking Changes**: Identification and mitigation strategies

### 🎛️ **Interactive Features**
- **Click Elements**: View detailed change information
- **Filter Changes**: By type, impact, or breaking changes
- **Search**: Find specific changes or services
- **Export**: Generate comparison reports

### ✅ **Approval Workflow**
- **Review Process**: Structured approval workflow
- **Comments**: Detailed feedback and conditions
- **History**: Track approval decisions over time
- **Timeline**: Implementation scheduling

## Components

### ArchitectureComparison
Main comparison component that orchestrates all features.

```tsx
import { ArchitectureComparison } from './components/architecture';

<ArchitectureComparison
  currentArchitecture={currentArch}
  proposedArchitecture={proposedArch}
  changes={changes}
  impactAnalysis={impactAnalysis}
  onApprove={handleApprove}
  onReject={handleReject}
  onExport={handleExport}
  viewMode="side-by-side"
  showImpactAnalysis={true}
  showApprovalWorkflow={true}
/>
```

### ChangesPanel
Detailed list of all architecture changes with filtering and search.

```tsx
import { ChangesPanel } from './components/architecture/comparison';

<ChangesPanel
  changes={changes}
  impactAnalysis={impactAnalysis}
  onChangeClick={handleChangeClick}
  onFilterChange={handleFilterChange}
  selectedChangeId={selectedId}
/>
```

### ImpactAnalysisPanel
Comprehensive impact analysis with risk factors and recommendations.

```tsx
import { ImpactAnalysisPanel } from './components/architecture/comparison';

<ImpactAnalysisPanel
  impactAnalysis={impactAnalysis}
  changes={changes}
  onRecommendationClick={handleRecommendationClick}
/>
```

### ApprovalWorkflow
Structured approval process with comments and decision tracking.

```tsx
import { ApprovalWorkflow } from './components/architecture/comparison';

<ApprovalWorkflow
  onApprove={handleApprove}
  onReject={handleReject}
  onRequestChanges={handleRequestChanges}
  currentApprover="john.doe@company.com"
  approvalHistory={history}
/>
```

### DiffVisualization
Single view with changes highlighted using color coding.

```tsx
import { DiffVisualization } from './components/architecture/comparison';

<DiffVisualization
  currentServices={currentServices}
  proposedServices={proposedServices}
  currentDependencies={currentDeps}
  proposedDependencies={proposedDeps}
  changes={changes}
  onElementClick={handleElementClick}
/>
```

## Data Models

### ArchitectureChange
```typescript
interface ArchitectureChange {
  id: string;
  type: 'add' | 'modify' | 'remove' | 'deprecate';
  entity: 'service' | 'component' | 'dependency' | 'interface' | 'data_model';
  name: string;
  description: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  affectedServices: string[];
  breakingChange: boolean;
  migrationRequired: boolean;
  estimatedEffort: number; // in hours
  riskLevel: 'low' | 'medium' | 'high';
  dependencies: string[];
  metadata?: {
    reason?: string;
    alternatives?: string[];
    rollbackPlan?: string;
    testingRequired?: boolean;
    documentationRequired?: boolean;
  };
}
```

### ImpactAnalysis
```typescript
interface ImpactAnalysis {
  overallImpact: ImpactLevel;
  affectedSystems: string[];
  riskFactors: {
    breakingChanges: number;
    dataMigrationRequired: boolean;
    downtimeRequired: boolean;
    rollbackComplexity: ImpactLevel;
    testingComplexity: ImpactLevel;
  };
  recommendations: {
    implementation: string[];
    testing: string[];
    deployment: string[];
    monitoring: string[];
  };
  timeline: {
    planning: number; // days
    development: number; // days
    testing: number; // days
    deployment: number; // days
    total: number; // days
  };
}
```

### ApprovalDecision
```typescript
interface ApprovalDecision {
  approved: boolean;
  approver: string;
  comments: string;
  conditions?: string[];
  timeline?: {
    startDate: string;
    endDate: string;
  };
}
```

## Usage Examples

### Basic Comparison
```tsx
import React from 'react';
import { ArchitectureComparison } from './components/architecture';

const MyComparisonView = () => {
  const currentArch = {
    services: [/* current services */],
    dependencies: [/* current dependencies */],
    metadata: { /* metadata */ }
  };

  const proposedArch = {
    services: [/* proposed services */],
    dependencies: [/* proposed dependencies */],
    metadata: { /* metadata */ }
  };

  const changes = [
    {
      id: 'service-add-1',
      type: 'add',
      entity: 'service',
      name: 'new-service',
      description: 'New microservice for feature X',
      impact: 'medium',
      affectedServices: ['new-service'],
      breakingChange: false,
      migrationRequired: false,
      estimatedEffort: 40,
      riskLevel: 'low',
      dependencies: [],
    },
    // ... more changes
  ];

  const impactAnalysis = {
    overallImpact: 'medium',
    affectedSystems: ['existing-service', 'new-service'],
    riskFactors: {
      breakingChanges: 0,
      dataMigrationRequired: false,
      downtimeRequired: false,
      rollbackComplexity: 'low',
      testingComplexity: 'medium',
    },
    recommendations: {
      implementation: ['Deploy new service first', 'Use feature flags'],
      testing: ['Integration testing', 'Load testing'],
      deployment: ['Blue-green deployment', 'Gradual rollout'],
      monitoring: ['Set up alerts', 'Monitor performance'],
    },
    timeline: {
      planning: 3,
      development: 10,
      testing: 5,
      deployment: 2,
      total: 20,
    },
  };

  const handleApprove = (decision) => {
    console.log('Approved:', decision);
  };

  const handleReject = (reason) => {
    console.log('Rejected:', reason);
  };

  const handleExport = (format) => {
    console.log('Export:', format);
  };

  return (
    <div className="w-full h-screen">
      <ArchitectureComparison
        currentArchitecture={currentArch}
        proposedArchitecture={proposedArch}
        changes={changes}
        impactAnalysis={impactAnalysis}
        onApprove={handleApprove}
        onReject={handleReject}
        onExport={handleExport}
        viewMode="side-by-side"
        showImpactAnalysis={true}
        showApprovalWorkflow={true}
      />
    </div>
  );
};
```

### Custom Change Detection
```tsx
import { detectChanges } from './utils/change-detection';

const detectArchitectureChanges = (current, proposed) => {
  const changes = detectChanges(current, proposed);
  
  // Filter for high-impact changes
  const highImpactChanges = changes.filter(change => 
    change.impact === 'high' || change.impact === 'critical'
  );
  
  // Group by type
  const changesByType = changes.reduce((acc, change) => {
    if (!acc[change.type]) acc[change.type] = [];
    acc[change.type].push(change);
    return acc;
  }, {});
  
  return { changes, highImpactChanges, changesByType };
};
```

### Export Functionality
```tsx
const handleExport = async (format) => {
  switch (format) {
    case 'pdf':
      await exportToPDF({
        currentArchitecture,
        proposedArchitecture,
        changes,
        impactAnalysis,
        includeCharts: true,
        includeDetails: true,
      });
      break;
      
    case 'json':
      const data = {
        currentArchitecture,
        proposedArchitecture,
        changes,
        impactAnalysis,
        exportedAt: new Date().toISOString(),
      };
      downloadJSON(data, 'architecture-comparison.json');
      break;
      
    case 'html':
      await exportToHTML({
        currentArchitecture,
        proposedArchitecture,
        changes,
        impactAnalysis,
        template: 'comparison-report',
      });
      break;
  }
};
```

## Change Detection

### Automatic Change Detection
The system automatically detects changes by comparing:
- **Service Properties**: Name, technology, status, metadata
- **Dependencies**: Source, target, type, protocol
- **Endpoints**: Added, removed, modified API endpoints
- **Configuration**: Environment variables, settings

### Manual Change Annotation
```tsx
const manualChanges = [
  {
    id: 'manual-change-1',
    type: 'modify',
    entity: 'service',
    name: 'user-service',
    description: 'Manual annotation for business logic change',
    impact: 'high',
    affectedServices: ['user-service'],
    breakingChange: true,
    migrationRequired: true,
    estimatedEffort: 32,
    riskLevel: 'high',
    dependencies: ['user-database'],
    metadata: {
      reason: 'Business requirement change',
      alternatives: ['Alternative approach A', 'Alternative approach B'],
      rollbackPlan: 'Revert to previous version with data migration',
      testingRequired: true,
      documentationRequired: true,
    },
  },
];
```

## Impact Analysis

### Risk Assessment
The system calculates risk scores based on:
- **Breaking Changes**: Number and severity
- **Data Migration**: Required data transformations
- **Downtime**: System availability impact
- **Rollback Complexity**: Ease of reverting changes
- **Testing Complexity**: Required testing effort

### Recommendations Engine
Generates recommendations for:
- **Implementation**: Deployment strategies and best practices
- **Testing**: Required test coverage and scenarios
- **Deployment**: Rollout strategies and monitoring
- **Monitoring**: Alerting and observability setup

## Approval Workflow

### Approval Process
1. **Review**: Architecture team reviews changes
2. **Impact Analysis**: Assess risks and effort
3. **Decision**: Approve, reject, or request changes
4. **Conditions**: Set implementation conditions
5. **Timeline**: Define implementation schedule

### Approval History
```tsx
const approvalHistory = [
  {
    id: 'approval-1',
    approver: 'john.doe@company.com',
    decision: 'changes_requested',
    comments: 'Please add more detailed testing plan',
    timestamp: '2024-01-15T10:30:00Z',
    version: '1.0.0',
  },
  {
    id: 'approval-2',
    approver: 'jane.smith@company.com',
    decision: 'approved',
    comments: 'Changes look good, approved for implementation',
    timestamp: '2024-01-16T14:20:00Z',
    version: '1.1.0',
  },
];
```

## Customization

### Custom Change Types
```tsx
const customChangeTypes = {
  'security-update': {
    color: '#8b5cf6',
    icon: '🔒',
    label: 'Security Update',
  },
  'performance-optimization': {
    color: '#06b6d4',
    icon: '⚡',
    label: 'Performance Optimization',
  },
};
```

### Custom Impact Metrics
```tsx
const customImpactMetrics = {
  securityRisk: 'low' | 'medium' | 'high' | 'critical',
  complianceImpact: 'none' | 'minor' | 'major',
  userExperienceImpact: 'positive' | 'neutral' | 'negative',
};
```

## Performance Optimization

### Large Architecture Handling
- **Virtualization**: Only render visible changes
- **Lazy Loading**: Load change details on demand
- **Debounced Search**: Reduce search frequency
- **Memoization**: Cache expensive calculations

### Memory Management
- **Cleanup**: Remove unused event listeners
- **Garbage Collection**: Clear old data
- **Efficient Updates**: Minimize re-renders

## Accessibility

### Keyboard Navigation
- **Tab**: Navigate between controls
- **Enter**: Activate buttons and links
- **Escape**: Close panels and dialogs
- **Arrow Keys**: Navigate comparison views

### Screen Reader Support
- **ARIA Labels**: Descriptive labels for all elements
- **Role Attributes**: Proper semantic roles
- **Live Regions**: Announce dynamic changes

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

### Development Dependencies
- **Lucide React** - Icons
- **React Testing Library** - Testing
- **Jest** - Test runner

## Installation

```bash
npm install react react-flow-renderer lucide-react
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
      colors: {
        'change-add': '#10b981',
        'change-modify': '#f59e0b',
        'change-remove': '#ef4444',
        'change-deprecate': '#8b5cf6',
        'change-unchanged': '#6b7280',
      },
    },
  },
};
```

## Testing

### Unit Tests
```tsx
import { render, screen } from '@testing-library/react';
import { ArchitectureComparison } from './ArchitectureComparison';

test('renders architecture comparison', () => {
  render(
    <ArchitectureComparison
      currentArchitecture={mockCurrentArch}
      proposedArchitecture={mockProposedArch}
      changes={mockChanges}
      impactAnalysis={mockImpactAnalysis}
      onApprove={jest.fn()}
      onReject={jest.fn()}
      onExport={jest.fn()}
    />
  );
  
  expect(screen.getByText('Architecture Comparison')).toBeInTheDocument();
});
```

### Integration Tests
```tsx
import { render, fireEvent } from '@testing-library/react';
import { ArchitectureComparisonDemo } from './ArchitectureComparisonDemo';

test('handles approval workflow', () => {
  const { getByText } = render(<ArchitectureComparisonDemo />);
  
  // Click approve button
  fireEvent.click(getByText('Approve'));
  
  // Verify approval state
  expect(getByText('Architecture changes approved!')).toBeInTheDocument();
});
```

## Troubleshooting

### Common Issues

1. **Performance with Large Architectures**
   - Use virtualization for 100+ services
   - Implement change pagination
   - Optimize rendering with React.memo

2. **Memory Leaks**
   - Clean up event listeners
   - Remove unused subscriptions
   - Clear intervals and timeouts

3. **Change Detection Issues**
   - Verify data structure consistency
   - Check for circular references
   - Ensure proper ID matching

### Debug Mode
Enable debug logging:

```tsx
<ArchitectureComparison
  currentArchitecture={currentArch}
  proposedArchitecture={proposedArch}
  changes={changes}
  impactAnalysis={impactAnalysis}
  onApprove={handleApprove}
  onReject={handleReject}
  onExport={handleExport}
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
