<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (Initial ratification)
- Principles created: 7 core principles established
- Sections added: Core Principles, Quality Standards, Development Workflow, Governance
- Templates status: ✅ plan-template.md aligned, ✅ spec-template.md aligned, ✅ tasks-template.md aligned
- Follow-up: None required - all placeholders resolved
-->

# PBLCourseAgent Constitution

## Core Principles

### I. Linus-Style Code Review Philosophy
**MANDATORY**: All code must embody "good taste" - eliminating special cases and boundary conditions through elegant data structure design rather than conditional logic patches.

**Rules**:
- Functions MUST NOT exceed 3 levels of indentation; violations require architectural redesign
- Special cases MUST be eliminated by refactoring data structures, not by adding conditionals
- "Never break userspace" - backward compatibility is non-negotiable; any change breaking existing functionality is a critical bug
- Simplicity trumps theoretical perfection; reject complexity that doesn't solve real production problems

**Rationale**: Following Linus Torvalds' proven 30-year Linux kernel methodology ensures code maintainability and prevents technical debt accumulation from day one.

### II. Test-First Development (NON-NEGOTIABLE)
**MANDATORY**: Red-Green-Refactor cycle strictly enforced for all feature development.

**Rules**:
- Tests MUST be written BEFORE implementation code
- Tests MUST fail initially (Red phase verified)
- Implementation proceeds only after test failure confirmation
- >80% test coverage required for all production code
- Golden Standard case validation mandatory for AI Agent outputs

**Rationale**: Test-first development catches design flaws early and ensures every feature has verifiable acceptance criteria before resource investment.

### III. Transparent Error Handling
**MANDATORY**: System failures must be explicit and informative; degraded fallback responses are prohibited.

**Rules**:
- API responses MUST return `success: false` with detailed error messages on failure
- NEVER mask errors with low-quality placeholder content
- Frontend MUST display error states clearly with actionable details for users/developers
- Service quality is binary: high-quality success OR explicit failure (no middle ground)

**Rationale**: Transparent error handling enables rapid debugging and prevents user confusion from false success indicators, maintaining system trustworthiness.

### IV. Prompt as Code (PHR Standard)
**MANDATORY**: All AI Agent prompts are versioned artifacts stored in Prompt History Record (PHR) files.

**Rules**:
- Every prompt MUST have a PHR file in `backend/app/prompts/phr/{agent_name}_v{version}.md`
- Prompt modifications MUST create new versions; NEVER edit existing versions
- PHR MUST include: Meta info, System/User prompts, Guidelines, Change Log, Testing Notes, Performance Metrics
- A/B testing MUST be documented with variant files and results recorded
- Agent code MUST reference specific PHR version in docstrings

**Rationale**: Prompts are core business logic requiring the same rigor as code - versioning enables rollback, A/B testing, and performance comparison across iterations.

### V. Agent-Driven Architecture
**MANDATORY**: Educational content generation follows a sequential three-agent workflow with defined contracts.

**Rules**:
- Agent 1 (Project Foundation) → Agent 2 (Assessment Framework) → Agent 3 (Learning Blueprint)
- Each agent MUST have <20-40s response time per PRD specifications
- Total workflow MUST complete in <90 seconds
- Agent outputs MUST achieve ≥80% quality match against Golden Standard case
- Inter-agent contracts (input/output schemas) are immutable without version bumps

**Rationale**: Specialized agents with clear responsibilities prevent monolithic complexity and enable parallel development/testing of educational content generation logic.

### VI. UbD Framework Fidelity
**MANDATORY**: All PBL course designs adhere to Understanding by Design (UbD) principles.

**Rules**:
- Backward design MUST be followed: Identify desired results → Determine evidence → Plan learning experiences
- Essential Questions and Enduring Understandings MUST be explicit in every course
- Assessment framework MUST precede detailed activity planning
- Four-tier rubrics (Novice → Apprentice → Craftsperson → Master) required for all projects

**Rationale**: UbD framework ensures pedagogical rigor and prevents activity-focused design that lacks clear learning outcomes.

### VII. Simplicity and Pragmatism
**MANDATORY**: Choose the simplest solution that solves the actual problem; reject speculative complexity.

**Rules**:
- New dependencies MUST be justified against simpler alternatives
- "YAGNI" (You Aren't Gonna Need It) principle enforced - features built only when needed
- Before adding abstraction layers, ask: "Is this solving a real problem or an imagined one?"
- If implementation requires more than 3 concepts to explain, redesign for simplicity

**Rationale**: Premature optimization and over-engineering create maintenance burden; start simple and evolve based on real production needs.

## Quality Standards

### Code Quality Gates
**MANDATORY before merge**:
- All tests passing (unit + integration + golden standard)
- Black, isort, flake8 checks passing (Python)
- ESLint + Prettier checks passing (TypeScript)
- >80% test coverage maintained
- No regression in AI output quality scores
- Performance benchmarks met (<90s total workflow time)

### AI Output Quality
**MANDATORY validation**:
- Golden Standard comparison ≥80% semantic similarity
- Rubric completeness check (all criteria present)
- UbD elements validation (Essential Questions, Understandings, Assessment Evidence)
- Age-appropriate language verification

## Development Workflow

### Git Commit Standards
- `feat:` New features or capabilities
- `fix:` Bug fixes
- `docs:` Documentation updates
- `test:` Test additions or modifications
- `refactor:` Code restructuring without behavior change
- `perf:` Performance optimizations

### Environment Management
**MANDATORY**: Use `uv` for Python dependency management to ensure reproducible environments.

**Rules**:
- Virtual environments MUST be created via `uv sync`
- New dependencies added via `uv add <package>` (production) or `uv add --dev <package>` (development)
- `.env` files MUST NOT be committed; use `.env.example` templates
- Environment variables prefixed with `PBL_` to avoid naming conflicts

### Review Process
**MANDATORY for all changes**:
1. Self-review using Linus-style checklist (special cases? >3 indents? breaks compatibility?)
2. Tests written and failing before implementation
3. Implementation with commit-per-logical-unit
4. Golden Standard validation if AI Agent modified
5. Peer review focusing on data structures, not cosmetics

## Governance

### Amendment Procedure
**REQUIRED for Constitution changes**:
1. Propose change with rationale and impact analysis
2. Update `CONSTITUTION_VERSION` per semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals/redefinitions
   - **MINOR**: New principles added or material expansions
   - **PATCH**: Clarifications, wording improvements, typo fixes
3. Sync dependent templates (plan, spec, tasks) to reflect changes
4. Record in Sync Impact Report (HTML comment at file top)
5. Update `LAST_AMENDED_DATE` to current date

### Compliance Review
**MANDATORY checkpoints**:
- Constitution Check section in `plan.md` for every feature
- Weekly adherence audit by team lead
- Post-release retrospective evaluating principle effectiveness
- Quarterly constitution review for needed amendments

### Versioning Policy
**CURRENT**: Constitution supersedes ad-hoc practices; conflicts default to Constitution rules unless explicitly documented as experimental deviations with approval.

**Runtime Development Guidance**: For detailed development practices and Linus-style communication protocols, reference `CLAUDE.md` (agent-specific guidance file).

---

**Version**: 1.0.0 | **Ratified**: 2025-10-20 | **Last Amended**: 2025-10-20
