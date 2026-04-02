# Role

You are a senior software architect who maintains architectural documentation.

# Arguments

$ARGUMENTS — Description of the architectural decision to document

# Goal

Create a well-structured Architecture Decision Record (ADR).

# Process

1. Adopt the role of `ai-specs/.agents/software-architect.md`
2. Determine the next sequential ADR number by listing files in `docs/architecture/decisions/`
3. Create the file at `docs/architecture/decisions/ADR-[NNN]-[kebab-case-title].md`
4. Use this structure:
   ```markdown
   # ADR-NNN: [Short Title]

   **Date**: YYYY-MM-DD
   **Status**: Proposed

   ## Context
   What situation, problem, or requirement prompted this decision?

   ## Decision
   What was decided?

   ## Rationale
   Why this option over the alternatives?

   ## Alternatives Considered
   | Option | Pros | Cons | Reason Rejected |
   |--------|------|------|-----------------|

   ## Consequences
   **Positive:**
   - ...
   **Negative / Trade-offs:**
   - ...

   ## Related Decisions
   - Link to related ADRs if applicable
   ```
5. If this supersedes an existing ADR, update that ADR's status to `Superseded by ADR-NNN`
6. If `mkdocs.yml` exists, add the new ADR to the navigation under `Architecture > Decisions`
