# Brownfield Frontend Implementation

This document describes the frontend implementation for brownfield project support in ArchMesh, including the new components and updated project page functionality.

## Overview

The brownfield frontend implementation provides a complete user interface for managing existing system integration projects. It includes mode selection, GitHub repository analysis, existing architecture visualization, and architecture comparison capabilities.

## Components

### 1. ModeSelector Component

**File**: `src/components/ModeSelector.tsx`

A component that allows users to choose between greenfield and brownfield project modes.

**Features**:
- Visual mode selection with icons and descriptions
- Mode-specific feature highlights
- Help text and guidance
- Responsive design with dark mode support

**Props**:
```typescript
interface ModeSelectorProps {
  value: 'greenfield' | 'brownfield';
  onChange: (mode: 'greenfield' | 'brownfield') => void;
  options?: ModeOption[];
  disabled?: boolean;
  className?: string;
}
```

**Usage**:
```tsx
<ModeSelector
  value={project.mode}
  onChange={updateProjectMode}
  className="mb-8"
/>
```

### 2. GitHubConnector Component

**File**: `src/components/GitHubConnector.tsx`

A component for connecting to and analyzing GitHub repositories.

**Features**:
- Repository URL input with validation
- Branch selection
- Optional GitHub token for private repositories
- Real-time analysis progress
- Analysis results display
- Error handling and user feedback

**Props**:
```typescript
interface GitHubConnectorProps {
  projectId: string;
  onAnalysisComplete: (result: GitHubAnalysisResult) => void;
  onError?: (error: string) => void;
  className?: string;
}
```

**Usage**:
```tsx
<GitHubConnector
  projectId={projectId}
  onAnalysisComplete={handleGitHubAnalysisComplete}
  onError={handleGitHubAnalysisError}
/>
```

### 3. Updated Project Page

**File**: `app/projects/[id]/page.tsx`

The main project page has been updated to support brownfield mode with conditional rendering based on project type.

**New Features**:
- Mode selector integration
- GitHub repository analysis
- Existing architecture visualization
- Architecture comparison
- Brownfield-specific workflow support

**Key Updates**:
- Added brownfield state management
- Integrated ModeSelector component
- Added GitHubConnector for repository analysis
- Implemented architecture comparison view
- Added conversion functions for data format compatibility

## Type Definitions

### Updated Types

**File**: `types/index.ts`

Extended the existing type definitions to support brownfield functionality:

