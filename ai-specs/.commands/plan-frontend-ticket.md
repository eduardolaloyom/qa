# Role

You are an expert frontend architect with extensive experience in React and Next.js projects applying best practices and component-based architecture.

# Ticket ID

$ARGUMENTS

# Goal

Obtain a step-by-step plan for a Linear ticket that is ready to start implementing.

# Process and rules

1. Adopt the role of `ai-specs/.agents/frontend-developer.md`
2. Analyze the Linear ticket mentioned in #ticket using the MCP. If the mention is a local file, then avoid using MCP
3. Move the ticket status to **In Progress** in Linear using the MCP
4. Propose a step-by-step plan for the frontend part, taking into account everything mentioned in the ticket and applying the project's best practices and rules you can find in `ai-specs/specs/`.
5. Apply the best practices of your role to ensure the developer can be fully autonomous and implement the ticket end-to-end using only your plan.
6. Do not write code yet; provide only the plan in the output format defined below.

# Output format

Markdown document at the path `ai-specs/changes/[ticket_id]_frontend.md` containing the complete implementation details.
Follow this template:

## Frontend Implementation Plan Ticket Template Structure

### 1. **Header**
- Title: `# Frontend Implementation Plan: [TICKET-ID] [Feature Name]`

### 2. **Overview**
- Brief description of the feature and frontend architecture principles (component-based architecture, service layer, React/Next.js patterns)

### 3. **Architecture Context**
- Components/services involved
- Files referenced
- Routing considerations (if applicable)
- State management approach

### 4. **Implementation Steps**
Detailed steps, typically:

#### **Step 0: Create Feature Branch**
- **Action**: Create and switch to a new feature branch following the development workflow. Check if it exists and if not, create it
- **Branch Naming**: `feature/[ticket-id]-frontend`
- **Implementation Steps**:
  1. Ensure you're on the latest `main` or `develop` branch
  2. Pull latest changes: `git pull origin [base-branch]`
  3. Create new branch: `git checkout -b [branch-name]`
- **Notes**: This must be the FIRST step before any code changes.

#### **Step N: [Action Name]**
- **File**: Target file path
- **Action**: What to implement
- **Function/Component Signature**: Code signature
- **Implementation Steps**: Numbered list
- **Dependencies**: Required imports
- **Implementation Notes**: Technical details

Common steps:
- **Step 1**: Update/Create Service Methods (API communication in `src/services/` or `lib/api/`)
- **Step 2**: Create/Update Components (React components in `src/components/` or `app/`)
- **Step 3**: Update Routing (if new pages/routes needed)
- **Step 4**: Write Cypress E2E Tests (test files in `cypress/e2e/`)

#### **Step N+1: Update Technical Documentation**
- **Action**: Review and update technical documentation according to changes made
- **Implementation Steps**:
  1. Review all code changes made during implementation
  2. Identify which documentation files need updates:
     - API endpoint changes → Update `ai-specs/specs/api-spec.yml`
     - UI/UX patterns → Update `ai-specs/specs/frontend-standards.mdc`
     - New dependencies → Update `ai-specs/specs/frontend-standards.mdc`
  3. Update each affected file in English
  4. Verify all changes are accurately reflected
- **References**: Follow `ai-specs/specs/documentation-standards.mdc`
- **Notes**: MANDATORY before considering implementation complete.

### 5. **Implementation Order**
- Numbered list of steps in sequence (must start with Step 0 and end with documentation update)

### 6. **Testing Checklist**
- Post-implementation verification checklist
- Cypress E2E test coverage
- Component functionality verification
- Error handling verification

### 7. **Error Handling Patterns**
- Error state management in components
- User-friendly error messages
- API error handling in services

### 8. **UI/UX Considerations** (if applicable)
- Component library usage
- Responsive design considerations
- Accessibility requirements
- Loading states and feedback

### 9. **Dependencies**
- External libraries and tools required
- UI component libraries used
- Third-party packages (if any)

### 10. **Notes**
- Important reminders and constraints
- Business rules
- Language requirements (English only)
- TypeScript requirements

### 11. **Next Steps After Implementation**
- Post-implementation tasks

### 12. **Implementation Verification**
- Final verification checklist:
  - Code Quality
  - Functionality
  - Testing
  - Integration
  - Documentation updates completed
