# 🔄 **COMPLETE WORKFLOW EXECUTION FLOW**

## **User Journey: From "Start Workflow" Button to Workflow Completion**

### **📱 Frontend Pages & Components**

```
1. PROJECTS OVERVIEW PAGE (/projects)
   ├── User Authentication Status (Login/Logout)
   ├── Project Cards Display
   ├── "Create Project" Button
   └── Navigation to Project Detail

2. PROJECT CREATION PAGE (/projects/create)
   ├── Project Type Selection (Greenfield vs Brownfield)
   ├── Information about differences between types
   ├── Project Name and Description
   ├── Domain Selection (Cloud-Native, Data Platform, Enterprise)
   └── Create Project Button

3. PROJECT DETAIL PAGE (/projects/[id])
   ├── Project Information
   ├── Workflow Statistics (Total, Active, Completed)
   ├── Current Workflow Status Card
   ├── Workflow History (Previous runs, status, results)
   ├── Team Collaboration (Add users, permissions)
   ├── "Start Workflow" Button
   └── Navigation to Upload Page

4. UPLOAD PAGE (/projects/[id]/upload)
   ├── File Upload Component
   ├── Project Context Textarea
   ├── LLM Provider Selection
   ├── Domain Selection
   └── "Start Workflow" Submit Button

5. WORKFLOW VALIDATION (2-Step Process)
   ├── Step 1: Client-side validation
   │   ├── Check file format and size
   │   ├── Validate required fields
   │   ├── Show validation errors if any
   │   └── Redirect to Project Detail if valid
   └── Step 2: Server-side workflow execution
       ├── Show notification with workflow ID
       ├── Start background LLM processing
       ├── Display progress indicators
       └── Handle errors with retry options

6. PROJECT DETAIL PAGE (With Active Workflow)
   ├── Workflow Status Updates (Real-time)
   ├── Progress Indicators
   ├── Error Messages with Retry Options
   ├── Workflow History
   ├── Workflow Metadata (ID, duration, execution time)
   └── Rerun Workflow (with prefilled information)
```

