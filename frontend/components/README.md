# Components Documentation

This directory contains reusable React components for the ArchMesh PoC frontend.

## DocumentUploader Component

A comprehensive drag-and-drop file upload component with validation, progress tracking, and beautiful UI.

### Features

- ✅ **Drag and Drop**: Intuitive file upload with visual feedback
- ✅ **File Validation**: Type and size validation with error messages
- ✅ **Progress Tracking**: Real-time upload progress with progress bars
- ✅ **Multiple Files**: Support for uploading multiple files simultaneously
- ✅ **File Management**: Remove uploaded files with confirmation
- ✅ **Beautiful UI**: Modern design with Tailwind CSS and shadcn/ui
- ✅ **Toast Notifications**: User feedback for all actions
- ✅ **Responsive Design**: Works on all screen sizes

### Props

```typescript
interface DocumentUploaderProps {
  onUploadComplete: (file: File) => void;
  projectId: string;
}
```

- `onUploadComplete`: Callback function called when a file is successfully uploaded
- `projectId`: Project ID for context (currently used for display purposes)

### Supported File Types

| Type | Extensions | Description |
|------|------------|-------------|
| Text Files | `.txt`, `.md`, `.rst` | Plain text, Markdown, reStructuredText |
| Documents | `.pdf`, `.docx`, `.doc` | PDF and Word documents |
| Presentations | `.pptx`, `.ppt` | PowerPoint presentations |

### File Size Limits

- **Maximum file size**: 50MB per file
- **Multiple files**: No limit on number of files
- **Validation**: Real-time validation with user feedback

### Usage Example

```tsx
import { DocumentUploader } from '@/components/DocumentUploader';

function MyComponent() {
  const handleFileUpload = (file: File) => {
    console.log('File uploaded:', file.name);
    // Handle the uploaded file
  };

  return (
    <DocumentUploader 
      onUploadComplete={handleFileUpload}
      projectId="my-project-123"
    />
  );
}
```

### Component Structure

```
DocumentUploader/
├── Upload Zone (Drag & Drop)
├── File Validation
├── Progress Tracking
├── Uploaded Files List
├── File Type Information
└── Tips & Guidelines
```

### Styling

The component uses:
- **Tailwind CSS** for styling
- **shadcn/ui components** for UI elements
- **Custom animations** for drag states
- **Responsive design** for all screen sizes

### Error Handling

The component handles various error scenarios:
- Invalid file types
- Files too large
- Network errors
- Upload failures

All errors are displayed with descriptive messages and toast notifications.

### Accessibility

- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus management

### Dependencies

- `react-dropzone` - Drag and drop functionality
- `@/components/ui/*` - shadcn/ui components
- `sonner` - Toast notifications
- `tailwindcss` - Styling

### Demo

Visit `/demo-upload` to see the component in action with:
- Live file upload testing
- Feature demonstration
- Usage examples
- Component documentation

## RequirementsViewer Component

A comprehensive component for displaying and reviewing structured requirements with approval workflows.

### Features

- ✅ **Structured Display**: Organized sections for all requirement types
- ✅ **Interactive Tabs**: Non-functional requirements in categorized tabs
- ✅ **Stakeholder Cards**: Visual stakeholder information with concerns
- ✅ **Priority Indicators**: Color-coded clarification questions by priority
- ✅ **Confidence Scoring**: Visual progress bar with confidence levels
- ✅ **Approval Workflow**: Approve/Reject actions with feedback
- ✅ **JSON Export**: Download requirements as structured JSON
- ✅ **Summary Statistics**: Overview of requirement counts

### Props

```typescript
interface RequirementsViewerProps {
  requirements: Requirements;
  onApprove: () => void;
  onReject: () => void;
}
```

### Usage Example

```tsx
import { RequirementsViewer } from '@/components/RequirementsViewer';

function MyComponent() {
  const handleApprove = async () => {
    // Handle approval logic
    console.log('Requirements approved');
  };

  const handleReject = async () => {
    // Handle rejection logic
    console.log('Requirements rejected');
  };

  return (
    <RequirementsViewer 
      requirements={requirements}
      onApprove={handleApprove}
      onReject={handleReject}
    />
  );
}
```

### Sections Displayed

