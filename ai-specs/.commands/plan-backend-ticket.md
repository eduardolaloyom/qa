# Role

You are an expert software architect with extensive experience in Node.js/TypeScript/NestJS projects applying Domain-Driven Design (DDD) and Clean/Hexagonal Architecture.

# Ticket ID

$ARGUMENTS

# Goal

Obtain a step-by-step plan for a Linear ticket that is ready to start implementing.

# Process and rules

1. Adopt the role of `ai-specs/.agents/backend-developer.md`
2. Analyze the Linear ticket mentioned in #ticket using the MCP. If the mention is a local file, then avoid using MCP
3. Move the ticket status to **In Progress** in Linear using the MCP
4. Propose a step-by-step plan for the backend part, taking into account everything mentioned in the ticket and applying the project's best practices and rules you can find in `ai-specs/specs/`.
5. Apply the best practices of your role to ensure the developer can be fully autonomous and implement the ticket end-to-end using only your plan.
6. Do not write code yet; provide only the plan in the output format defined below.

# Output format

Markdown document at the path `ai-specs/changes/[ticket_id]_backend.md` containing the complete implementation details.
Follow this template:

## Backend Implementation Plan Ticket Template Structure

### 1. **Header**
- Title: `# Backend Implementation Plan: [TICKET-ID] [Feature Name]`

### 2. **Overview**
- Brief description of the feature and architecture principles (DDD, clean architecture, hexagonal)

### 3. **Architecture Context**
- Layers involved (Domain, Application, Infrastructure, Presentation)
- Components/files referenced

### 4. **Implementation Steps**
Detailed steps, typically:

#### **Step 0: Create Feature Branch**
- **Action**: Create and switch to a new feature branch following the development workflow. Check if it exists and if not, create it
- **Branch Naming**: `feature/[ticket-id]-backend`
- **Implementation Steps**:
  1. Ensure you're on the latest `main` or `develop` branch
  2. Pull latest changes: `git pull origin [base-branch]`
  3. Create new branch: `git checkout -b [branch-name]`
- **Notes**: This must be the FIRST step before any code changes.

#### **Step N: [Action Name]**
- **File**: Target file path
- **Action**: What to implement
- **Function Signature**: Code signature
- **Implementation Steps**: Numbered list
- **Dependencies**: Required imports
- **Implementation Notes**: Technical details

Common steps:
- **Step 1**: Create/Update Domain Entity or Value Object
- **Step 2**: Define Repository Interface (port)
- **Step 3**: Implement Application Service / Use Case
- **Step 4**: Implement Infrastructure adapter (repository, external service)
- **Step 5**: Create Controller and Route
- **Step 6**: Write Unit Tests (TDD — write failing tests first)
  - Subcategories: Successful Cases, Validation Errors, Not Found, Server Errors, Edge Cases

#### **Step N+1: Update Technical Documentation**
- **Action**: Review and update technical documentation according to changes made
- **Implementation Steps**:
  1. Review all code changes made during implementation
  2. Identify which documentation files need updates:
     - Data model changes → Update `ai-specs/specs/data-model.md`
     - API endpoint changes → Update `ai-specs/specs/api-spec.yml`
     - Standards/config changes → Update relevant `*-standards.mdc` files
  3. Update each affected file in English
  4. Verify all changes are accurately reflected
- **References**: Follow `ai-specs/specs/documentation-standards.mdc`
- **Notes**: MANDATORY before considering implementation complete.

### 5. **Implementation Order**
- Numbered list of steps in sequence (must start with Step 0 and end with documentation update)

### 6. **Testing Checklist**
- Post-implementation verification checklist (TDD: write tests before implementation)

### 7. **Error Response Format**
- JSON structure
- HTTP status code mapping

### 8. **Partial Update Support** (if applicable)
- Behavior for partial updates

### 9. **Dependencies**
- External libraries and tools required

### 10. **Notes**
- Important reminders and constraints
- Business rules
- Language requirements (English only)

### 11. **Next Steps After Implementation**
- Post-implementation tasks

### 12. **Implementation Verification**
- Final verification checklist:
  - Code Quality
  - Functionality
  - Testing (90%+ coverage)
  - Integration
  - Documentation updates completed
