# Using AnythingLLM with Coding Agents for Large Brownfield Projects

This document describes **typical, production-proven architectures** for
using **AnythingLLM** together with coding agents such as **Claude
Code**, **Cursor**, or **Gemini CLI** for **brownfield projects**
involving enhancements, refactoring, and deep code understanding.

Nothing has been summarized or removed. All architectural details are
preserved.

------------------------------------------------------------------------

## Why AnythingLLM Is Relevant for Brownfield Coding

AnythingLLM is **not** intended to replace IDE-based coding agents.
Instead, it fills a critical gap that brownfield projects suffer from:

-   missing or fragmented documentation
-   historical decisions not reflected in code
-   tribal knowledge scattered across docs, tickets, PRs, and runbooks
-   the need for long-lived "project memory"

In these architectures: - **Claude Code / Cursor / Gemini CLI** = *make
changes* - **AnythingLLM** = *understand the system and its history* -
**Code index services** = *precise symbol-level navigation* - **Optional
execution tools** = *safe validation of changes*

The key principle is **hybrid retrieval**, not a single tool doing
everything.

------------------------------------------------------------------------

## Architecture 1 --- AnythingLLM as Shared RAG Hub + Context Packs

**Best when** - You want minimal moving parts - The agent mostly needs
high-level understanding plus targeted excerpts - Early brownfield
exploration and onboarding

### Flow

1.  Developer prompts Claude Code / Cursor / Gemini CLI
2.  A wrapper script (or manual step) queries AnythingLLM for:
    -   system overview
    -   relevant subsystems
    -   coding conventions
    -   known pitfalls
3.  The wrapper builds a **context pack** (Markdown bundle)
4.  The coding agent uses this context to plan and apply changes

### Components

**AnythingLLM Server** - Self-hosted - Workspaces per: - repository -
subsystem - team or product - Ingested content: - `/docs` - ADRs -
runbooks - onboarding guides - PR summaries - selected code directories
(not necessarily the whole repo) - manually curated "brownfield notes"

**Optional Local Helpers** - `ripgrep` for exact text search - simple
repo-map generator: - key modules - entry points - ownership hints

### Strengths

-   Extremely fast to stand up
-   Excellent for "what is this thing?" questions
-   Reduces agent confusion in legacy systems

### Limitations

-   Not precise for:
    -   "find all references"
    -   "go to definition"
-   Needs a code indexer for deeper refactoring

------------------------------------------------------------------------

## Architecture 2 --- AnythingLLM + Dedicated Code Indexer (Recommended Baseline)

**Best when** - You need both conceptual understanding and surgical
precision - Brownfield refactoring and enhancements are regular tasks

### Flow

Claude Code / Cursor / Gemini CLI\
→ tool calls to: - **AnythingLLM** (docs, architecture, history) -
**Code Index Service** (symbols, refs, exact search)

### Components

#### AnythingLLM (RAG Hub)

-   Primary role:
    -   documentation RAG
    -   architectural explanations
    -   historical decisions
-   Content types:
    -   ADRs
    -   runbooks
    -   design docs
    -   onboarding material
    -   selected "conceptual" code excerpts

#### Code Index Service (Precision Layer)

-   Language-aware parsing (tree-sitter)
-   Keyword search (ripgrep / BM25)
-   Optional symbol DB (ctags / LSP-derived)
-   Typical APIs:
    -   `search_code(query)`
    -   `get_def(symbol)`
    -   `get_refs(symbol)`
    -   `open_file(path, range)`
    -   `list_entry_points()`

#### Agent Integration

-   Preferred: MCP server exposing both tool sets
-   Alternative: wrapper script that:
    1.  queries AnythingLLM
    2.  queries code indexer
    3.  injects results into the agent prompt

### Typical Agent Behavior

1.  Ask AnythingLLM which subsystem is relevant
2.  Use code indexer to locate exact definitions and references
3.  Open concrete files
4.  Apply refactor or enhancement

### Why This Works

-   AnythingLLM provides the **map**
-   Code indexer provides the **coordinates**
-   The agent avoids random exploration

------------------------------------------------------------------------

## Architecture 3 --- AnythingLLM as OpenAI-Compatible Proxy with Automatic RAG Injection

**Best when** - You want consistent behavior across many developers -
You want retrieval "always on"

### Flow

