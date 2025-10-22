/**
 * BROWNFIELD WORKFLOW TESTS - TDD Test Suite
 * 
 * Tests brownfield scenarios using real-world repository data from:
 * https://github.com/PocketPeer/archMesh
 * 
 * Brownfield scenarios include:
 * 1. Existing Codebase Analysis
 * 2. Architecture Discovery
 * 3. Technical Debt Assessment
 * 4. Modernization Recommendations
 * 5. Migration Planning
 * 6. Legacy System Integration
 */

import { test, expect } from '@playwright/test';

test.describe('Brownfield Workflow - TDD', () => {
  let testUser: { email: string; password: string; name: string };
  let testProject: { id: string; name: string };

  test.beforeEach(async ({ page }) => {
    const timestamp = Date.now();
    testUser = {
      email: `brownfieldtest${timestamp}@example.com`,
      password: 'TestPass1!',
      name: 'Brownfield Test User'
    };

    // Register and login
    await page.goto('http://localhost:3000/register');
    await page.fill('input[id="name"]', testUser.name);
    await page.fill('input[id="email"]', testUser.email);
    await page.fill('input[id="password"]', testUser.password);
    await page.fill('input[id="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to projects page (with longer timeout for auto-login)
    await expect(page).toHaveURL('http://localhost:3000/projects', { timeout: 30000 });
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();
  });

  test.describe('Existing Codebase Analysis', () => {
    test('should analyze existing ArchMesh codebase structure', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'ArchMesh Brownfield Analysis ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Analysis of existing ArchMesh codebase for modernization');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set project mode to brownfield
      await page.click('text=Existing System (Brownfield)');
      await expect(page.locator('text=Existing System (Brownfield)')).toBeVisible();

      // Navigate to upload page
      await page.click('text=Start Workflow');
      await expect(page.locator('[data-slot="card-title"]:has-text("Upload Requirements Document")').first()).toBeVisible();

      // Upload ArchMesh repository structure as requirements
      const archmeshStructure = `
# ArchMesh Repository Analysis

## Project Structure
- backend/ (Python FastAPI application)
- frontend/ (Next.js React application)
- sample-docs/ (Documentation and examples)
- docker-compose.yml (Container orchestration)
- README.md (Project documentation)

## Technology Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Database: PostgreSQL
- Cache: Redis
- AI/ML: OpenAI, Anthropic, DeepSeek integration
- Container: Docker, Docker Compose

## Key Components
- Document processing and analysis
- AI-powered requirements extraction
- Architecture generation
- Multiple LLM provider support
- Local development with DeepSeek

## Current Architecture
- Monolithic backend with modular structure
- React SPA frontend
- RESTful API design
- Database migrations with Alembic
- Redis for caching and session management
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'archmesh-analysis.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(archmeshStructure)
      });

      // Start brownfield analysis workflow
      await page.click('text=Start Workflow');
      
      // Should see brownfield-specific processing
      await expect(page.locator('text=Analyzing Existing Codebase')).toBeVisible();
      await expect(page.locator('text=Brownfield Analysis')).toBeVisible();
      
      // Wait for analysis completion
      await page.waitForSelector('text=Codebase Analysis Complete', { timeout: 300000 });
      
      // Should see analysis results
      await expect(page.locator('text=Existing Architecture')).toBeVisible();
      await expect(page.locator('text=Technology Stack')).toBeVisible();
      await expect(page.locator('text=Code Quality Assessment')).toBeVisible();
    });

    test('should identify technical debt and modernization opportunities', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Technical Debt Analysis ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Technical debt analysis for ArchMesh modernization');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload technical debt analysis
      const technicalDebtContent = `
# ArchMesh Technical Debt Analysis

## Current Issues
- Monolithic backend structure
- Tight coupling between components
- Limited test coverage
- Manual deployment processes
- No CI/CD pipeline
- Inconsistent error handling
- Missing API versioning
- No monitoring or observability

## Modernization Opportunities
- Microservices architecture
- Container orchestration with Kubernetes
- Automated testing and CI/CD
- API gateway implementation
- Monitoring and logging
- Security enhancements
- Performance optimization
- Documentation improvements

## Migration Strategy
- Phase 1: Infrastructure modernization
- Phase 2: Service decomposition
- Phase 3: Data migration
- Phase 4: Testing and validation
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'technical-debt.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(technicalDebtContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Technical Debt Analysis Complete', { timeout: 300000 });

      // Should see technical debt results
      await expect(page.locator('text=Technical Debt Report')).toBeVisible();
      await expect(page.locator('text=Modernization Recommendations')).toBeVisible();
      await expect(page.locator('text=Migration Roadmap')).toBeVisible();
    });
  });

  test.describe('Architecture Discovery', () => {
    test('should discover existing architecture patterns', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Architecture Discovery ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Architecture discovery for ArchMesh system');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload architecture discovery content
      const architectureContent = `
# ArchMesh Architecture Discovery

## Current Architecture Patterns
- Layered Architecture (Presentation, Business, Data layers)
- Repository Pattern for data access
- Dependency Injection for loose coupling
- RESTful API design
- Event-driven architecture for AI processing

## Data Flow
1. User uploads document via frontend
2. Frontend sends to backend API
3. Backend processes with AI agents
4. Results stored in database
5. Real-time updates via WebSocket

## Integration Points
- OpenAI API for document analysis
- Anthropic Claude for complex reasoning
- DeepSeek for local processing
- PostgreSQL for data persistence
- Redis for caching and sessions

## Scalability Considerations
- Horizontal scaling with load balancers
- Database connection pooling
- Caching strategies
- Async processing for AI tasks
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'architecture-discovery.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(architectureContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Architecture Discovery Complete', { timeout: 300000 });

      // Should see architecture discovery results
      await expect(page.locator('text=Architecture Patterns')).toBeVisible();
      await expect(page.locator('text=Data Flow Analysis')).toBeVisible();
      await expect(page.locator('text=Integration Points')).toBeVisible();
      await expect(page.locator('text=Scalability Assessment')).toBeVisible();
    });

    test('should analyze dependencies and relationships', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Dependency Analysis ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Dependency analysis for ArchMesh modernization');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload dependency analysis
      const dependencyContent = `
# ArchMesh Dependency Analysis

## External Dependencies
- OpenAI API (GPT-4, GPT-3.5-turbo)
- Anthropic Claude API
- DeepSeek local model
- PostgreSQL database
- Redis cache
- Docker containers

## Internal Dependencies
- FastAPI backend framework
- SQLAlchemy ORM
- Alembic migrations
- Next.js frontend framework
- React components
- TypeScript types

## Critical Dependencies
- AI/ML model providers
- Database connectivity
- Authentication services
- File processing libraries

## Dependency Risks
- API rate limits
- Model availability
- Database connection issues
- Version compatibility
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'dependency-analysis.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(dependencyContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Dependency Analysis Complete', { timeout: 300000 });

      // Should see dependency analysis results
      await expect(page.locator('text=Dependency Map')).toBeVisible();
      await expect(page.locator('text=Risk Assessment')).toBeVisible();
      await expect(page.locator('text=Modernization Impact')).toBeVisible();
    });
  });

  test.describe('Modernization Recommendations', () => {
    test('should generate modernization roadmap', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Modernization Roadmap ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Modernization roadmap for ArchMesh');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload modernization requirements
      const modernizationContent = `
# ArchMesh Modernization Requirements

## Business Goals
- Improve system scalability
- Reduce operational costs
- Enhance developer productivity
- Increase system reliability
- Better user experience

## Technical Objectives
- Microservices architecture
- Cloud-native deployment
- Automated CI/CD pipeline
- Enhanced monitoring
- Security improvements
- Performance optimization

## Constraints
- Minimal downtime during migration
- Preserve existing functionality
- Budget limitations
- Timeline constraints
- Team skill requirements

## Success Metrics
- 50% reduction in deployment time
- 99.9% uptime
- 3x faster development cycles
- 40% cost reduction
- Improved security posture
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'modernization-requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(modernizationContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Modernization Analysis Complete', { timeout: 300000 });

      // Should see modernization recommendations
      await expect(page.locator('text=Modernization Roadmap')).toBeVisible();
      await expect(page.locator('text=Implementation Phases')).toBeVisible();
      await expect(page.locator('text=Risk Mitigation')).toBeVisible();
      await expect(page.locator('text=Success Metrics')).toBeVisible();
    });

    test('should provide migration strategies', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Migration Strategy ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Migration strategy for ArchMesh modernization');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload migration requirements
      const migrationContent = `
# ArchMesh Migration Strategy

## Migration Approach
- Strangler Fig Pattern for gradual replacement
- Database migration with zero downtime
- Blue-green deployment strategy
- Feature flags for controlled rollout
- Canary releases for risk mitigation

## Migration Phases
1. Infrastructure preparation
2. Service extraction
3. Data migration
4. Testing and validation
5. Production cutover
6. Legacy system decommission

## Risk Mitigation
- Comprehensive testing strategy
- Rollback procedures
- Monitoring and alerting
- Team training and preparation
- Stakeholder communication

## Success Criteria
- Zero data loss
- Minimal business disruption
- Performance improvements
- Cost optimization
- Enhanced maintainability
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'migration-strategy.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(migrationContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Migration Strategy Complete', { timeout: 300000 });

      // Should see migration strategy results
      await expect(page.locator('text=Migration Plan')).toBeVisible();
      await expect(page.locator('text=Risk Assessment')).toBeVisible();
      await expect(page.locator('text=Timeline')).toBeVisible();
      await expect(page.locator('text=Resource Requirements')).toBeVisible();
    });
  });

  test.describe('Legacy System Integration', () => {
    test('should analyze legacy system integration points', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Legacy Integration ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Legacy system integration analysis');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload legacy integration content
      const legacyContent = `
# ArchMesh Legacy Integration Analysis

## Legacy Systems
- Existing document management system
- Legacy authentication service
- Old database systems
- Legacy API endpoints
- Legacy file storage systems

## Integration Challenges
- Different data formats
- Authentication mechanisms
- API versioning issues
- Performance bottlenecks
- Security vulnerabilities
- Maintenance overhead

## Integration Strategies
- API gateway for legacy systems
- Data transformation layers
- Authentication federation
- Message queuing for async processing
- Event-driven architecture
- Service mesh implementation

## Modernization Benefits
- Improved performance
- Enhanced security
- Better maintainability
- Cost reduction
- Scalability improvements
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'legacy-integration.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(legacyContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Legacy Integration Analysis Complete', { timeout: 300000 });

      // Should see legacy integration results
      await expect(page.locator('text=Legacy System Map')).toBeVisible();
      await expect(page.locator('text=Integration Points')).toBeVisible();
      await expect(page.locator('text=Modernization Strategy')).toBeVisible();
      await expect(page.locator('text=Cost-Benefit Analysis')).toBeVisible();
    });

    test('should provide brownfield architecture recommendations', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Brownfield Architecture ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Brownfield architecture recommendations');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Upload brownfield architecture content
      const brownfieldContent = `
# ArchMesh Brownfield Architecture

## Current State Analysis
- Monolithic FastAPI backend
- React SPA frontend
- PostgreSQL database
- Redis caching
- Docker containerization
- AI/ML integration

## Target Architecture
- Microservices architecture
- API gateway
- Service mesh
- Event-driven architecture
- Cloud-native deployment
- Container orchestration

## Migration Strategy
- Incremental modernization
- Service extraction
- Database decomposition
- Infrastructure migration
- Testing and validation

## Technology Recommendations
- Kubernetes for orchestration
- Istio for service mesh
- Prometheus for monitoring
- Grafana for visualization
- ELK stack for logging
- Vault for secrets management
      `;

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'brownfield-architecture.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(brownfieldContent)
      });

      await page.click('text=Start Workflow');
      await page.waitForSelector('text=Brownfield Architecture Complete', { timeout: 300000 });

      // Should see brownfield architecture results
      await expect(page.locator('text=Current State Assessment')).toBeVisible();
      await expect(page.locator('text=Target Architecture')).toBeVisible();
      await expect(page.locator('text=Migration Roadmap')).toBeVisible();
      await expect(page.locator('text=Technology Stack')).toBeVisible();
      await expect(page.locator('text=Implementation Plan')).toBeVisible();
    });
  });

  test.describe('AI Assistant for Brownfield', () => {
    test('should provide brownfield-specific AI assistance', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'AI Brownfield Assistant ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'AI assistant for brownfield modernization');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Open AI Assistant
      await page.click('text=AI Assistant');
      await expect(page.locator('text=AI Assistant')).toBeVisible();

      // Ask brownfield-specific questions
      await page.fill('textarea[placeholder*="message"]', 'What are the key considerations for modernizing a monolithic application to microservices?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Should receive brownfield-specific guidance
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('microservices');
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('modernization');

      // Ask about migration strategies
      await page.fill('textarea[placeholder*="message"]', 'What migration patterns should I consider for a brownfield project?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Should receive migration guidance
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('migration');
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('strangler');
    });

    test('should maintain context across brownfield workflow steps', async ({ page }) => {
      // Create brownfield project
      await page.click('text=Create Project');
      testProject = {
        id: '',
        name: 'Context Brownfield Test ' + Date.now()
      };
      await page.fill('input[placeholder="Enter project name"]', testProject.name);
      await page.fill('textarea[placeholder="Enter project description (optional)"]', 'Context testing for brownfield workflow');
      await page.selectOption('[role="dialog"] select', 'enterprise');
      await page.click('[role="dialog"] button:has-text("Create Project")');

      // Set to brownfield mode
      await page.click('text=Existing System (Brownfield)');
      await page.click('text=Start Workflow');

      // Open AI Assistant
      await page.click('text=AI Assistant');

      // Establish brownfield context
      await page.fill('textarea[placeholder*="message"]', 'I am working on modernizing the ArchMesh application from a monolithic to microservices architecture.');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // Upload brownfield requirements
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'brownfield-requirements.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('Modernize ArchMesh from monolithic to microservices architecture.')
      });

      // Start workflow
      await page.click('text=Start Workflow');

      // Ask context-aware question
      await page.fill('textarea[placeholder*="message"]', 'What should I consider for the ArchMesh modernization?');
      await page.click('button[type="submit"]');
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 30000 });

      // AI should understand the ArchMesh context
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('ArchMesh');
      await expect(page.locator('[data-testid="ai-response"]')).toContainText('modernization');
    });
  });
});
