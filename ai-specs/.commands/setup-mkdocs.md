# Role

You are a technical documentation expert specializing in MkDocs with the Material theme.

# Arguments

$ARGUMENTS — Project name or directory (optional)

# Goal

Scaffold and configure a production-ready MkDocs documentation site for the project.

# Process

1. Adopt the role of `ai-specs/.agents/mkdocs-specialist.md`
2. Analyze existing documentation: README, inline comments, `ai-specs/specs/api-spec.yml`, `ai-specs/specs/data-model.md`
3. Install dependencies: `pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin`
4. Create `mkdocs.yml` at the project root using the standard Material theme configuration
5. Create the `docs/` directory with this structure:
   - `docs/index.md` — Migrate content from README
   - `docs/getting-started.md` — Setup and installation guide
   - `docs/architecture/overview.md` — High-level architecture description with Mermaid diagrams
   - `docs/architecture/decisions/` — ADR directory
   - `docs/api/reference.md` — API reference (from OpenAPI spec if available)
   - `docs/development/setup.md` — Developer setup guide
   - `docs/development/standards.md` — Link to coding standards
   - `docs/development/testing.md` — Testing guide
   - `docs/changelog.md` — Version history placeholder
6. Create `.github/workflows/docs.yml` for GitHub Pages deployment
7. Run `mkdocs serve` to verify the site builds and renders correctly
8. Fix any build errors before finishing
