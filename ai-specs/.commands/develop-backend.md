Implement the backend feature described in the plan file: $ARGUMENTS

Follow these steps strictly in order:

1. Read the implementation plan file provided in $ARGUMENTS thoroughly before starting
2. If no plan file is provided, first run `/plan-backend-ticket` to generate one
3. Move to the feature branch specified in Step 0 of the plan (create it if it doesn't exist)
4. Implement each step of the plan in order, following TDD:
   - Write failing unit tests FIRST for the step
   - Implement the code to make tests pass
   - Refactor if needed
5. After each step, run the test suite to verify it passes before proceeding
6. Ensure code passes linting and TypeScript type checking with no errors
7. Follow all standards in `ai-specs/specs/backend-standards.mdc`
8. Update technical documentation as specified in the last step of the plan
9. Run `/ship-it` to stage, commit, push, and create the PR
10. Move the ticket status to **In Review** in Linear using the MCP

TDD Cycle for each step:
- RED: Write a failing test that describes the expected behavior
- GREEN: Write the minimum code to make the test pass
- REFACTOR: Clean up the code while keeping tests green
