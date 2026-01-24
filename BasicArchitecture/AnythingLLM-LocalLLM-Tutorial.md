# AnythingLLM with Local LLM Providers: Complete Setup Tutorial

A comprehensive guide for setting up AnythingLLM with local language models optimized for **C++ code review and development assistance**.

---

## Table of Contents

**Single User (Windows 11)**

1. [Goals](#goals)
2. [Overview & Architecture](#overview-architecture)
3. [Part A: CPU-Only LLM Setup (Windows 11)](#part-a-details)
4. [Part B: AnythingLLM Single-User Configuration (No GPU)](#part-b-details)
5. [Part C: Single-User GPU Configuration](#part-c-details)
6. [Part D: Coding Agent Integration (Single User)](#part-d-details)

**Multi-User / GPU Server (Production)**

7. [Part E: GPU Server LLM Setup](#part-e-details)
8. [Part F: AnythingLLM Multi-User Deployment](#part-f-details)
9. [Part G: Coding Agent Integration (Multi-User)](#part-g-details)

**Reference**

10. [Model Recommendations for C++ Development](#model-recommendations-for-c-development)
11. [Troubleshooting](#troubleshooting)

---

## Goals

This tutorial is organized into two tracks for setting up a local AI-powered code assistant specialized in **C++ development and code review**:

---

### Track 1: Single User (Windows 11)

For individual developers working on a Windows 11 workstation.

#### [Part A: CPU-Only LLM Setup](#part-a-details)

**Objective:** Identify the optimal LLM tool and model for running locally on Windows 11 **without a GPU**.

- Evaluate tools: LM Studio, Ollama, vLLM (WSL), and others
- Select a model optimized for **C++ coding and code review tasks**
- Balance inference speed with code understanding quality on CPU-only hardware
- Provide practical RAM and performance guidelines

#### [Part B: AnythingLLM Single-User Configuration (No GPU)](#part-b-details)

**Objective:** Configure AnythingLLM Desktop for an **individual developer** workflow without GPU.

- Connect AnythingLLM to the local CPU-based LLM (from Part A)
- Set up RAG (Retrieval-Augmented Generation) for codebase understanding
- Create workspaces for C++ project analysis
- Enable document embedding for context-aware code review

#### [Part C: Single-User GPU Configuration](#part-c-details)

**Objective:** Configure LM Studio or Ollama with **local GPU acceleration** for faster inference.

- Enable GPU offloading in LM Studio or Ollama
- Select larger models that fit in VRAM
- Achieve significantly faster inference while keeping single-user simplicity

#### [Part D: Coding Agent Integration (Single User)](#part-d-details)

**Objective:** Use AnythingLLM as a **RAG knowledge hub** alongside coding agents (Cursor, Claude Code, Gemini CLI) for **brownfield C++ projects** on a local workstation.

- Configure AnythingLLM as a context provider for Cursor/Claude Code
- Set up workspace structure for brownfield project knowledge
- Create "context packs" for coding agent sessions
- Integrate with local code indexing tools (ripgrep, ctags)

---

### Track 2: Multi-User / GPU Server (Production)

For development teams with a dedicated GPU server.

#### [Part E: GPU Server LLM Setup](#part-e-details)

**Objective:** Identify the optimal LLM tool and model for running on a **dedicated server with GPU acceleration**.

- Recommend the best operating system for GPU-based LLM inference
- Configure vLLM for high-throughput, multi-user scenarios
- Select a larger, more capable model for **advanced C++ code analysis**
- Enable concurrent request handling for team use

#### [Part F: AnythingLLM Multi-User Deployment](#part-f-details)

**Objective:** Deploy AnythingLLM for a **development team** with shared access.

- Connect AnythingLLM to the GPU server (from Part E)
- Deploy using Docker for scalability and maintainability
- Configure multi-user authentication and workspace permissions
- Secure the deployment with HTTPS and proper access controls

#### [Part G: Coding Agent Integration (Multi-User)](#part-g-details)

**Objective:** Use AnythingLLM as a **shared RAG knowledge hub** for a development team using coding agents on **brownfield C++ projects**.

- Deploy AnythingLLM as a shared RAG hub for the development team
- Configure MCP (Model Context Protocol) server for agent integration
- Set up hybrid retrieval: AnythingLLM (docs/history) + Code Indexer (symbols/refs)
- Implement the "Two-Speed Knowledge Model" for long-term maintainability
- Enable gated execution for safe refactoring workflows

---

### Why Brownfield Projects Need Special Attention

Brownfield projects present unique challenges that AnythingLLM addresses:
- Missing or fragmented documentation
- Historical decisions not reflected in code
- Tribal knowledge scattered across docs, tickets, PRs, and runbooks
- Need for long-lived "project memory"

### Target Use Cases

This setup enables the following C++ development workflows:

| Use Case | Description |
|----------|-------------|
| **Code Review** | Analyze C++ code for bugs, memory leaks, thread safety issues |
| **Refactoring Suggestions** | Get recommendations for modernizing legacy C++ code |
| **Documentation Generation** | Generate documentation from code comments and structure |
| **Architecture Analysis** | Understand complex codebases through RAG-powered Q&A |
| **Best Practices** | Receive guidance on C++ standards compliance (C++11/14/17/20) |
| **Security Audit** | Identify potential security vulnerabilities in C++ code |
| **Brownfield Enhancement** | Safely modify legacy code with full historical context |
| **Knowledge Preservation** | Capture tribal knowledge and architectural decisions |
| **Agent-Assisted Refactoring** | Use coding agents with RAG-augmented project understanding |

---

## Overview & Architecture

### What You'll Build

#### Track 1: Single User

| Parts | Hardware | LLM Tool | AnythingLLM Mode | Best For |
|-------|----------|----------|------------------|----------|
| **[A](#part-a-details) + [B](#part-b-details)** | Windows 11, No GPU | LM Studio / Ollama | Desktop | Individual developer, code review |
| **[A](#part-a-details) + [C](#part-c-details)** | Windows 11, With GPU | LM Studio / Ollama (GPU) | Desktop | Individual developer, GUI preference |
| **[A](#part-a-details) + [C](#part-c-details) (Alt)** | Windows 11, With GPU | vLLM (WSL) | Desktop | Individual developer, max performance |
| **[A](#part-a-details) + [B](#part-b-details) + [D](#part-d-details)** | Windows 11, No GPU | Ollama + Code Indexer | Desktop + Coding Agent | Brownfield developer, automation focus |
| **[A](#part-a-details) + [C](#part-c-details) + [D](#part-d-details)** | Windows 11, With GPU | Ollama (GPU) or vLLM (WSL) + Code Indexer | Desktop + Coding Agent | Brownfield developer, faster inference |

#### Track 2: Multi-User / GPU Server

| Parts | Hardware | LLM Tool | AnythingLLM Mode | Best For |
|-------|----------|----------|------------------|----------|
| **[E](#part-e-details) + [F](#part-f-details)** | Linux Server + GPU | vLLM | Docker (Multi-User) | Development team |
| **[E](#part-e-details) + [F](#part-f-details) + [G](#part-g-details)** | Linux Server + GPU | vLLM + Code Indexer | Docker + Coding Agents | Brownfield development team |

### Why These Choices?

- **LM Studio** (CPU/GPU): Native Windows support, GUI model browser, optimized GGUF quantization via llama.cpp, easiest setup
- **Ollama** (CPU/GPU): CLI-first design, lightweight background service, excellent for automation and scripting, easy model management
- **vLLM** (GPU): Industry-leading throughput via PagedAttention, continuous batching, native AWQ/GPTQ support, best for maximum performance
- **AnythingLLM**: RAG capabilities for codebase understanding, workspace organization, document embedding

> **Choosing Between Tools:** LM Studio is ideal if you prefer a GUI. Ollama excels for CLI workflows and coding agent integration. vLLM (via WSL) offers maximum GPU performance for users comfortable with Linux environments.

> **Consider Native Linux:** If you plan to do heavy GPU inference, extensive automation, or eventually scale to multi-user deployment, consider using Linux (native or dual-boot) from the start. Linux provides native CUDA support without WSL overhead (expect 5-10% better GPU performance), simpler systemd service management, and is the standard environment for production ML workloads. Track 2 already assumes Linux for these reasons.

---

# Track 1: Single User (Windows 11)

The following sections are for individual developers on Windows 11 workstations.

---

<a id="part-a-details"></a>
## Part A: CPU-Only LLM Setup (Windows 11)

### Recommended Tool: **LM Studio**

For CPU-only Windows 11 workstations, **LM Studio** is the optimal choice:

| Feature | LM Studio | Ollama | vLLM (WSL) |
|---------|-----------|--------|------------|
| Windows Native | ✅ Yes | ✅ Yes | 🔧 Requires WSL |
| GUI Model Browser | ✅ Yes | 🔧 CLI only | 🔧 CLI only |
| GGUF Quantization | ✅ Excellent | ✅ Good | ⚡ Native FP16/AWQ |
| CPU Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| GPU Throughput | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup Complexity | Easy | Easy | Moderate |

> **Note on WSL and CLI-only tools:** WSL is not a disadvantage if it enables access to superior tooling—vLLM offers industry-leading GPU throughput and native support for production-grade quantization formats (AWQ, GPTQ). Similarly, CLI-only interfaces like Ollama provide lightweight operation, easy scripting/automation, and lower resource overhead. Choose based on your priorities: GUI convenience vs. performance/automation benefits.

### Recommended Model for C++ Code Review (CPU)

**Primary Choice:** `Qwen2.5-Coder-7B-Instruct-GGUF` (Q4_K_M quantization)

- **Why Qwen2.5-Coder?**
  - Specifically trained on code with strong C/C++ performance
  - Excellent at code review, bug detection, and refactoring suggestions
  - 7B parameter size balances quality and CPU performance
  - Q4_K_M quantization: ~4.5 GB RAM, good quality retention

**Alternative (Lower RAM):** `Qwen2.5-Coder-3B-Instruct-GGUF` (Q5_K_M)
- ~2.5 GB RAM requirement
- Faster inference, slightly reduced quality

**Alternative (Better Quality, More RAM):** `DeepSeek-Coder-V2-Lite-Instruct-GGUF`
- Strong C++ understanding
- Requires 16GB+ RAM

### Step-by-Step: LM Studio Installation

#### 1. Download and Install LM Studio

1. Visit [https://lmstudio.ai](https://lmstudio.ai)
2. Download the **Windows** installer
3. Run the installer with default options
4. Launch LM Studio from the Start Menu

#### 2. Download a C++ Coding Model

1. In LM Studio, click the **Search** tab (magnifying glass icon)
2. Search for: `Qwen2.5-Coder-7B-Instruct GGUF`
3. Look for quantizations from **bartowski** or **TheBloke** (trusted quantizers)
4. Select **Q4_K_M** quantization (best balance for CPU)
5. Click **Download**

> **RAM Guidelines:**
> - 8 GB RAM → Use 3B model with Q4 quantization
> - 16 GB RAM → Use 7B model with Q4_K_M quantization
> - 32 GB RAM → Use 7B model with Q6_K or higher

#### 3. Start the Local Server

1. Go to the **Local Server** tab (left sidebar, server icon)
2. Select your downloaded model from the dropdown
3. Configure server settings:
   - **Port:** `1234` (default)
   - **Context Length:** `4096` (increase to 8192 if you have 32GB+ RAM)
4. Click **Start Server**
5. Verify the server is running (green status indicator)

The API will be available at: `http://localhost:1234/v1`

#### 4. Test the Server

Open PowerShell and run:

```powershell
curl http://localhost:1234/v1/models
```

You should see your model listed in the JSON response.

---

### Alternative: Ollama Setup (Simpler, CLI-Based)

If you prefer a lighter-weight solution:

#### 1. Install Ollama

```powershell
# Download from https://ollama.com and run the installer
# Or use winget:
winget install Ollama.Ollama
```

#### 2. Pull a Coding Model

```powershell
# Best for C++ code review on CPU
ollama pull qwen2.5-coder:7b

# Alternative: smaller model for lower RAM
ollama pull qwen2.5-coder:3b

# Alternative: DeepSeek Coder
ollama pull deepseek-coder-v2:lite
```

#### 3. Start the Server

Ollama runs automatically as a service. The API is available at:
`http://localhost:11434/v1`

---

<a id="part-b-details"></a>
## Part B: AnythingLLM Single-User Configuration (No GPU)

This section combines AnythingLLM Desktop with the CPU setup from Part A.

### 1. Install AnythingLLM Desktop

1. Visit [https://anythingllm.com/download](https://anythingllm.com/download)
2. Download the **Windows** installer
3. Run the installer
4. Launch AnythingLLM from the Start Menu

### 2. Configure LLM Provider

#### Option 1: Connect to LM Studio

1. **Ensure LM Studio server is running** (Part A, Step 3)
2. In AnythingLLM, click the **Settings** icon (gear/wrench, bottom left)
3. Navigate to **AI Providers** → **LLM**
4. Select **LM Studio** as the provider
5. Configure:
   - **Base URL:** `http://localhost:1234/v1`
   - **Model:** Select your model from the dropdown (click refresh if needed)
   - **Token Context Window:** `4096`
6. Click **Save Changes**

#### Option 2: Connect to Ollama

1. **Ensure Ollama is running** (it runs as a service by default)
2. In AnythingLLM Settings → **AI Providers** → **LLM**
3. Select **Ollama** as the provider
4. Configure:
   - **Base URL:** `http://localhost:11434`
   - **Model:** Select `qwen2.5-coder:7b` from dropdown
   - **Token Context Window:** `4096`
5. Click **Save Changes**

### 3. Configure Embedding Model (Important for RAG)

For code search to work well, configure a local embedding model:

1. Go to **AI Providers** → **Embedder**
2. Select **LM Studio** or **Ollama**
3. For Ollama, pull an embedding model first:
   ```powershell
   ollama pull nomic-embed-text
   ```
4. Select the embedding model
5. Click **Save Changes**

### 4. Create a C++ Project Workspace

1. Click **New Workspace** in the sidebar
2. Name it (e.g., "MyProject Code Review")
3. Click the workspace to open it

### 5. Upload Your C++ Codebase

1. In the workspace, click the **Upload** icon (document with arrow)
2. Select files or folders:
   - `.cpp`, `.hpp`, `.h`, `.c` files
   - `CMakeLists.txt`, `Makefile`
   - Documentation (`.md`, `.txt`)
3. Click **Move to Workspace**
4. Click **Save and Embed**
5. Wait for embedding to complete

### 6. Start Code Review Conversations

Example prompts for C++ code review:

```
Review the memory management in the uploaded source files. 
Are there any potential memory leaks or dangling pointers?
```

```
Analyze the error handling patterns in this codebase. 
Suggest improvements following C++ best practices.
```

```
Find all uses of raw pointers and suggest where smart pointers 
(unique_ptr, shared_ptr) would be more appropriate.
```

```
Review the thread safety of the classes in the uploaded code. 
Are there any race conditions or deadlock risks?
```

---

<a id="part-c-details"></a>
## Part C: Single-User GPU Configuration

For individual developers with a local GPU (NVIDIA RTX 3060 or better). This provides significantly faster inference while keeping the single-user simplicity of Part B.

> **Prerequisites:** Complete [Part A](#part-a-cpu-only-llm-setup-windows-11) first.

### LM Studio with GPU

LM Studio auto-detects NVIDIA GPUs. To enable GPU acceleration:

1. In LM Studio, go to **Local Server** tab
2. Select your model
3. In **Model Configuration**, set **GPU Offload** to maximum layers (or "max")
4. Use higher quality quantizations (Q5_K_M, Q6_K) since GPU handles them efficiently

### Ollama with GPU

Ollama auto-detects CUDA on Windows. Pull larger models:

```powershell
# For 8GB+ VRAM
ollama pull qwen2.5-coder:14b

# For 12GB+ VRAM
ollama pull qwen2.5-coder:14b-instruct-q6_K
```

### Model Recommendations (Single-User GPU)

| VRAM | Model | Context | Notes |
|------|-------|---------|-------|
| 8GB | Qwen2.5-Coder-7B-Q6_K | 8192 | Better quality than CPU Q4 |
| 12GB | Qwen2.5-Coder-14B-Q4_K_M | 8192 | Larger model, good quality |
| 16GB+ | Qwen2.5-Coder-14B-Q6_K | 16384 | Best single-user experience |

### AnythingLLM Configuration

AnythingLLM configuration remains the same as [Part B](#part-b-anythingllm-single-user-configuration-no-gpu). The only difference is that your LM Studio or Ollama backend now uses GPU acceleration.

---

### Alternative: vLLM on WSL2 (Maximum GPU Performance)

For users who prioritize inference speed and are comfortable with CLI workflows, **vLLM running in WSL2** offers significant advantages over native Windows tools.

#### Why Consider vLLM for Single-User GPU?

| Factor | LM Studio / Ollama (Native) | vLLM (WSL) |
|--------|----------------------------|------------|
| **Throughput** | Good | Excellent (2-3x via PagedAttention) |
| **VRAM Efficiency** | Standard | Better (fit larger models/contexts) |
| **Quantization** | GGUF | Native AWQ/GPTQ (GPU-optimized) |
| **Automation** | Limited | Excellent (CLI, scripting) |
| **Setup** | Easy | Moderate |

**Choose vLLM (WSL) if you:**
- Need maximum inference speed
- Are comfortable with command-line tools
- Want to automate/script your workflows
- Plan to eventually scale to multi-user (same stack)
- Prefer native HuggingFace model formats

> **Native Linux Alternative:** If you're setting up vLLM via WSL, consider whether a native Linux installation (dual-boot or dedicated machine) might better suit your needs. Native Linux eliminates WSL virtualization overhead (5-10% performance gain), provides direct CUDA access, and simplifies long-term maintenance. The vLLM setup steps below work identically on native Ubuntu.

#### Prerequisites

- Windows 11 with WSL2 enabled
- NVIDIA GPU with CUDA support (RTX 3060 or better)
- At least 16GB VRAM recommended for best experience

#### Step 1: Install WSL2 with Ubuntu

Open PowerShell as Administrator:

```powershell
# Enable WSL and install Ubuntu
wsl --install -d Ubuntu-22.04

# Restart your computer when prompted
# After restart, Ubuntu will complete setup - create a username/password
```

#### Step 2: Install NVIDIA CUDA in WSL

Inside your WSL Ubuntu terminal:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify GPU access (should show your NVIDIA GPU)
nvidia-smi
```

> **Note:** WSL2 automatically has access to your Windows NVIDIA drivers. If `nvidia-smi` doesn't work, ensure you have the latest NVIDIA Game Ready or Studio drivers installed on Windows.

#### Step 3: Set Up vLLM Environment

```bash
# Create project directory
mkdir -p ~/vllm-local
cd ~/vllm-local

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install vLLM
pip install --upgrade pip
pip install vllm
```

#### Step 4: Start vLLM Server

**For 12-16GB VRAM (RTX 3060, 4070, 4080):**

```bash
vllm serve Qwen/Qwen2.5-Coder-14B-Instruct-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90
```

**For 24GB+ VRAM (RTX 3090, 4090):**

```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90
```

The server will download the model on first run (may take several minutes).

#### Step 5: Connect AnythingLLM to vLLM

1. In AnythingLLM, go to **Settings** → **AI Providers** → **LLM**
2. Select **Generic OpenAI** as the provider
3. Configure:
   - **Base URL:** `http://localhost:8000/v1`
   - **API Key:** Leave empty (or set one if you started vLLM with `--api-key`)
   - **Chat Model Name:** `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` (or your model)
   - **Token Context Window:** `8192` (match your `--max-model-len`)
4. Click **Save Changes**

#### Step 6: Create a Startup Script (Optional)

Create `~/vllm-local/start-server.sh`:

```bash
#!/bin/bash
cd ~/vllm-local
source .venv/bin/activate
vllm serve Qwen/Qwen2.5-Coder-14B-Instruct-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90
```

Make it executable:

```bash
chmod +x ~/vllm-local/start-server.sh
```

Now you can start your server with: `~/vllm-local/start-server.sh`

#### Model Recommendations (vLLM on WSL)

| VRAM | Model | Context | Notes |
|------|-------|---------|-------|
| 12GB | Qwen2.5-Coder-7B-Instruct-AWQ | 16384 | Fast, good quality |
| 16GB | Qwen2.5-Coder-14B-Instruct-AWQ | 8192 | Best balance |
| 24GB | Qwen2.5-Coder-32B-Instruct-AWQ | 16384 | Maximum quality |

---

<a id="part-d-details"></a>
## Part D: Coding Agent Integration (Single User)

This section covers using AnythingLLM as a **knowledge hub** alongside coding agents like **Cursor**, **Claude Code**, or **Gemini CLI** for brownfield C++ projects on a **single-user Windows workstation**.

> **Prerequisites:** Complete [Part A](#part-a-cpu-only-llm-setup-windows-11) and [Part B](#part-b-anythingllm-single-user-configuration-no-gpu) (or [Part C](#part-c-single-user-gpu-configuration)) first.

### Why AnythingLLM for Brownfield Projects?

AnythingLLM is **not** intended to replace IDE-based coding agents. Instead, it fills a critical gap:

| Challenge | How AnythingLLM Helps |
|-----------|----------------------|
| Missing documentation | RAG over existing docs, ADRs, runbooks |
| Historical decisions not in code | Captures "why" behind architectural choices |
| Tribal knowledge scattered | Centralizes info from tickets, PRs, wikis |
| Long-lived project memory | Persistent workspaces across sessions |

**The Key Principle:** Hybrid retrieval, not a single tool doing everything.

- **Coding Agents** (Cursor/Claude Code/Gemini CLI) = *make changes*
- **AnythingLLM** = *understand the system and its history*
- **Code Index Services** = *precise symbol-level navigation*

---

### Architecture for Single-User Setup

#### Architecture 1: Context Packs (Simplest)

Best for: Individual developers, early exploration, minimal setup.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Developer      │────▶│  AnythingLLM     │────▶│  Context Pack   │
│  Query          │     │  (RAG Query)     │     │  (Markdown)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Cursor /       │
                                                 │  Claude Code    │
                                                 │  (Apply Changes)│
                                                 └─────────────────┘
```

#### Architecture 2: RAG Hub + Code Indexer (Recommended)

Best for: Regular brownfield work, refactoring, enhancements.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Coding Agent (Cursor/Claude Code)           │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│     AnythingLLM         │     │    Code Index Service   │
│  (Docs, Architecture,   │     │  (Symbols, Refs, Search)│
│   History, Decisions)   │     │                         │
└─────────────────────────┘     └─────────────────────────┘
```

---

### Recommended LLM Backend for Coding Agent Integration

For integration with coding agents (Cursor, Claude Code, Gemini CLI), **Ollama is recommended over LM Studio** as the local LLM backend:

| Factor | Ollama | LM Studio |
|--------|--------|-----------|
| **CLI/Scripting** | ✅ Excellent | ⚠️ Limited |
| **Background Service** | ✅ Runs quietly | ⚠️ Requires GUI open |
| **Resource Overhead** | ✅ Minimal when idle | ⚠️ Higher |
| **Model Management** | ✅ Simple CLI commands | ✅ GUI browser |
| **API Compatibility** | ✅ OpenAI-compatible | ✅ OpenAI-compatible |
| **Automation** | ✅ Easy to script | ⚠️ Manual |

**Why Ollama for Coding Agents:**

1. **CLI-first design** — Integrates naturally with developer workflows
2. **Background service** — Always available without keeping a GUI window open
3. **Lower overhead** — Minimal resource usage when not actively inferring
4. **Easy model switching** — `ollama run model-name` to switch models instantly
5. **Scriptable** — Automate model pulls, server restarts, and health checks

**Alternative: vLLM (WSL)** — If you set up vLLM in Part C, you can use it here for maximum performance. vLLM's CLI-first design and superior throughput make it excellent for coding agent integration, especially for larger refactoring tasks.

> **LM Studio** remains a good choice if you prefer a GUI for model browsing and don't need automation capabilities.

---

### Single-User Setup: AnythingLLM + Cursor/Claude Code

#### Step 1: Organize AnythingLLM Workspaces

Create workspaces structured for brownfield knowledge:

```
AnythingLLM Workspaces
├── MyProject-Architecture
│   ├── ADRs (Architecture Decision Records)
│   ├── Design docs
│   └── System overview diagrams (as text descriptions)
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

#### Step 2: Ingest Brownfield Knowledge

Upload to AnythingLLM:

1. **Architecture docs** (`/docs`, ADRs, design documents)
2. **Onboarding guides** (how the system works)
3. **Runbooks** (operational procedures)
4. **PR summaries** (why changes were made)
5. **Selected code** (entry points, interfaces—not entire repo)
6. **Brownfield notes** (manually curated "gotchas" and historical context)

#### Step 3: Create Context Packs for Coding Sessions

Before starting a coding task in Cursor/Claude Code, query AnythingLLM:

**Example workflow:**

1. **Query AnythingLLM:**
   ```
   I need to refactor the memory allocation in the device driver module.
   What are the key considerations, historical decisions, and known pitfalls?
   ```

2. **Copy the response** as context for your coding agent

3. **In Cursor/Claude Code**, paste the context and your task:
   ```
   ## Context from Project Knowledge Base
   [Paste AnythingLLM response here]
   
   ## Task
   Refactor the memory allocation in src/drivers/device.cpp to use 
   smart pointers instead of raw pointers.
   ```

#### Step 4: Set Up Local Code Indexing (Optional but Recommended)

For precise symbol navigation alongside AnythingLLM's conceptual knowledge:

**Install ripgrep** (fast code search):

```powershell
winget install BurntSushi.ripgrep.MSVC
```

**Install Universal Ctags** (symbol indexing):

```powershell
winget install UniversalCtags.Ctags
```

**Generate tags for your project:**

```powershell
cd C:\path\to\your\cpp\project
ctags -R --languages=C,C++ --extras=+q .
```

Now you can use these alongside AnythingLLM:
- **AnythingLLM**: "Which subsystem handles device initialization?"
- **ripgrep**: `rg "DeviceInit" --type cpp`
- **ctags**: Jump to definition in your IDE

---

# Track 2: Multi-User / GPU Server (Production)

The following sections are for development teams with a dedicated GPU server.

---

<a id="part-e-details"></a>
## Part E: GPU Server LLM Setup

> **Note:** This section is for Track 2 (Multi-User / GPU Server). If you completed Track 1 (Parts A-D), you can skip to this section when ready to scale up.

### Recommended Stack

| Component | Recommendation |
|-----------|----------------|
| **Operating System** | Ubuntu 22.04 LTS Server |
| **LLM Runtime** | vLLM |
| **GPU** | NVIDIA (RTX 3090/4090 or A100/H100) |
| **Model** | Qwen2.5-Coder-32B-Instruct |

### Why Ubuntu 22.04 LTS?

- Native NVIDIA CUDA support with minimal configuration
- Long-term support (until 2027)
- Best compatibility with vLLM and ML frameworks
- Excellent Docker integration
- Lower overhead than Windows Server

### Recommended Model for C++ Code Review (GPU)

**Primary Choice:** `Qwen/Qwen2.5-Coder-32B-Instruct`

- State-of-the-art code understanding
- Excellent C++ syntax and semantics comprehension
- Strong at identifying bugs, security issues, and code smells
- Requires ~24GB VRAM (fits on RTX 3090/4090 with AWQ quantization)

**For Larger Teams (Multiple GPUs):** `Qwen/Qwen2.5-Coder-32B-Instruct` with tensor parallelism

**Budget Option (Single 16GB GPU):** `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ`

### Step-by-Step: vLLM Server Setup

#### 1. Prepare Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install NVIDIA drivers (if not already installed)
sudo apt install -y nvidia-driver-535

# Reboot to load drivers
sudo reboot
```

#### 2. Verify GPU Access

```bash
nvidia-smi
```

You should see your GPU(s) listed with driver version and CUDA version.

#### 3. Install Python Environment

```bash
# Install Python and venv
sudo apt install -y python3.11 python3.11-venv python3-pip

# Create project directory
mkdir -p ~/vllm-server
cd ~/vllm-server

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 4. Install vLLM

```bash
pip install vllm
```

#### 5. Start vLLM Server

**For 24GB+ VRAM (RTX 3090/4090, A5000):**

```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --api-key your-secure-api-key
```

**For 16GB VRAM (RTX 4080, A4000):**

```bash
vllm serve Qwen/Qwen2.5-Coder-14B-Instruct-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90 \
  --api-key your-secure-api-key
```

**For Multi-GPU Setup:**

```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --max-model-len 16384 \
  --api-key your-secure-api-key
```

#### 6. Create Systemd Service (Production)

Create `/etc/systemd/system/vllm.service`:

```ini
[Unit]
Description=vLLM OpenAI-Compatible Server
After=network.target

[Service]
Type=simple
User=vllm
WorkingDirectory=/home/vllm/vllm-server
Environment="PATH=/home/vllm/vllm-server/.venv/bin"
ExecStart=/home/vllm/vllm-server/.venv/bin/vllm serve Qwen/Qwen2.5-Coder-32B-Instruct-AWQ --host 0.0.0.0 --port 8000 --max-model-len 8192 --gpu-memory-utilization 0.90 --api-key your-secure-api-key
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vllm
sudo systemctl start vllm
```

#### 7. Verify Server

```bash
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer your-secure-api-key"
```

---

<a id="part-f-details"></a>
## Part F: AnythingLLM Multi-User Deployment

> **Prerequisites:** Complete [Part E](#part-e-gpu-server-llm-setup) first.

This section combines AnythingLLM Docker deployment with the vLLM GPU server from Part E.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Network                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐         ┌──────────────────────────────┐ │
│   │   Users      │         │     GPU Server (Ubuntu)      │ │
│   │  (Browsers)  │         │  ┌────────────────────────┐  │ │
│   │              │   HTTP  │  │   vLLM                 │  │ │
│   │  User 1 ─────┼────────▶│  │   Port 8000            │  │ │
│   │  User 2 ─────┼─────┐   │  │   Qwen2.5-Coder-32B    │  │ │
│   │  User 3 ─────┼──┐  │   │  └────────────────────────┘  │ │
│   └──────────────┘  │  │   │                              │ │
│                     │  │   │  ┌────────────────────────┐  │ │
│                     │  │   │  │   AnythingLLM Docker   │  │ │
│                     │  └───┼─▶│   Port 3001            │  │ │
│                     └──────┼─▶│   Multi-user mode      │  │ │
│                            │  └────────────────────────┘  │ │
│                            └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1. Install Docker on Ubuntu Server

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

### 2. Create AnythingLLM Docker Configuration

Create a directory for AnythingLLM:

```bash
mkdir -p ~/anythingllm
cd ~/anythingllm
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  anythingllm:
    image: mintplexlabs/anythingllm
    container_name: anythingllm
    ports:
      - "3001:3001"
    environment:
      - STORAGE_DIR=/app/server/storage
      - JWT_SECRET=your-very-long-random-secret-key-here
      - SIG_KEY=your-signature-key-for-security
      - SIG_SALT=your-signature-salt-value
      # Multi-user mode
      - DISABLE_TELEMETRY=true
    volumes:
      - ./storage:/app/server/storage
      - ./env:/app/server/.env
    restart: unless-stopped
```

Create the storage directory:

```bash
mkdir -p storage
```

### 3. Start AnythingLLM

```bash
docker compose up -d
```

Verify it's running:

```bash
docker logs anythingllm
```

### 4. Initial Setup (First Access)

1. Open browser: `http://your-server-ip:3001`
2. Complete the setup wizard:
   - Create admin account
   - Set instance password (for multi-user)

### 5. Configure vLLM as LLM Provider

1. Log in as admin
2. Go to **Settings** (gear icon) → **AI Providers** → **LLM**
3. Select **Generic OpenAI** as provider
4. Configure:
   - **Base URL:** `http://localhost:8000/v1` (or server IP if vLLM is on different host)
   - **API Key:** `your-secure-api-key` (from vLLM setup)
   - **Chat Model Name:** `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ`
   - **Token Context Window:** `8192`
5. Click **Save Changes**

### 6. Enable Multi-User Mode

1. Go to **Settings** → **Users**
2. Click **Enable Multi-User Mode**
3. Create user accounts for your team:
   - Set usernames and passwords
   - Assign roles (Admin, Manager, Default)

### 7. Configure Workspaces for Team

1. Create shared workspaces for different projects
2. Upload common C++ codebases
3. Set workspace permissions per user/role

### 8. Secure the Deployment (Production)

#### Set Up Nginx Reverse Proxy with SSL

Install Nginx:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/anythingllm`:

```nginx
server {
    listen 80;
    server_name llm.yourcompany.com;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and get SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/anythingllm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate (requires domain pointing to server)
sudo certbot --nginx -d llm.yourcompany.com
```

#### Firewall Configuration

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

<a id="part-g-details"></a>
## Part G: Coding Agent Integration (Multi-User)

This section covers using AnythingLLM as a **shared knowledge hub** for development teams using coding agents on brownfield C++ projects.

> **Prerequisites:** Complete [Part E](#part-e-gpu-server-llm-setup) and [Part F](#part-f-anythingllm-multi-user-deployment) first.

### Architecture for Multi-User Setup

#### Architecture 3: Gated Execution (Safe Refactoring)

Best for: Multi-step refactors, team environments, safety-critical code.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Coding Agent                                 │
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ AnythingLLM   │   │ Code Indexer  │   │ Tool Router   │
│ (Knowledge)   │   │ (Precision)   │   │ (Execution)   │
└───────────────┘   └───────────────┘   └───────────────┘
                                                │
                            ┌───────────────────┼───────────────────┐
                            ▼                   ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                    │ run_tests   │     │ run_build   │     │ apply_patch │
                    └─────────────┘     └─────────────┘     └─────────────┘
```

---

### Multi-User Setup: Shared RAG Hub for Teams

#### Step 1: Deploy AnythingLLM as Team Knowledge Hub

Use the Docker deployment from Part F, with workspace structure for the team:

```yaml
# docker-compose.yml additions for team use
services:
  anythingllm:
    image: mintplexlabs/anythingllm
    environment:
      # ... existing config ...
      - ALLOW_ACCOUNT_CREATION=false  # Admin creates accounts
    volumes:
      - ./storage:/app/server/storage
      - ./shared-docs:/app/server/shared-docs  # Mounted docs
```

#### Step 2: Configure Team Workspaces

Create a workspace hierarchy that maps to your organization:

| Workspace | Content | Access |
|-----------|---------|--------|
| `company-standards` | C++ style guide, coding conventions, security policies | All users |
| `project-alpha-arch` | Architecture docs, ADRs, design decisions | Project Alpha team |
| `project-alpha-code` | Key interfaces, entry points, module docs | Project Alpha team |
| `project-beta-arch` | Architecture docs for Project Beta | Project Beta team |
| `platform-infra` | Build system, CI/CD, deployment docs | DevOps + leads |

#### Step 3: Implement Two-Speed Knowledge Model

**Long-Lived Knowledge (in AnythingLLM):**
- Architecture documentation
- ADRs and design decisions
- Coding standards and conventions
- "How we do X here" guides
- Module ownership information
- Curated hotspot summaries

**Ephemeral Knowledge (per coding session):**
- Exact files opened
- Symbol reference lists
- Diffs and patches
- Test/build logs
- Session summaries

**Workflow:**
1. Agent reads baseline context from AnythingLLM
2. Agent performs refactor using code indexer
3. After merge: write back a concise "what changed and why" note to AnythingLLM

This prevents the RAG corpus from becoming a junk drawer.

#### Step 4: Set Up MCP Server for Agent Integration (Advanced)

For seamless integration with coding agents, expose AnythingLLM via MCP (Model Context Protocol):

**Minimum Tool Contract:**

From AnythingLLM:
```
rag_query(question, workspace, filters) → cited passages/snippets
list_workspaces() → available knowledge bases
list_collections() → document collections
```

From Code Indexer:
```
search_code(query) → matching code snippets
get_def(symbol) → definition location
get_refs(symbol) → all references
open_file(path, start, end) → file contents
```

Optional Execution Tools:
```
run_tests(target) → test results
run_build() → build output
run_lint() → linting results
apply_patch(diff) → apply changes (with limits)
```

#### Step 5: Configure Proxy for Automatic RAG Injection (Optional)

For consistent behavior across all team members, set up a proxy that automatically injects AnythingLLM context:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Cursor /       │────▶│  Proxy/Gateway  │────▶│  Claude API /   │
│  Claude Code    │     │  Service        │     │  vLLM Server    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  AnythingLLM    │
                        │  (Auto-inject   │
                        │   context)      │
                        └─────────────────┘
```

The proxy:
1. Intercepts requests from coding agents
2. Queries AnythingLLM for relevant context
3. Injects context into the prompt
4. Forwards to the LLM backend
5. Returns response to the agent

Benefits:
- Uniform agent behavior across team
- Centralized policy enforcement
- Audit logging
- Token budget management

---

### Practical Workspace Structure for C++ Brownfield Projects

#### Suggested Directory/Tag Organization in AnythingLLM

| Collection | Content Examples |
|------------|------------------|
| `adr/` | Architecture Decision Records |
| `runbook/` | Operational procedures, troubleshooting guides |
| `onboarding/` | New developer guides, system overviews |
| `patterns/` | Common code patterns, idioms used in project |
| `postmortems/` | Incident reports, lessons learned |
| `api-contracts/` | Interface definitions, API documentation |
| `build-system/` | CMake guides, build configuration docs |

#### Code Ingestion Guidelines

**DO Ingest:**
- Stable entry points (`main.cpp`, initialization code)
- Public interfaces (`.h` files defining APIs)
- Boundary modules (code at subsystem interfaces)
- Configuration files (`CMakeLists.txt`, `.clang-format`)

**AVOID Ingesting:**
- Entire monorepos (unless chunking is well-controlled)
- Generated code
- Third-party dependencies
- Binary files

---

### Example: Complete Brownfield Workflow

**Scenario:** Refactoring legacy memory management in a C++ device driver.

#### 1. Query AnythingLLM for Context

```
What is the memory management strategy in the device driver subsystem?
Are there any historical decisions or known issues I should be aware of?
```

**AnythingLLM Response:**
> The device driver uses a custom memory pool allocator introduced in 2019 
> (see ADR-047). Key considerations:
> - Pool sizes are tuned for embedded targets with limited RAM
> - The allocator is NOT thread-safe (single-threaded driver design)
> - Known issue: fragmentation under high churn (see postmortem PM-2023-08)
> - Migration to smart pointers was attempted in 2021 but reverted due to...

#### 2. Use Code Indexer for Precise Locations

```bash
# Find all allocator usages
rg "MemPool::" --type cpp

# Find the allocator definition
ctags -x --c++-kinds=c MemPool
```

#### 3. Provide Context to Coding Agent (Cursor/Claude Code)

```
## Project Context
[Paste AnythingLLM response]

## Current Code Locations
- Allocator defined in: src/memory/mempool.h
- Main usage in: src/drivers/device.cpp (lines 145-280)
- Pool configuration: src/config/memory_config.h

## Task
Refactor the device driver to use std::unique_ptr while maintaining 
compatibility with the custom allocator. Preserve the single-threaded 
assumption but add comments for future thread-safety work.
```

#### 4. After Successful Merge: Update AnythingLLM

Add a note to the project workspace:

```
## Memory Management Refactor (January 2026)

Changed device.cpp to use std::unique_ptr with custom deleters that 
return memory to MemPool. This preserves the existing allocation 
strategy while improving safety.

Key changes:
- DeviceHandle now uses unique_ptr<Device, PoolDeleter>
- Added PoolDeleter functor in mempool.h
- No thread-safety changes (deferred to future work)

Related: ADR-047, PM-2023-08
```

---

### Architecture Selection Guide

| Situation | Recommended Architecture |
|-----------|-------------------------|
| Just getting started | **Architecture 1** (Context Packs) |
| Regular brownfield work | **Architecture 2** (RAG Hub + Code Indexer) |
| Team-wide consistency needed | **Architecture 3** (Proxy with auto-injection) |
| Safety-critical refactoring | **Gated Execution** variant |
| Long-term maintainability | Combine with **Two-Speed Knowledge Model** |

---

## Model Recommendations for C++ Development

### Summary Table

| Use Case | Model | Size | Min RAM/VRAM | Quality |
|----------|-------|------|--------------|---------|
| CPU (8GB RAM) | Qwen2.5-Coder-3B-Q4_K_M | 2.5 GB | 8 GB RAM | ⭐⭐⭐ |
| CPU (16GB RAM) | Qwen2.5-Coder-7B-Q4_K_M | 4.5 GB | 16 GB RAM | ⭐⭐⭐⭐ |
| CPU (32GB RAM) | Qwen2.5-Coder-7B-Q6_K | 6 GB | 32 GB RAM | ⭐⭐⭐⭐⭐ |
| GPU (16GB VRAM) | Qwen2.5-Coder-14B-AWQ | 8 GB | 16 GB VRAM | ⭐⭐⭐⭐ |
| GPU (24GB VRAM) | Qwen2.5-Coder-32B-AWQ | 18 GB | 24 GB VRAM | ⭐⭐⭐⭐⭐ |
| Multi-GPU | Qwen2.5-Coder-32B | 64 GB | 48 GB+ VRAM | ⭐⭐⭐⭐⭐ |

### Why Qwen2.5-Coder for C++?

1. **Code-Specific Training**: Trained on 5.5 trillion tokens including extensive C/C++ codebases
2. **Long Context**: Supports up to 128K context (model dependent), crucial for large files
3. **Instruction Following**: Excellent at following code review instructions
4. **Multi-Language**: Understands C++, CMake, Makefiles, and documentation together

### Alternative Models

- **DeepSeek-Coder-V2**: Strong alternative, especially for complex algorithmic code
- **CodeLlama-34B**: Meta's coding model, good C++ support
- **StarCoder2**: Open-source, trained on The Stack v2

---

## Troubleshooting

### LM Studio Issues

**Problem:** Model won't load
- **Solution:** Check RAM availability, try smaller quantization (Q4_0 instead of Q4_K_M)

**Problem:** Very slow inference
- **Solution:** Reduce context length, close other applications, ensure CPU supports AVX2

### Ollama Issues

**Problem:** `ollama: command not found`
- **Solution:** Restart terminal or add to PATH: `export PATH=$PATH:/usr/local/bin`

**Problem:** Model download fails
- **Solution:** Check internet connection, try `ollama pull` again

### vLLM Issues

**Problem:** CUDA out of memory
- **Solution:** Reduce `--max-model-len`, use AWQ quantized model, lower `--gpu-memory-utilization`

**Problem:** Model not found
- **Solution:** Check Hugging Face model name, ensure you have access (some models are gated)

### AnythingLLM Issues

**Problem:** Cannot connect to LLM provider
- **Solution:** 
  1. Verify the LLM server is running (`curl http://localhost:PORT/v1/models`)
  2. Check firewall settings
  3. Verify Base URL in settings matches server address

**Problem:** Embedding fails
- **Solution:** Configure an embedding model in AI Providers → Embedder

**Problem:** Slow document processing
- **Solution:** Process smaller batches, use a dedicated embedding model

---

## Quick Reference Commands

### LM Studio
```powershell
# Server runs via GUI - no CLI needed
# Default API: http://localhost:1234/v1
```

### Ollama
```powershell
# List models
ollama list

# Pull model
ollama pull qwen2.5-coder:7b

# Run interactive
ollama run qwen2.5-coder:7b

# Check service
ollama serve
```

### vLLM
```bash
# Start server
vllm serve MODEL_NAME --host 0.0.0.0 --port 8000

# Check status
curl http://localhost:8000/v1/models -H "Authorization: Bearer API_KEY"

# View logs (systemd)
sudo journalctl -u vllm -f
```

### Docker (AnythingLLM)
```bash
# Start
docker compose up -d

# Stop
docker compose down

# View logs
docker logs -f anythingllm

# Restart
docker compose restart
```

---

## Summary

### Track 1: Single User (Windows 11)

| Scenario | Setup Time | Best For |
|----------|------------|----------|
| **A + B** (LM Studio/Ollama CPU + AnythingLLM Desktop) | 30 min | Individual developer, no GPU |
| **A + C** (LM Studio/Ollama GPU + AnythingLLM Desktop) | 30 min | Individual developer, GUI preference |
| **A + C Alt** (vLLM WSL + AnythingLLM Desktop) | 1 hour | Individual developer, max GPU performance |
| **A + B + D** (Ollama CPU + Coding Agent Integration) | 1 hour | Brownfield developer, no GPU |
| **A + C + D** (Ollama GPU or vLLM WSL + Coding Agents) | 1-2 hours | Brownfield developer, with GPU |

### Track 2: Multi-User / GPU Server (Production)

| Scenario | Setup Time | Best For |
|----------|------------|----------|
| **E + F** (vLLM + AnythingLLM Docker) | 2-3 hours | Development team, production use |
| **E + F + G** (+ Coding Agent Integration) | 4-6 hours | Brownfield development team |

### Tool Selection Quick Guide

| Priority | CPU Only | GPU (GUI preference) | GPU (Max Performance) |
|----------|----------|---------------------|----------------------|
| **Ease of use** | LM Studio | LM Studio | Ollama |
| **Automation/Scripting** | Ollama | Ollama | vLLM (WSL) |
| **Coding Agent Integration** | Ollama | Ollama | vLLM (WSL) |
| **Maximum Throughput** | N/A | Ollama | vLLM (WSL) |

> **When to Consider Native Linux:** For heavy GPU workloads, automation-heavy setups, or if you plan to scale to multi-user, native Linux eliminates WSL overhead (5-10% faster inference) and provides the standard ML production environment. Windows remains ideal for casual use, GUI preference, or when your primary work is Windows-based development.

### Choosing Your Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    START HERE                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │  Single user or team?  │
                 └────────────────────────┘
                    │                │
                 Single            Team
                    │                │
                    ▼                ▼
         ┌──────────────┐    ┌──────────────┐
         │  Have GPU?   │    │   TRACK 2    │
         └──────────────┘    │  Part E + F  │
           │          │      │  (GPU Server)│
          No         Yes     └──────────────┘
           │          │              │
           ▼          ▼              │
      ┌────────┐ ┌─────────────────┐ │
      │ Part B │ │    Part C       │ │
      │(No GPU)│ │ ┌─────────────┐ │ │
      │Ollama/ │ │ │ GUI? → LM   │ │ │
      │LMStudio│ │ │      Studio │ │ │
      └────────┘ │ │ CLI? → vLLM │ │ │
           │     │ │      (WSL)  │ │ │
           │     │ └─────────────┘ │ │
           │     └─────────────────┘ │
           │          │              │
           └────┬─────┘              │
                ▼                    ▼
         ┌─────────────────────────────────┐
         │  Working on brownfield/legacy   │
         │  code with coding agents?       │
         └─────────────────────────────────┘
                    │                │
                   Yes              No
                    │                │
                    ▼                ▼
              ┌──────────┐    ┌──────────────┐
              │  Add     │    │  Done!       │
              │ Part D/G │    │              │
              │(Ollama or│    │              │
              │ vLLM rec)│    │              │
              └──────────┘    └──────────────┘
```

For C++ code review, the **Qwen2.5-Coder** family provides the best balance of code understanding, instruction following, and availability across different hardware configurations.

For brownfield projects, **AnythingLLM becomes your system's long-term memory and explanation layer**, while coding agents focus on **changing code safely and precisely**.