Cursor / Claude Code / Gemini CLI\
→ points to a **proxy endpoint**\
→ proxy: 1. queries AnythingLLM 2. optionally queries code indexer 3.
injects context automatically 4. forwards request to Claude/Gemini 5.
returns response

### Components

-   AnythingLLM (RAG backend)
-   Optional code index service
-   Proxy/Gateway service:
    -   token budget enforcement
    -   max-chunk limits
    -   path allow/deny rules
    -   ACL enforcement
    -   secret redaction
    -   audit logs

### Advantages

-   Uniform agent behavior
-   Centralized policy enforcement
-   Easier governance

### Tradeoffs

-   Higher engineering effort
-   Requires transparency tooling so devs can see injected context

------------------------------------------------------------------------

## Architecture 4 --- AnythingLLM + Gated Execution for Safe Refactoring

**Best when** - The agent should perform multi-step refactors - Safety
and validation matter

### Flow

Claude Code / Cursor / Gemini CLI (agent)\
→ retrieval: - AnythingLLM (docs, history) - code indexer (defs, refs) →
edit: - agent proposes patch → validate: - gated execution tools →
iterate until green

### Components

-   AnythingLLM workspace(s)
-   Code index service
-   Tool Router with strict allowlists:
    -   `run_tests(target)`
    -   `run_build()`
    -   `run_lint()`
    -   `apply_patch(diff)` (repo-scoped, size-limited)
    -   `open_file`
    -   `grep`
-   Policy layer:
    -   command allowlists
    -   resource and time limits
    -   network isolation or allowlists
    -   secret isolation
-   Optional CI integration:
    -   branch creation
    -   PR creation
    -   pipeline execution
    -   result feedback

### Why AnythingLLM Matters Here

Hidden invariants and historical context often live outside code.
AnythingLLM captures and retrieves exactly that information.

------------------------------------------------------------------------

## Architecture 5 --- Two-Speed Knowledge Model

**Best when** - You want long-term knowledge without polluting RAG with
noise

### Long-Lived Knowledge (AnythingLLM)

-   architecture documentation
-   ADRs
-   coding standards
-   "how we do X here" guides
-   refactor playbooks
-   module ownership
-   curated hotspot summaries

### Ephemeral Knowledge (Per Agent Run)

-   exact files opened
-   symbol reference lists
-   diffs and patches
-   test/build logs
-   session summaries

### Flow

1.  Agent reads baseline context from AnythingLLM
2.  Agent performs refactor using code indexer
3.  After merge:
    -   write back a concise "what changed and why" note to AnythingLLM

This prevents the RAG corpus from becoming a junk drawer.

------------------------------------------------------------------------

## Practical Workspace Structure in AnythingLLM

-   Workspace per:
    -   repository
    -   major subsystem
-   One cross-cutting workspace for:
    -   platform standards
    -   infrastructure conventions

### Suggested Collections / Tags

-   `adr/`
-   `runbook/`
-   `onboarding/`
-   `patterns/`
-   `postmortems/`
-   `api-contracts/`

### Code Ingestion Guidance

-   Prefer:
    -   stable entry points
    -   public interfaces
    -   boundary modules
-   Avoid:
    -   dumping entire monorepos unless chunking and budgets are well
        controlled

------------------------------------------------------------------------

## Minimum Tool Contract for Coding Agents

### From AnythingLLM

-   `rag_query(question, workspace, filters)` → cited passages/snippets
-   `list_workspaces()` / `list_collections()` (optional)

### From Code Indexer

-   `search_code(query)`
-   `get_def(symbol)`
-   `get_refs(symbol)`
-   `open_file(path, start, end)`

### Optional Execution Tools

-   `run_tests`
-   `run_build`
-   `run_lint`
-   `apply_patch`

------------------------------------------------------------------------

## Architecture Selection Guidance

-   Fastest start: **Architecture 1**
-   Best practical baseline: **Architecture 2**
-   Org-wide consistency: **Architecture 3**
-   Safe large refactors: **Architecture 4**
-   Long-term maintainability: **Architecture 5** (combined with 2 or 4)

------------------------------------------------------------------------

## Final Recommendation

For brownfield enhancements, refactoring, and understanding: - Start
with **Architecture 2** - Add **Architecture 4** when automation and
safety matter - Apply **Architecture 5** to keep knowledge clean over
time

AnythingLLM becomes the system's **long-term memory and explanation
layer**, while coding agents focus on **changing code safely and
precisely**.
