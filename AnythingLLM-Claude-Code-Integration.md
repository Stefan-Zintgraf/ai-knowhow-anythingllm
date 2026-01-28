# Using AnythingLLM as RAG Provider for Claude Code

This guide explains how to integrate AnythingLLM as a RAG (Retrieval-Augmented Generation) provider for Claude Code, enabling Claude to access your project's documentation, architecture decisions, and codebase knowledge.

---

## Overview

AnythingLLM serves as your **knowledge hub** that Claude Code can query to understand:
- Project architecture and design decisions
- Historical context and ADRs (Architecture Decision Records)
- Coding conventions and patterns
- Runbooks and operational procedures
- Selected code excerpts and interfaces

**Key Principle:** AnythingLLM provides the **map** (conceptual understanding), while Claude Code handles the **execution** (code changes).

---

## Integration Approaches

### Approach 1: Manual Context Packs (Simplest - Recommended to Start)

**Best for:** Quick setup, individual developers, occasional use

#### How It Works

1. Query AnythingLLM manually for relevant context
2. Copy the response as a context pack
3. Paste into Claude Code conversation

#### Step-by-Step

**Step 1: Set Up AnythingLLM Workspace**

1. Install and configure AnythingLLM (see `BasicArchitecture/AnythingLLM-LocalLLM-Tutorial.md`)
2. Create a workspace for your project (e.g., "MyProject-Architecture")
3. Upload relevant documents:
   - Architecture docs (`/docs`, ADRs)
   - Design documents
   - Onboarding guides
   - Runbooks
   - Selected code files (entry points, interfaces)

**Step 2: Query AnythingLLM Before Coding**

Before starting a task in Claude Code, query AnythingLLM:

```
I need to refactor the memory allocation in the device driver module.
What are the key considerations, historical decisions, and known pitfalls?
```

**Step 3: Create Context Pack for Claude Code**

Copy AnythingLLM's response and format it as a context pack:

```markdown
## Project Context from Knowledge Base

[Paste AnythingLLM response here]

## Task
Refactor the memory allocation in src/drivers/device.cpp to use 
smart pointers instead of raw pointers.
```

**Step 4: Use in Claude Code**

Paste the context pack into your Claude Code conversation. Claude will use this context to make informed decisions.

#### Advantages

- ✅ Zero technical setup
- ✅ Full control over context
- ✅ Works immediately
- ✅ No API dependencies

#### Limitations

- ⚠️ Manual process (not automated)
- ⚠️ Requires remembering to query AnythingLLM first

---

### Approach 2: AnythingLLM API Integration (Automated)

**Best for:** Regular use, automation, scripting

#### Prerequisites

- AnythingLLM running (Desktop or Docker)
- API access enabled (default in multi-user mode, may need API key)

#### Step 1: Enable API Access

**For AnythingLLM Desktop:**
- API is typically available at `http://localhost:3001/api` (check with `http://localhost:3001/api/ping`)
- Check if API key is required in Settings → Security

**For AnythingLLM Docker:**
- API available at `http://your-server:3001/api`
- May require authentication token

#### Step 2: Query AnythingLLM API

AnythingLLM exposes REST API endpoints. Here's how to query a workspace:

**Get Workspace List:**
```bash
curl -X GET "http://localhost:3001/api/v1/workspaces" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Query a Workspace (RAG Query):**
```bash
curl -X POST "http://localhost:3001/api/v1/admin/workspace/{workspaceId}/chat" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the memory management strategy in the device driver subsystem?",
    "mode": "query"
  }'
```

#### Step 3: Create a Wrapper Script

Create a script that queries AnythingLLM and formats the response for Claude Code:

**PowerShell Script (`get-context.ps1`):**
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Question,
    
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceId,
    
    [string]$ApiKey = "",
    [string]$AnythingLLMUrl = "http://localhost:3001"
)

$headers = @{
    "Content-Type" = "application/json"
}

if ($ApiKey) {
    $headers["Authorization"] = "Bearer $ApiKey"
}

$body = @{
    message = $Question
    mode = "query"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$AnythingLLMUrl/api/workspace/$WorkspaceId/chat" `
    -Method Post `
    -Headers $headers `
    -Body $body

# Format as context pack
Write-Host "## Project Context from AnythingLLM" -ForegroundColor Green
Write-Host ""
Write-Host $response.response
Write-Host ""
Write-Host "---" -ForegroundColor Gray
Write-Host "Copy the above context and paste it into Claude Code"
```

**Usage:**
```powershell
.\get-context.ps1 -Question "What are the key considerations for refactoring memory allocation?" -WorkspaceId "workspace-123"
```

**Python Script (`get_context.py`):**
```python
#!/usr/bin/env python3
import requests
import sys
import json

