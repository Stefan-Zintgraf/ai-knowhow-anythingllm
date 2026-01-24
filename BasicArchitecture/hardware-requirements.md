# Local LLM Hardware Requirements

This document provides guidance for planning workstation and server builds that balance large context windows with practical hardware limits—particularly for **C++ coding and code-review workflows** using AnythingLLM with coding agents.

---

## Table of Contents

**General**

1. [Memory Limits & Constraints](#1-memory-limits--constraints)
2. [Context Capacity Formulas](#2-context-capacity-formulas)
3. [Strategies to Extend Context](#3-strategies-to-extend-context)
   - [Hardware for Extreme Context Windows (200k–1M)](#31-hardware-for-extreme-context-windows-200k1m-tokens)

**Use Case: Single-User with GPU + Coding Agent**

4. [Single-User Hardware Recommendations](#4-single-user-hardware-recommendations)
5. [Single-User Configuration](#5-single-user-configuration)

**Use Case: Multi-User GPU Server + Coding Agents**

6. [Multi-User Server Hardware Recommendations](#6-multi-user-server-hardware-recommendations)
7. [Multi-User Configuration](#7-multi-user-configuration)

**Reference**

8. [Model Recommendations for C++ Development](#8-model-recommendations-for-c-development)
9. [Quick Checklists](#9-quick-checklists)

---

# General

## 1. Memory Limits & Constraints

### A) Model context limit (hard cap)

Each model has a maximum supported context length (e.g., 32k, 128k, 200k, 1M) defined in its config (`max_position_embeddings`, `max_seq_len`, etc.).

> **Hardware alone cannot exceed the model's native limit.**  
> You can attempt RoPE scaling / YaRN context-extension methods, but reliability and quality vary.

### B) Runtime memory limit (your machine)

Even if a model supports 200k/1M, you still need enough memory for:

- **Model weights** (in VRAM and/or RAM)
- **KV cache** (dominant cost for long context)
- Runtime overhead (activations, workspace buffers, fragmentation)

---

## 2. Context Capacity Formulas

### Total VRAM needed

$$\text{Total VRAM} = \text{Model Weights} + \text{KV Cache}$$

### Model weights (4-bit quantized)

$$\text{Weights (GB)} \approx \text{Parameters (B)} \times 0.7$$

| Model | Approx weights |
| :--- | :--- |
| Qwen-2.5-32B / Qwen Coder 32B | ~20–24 GB |
| Llama-3-70B | ~40–49 GB |
| DeepSeek-R1 (distilled) | ~40 GB |

### KV cache (detailed)

$$\text{KV bytes/token} = 2 \times L \times H_{kv} \times D_{head} \times \text{bytes\_per\_element}$$

- `L` = transformer layers
- `H_kv` = KV heads (often < attention heads due to GQA/MQA)
- `D_head` = head dimension
- `bytes_per_element` = 2 (FP16), 1 (FP8/int8)

**Example (8B-class model, FP16 KV):** ~128 KB/token → 200k tokens ≈ 25.6 GB KV cache alone.

**Rule of thumb for 70B models at FP16:** ~1 GB VRAM per 4k tokens.

---

## 3. Strategies to Extend Context

### Path A: System RAM offloading (Slow & Cheap)

- **Hardware:** 128–256 GB DDR5 (~€400–€800).
- **Behavior:** Once VRAM saturates, the KV cache spills to CPU/RAM → ~1–3 tokens/sec after the first ~32k tokens.
- **Best for:** Occasional massive-context analysis where latency is acceptable.

### Path B: Unified memory on Apple Silicon

- **Hardware:** Mac Studio M2/M3 Ultra with 192 GB unified memory.
- **Behavior:** GPU can access the full memory pool → stable 10–15 tokens/sec even past 150k context.

### Path C: Context / KV cache quantization (Software trick)

- **Hardware:** Existing GPUs.
- **Mechanism:** Use loaders like `llama.cpp` (`-ctk q8_0` / `-ctk q4_0`) or ExLlamaV2 to shrink the KV cache from FP16 to FP8/int8/4-bit.
- **Result:** ~2–4× the context per VRAM. On dual 4090s you might reach 64k–90k for a 70B model; 200k remains out of reach without offloading.

### Path D: RoPE / YaRN context extension

- **Mechanism:** Rescale positional embeddings (YaRN, NTK scaling) to stretch a model beyond its pretrained context.
- **Trade-off:** Quality may degrade at the far end of the extended window; not all models respond well.

---

## 3.1 Hardware for Extreme Context Windows (200k–1M tokens)

For use cases requiring very large context windows (analyzing entire codebases, long documents, or extensive conversation history), specialized hardware configurations are needed.

### 200k Context Window Requirements

| Model Size | Hardware Option | Speed | Cost |
| :--- | :--- | :--- | :--- |
| 8B model | Single RTX 4090 (24 GB) + KV quantization | ⚡ Fast | ~€2,000 |
| 8B model | Single RTX 5090 (32 GB) | ⚡ Fast | ~€2,500 |
| 32B model | Dual RTX 4090 (48 GB) + KV offload to RAM | 🐢 Slow | ~€5,000 |
| 32B model | Single A100 (80 GB) | ⚡ Fast | ~€15,000 |
| 32B model | Mac Studio M3 Ultra (192 GB unified) | ⚡ Moderate | ~€6,000 |
| 70B model | 4× RTX 4090 (96 GB) tensor parallel | ⚡ Moderate | ~€12,000 |
| 70B model | Dual A100 (160 GB) | ⚡ Fast | ~€30,000 |

### 1M Context Window Requirements

| Model Size | Hardware Option | Speed | Cost |
| :--- | :--- | :--- | :--- |
| 8B model | RTX 4090 + 256 GB system RAM (KV offload) | 🐢 Very slow (1–3 tok/s) | ~€3,000 |
| 8B model | Mac Studio M3 Ultra (192 GB unified) | ⚡ Moderate (10–15 tok/s) | ~€6,000 |
| 32B model | 256 GB system RAM (full offload) | 🐢 Very slow (0.5–2 tok/s) | ~€4,000 |
| 32B model | 4× A100 (320 GB) tensor parallel | ⚡ Fast | ~€60,000 |
| 70B model | 8× A100 / H100 cluster | ⚡ Fast | €100,000+ |

### Practical Guidance for Extreme Context

> **Important:** Loading 200k–1M tokens of raw code into context is rarely the optimal approach for C++ development. Consider these alternatives first:

| Approach | When to Use | Hardware Impact |
| :--- | :--- | :--- |
| **RAG (Recommended)** | Large codebases, multi-file projects | Standard GPU sufficient |
| **Chunked analysis** | Processing files sequentially | Standard GPU sufficient |
| **Hybrid: RAG + moderate context** | Complex refactoring with history | 32k–64k context + RAG |
| **Full context load** | Single massive file, legal/compliance review | Requires extreme hardware |

### Hardware Summary by Context Goal

| Context Goal | Minimum Hardware | Recommended Hardware | Notes |
| :--- | :--- | :--- | :--- |
| 32k tokens | RTX 4070 (12 GB) | RTX 4090 (24 GB) | Most coding tasks |
| 64k tokens | RTX 4090 (24 GB) | RTX 5090 (32 GB) | Multi-file reviews |
| 128k tokens | Dual RTX 4090 (48 GB) | A100 (80 GB) | Module-level analysis |
| 200k tokens | A100 (80 GB) or Mac Studio Ultra | Dual A100 (160 GB) | Rare use cases |
| 1M tokens | Mac Studio Ultra (192 GB) | Multi-GPU cluster | Specialized workloads only |

### Cost vs. Context Trade-off

```
Context Window
     ▲
  1M │                                    ████ €100k+ (8× A100/H100)
     │                              ████ €30k (Dual A100)
     │                        ████ €15k (Single A100)
200k │                  ████ €6k (Mac Studio Ultra)
     │            ████ €5k (Dual RTX 4090 + RAM offload)
128k │      ████ €3.5k (Dual RTX 4090)
 64k │████ €2.5k (RTX 5090)
 32k │████ €2k (RTX 4090)
     └────────────────────────────────────────────────▶ Cost (€)
```

> **Recommendation:** For most C++ development workflows, invest in a good GPU (RTX 4090/5090) plus AnythingLLM for RAG rather than chasing extreme context windows. RAG provides better results for large codebases at a fraction of the cost.

---

# Use Case: Single-User with GPU + Coding Agent

This configuration is for individual developers on Windows 11 workstations with a local GPU, using AnythingLLM as a knowledge hub alongside coding agents (Cursor, Claude Code, Gemini CLI) for brownfield C++ projects.

## 4. Single-User Hardware Recommendations

### Recommended GPU Configurations

| GPU | VRAM | Best Model | Max Context | Cost |
| :--- | :--- | :--- | :--- | :--- |
| RTX 3060 12GB | 12 GB | Qwen2.5-Coder-7B-AWQ | 16k tokens | ~€350 |
| RTX 4070 | 12 GB | Qwen2.5-Coder-7B-Q6_K | 16k tokens | ~€600 |
| RTX 4080 | 16 GB | Qwen2.5-Coder-14B-AWQ | 8k tokens | ~€1,200 |
| RTX 4090 | 24 GB | Qwen2.5-Coder-14B-Q6_K | 16k tokens | ~€2,000 |
| RTX 5090 | 32 GB | Qwen2.5-Coder-32B-Q4_K_M | 32–64k tokens | ~€2,500 |

### System RAM Requirements

| Scenario | Minimum RAM | Recommended RAM |
| :--- | :--- | :--- |
| GPU-only inference (no offload) | 16 GB | 32 GB |
| KV cache offload for extended context | 64 GB | 128 GB |
| Running vLLM on WSL + AnythingLLM | 32 GB | 64 GB |

### Storage

- **SSD required:** Models are 4–20 GB; fast loading improves workflow
- **Recommended:** NVMe SSD with 500 GB+ free space for model storage

---

## 5. Single-User Configuration

### LLM Backend Options

| Tool | Best For | GPU Performance | Automation |
| :--- | :--- | :--- | :--- |
| **Ollama** | CLI workflows, coding agent integration | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **LM Studio** | GUI preference, model browsing | ⭐⭐⭐ | ⭐⭐ |
| **vLLM (WSL)** | Maximum throughput, power users | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation for Coding Agent Integration:** Use **Ollama** or **vLLM (WSL)** for their CLI-first design and background service operation.

### Architecture: RAG Hub + Code Indexer

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
│   History, Decisions)   │     │  ripgrep + ctags        │
└─────────────────────────┘     └─────────────────────────┘
```

### Workflow

1. **Query AnythingLLM** for project context (architecture, historical decisions, gotchas)
2. **Use code indexer** (ripgrep, ctags) for precise symbol locations
3. **Provide context** to coding agent (Cursor/Claude Code)
4. **After merge:** Update AnythingLLM with "what changed and why"

### Hardware vs. Task Fit

| Task | Token Budget | Recommended GPU |
| :--- | :--- | :--- |
| Single-file code review | 5k–15k | RTX 4070 / 4080 |
| Multi-file refactoring | 30k–60k | RTX 4090 / 5090 |
| Large codebase analysis | Use RAG | Any GPU + AnythingLLM |

### Latency Expectations (Single User)

| Scenario | Target tokens/sec | Achievable with |
| :--- | :--- | :--- |
| Interactive code completion | ≥30 | 7B model, RTX 4070+ |
| Code review / explanation | 10–15 | 14B model, RTX 4080+ |
| Complex refactoring context | 5–10 | 32B model, RTX 4090/5090 |

---

# Use Case: Multi-User GPU Server + Coding Agents

This configuration is for development teams with a dedicated GPU server, using AnythingLLM as a shared knowledge hub for brownfield C++ projects.

## 6. Multi-User Server Hardware Recommendations

### Recommended Server Configurations

| Team Size | GPU Configuration | Model | Concurrent Users | Cost |
| :--- | :--- | :--- | :--- | :--- |
| 2–5 developers | Single RTX 4090 (24 GB) | Qwen2.5-Coder-32B-AWQ | 2–3 | ~€5,000 |
| 5–10 developers | Dual RTX 4090 (48 GB) | Qwen2.5-Coder-32B | 5–8 | ~€8,000 |
| 10–20 developers | Single A100 (80 GB) | Qwen2.5-Coder-32B | 10–15 | ~€15,000 |
| 20+ developers | Dual A100 / H100 | Qwen2.5-Coder-32B (tensor parallel) | 20+ | €30,000+ |

### Server Specifications

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **CPU** | 8 cores | 16+ cores (Xeon/EPYC) |
| **System RAM** | 64 GB | 128 GB |
| **Storage** | 500 GB NVMe | 1 TB NVMe |
| **Network** | 1 Gbps | 10 Gbps |

### Why Ubuntu 22.04 LTS?

- Native NVIDIA CUDA support with minimal configuration
- Long-term support (until 2027)
- Best compatibility with vLLM and ML frameworks
- Excellent Docker integration
- Lower overhead than Windows Server

---

## 7. Multi-User Configuration

### LLM Backend: vLLM

vLLM is the recommended backend for multi-user deployments:

| Feature | Benefit |
| :--- | :--- |
| PagedAttention | 2–3× throughput improvement |
| Continuous batching | Efficient concurrent request handling |
| Native AWQ/GPTQ | GPU-optimized quantization |
| OpenAI-compatible API | Drop-in replacement for existing tools |

### Architecture: Gated Execution

```
┌─────────────────────────────────────────────────────────────────┐
│                     Coding Agents (Team)                         │
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

### Deployment Stack

| Component | Technology | Port |
| :--- | :--- | :--- |
| LLM Inference | vLLM (systemd service) | 8000 |
| Knowledge Hub | AnythingLLM (Docker) | 3001 |
| Reverse Proxy | Nginx + SSL | 443 |
| Authentication | AnythingLLM multi-user mode | — |

### Concurrent User Capacity

| GPU Config | Context per User | Max Concurrent |
| :--- | :--- | :--- |
| RTX 4090 (24 GB) | 4k tokens | 3–4 users |
| RTX 4090 (24 GB) | 8k tokens | 2 users |
| Dual RTX 4090 (48 GB) | 8k tokens | 4–5 users |
| A100 (80 GB) | 8k tokens | 8–10 users |

### Two-Speed Knowledge Model

| Knowledge Type | Storage | Update Frequency |
| :--- | :--- | :--- |
| **Long-lived** (architecture, ADRs, standards) | AnythingLLM | Rarely |
| **Ephemeral** (session files, diffs, logs) | Per-session | Discarded |

This prevents the RAG corpus from becoming cluttered while maintaining valuable project memory.

### Network & Security

| Requirement | Implementation |
| :--- | :--- |
| HTTPS | Nginx + Let's Encrypt / internal CA |
| Authentication | AnythingLLM multi-user mode |
| API Security | vLLM `--api-key` flag |
| Firewall | UFW: allow 22, 80, 443 only |

---

# Reference

## 8. Model Recommendations for C++ Development

### Summary Table

| Use Case | Model | Size | Min VRAM | Quality |
| :--- | :--- | :--- | :--- | :--- |
| Single-user (12GB VRAM) | Qwen2.5-Coder-7B-AWQ | 4 GB | 12 GB | ⭐⭐⭐⭐ |
| Single-user (16GB VRAM) | Qwen2.5-Coder-14B-AWQ | 8 GB | 16 GB | ⭐⭐⭐⭐ |
| Single-user (24GB VRAM) | Qwen2.5-Coder-14B-Q6_K | 10 GB | 24 GB | ⭐⭐⭐⭐⭐ |
| Multi-user (24GB VRAM) | Qwen2.5-Coder-32B-AWQ | 18 GB | 24 GB | ⭐⭐⭐⭐⭐ |
| Multi-user (48GB+ VRAM) | Qwen2.5-Coder-32B | 64 GB | 48 GB | ⭐⭐⭐⭐⭐ |

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

## 9. Quick Checklists

### Single-User Setup Checklist

- [ ] GPU with 12GB+ VRAM (RTX 3060 minimum, RTX 4090/5090 recommended)
- [ ] 32GB+ system RAM
- [ ] Install Ollama or vLLM (WSL)
- [ ] Pull Qwen2.5-Coder model appropriate for VRAM
- [ ] Install AnythingLLM Desktop
- [ ] Configure LLM provider connection
- [ ] Install ripgrep and ctags for code indexing
- [ ] Create workspace structure for project knowledge

### Multi-User Server Setup Checklist

- [ ] Ubuntu 22.04 LTS server with NVIDIA GPU(s)
- [ ] 64GB+ system RAM
- [ ] Install NVIDIA drivers and CUDA
- [ ] Set up vLLM with systemd service
- [ ] Deploy AnythingLLM via Docker
- [ ] Configure multi-user authentication
- [ ] Set up Nginx reverse proxy with SSL
- [ ] Configure firewall (UFW)
- [ ] Create team workspaces with appropriate permissions

### To Measure Your Max Context

- [ ] Identify model's supported context (model card / config)
- [ ] Run with increasing context sizes
- [ ] Watch logs for KV allocation + OOM
- [ ] Monitor VRAM via `nvidia-smi` (stay below ~90%)
- [ ] Note latency degradation threshold

### To Push Toward Extended Context

- [ ] Use a model that supports ≥128k context
- [ ] Quantize weights (4-bit AWQ/GPTQ) to free VRAM
- [ ] Enable KV cache quantization (FP8/int8) if supported
- [ ] Consider system RAM offloading for occasional long-context tasks
- [ ] Keep concurrent sessions low on shared servers

---

## Notes / Terminology

- **Tokens** are subword units; 200k tokens ≈ many hundreds of pages of code
- **KV cache** stores attention keys/values so the model can attend to prior context efficiently
- **AWQ/GPTQ** are GPU-optimized quantization formats (vs. GGUF for CPU)
- **RAG** (Retrieval-Augmented Generation) retrieves relevant context rather than loading entire codebases
- **Long context** often benefits from careful prompting and retrieval strategies; raw 1M context is rarely the best way to solve large-repo problems
