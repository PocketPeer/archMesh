# 🎨 ArchMesh Diagram Generation Workflow Guide

## Overview

This guide demonstrates how to use the comprehensive diagram generation system in ArchMesh for both greenfield and brownfield projects. The system provides automated architecture documentation through C4 diagrams, sequence diagrams, and NFR mapping.

## 🚀 Quick Start

### 1. Access Diagram Generation

1. **Navigate to Project**: Go to your project detail page
2. **Click "Diagrams" Button**: Located in the project header
3. **Choose Diagram Type**: Select from C4, Sequence, or NFR mapping

### 2. Generate Your First Diagram

#### C4 Context Diagram
```bash
# Navigate to: /projects/{project-id}/diagrams
# Click: "Context View" button
# Result: System boundaries and external actors
```

#### Sequence Diagram
```bash
# Click: "Generate Sequence Diagrams" button
# Result: Interaction flows for key use-cases
```

#### NFR Mapping
```bash
# Click: "Generate NFR Mapping" button
# Result: Non-functional requirements with trade-off analysis
```

## 🏗️ Detailed Workflows

### Greenfield Project Workflow

#### Step 1: Project Setup
1. **Create Project**: Start with a new greenfield project
2. **Upload Requirements**: Add requirements documents
3. **Run Workflow**: Execute requirements analysis workflow
4. **Review Results**: Approve requirements and architecture

#### Step 2: Generate Architecture Diagrams
1. **Navigate to Diagrams**: Click "Diagrams" button in project header
2. **Generate C4 Context**: Create system boundary diagram
3. **Generate C4 Container**: Create high-level architecture diagram
4. **Generate C4 Component**: Create detailed component diagram
5. **Generate Sequence**: Create use-case interaction diagrams
6. **Generate NFR Mapping**: Map non-functional requirements

#### Step 3: Iterative Refinement
1. **Review Diagrams**: Check generated diagrams for accuracy
2. **Refine Architecture**: Update architecture based on diagrams
3. **Regenerate Diagrams**: Create updated diagrams
4. **Export & Share**: Download diagrams for team review

### Brownfield Project Workflow

#### Step 1: Repository Analysis
1. **Connect GitHub**: Link existing repository
2. **Run Analysis**: Execute brownfield analysis workflow
3. **Extract Architecture**: System extracts current architecture
4. **Build Knowledge Base**: Creates comprehensive knowledge base

#### Step 2: Generate Integration Diagrams
1. **Navigate to Diagrams**: Access diagram generation
2. **Generate Context**: Show existing system boundaries
3. **Generate Container**: Display current architecture
4. **Generate Sequence**: Show integration flows
5. **Generate NFR Mapping**: Map performance requirements

#### Step 3: Integration Planning
1. **Compare Architectures**: Old vs. new system comparison
2. **Plan Integration**: Design integration strategy
3. **Generate Migration Diagrams**: Create migration sequence diagrams
4. **Document Trade-offs**: Map integration trade-offs

## 📊 Diagram Types and Use Cases

### C4 Diagrams

#### Context Level
- **Purpose**: System boundaries and external actors
- **Use Cases**: Stakeholder communication, system overview
- **When to Use**: Project kickoff, stakeholder meetings

#### Container Level
- **Purpose**: High-level architecture with containers
- **Use Cases**: Architecture review, technology decisions
- **When to Use**: Technical architecture discussions

#### Component Level
- **Purpose**: Detailed component interactions
- **Use Cases**: Implementation planning, code organization
- **When to Use**: Development team coordination

### Sequence Diagrams

#### Use-Case Sequences
- **Purpose**: Interaction flows for key use-cases
- **Use Cases**: API design, user journey mapping
- **When to Use**: API documentation, user experience design

#### Integration Sequences
- **Purpose**: Service communication patterns
- **Use Cases**: Microservices design, system integration
- **When to Use**: Integration planning, service design

### NFR Mapping

#### Performance Requirements
- **Purpose**: Map performance requirements to components
- **Use Cases**: Performance planning, capacity planning
- **When to Use**: Performance optimization, scaling decisions

#### Security Requirements
- **Purpose**: Map security requirements to components
- **Use Cases**: Security planning, compliance
- **When to Use**: Security reviews, compliance audits

## 🔄 Knowledge Base Integration

### Automatic Knowledge Collection

The system automatically collects knowledge during workflow execution:

1. **Requirements Analysis**: Extracts functional and non-functional requirements
2. **Architecture Design**: Captures architectural decisions and patterns
3. **Constraint Identification**: Records business and technical constraints
4. **Stakeholder Input**: Incorporates stakeholder feedback and preferences
5. **Technology Decisions**: Tracks technology stack choices and rationale

### Iterative Knowledge Refinement

1. **LLM-Assisted Refinement**: Uses multiple LLMs for knowledge validation
2. **Cross-Validation**: Ensures knowledge consistency across sources
3. **Quality Assessment**: Continuous quality improvement
4. **Context Enrichment**: Adds contextual information to knowledge entities

### Knowledge-Driven Diagram Generation