def query_anythingllm(question, workspace_id, api_key=None, base_url="http://localhost:3001"):
    """Query AnythingLLM workspace and return formatted context."""
    
    url = f"{base_url}/api/workspace/{workspace_id}/chat"
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "message": question,
        "mode": "query"  # Use query mode to only use document context
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error querying AnythingLLM: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python get_context.py <question> <workspace_id> [api_key]")
        sys.exit(1)
    
    question = sys.argv[1]
    workspace_id = sys.argv[2]
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    
    context = query_anythingllm(question, workspace_id, api_key)
    
    if context:
        print("## Project Context from AnythingLLM\n")
        print(context)
        print("\n---\nCopy the above context and paste it into Claude Code")
    else:
        sys.exit(1)
```

**Usage:**
```bash
python get_context.py "What is the memory management strategy?" workspace-123
```

#### Step 4: Integrate with Claude Code Workflow

**Option A: Pre-query Script**
Before starting a coding session, run the script to get context:

```powershell
# Get context about the task
$context = .\get-context.ps1 -Question "Memory management patterns in device drivers" -WorkspaceId "my-project"

# Copy to clipboard (Windows)
$context | Set-Clipboard

# Then paste into Claude Code conversation
```

**Option B: Claude Code Custom Command**
If Claude Code supports custom commands or extensions, you could create a command that:
1. Takes your current question/task
2. Queries AnythingLLM
3. Injects the context automatically

---

### Approach 3: MCP Server Integration (Advanced)

**Best for:** Seamless integration, team-wide consistency

#### What is MCP?

Model Context Protocol (MCP) is a standard protocol for connecting AI assistants to external data sources and tools. An MCP server can expose AnythingLLM's RAG capabilities as tools that Claude Code can call directly.

#### Setup

**Option A: Use Existing MCP Server**

There's a community MCP server for AnythingLLM:
- Repository: `raqueljezweb/anythingllm-mcp-server`
- Implements MCP protocol to expose AnythingLLM workspaces as tools

**Installation:**
```bash
# Clone or install the MCP server
# Configure it to point to your AnythingLLM instance
# Connect Claude Code to the MCP server
```

**Option B: Build Custom MCP Server**

Create an MCP server that exposes these tools:

```python
# Example MCP server structure
tools = [
    {
        "name": "rag_query",
        "description": "Query AnythingLLM workspace for project context",
        "parameters": {
            "question": "The question to ask",
            "workspace_id": "The AnythingLLM workspace ID"
        }
    },
    {
        "name": "list_workspaces",
        "description": "List available AnythingLLM workspaces"
    }
]
```

#### Benefits

- ✅ Automatic context injection
- ✅ Claude Code can query AnythingLLM on-demand
- ✅ No manual copy-paste
- ✅ Consistent across team

#### Limitations

- ⚠️ Requires MCP server setup
- ⚠️ More complex initial configuration

---

### Approach 4: Proxy/Gateway Service (Team-Wide)

**Best for:** Organizations, consistent behavior across all developers

#### Architecture

```
Claude Code → Proxy/Gateway → Claude API
                ↓
           AnythingLLM
           (Auto-inject context)
```

The proxy:
1. Intercepts requests from Claude Code
2. Queries AnythingLLM for relevant context based on the prompt
3. Injects context into the request
4. Forwards to Claude API
5. Returns response

#### Implementation

This requires building a custom proxy service. Key components:

- **Request Interceptor:** Captures Claude Code API calls
- **Context Extractor:** Analyzes prompt to determine relevant AnythingLLM query
- **RAG Query:** Queries AnythingLLM workspace
- **Context Injector:** Adds AnythingLLM response to prompt
- **API Forwarder:** Sends augmented request to Claude API

#### Benefits

- ✅ Automatic context injection for all users
- ✅ Centralized policy enforcement
- ✅ Audit logging
- ✅ Token budget management

#### Limitations

- ⚠️ Significant engineering effort
- ⚠️ Requires infrastructure setup
- ⚠️ Needs transparency tooling

---

## Recommended Workflow

### For Individual Developers (Start Here)

1. **Set up AnythingLLM** (see `BasicArchitecture/AnythingLLM-LocalLLM-Tutorial.md`)
2. **Create project workspace** and upload key documents
3. **Use Approach 1 (Manual Context Packs)** initially
4. **Upgrade to Approach 2 (API Scripts)** when you want automation

### For Teams

1. **Deploy AnythingLLM** (Docker, multi-user mode)
2. **Create shared workspaces** for common knowledge
3. **Use Approach 2 (API Scripts)** with shared scripts
4. **Consider Approach 3 (MCP)** or **Approach 4 (Proxy)** for full automation

---

## Example: Complete Workflow

### Scenario: Refactoring Legacy Memory Management

**Step 1: Query AnythingLLM**

```
What is the memory management strategy in the device driver subsystem?
Are there any historical decisions or known issues I should be aware of?
```

**Step 2: Get Context Response**

AnythingLLM responds:
> The device driver uses a custom memory pool allocator introduced in 2019 (see ADR-047). Key considerations:
> - Pool sizes are tuned for embedded targets with limited RAM
> - The allocator is NOT thread-safe (single-threaded driver design)
> - Known issue: fragmentation under high churn (see postmortem PM-2023-08)
> - Migration to smart pointers was attempted in 2021 but reverted due to performance concerns

**Step 3: Provide to Claude Code**

```markdown
## Project Context from Knowledge Base