```typescript
// Updated Project interface
export interface Project {
  id: string;
  name: string;
  description?: string;
  domain: 'cloud-native' | 'data-platform' | 'enterprise';
  mode: 'greenfield' | 'brownfield';  // New field
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  // Brownfield specific fields
  repository_url?: string;
  existing_architecture?: ExistingArchitecture;
  proposed_architecture?: ProposedArchitecture;
  changes?: ArchitectureChange[];
}

// New brownfield-specific types
export interface ExistingArchitecture {
  repository_url: string;
  branch: string;
  services: Service[];
  dependencies: Dependency[];
  technology_stack: Record<string, any>;
  quality_score: number;
  analysis_metadata: {
    analyzed_at: string;
    services_count: number;
    dependencies_count: number;
    technologies_detected: string[];
  };
}

export interface ProposedArchitecture {
  architecture_overview: {
    style: string;
    integration_approach: string;
    rationale: string;
  };
  new_services: Service[];
  modified_services: Service[];
  integration_points: IntegrationPoint[];
  impact_analysis: {
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    breaking_changes: boolean;
    downtime_required: boolean;
  };
}

export interface ArchitectureChange {
  id: string;
  type: 'add' | 'modify' | 'remove' | 'deprecate';
  entity: 'service' | 'component' | 'dependency' | 'interface' | 'data_model';
  name: string;
  description: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  affectedServices: string[];
  breakingChange: boolean;
  migrationRequired: boolean;
  estimatedEffort: number;
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

## Demo Page

**File**: `app/demo-brownfield/page.tsx`

A comprehensive demo page showcasing all brownfield functionality with mock data.

**Features**:
- Interactive mode selection
- Mock GitHub repository analysis
- Complete architecture comparison workflow
- Real-time state management
- User-friendly controls and feedback

**Demo Workflow**:
1. **Mode Selection**: Choose between greenfield and brownfield modes
2. **Repository Analysis**: Simulate GitHub repository analysis
3. **Architecture Visualization**: View existing system architecture
4. **Integration Design**: See proposed architecture changes
5. **Comparison**: Compare current vs. proposed architecture
6. **Approval Workflow**: Approve or reject integration plans

## Integration with Architecture Components

The brownfield frontend integrates with existing architecture visualization components:

### ArchitectureComparison Component

The brownfield implementation uses the existing `ArchitectureComparison` component from `src/components/architecture/ArchitectureComparison.tsx` to display side-by-side comparisons of current and proposed architectures.

**Data Conversion**:
```typescript
const convertToArchitectureGraph = (architecture: ExistingArchitecture | ProposedArchitecture): ArchitectureGraph => {
  // Converts brownfield data format to ArchitectureGraph format
  // Handles both existing and proposed architectures
}
```

## User Experience Flow

### 1. Project Creation
- User creates a new project
- Selects project mode (greenfield/brownfield)
- For brownfield: provides repository URL

### 2. Repository Analysis
- GitHub repository is analyzed
- Existing architecture is extracted
- Technology stack is identified
- Quality metrics are calculated

### 3. Requirements Processing
- User uploads requirements documents
- System parses requirements with brownfield context
- Integration points are identified

### 4. Architecture Design
- System designs new architecture with existing context
- Integration strategy is generated
- Impact analysis is performed

### 5. Review and Approval
- User reviews proposed changes
- Architecture comparison is displayed
- Integration plan is approved or rejected

### 6. Implementation
- Approved changes are implemented
- Progress is tracked
- Integration is monitored

## Styling and Theming

The brownfield components follow the existing design system:

- **Colors**: Consistent with the existing color palette
- **Typography**: Uses the same font families and sizes
- **Spacing**: Follows the established spacing system
- **Dark Mode**: Full support for dark mode
- **Responsive**: Mobile-first responsive design

## Error Handling

Comprehensive error handling is implemented throughout:

- **Network Errors**: Graceful handling of API failures
- **Validation Errors**: User-friendly validation messages
- **Analysis Errors**: Clear feedback for repository analysis issues
- **State Errors**: Proper state management and recovery

## Performance Considerations

- **Lazy Loading**: Components are loaded on demand
- **Memoization**: Expensive calculations are memoized
- **Virtualization**: Large lists are virtualized
- **Caching**: Analysis results are cached

## Accessibility

All components are built with accessibility in mind:

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and descriptions
- **Color Contrast**: WCAG compliant color combinations
- **Focus Management**: Proper focus handling

## Testing

The implementation includes comprehensive testing:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full workflow testing
- **Visual Tests**: Screenshot comparison testing

## Future Enhancements

Planned improvements include:

1. **Real-time Collaboration**: Multiple users working on the same project
2. **Advanced Analytics**: Detailed integration metrics and insights
3. **Automated Testing**: Integration test generation
4. **CI/CD Integration**: Direct deployment pipeline integration
5. **Mobile App**: Native mobile application support

## Getting Started

To use the brownfield frontend:

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **View Demo**:
   Navigate to `/demo-brownfield` to see the complete brownfield workflow

4. **Create Project**:
   Use the project creation flow to start a new brownfield project

## API Integration

The frontend integrates with the brownfield backend APIs:

- **Repository Analysis**: `POST /api/v1/brownfield/analyze-repository`
- **Knowledge Search**: `POST /api/v1/brownfield/search-knowledge`
- **Architecture Graph**: `GET /api/v1/brownfield/project/{id}/architecture-graph`
- **Project Context**: `GET /api/v1/brownfield/project/{id}/context`

## Troubleshooting

Common issues and solutions:

1. **Repository Analysis Fails**:
   - Check repository URL format
   - Verify GitHub token permissions
   - Ensure repository is accessible

2. **Architecture Comparison Not Loading**:
   - Verify both existing and proposed architectures are loaded
   - Check data format compatibility
   - Review console for errors

3. **Mode Selection Not Working**:
   - Check project state management
   - Verify event handlers are properly bound
   - Review component props

## Contributing

To contribute to the brownfield frontend:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure accessibility compliance
5. Test across different browsers and devices

## License

This implementation is part of the ArchMesh project and follows the same licensing terms.