### **🔄 Complete Execution Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CLICKS "START WORKFLOW"                │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: CLIENT-SIDE VALIDATION               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. File Upload Validation                              │    │
│  │    - Check file type (txt, pdf, docx)                  │    │
│  │    - Validate file size (< 10MB)                       │    │
│  │    - Check file content (not empty)                   │    │
│  │    - Show validation errors if any                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. Form Data Validation                                │    │
│  │    - Check required fields (projectId, domain)          │    │
│  │    - Validate project context (min 10 characters)      │    │
│  │    - Check LLM provider selection                      │    │
│  │    - Show field-specific errors                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. Validation Result                                   │    │
│  │    ├── If VALID: Redirect to Project Detail            │    │
│  │    └── If INVALID: Show errors, stay on upload page   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 2: SERVER-SIDE WORKFLOW EXECUTION       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. Show Notification                                   │    │
│  │    - Display "Workflow started" notification           │    │
│  │    - Show workflow ID in notification center          │    │
│  │    - Add "View Progress" call-to-action button        │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. API Call to Backend                                 │    │
│  │    - POST /workflows/start-architecture                │    │
│  │    - Send FormData with file and metadata              │    │
│  │    - Handle authentication headers                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. Backend Processing                                  │    │
│  │    ├── Project Validation                              │    │
│  │    ├── File Storage & Validation                       │    │
│  │    ├── Workflow Initialization                         │    │
│  │    ├── Database Session Creation                       │    │
│  │    └── Background Workflow Execution                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 4. Real-time Updates                                   │    │
│  │    ├── Poll workflow status every 5 seconds           │    │
│  │    ├── Update progress indicators                     │    │
│  │    ├── Display error messages with retry options      │    │
│  │    └── Show completion status                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION STAGES                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 1: DOCUMENT_ANALYSIS                             │    │
│  │ ├── Parse uploaded document                            │    │
│  │ ├── Extract text content                               │    │
│  │ ├── Identify document type                             │    │
│  │ └── Set stage_progress = 0.1                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 2: REQUIREMENT_EXTRACTION                         │    │
│  │ ├── Call RequirementsAgent.execute()                   │    │
│  │ ├── LLM Processing (DeepSeek → Ollama fallback)        │    │
│  │ ├── Extract functional requirements                    │    │
│  │ ├── Extract non-functional requirements               │    │
│  │ ├── Identify stakeholders                             │    │
│  │ ├── Generate confidence score                         │    │
│  │ └── Set stage_progress = 0.3                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 3: REQUIREMENTS_REVIEW                           │    │
│  │ ├── Human review required                             │    │
│  │ ├── Display extracted requirements                     │    │
│  │ ├── Wait for user approval                             │    │
│  │ ├── Handle feedback                                    │    │
│  │ └── Set stage_progress = 0.5                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 4: ARCHITECTURE_DESIGN                           │    │
│  │ ├── Call ArchitectureAgent.execute()                   │    │
│  │ ├── Generate system architecture                      │    │
│  │ ├── Create C4 diagrams                                │    │
│  │ ├── Select technology stack                           │    │
│  │ └── Set stage_progress = 0.7                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 5: ARCHITECTURE_REVIEW                           │    │
│  │ ├── Human review of architecture                      │    │
│  │ ├── Display generated architecture                     │    │
│  │ ├── Wait for user approval                            │    │
│  │ └── Set stage_progress = 0.9                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ STAGE 6: COMPLETED                                     │    │
│  │ ├── Set is_active = false                             │    │
│  │ ├── Set completed_at timestamp                         │    │
│  │ ├── Generate final report                             │    │
│  │ └── Set stage_progress = 1.0                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND REDIRECT & UPDATES                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. API Response Handling                              │    │
│  │    - Receive session_id from backend                  │    │
│  │    - Show success toast notification                  │    │
│  │    - Redirect to /projects/[id]?workflow=[session_id] │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. Project Detail Page Updates                        │    │
│  │    - Load workflow list (polling every 10s)          │    │
│  │    - Update workflow statistics                       │    │
│  │    - Display current workflow status                  │    │
│  │    - Show real-time progress                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. Real-time Status Updates                           │    │
│  │    - Poll workflow status every 5s                    │    │
│  │    - Update progress indicators                       │    │
│  │    - Display error messages                           │    │
│  │    - Show completion status                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING & FALLBACKS                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ LLM Connection Failures                               │    │
│  │ ├── DeepSeek API timeout (120s)                       │    │
│  │ ├── Fallback to Ollama (llama3.2:3b)                 │    │
│  │ ├── Retry mechanism (4 attempts)                     │    │
│  │ └── Error logging and user notification              │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ File Upload Errors                                     │    │
│  │ ├── Invalid file type                                 │    │
│  │ ├── File size too large                               │    │
│  │ ├── Corrupted file                                    │    │
│  │ └── Network timeout                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Database Errors                                       │    │
│  │ ├── Connection timeout                                │    │
│  │ ├── Transaction rollback                              │    │
│  │ ├── Constraint violations                             │    │
│  │ └── Retry with exponential backoff                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### **🔧 Key Components & Files**

#### **Frontend Components:**
- **UploadPage** (`/app/projects/[id]/upload/page.tsx`)
- **ProjectDetailPage** (`/app/projects/[id]/page.tsx`)
- **ProjectsPage** (`/app/projects/page.tsx`)
- **AIChatWidget** (`/src/components/ai-chat/AIChatWidget.tsx`)

#### **Backend Components:**
- **ArchitectureWorkflow** (`/app/workflows/architecture_workflow.py`)
- **RequirementsAgent** (`/app/agents/requirements_agent.py`)
- **ArchitectureAgent** (`/app/agents/architecture_agent.py`)
- **WorkflowSession** (`/app/models/workflow_session.py`)

#### **API Endpoints:**
- **POST** `/api/v1/workflows/start-architecture`
- **GET** `/api/v1/workflows/{session_id}/status`
- **GET** `/api/v1/workflows/?project_id={id}`
- **POST** `/api/v1/workflows/{session_id}/review`

### **📊 Status Tracking**

```
Workflow Status States:
├── starting (0% progress)
├── document_analysis (10% progress)
├── requirement_extraction (30% progress)
├── requirements_review (50% progress)
├── architecture_design (70% progress)
├── architecture_review (90% progress)
├── completed (100% progress)
└── failed (error state)
```

### **🔄 Real-time Updates**

```
Frontend Polling:
├── Workflow List: Every 10 seconds
├── Current Workflow: Every 5 seconds
├── Status Updates: Real-time via WebSocket
└── Error Handling: Immediate notification
```

This flow diagram shows the complete journey from button click to workflow completion, including all the pages, components, API calls, and error handling mechanisms.