The device driver uses a custom memory pool allocator introduced in 2019 (see ADR-047). Key considerations:
- Pool sizes are tuned for embedded targets with limited RAM
- The allocator is NOT thread-safe (single-threaded driver design)
- Known issue: fragmentation under high churn (see postmortem PM-2023-08)
- Migration to smart pointers was attempted in 2021 but reverted due to performance concerns

## Current Code Locations
- Allocator defined in: src/memory/mempool.h
- Main usage in: src/drivers/device.cpp (lines 145-280)
- Pool configuration: src/config/memory_config.h

## Task
Refactor the device driver to use std::unique_ptr while maintaining 
compatibility with the custom allocator. Preserve the single-threaded 
assumption but add comments for future thread-safety work.
```

**Step 4: Claude Code Uses Context**

Claude Code now understands:
- Why the custom allocator exists
- Previous failed attempts
- Constraints (single-threaded, embedded targets)
- Can make informed refactoring decisions

---

## Workspace Organization Tips

### Recommended Workspace Structure

```
AnythingLLM Workspaces
├── MyProject-Architecture
│   ├── ADRs (Architecture Decision Records)
│   ├── Design docs
│   └── System overview
├── MyProject-Codebase
│   ├── Key entry points (main.cpp, etc.)
│   ├── Public interfaces (.h files)
│   └── Module boundaries
├── MyProject-Operations
│   ├── Runbooks
│   ├── Deployment guides
│   └── Postmortems
└── Platform-Standards
    ├── Coding conventions
    ├── C++ style guide
    └── Common patterns
```

### What to Upload

**DO Upload:**
- Architecture documentation
- ADRs and design decisions
- Onboarding guides
- Runbooks and operational procedures
- Selected code (entry points, interfaces, key modules)
- Coding standards and conventions

**AVOID Uploading:**
- Entire codebase (too large, poor chunking)
- Generated code
- Third-party dependencies
- Binary files

---

## Troubleshooting

### API Access Issues

**Problem:** Cannot connect to AnythingLLM API
- **Solution:** 
  1. Verify AnythingLLM is running (`http://localhost:3001`)
  2. Check if API key is required (Settings → Security)
  3. Verify firewall/network settings

**Problem:** API returns 401 Unauthorized
- **Solution:** 
  1. Check API key is correct
  2. Ensure API access is enabled in AnythingLLM settings
  3. For multi-user mode, verify user permissions

### Context Quality Issues

**Problem:** AnythingLLM returns irrelevant context
- **Solution:**
  1. Improve document organization (use collections/tags)
  2. Upload more relevant documents
  3. Use more specific queries
  4. Adjust embedding model settings

**Problem:** Context is too verbose
- **Solution:**
  1. Use "Query Mode" instead of "Chat Mode" (strictly document-based)
  2. Adjust system prompt in AnythingLLM to request concise responses
  3. Post-process API responses to extract key points

---

## Next Steps

1. **Set up AnythingLLM** following `BasicArchitecture/AnythingLLM-LocalLLM-Tutorial.md`
2. **Create your first workspace** and upload project documentation
3. **Try Approach 1** (Manual Context Packs) to get familiar
4. **Automate with Approach 2** (API Scripts) when ready
5. **Consider MCP or Proxy** for team-wide automation

---

## Additional Resources

- **AnythingLLM Documentation:** https://docs.anythingllm.com
- **RAG Guide:** See `BasicArchitecture/RAG_Guide.md`
- **Architecture Patterns:** See `BasicArchitecture/anythingllm_brownfield_coding_architectures.md`
- **Local LLM Setup:** See `BasicArchitecture/AnythingLLM-LocalLLM-Tutorial.md`

---

## Summary

AnythingLLM serves as your project's **long-term memory and explanation layer**, while Claude Code focuses on **changing code safely and precisely**. The integration enables Claude to understand:

- **Why** decisions were made (historical context)
- **What** patterns and conventions exist (standards)
- **How** the system is structured (architecture)
- **Where** to find relevant information (documentation)

Start with manual context packs, then automate as needed. The key is having well-organized workspaces in AnythingLLM with relevant project knowledge.