1. **Context-Aware Generation**: Diagrams use project knowledge for accuracy
2. **Relationship Mapping**: Automatic relationship detection from knowledge
3. **Technology Stack Integration**: Diagrams reflect actual technology choices
4. **Constraint Visualization**: Business constraints shown in diagrams

## 🎯 Best Practices

### Diagram Generation

1. **Start with Context**: Always begin with C4 context diagrams
2. **Progressive Detail**: Move from context to container to component
3. **Use Templates**: Leverage pre-configured templates for common scenarios
4. **Iterate Frequently**: Regenerate diagrams as architecture evolves

### Knowledge Management

1. **Rich Metadata**: Add detailed metadata to knowledge entities
2. **Relationship Mapping**: Create explicit relationships between entities
3. **Regular Refinement**: Continuously refine knowledge quality
4. **Cross-Project Learning**: Share knowledge across similar projects

### Team Collaboration

1. **Share Diagrams**: Export and share diagrams with team members
2. **Version Control**: Track diagram changes over time
3. **Review Process**: Implement diagram review workflows
4. **Documentation**: Use diagrams as living documentation

## 🛠️ Technical Implementation

### API Endpoints

#### Get Available Diagram Types
```http
GET /api/v1/diagrams/types
```

#### Get Diagram Templates
```http
GET /api/v1/diagrams/templates
```

#### Generate C4 Diagram
```http
POST /api/v1/diagrams/c4
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "uuid",
  "diagram_type": "c4_context",
  "title": "System Context",
  "description": "High-level system boundaries",
  "include_nfr": true,
  "include_technology_stack": true
}
```

#### Generate Sequence Diagram
```http
POST /api/v1/diagrams/sequence
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "uuid",
  "use_cases": ["User Registration", "Order Processing"],
  "title": "Key Use-Case Sequences",
  "description": "Main user interaction flows"
}
```

#### Generate NFR Mapping
```http
POST /api/v1/diagrams/nfr-mapping
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "uuid",
  "nfr_requirements": [
    {
      "name": "Response Time",
      "metric": "latency",
      "target_value": "200",
      "unit": "ms",
      "priority": "high",
      "affected_components": ["api-gateway", "web-app"]
    }
  ],
  "title": "NFR Mapping",
  "description": "Non-functional requirements mapping"
}
```

### Frontend Integration

#### Component Usage
```tsx
import { ArchitectureDiagrams } from '@/components/ArchitectureDiagrams';

<ArchitectureDiagrams 
  projectId={projectId}
  workflowId={workflowId}
  onDiagramGenerated={(diagram) => {
    // Handle generated diagram
    console.log('Diagram generated:', diagram);
  }}
/>
```

#### Navigation
```tsx
// Add to project header
<Link href={`/projects/${projectId}/diagrams`}>
  <Button variant="outline">
    <BuildingIcon className="h-4 w-4 mr-2" />
    Diagrams
  </Button>
</Link>
```

## 📈 Advanced Features

### Round-trip Editing

1. **Edit Diagrams**: Modify generated diagrams
2. **Update Knowledge**: Changes automatically update knowledge base
3. **Regenerate**: Create updated diagrams from modified knowledge
4. **Version Control**: Track changes over time

### Multi-format Export

1. **PlantUML**: For detailed documentation and presentations
2. **Mermaid**: For GitHub integration and web rendering
3. **SVG/PNG**: For static image export
4. **PDF**: For formal documentation

### Template System

1. **Pre-configured Templates**: Common diagram patterns
2. **Custom Templates**: Create project-specific templates
3. **Template Sharing**: Share templates across projects
4. **Template Versioning**: Track template evolution

## 🔍 Troubleshooting

### Common Issues

#### Diagram Generation Fails
- **Check Authentication**: Ensure valid authentication token
- **Verify Project Access**: Confirm user has project access
- **Check Knowledge Base**: Ensure sufficient knowledge for generation

#### Poor Diagram Quality
- **Enrich Knowledge Base**: Add more detailed knowledge
- **Refine Requirements**: Improve requirement quality
- **Use Templates**: Leverage pre-configured templates

#### Export Issues
- **Check Format**: Ensure correct export format
- **Verify Content**: Check diagram content is valid
- **Test Browser**: Try different browser if issues persist

### Performance Optimization

1. **Cache Diagrams**: Generated diagrams are cached for performance
2. **Async Processing**: Large diagrams generated asynchronously
3. **Incremental Updates**: Only regenerate changed components
4. **Background Tasks**: Heavy processing done in background

## 🎉 Success Metrics

### Diagram Quality
- **Completeness**: All required components included
- **Accuracy**: Diagrams reflect actual architecture
- **Clarity**: Clear and understandable diagrams
- **Consistency**: Consistent style and format

### Knowledge Base Growth
- **Entity Count**: Number of knowledge entities
- **Relationship Density**: Connections between entities
- **Quality Score**: Average knowledge quality
- **Coverage**: Knowledge coverage across project aspects

### Team Adoption
- **Usage Frequency**: How often diagrams are generated
- **Export Rate**: How often diagrams are exported
- **Collaboration**: Team diagram sharing and review
- **Feedback**: User satisfaction and feedback

---

*This workflow guide provides comprehensive instructions for using the ArchMesh diagram generation system to create, manage, and evolve architectural documentation as part of your development workflow.*
