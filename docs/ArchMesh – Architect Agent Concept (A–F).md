ArchMesh – Architect Agent Concept (A–F)

Version: 1.0 • Scope: Inputs, Persona, Knowledge, Reasoning Workflow, Outputs, Agentic Behavior/Safety
Owner: ArchitectureAgent • Applies to: greenfield & brownfield modes

⸻

A. Inputs & Context Building

Goal: ingest heterogeneous sources (requirements, PPTs, repos, wikis) and normalize them into a project context package (PCP) used by retrieval and the architect persona.

A1. Minimum Viable Input
	•	L0: 1× requirements doc → baseline draft architecture.
	•	L1: + platform/guardrails doc → constraint-aware draft.
	•	L2: + 1 repo (code or IaC) → pattern extraction, concrete ADRs.

On ambiguity → trigger a clarification micro-interview (auto-Q templates).

A2. Source Connectors
	•	File drop (PDF/DOCX/MD/PPTX, ZIP)
	•	Repos: GitHub/GitLab/Bitbucket (sparse checkout, monorepo filters)
	•	Docs: Confluence/SharePoint/Google Drive
	•	Trackers: Jira/Azure Boards
	•	Object stores: S3/Azure Blob/GCS

Sync: initial full scan → incremental via webhooks or etags.
Change detection: content hash + lastModified; chunk-level re-index.

A3. Parsing & Normalization

RawSource → TypeDetect → Parser → Normalizer → Chunker → Embedder → Indexer

	•	Type-aware parsers (docs, PPTX, code/AST, IaC, tables, limited OCR)
	•	Common schema: title, body, struct, figures, provenance (repo, path, commit, page/slide)
	•	Chunking profiles: docs (700–1200 tok, 10–15% overlap), code (≤400 tok), slides (per-slide)

A4. Project Context Package (PCP)

A single JSON capturing project constraints, inputs, personas, and retrieval knobs (embedding model, hybrid weights). Stored and versioned beside the indexes.

A5. Retrieval Stores
	•	Vector (multilingual embeddings + rich metadata)
	•	Lexical (BM25/FTS for IDs/acronyms)
	•	Graph (optional): nodes Requirement|Decision|Service|Repo|ADR|Rule with edges satisfies|depends_on|violates|implements|duplicates
	•	Hybrid query plan: persona-aware expansion → BM25 ∪ Vector → RRF merge → graph hop → cross-encoder rerank (provenance-aware)

A6. Repo Intelligence
	•	Facts: language mix, deps, service map (docker/k8s), data stores, IaC resources.
	•	Heuristics: entrypoints, cross-cutting concerns (auth/logging/metrics), implicit NFRs.
	•	Outputs: per-service cards + candidate ADRs.

A7. Auto-Q Templates
	•	SLOs (tps/latency), data volume/day, regions/tenants, data residency, tech guardrails, reuse vs. new services, PII categories.

A8. Safety & Scope
	•	Per-project crawl scope (allow/deny), PII/secret detectors, quarantine/redaction, rate-limits, max bytes/run.
	•	Multilingual ingest (DE/EN/NL) with lang on chunks and glossary for org acronyms.

Integration pointers (code):
	•	Map PCP to ArchitectureAgent.execute() constraints and preferences.
	•	Use kb_service for brownfield lookups (_get_brownfield_context).

⸻

B. Architect Persona Definition

Goal: make the “software architect” behavior reproducible and customizable.

B1. Persona Schema (JSON)

{
  "id": "enterprise-architect-azure-opinionated",
  "domain_focus": ["cloud-native", "data-platform"],
  "tech_bias": {
    "cloud": ["Azure", "AKS", "Event Hubs", "APIM"],
    "data": ["PostgreSQL", "Redis", "Elasticsearch"],
    "messaging": ["Kafka", "RabbitMQ"]
  },
  "decision_heuristics": {
    "optimize_for": ["maintainability", "developer_experience"],
    "tradeoff_policy": {
      "latency_p99_ms": 100,
      "cost_ceiling": "medium",
      "reuse_first": true
    }
  },
  "communication_style": "concise-technical-with-citations",
  "guardrails": ["reuse existing platform services", "backwards compatibility"],
  "few_shots": ["ADR examples", "good/bad patterns"],
  "org_policies": ["GDPR", "ISO27001"],
  "learning_mode": "fixed|evolving"
}

B2. Training Sources
	•	Past repos/ADRs, platform docs, review board feedback, confluence spaces.
	•	Converted into persona memories (small distilled snippets) + few-shot exemplars.

B3. Runtime Binding
	•	Persona → modifies system prompt (see get_system_prompt), retrieval expansion, rerank rubric, and alternative weighting.

B4. Evolution
	•	If learning_mode=evolving: capture accepted decisions → append to persona memory (with curator review).

⸻

C. Knowledge Integration (RAG / Fine-tune / Graph)
	•	Default: Hybrid RAG (vector + BM25 + optional graph).
	•	Per-doc pipelines:
	•	Docs/PPTX: section/slide chunking + headings.
	•	Code: AST/dep index + embeddings over symbols.
	•	IaC: resource graph + policy tags.
	•	Result packing: provenance-rich context windows, framed by persona constraints.
	•	Optional domain-adapter or LoRA for local models (DeepSeek/Llama) to encode platform jargon.