1. **Business Goals** - High-level objectives with numbered list
2. **Functional Requirements** - System features and functionality
3. **Non-Functional Requirements** - Tabbed by category (Performance, Security, etc.)
4. **Constraints** - Project limitations and restrictions
5. **Stakeholders** - People and organizations with concerns
6. **Clarification Questions** - Prioritized questions needing answers
7. **Identified Gaps** - Missing or incomplete information
8. **Confidence Score** - AI confidence with visual progress bar

### Actions

- **Approve** - Green button to approve requirements
- **Reject** - Red button to reject requirements
- **Export JSON** - Download requirements as JSON file

## ArchitectureViewer Component

A comprehensive component for displaying and reviewing system architecture designs with interactive diagrams and approval workflows.

### Features

- ✅ **Architecture Overview**: Style and rationale display with status badges
- ✅ **C4 Diagram Rendering**: Interactive Mermaid diagrams with loading states
- ✅ **Component Cards**: Visual component information with technologies and responsibilities
- ✅ **Technology Stack**: Tabbed interface organized by layers (Frontend, Backend, Database, Infrastructure)
- ✅ **Alternatives Analysis**: Expandable cards with pros/cons and trade-offs
- ✅ **Approval Workflow**: Approve/Reject actions with feedback
- ✅ **Diagram Export**: Download C4 diagrams as PNG images
- ✅ **JSON Export**: Download architecture data as structured JSON

### Props

```typescript
interface ArchitectureViewerProps {
  architecture: Architecture;
  onApprove: () => void;
  onReject: () => void;
}
```

### Usage Example

```tsx
import { ArchitectureViewer } from '@/components/ArchitectureViewer';

function MyComponent() {
  const handleApprove = async () => {
    // Handle approval logic
    console.log('Architecture approved');
  };

  const handleReject = async () => {
    // Handle rejection logic
    console.log('Architecture rejected');
  };

  return (
    <ArchitectureViewer 
      architecture={architecture}
      onApprove={handleApprove}
      onReject={handleReject}
    />
  );
}
```

### Sections Displayed

1. **Architecture Overview** - Style badge and status information
2. **C4 Diagram** - Interactive Mermaid diagram with loading states
3. **System Components** - Card layout with technologies and responsibilities
4. **Technology Stack** - Tabbed interface by layer (Frontend, Backend, Database, Infrastructure)
5. **Alternatives Considered** - Expandable cards with pros/cons and trade-offs

### Actions

- **Approve** - Green button to approve architecture design
- **Reject** - Red button to reject architecture design
- **Export Diagram** - Download C4 diagram as PNG image
- **Export JSON** - Download architecture data as JSON file

### Dependencies

- `mermaid` - For C4 diagram rendering and visualization
- `@/components/ui/*` - shadcn/ui components (Card, Badge, Button, Tabs, Collapsible)
- `lucide-react` - Icon library for visual elements

### Demo

Visit `/demo-architecture` to see the component in action with:
- Live architecture display
- Interactive diagram rendering
- Feature demonstration
- Usage examples

## Other Components

### ApiTestComponent

A testing component for API connectivity and functionality.

**Location**: `components/ApiTestComponent.tsx`

**Features**:
- API health check
- Project operations testing
- Real-time error reporting
- Interactive testing interface

### UI Components

All shadcn/ui components are available in the `components/ui/` directory:

- `Button` - Various button styles and states
- `Card` - Content containers with headers
- `Badge` - Status and category indicators
- `Dialog` - Modal dialogs and overlays
- `Input` - Form input fields
- `Textarea` - Multi-line text input
- `Tabs` - Tabbed content navigation
- `Progress` - Progress bars and indicators
- `Sonner` - Toast notification system

## Development

### Adding New Components

1. Create component file in `components/` directory
2. Use TypeScript for type safety
3. Follow existing naming conventions
4. Include comprehensive prop interfaces
5. Add JSDoc comments for documentation
6. Test with different screen sizes
7. Ensure accessibility compliance

### Component Guidelines

- Use functional components with hooks
- Implement proper error boundaries
- Include loading states
- Provide user feedback
- Follow design system patterns
- Optimize for performance
- Write comprehensive tests

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow the established color palette
- Maintain consistent spacing
- Ensure responsive design
- Use semantic HTML elements
- Implement proper focus states
