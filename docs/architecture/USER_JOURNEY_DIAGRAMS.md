# 🎨 ArchMesh User Journey Diagrams

## Main User Flows

### 1. Greenfield Project Flow

```mermaid
graph TD
    A[🏠 Homepage] --> B[📋 Create New Project]
    B --> C[📝 Project Details Form]
    C --> D[💾 Project Created]
    D --> E[📤 Upload Requirements Document]
    E --> F[🤖 AI Analysis Starts]
    F --> G[📊 Requirements Review]
    G --> H[✅ Approve Requirements]
    H --> I[🏗️ Architecture Design]
    I --> J[📐 Architecture Review]
    J --> K[✅ Approve Architecture]
    K --> L[🎉 Project Complete]
    
    style A fill:#e1f5fe
    style L fill:#c8e6c9
    style F fill:#fff3e0
    style I fill:#f3e5f5
```

### 2. Brownfield Project Flow

```mermaid
graph TD
    A[🏠 Homepage] --> B[📋 Create New Project]
    B --> C[🔄 Select Brownfield Mode]
    C --> D[🔗 Connect GitHub Repository]
    D --> E[🔍 Repository Analysis]
    E --> F[📊 Existing Architecture Extracted]
    F --> G[📝 Add New Requirements]
    G --> H[🤖 Integration Design]
    H --> I[📐 Architecture Comparison]
    I --> J[✅ Approve Integration]
    J --> K[🎉 Integration Complete]
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
    style E fill:#fff3e0
    style H fill:#f3e5f5
```

### 3. Project Management Flow

```mermaid
graph TD
    A[🏠 Homepage] --> B[📂 View All Projects]
    B --> C[🔍 Project List]
    C --> D[👁️ View Project Details]
    D --> E[📊 Project Dashboard]
    E --> F[🔄 Active Workflows]
    E --> G[📈 Project Statistics]
    E --> H[⚙️ Project Settings]
    
    F --> I[📋 Workflow Status]
    I --> J[👤 Human Review Required]
    J --> K[💬 Submit Feedback]
    K --> L[🔄 Workflow Continues]
    
    style A fill:#e1f5fe
    style E fill:#e8f5e8
    style J fill:#fff3e0
```

## Current Issues Visualization

### 1. Navigation & UX Issues

```mermaid
graph LR
    A[User Uploads Document] --> B[❌ No Clear Next Steps]
    B --> C[❌ Workflow Status Unclear]
    C --> D[❌ User Gets Lost]
    
    style B fill:#ffebee
    style C fill:#ffebee
    style D fill:#ffebee
```

### 2. Workflow Management Issues

```mermaid
graph TD
    A[Workflow Starts] --> B[❌ No Real-time Updates]
    B --> C[❌ User Must Refresh Manually]
    C --> D[❌ Poor User Experience]
    
    E[Human Review Required] --> F[❌ No Notification System]
    F --> G[❌ User Doesn't Know to Check]
    G --> H[❌ Workflow Stalls]
    
    style B fill:#ffebee
    style C fill:#ffebee
    style F fill:#ffebee
    style H fill:#ffebee
```

### 3. Brownfield Integration Issues

```mermaid
graph TD
    A[GitHub Repository] --> B[❌ No Authentication Flow]
    B --> C[❌ Limited to Public Repos]
    C --> D[❌ No Private Repo Support]
    
    E[Repository Analysis] --> F[❌ No Progress Indicators]
    F --> G[❌ Long Wait Times]
    G --> H[❌ User Abandons Process]
    
    style B fill:#fff3e0
    style C fill:#fff3e0
    style F fill:#fff3e0
    style H fill:#fff3e0
```

## Proposed Solutions

### 1. Improved Workflow Navigation

```mermaid
graph TD
    A[Document Upload] --> B[✅ Clear Success Message]
    B --> C[✅ Auto-redirect to Workflow Status]
    C --> D[✅ Real-time Progress Updates]
    D --> E[✅ Clear Next Steps]
    
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

### 2. Notification System

```mermaid
graph TD
    A[Workflow Requires Review] --> B[✅ Browser Notification]
    A --> C[✅ Email Notification]
    A --> D[✅ In-app Notification]
    B --> E[✅ User Takes Action]
    C --> E
    D --> E
    
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

### 3. GitHub Integration

```mermaid
graph TD
    A[Connect GitHub] --> B[✅ OAuth Flow]
    B --> C[✅ Repository Selection]
    C --> D[✅ Analysis Progress]
    D --> E[✅ Results Display]
    
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        A[Homepage]
        B[Project Management]
        C[Workflow Status]
        D[Architecture Viewer]
        E[Brownfield Tools]
    end
    
    subgraph "Backend (FastAPI)"
        F[Projects API]
        G[Workflows API]
        H[Brownfield API]
        I[Health API]
    end
    
    subgraph "AI Agents"
        J[Requirements Agent]
        K[Architecture Agent]
        L[GitHub Analyzer]
    end
    
    subgraph "External Services"
        M[DeepSeek LLM]
        N[GitHub API]
        O[Pinecone Vector DB]
        P[Neo4j Graph DB]
    end
    
    A --> F
    B --> F
    C --> G
    D --> G
    E --> H
    
    F --> J
    G --> J
    G --> K
    H --> L
    
    J --> M
    K --> M
    L --> N
    L --> O
    L --> P
    
    style A fill:#e1f5fe
    style F fill:#e8f5e8
    style J fill:#fff3e0
    style M fill:#f3e5f5
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant A as AI Agents
    participant L as LLM
    participant D as Database
    
    U->>F: Upload Document
    F->>B: POST /workflows/start-architecture
    B->>D: Create Workflow Session
    B->>A: Start Requirements Agent
    A->>L: Analyze Document
    L-->>A: Structured Requirements
    A-->>B: Requirements Data
    B->>D: Update Workflow State
    B-->>F: Workflow Status
    F-->>U: Show Review Required
    
    U->>F: Approve Requirements
    F->>B: POST /workflows/{id}/review
    B->>A: Start Architecture Agent
    A->>L: Generate Architecture
    L-->>A: Architecture Design
    A-->>B: Architecture Data
    B->>D: Update Workflow State
    B-->>F: Workflow Complete
    F-->>U: Show Results
```

---

*Diagrams created: 2025-10-18*  
*Use these diagrams for team discussions and implementation planning*