Brownfield hooks: kb_service.search_similar_architectures, get_service_dependencies, get_context_for_new_feature.

⸻

D. Reasoning Workflow (Multi-Agent)

RequirementAnalyst  →  SystemArchitect  →  Reviewer/Critic  →  Planner
       |                     |                   |                |
   (gap check)         (design & ADRs)     (tradeoff/risk)   (phases/OKRs)

	•	RequirementAnalyst: validates inputs, runs clarification micro-interview, produces structured reqs + NFRs.
	•	SystemArchitect (this agent): builds JSON design, C4 description, tech stack, alternatives.
	•	Reviewer/Critic: adversarial check against NFRs, org guardrails, cost, and latency SLO; suggests corrections.
	•	Planner: converts accepted design to implementation plan (phases, risks, success metrics, Jira epics).

Reflection loop: iterate until risk/NFR gates pass (or user stops).

Latency-aware tips: async I/O; cache hot reads; co-locate stateful services with data stores; idempotent messaging; circuit breakers.

⸻

E. Outputs & Formats
	•	Primary: Structured JSON (already produced by ArchitectureAgent), including:
	•	architecture_overview, components, technology_stack, alternatives,
	•	implementation_plan, c4_diagram_description, c4_diagram_context (Mermaid).
	•	Artifacts:
	•	PlantUML / Mermaid C4 Context/Container,
	•	ADRs (Markdown template),
	•	Draw.io JSON (optional),
	•	PDF/Markdown Concept Paper (exported from JSON).
	•	Citations: include provenance for every claim (source path + commit/slide/page).
	•	Versioning: store each run as a concept version with diff vs. previous (hash on key sections).

UI hooks: “Open in Confluence”, “Create Jira Epics”, “Export ADRs”.

⸻

F. Agentic Behavior, Safety & Security

F1. Autonomy Levels
	•	Assist: requires confirmation for each decision.
	•	Suggest: proposes alternatives, auto-fills ADR drafts.
	•	Execute: (opt-in) opens PRs for boilerplate repos/IaC scaffolds.

F2. Quality Gates
	•	Requirements coverage, NFR checklist (perf/security/reliability/operability), risk table, platform guardrail compliance, cost envelope.

F3. Safety & Privacy
	•	Local-first inference (DeepSeek/Llama) for sensitive docs; external LLMs only with redaction & tenant-scoped anonymization.
	•	PII/secret detectors with quarantine and immutable audit logs.
	•	Tenant & project ACLs on all chunks; signed provenance on outputs.

F4. Observability
	•	Telemetry: doc/repo coverage, retrieval hit rates, self-critique deltas, design quality score.
	•	Drift detection: guardrail changes or SLO edits trigger re-review of affected ADRs.

⸻

Implementation Hooks (this repo)
	•	ArchitectureAgent:
	•	Accepts constraints, preferences, domain, mode; add persona_id (string) and pcp (dict) for persona-aware retrieval.
	•	_validate_and_enhance_architecture() stamps quality score and preserves brownfield fields.
	•	Expose this MD in UI via an accessor (see below).
	•	Next tasks (low effort):
	1.	Add persona_id to execute() input and to prompt builders.
	2.	Add pcp loader/validator module and wire to kb retrieval.
	3.	Add ADR Markdown generator & Confluence export.
	4.	Add “Clarification Micro-Interview” prompt bundle and UI.

⸻

ADR Template (drop into docs/adr/0001-record-architecture-decision.md)

# ADR-0001: <Decision Title>
- Date: <YYYY-MM-DD>
- Status: Proposed|Accepted|Superseded
- Context: <short>
- Decision: <what we choose>
- Consequences: <trade-offs>
- Alternatives: <list>
- References: <links to PCP chunks / provenance>


⸻

Optional: tiny accessor (UI can show/export this doc)

Add at the bottom of backend/app/agents/architecture_agent.py:

# === Embedded concept documentation: accessor ===
def get_concept_documentation() -> str:
    """
    Returns the Architect Agent concept (A–F) Markdown from
    docs/architect-agent-concept.md for display/export in the UI.
    """
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    # move from /backend/app/agents → repo root and into /docs
    repo_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    doc_path = os.path.join(repo_root, "docs", "architect-agent-concept.md")
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        # Fallback short note if the doc is moved or missing
        return "# ArchMesh – Architect Agent Concept\n\nDocumentation file not found at: " + doc_path


⸻

Why this plugs in smoothly
	•	Mirrors your agent’s current responsibilities (greenfield/brownfield, RAG, C4, alternatives, implementation plan).
	•	Introduces persona as a first-class input without breaking existing prompts (just add persona_id).
	•	Keeps all safety, provenance, and quality gates explicit so outputs are auditable in client contexts.

If you want, I can also provide:
	•	a minimal Pydantic schema for PCP & Persona, and
	•	a CLI ingest script stub wired to your kb_service.