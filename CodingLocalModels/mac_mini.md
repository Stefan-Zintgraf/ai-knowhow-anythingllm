# Mac mini (Apple Silicon) – Local Model Memory & Model Picks

This note captures the **actual memory limits** observed on a Mac mini running **Ollama** and recommends **which local models to use** for the roles/use-cases defined in `CodingLocalModels/model_stack.md`.

## 1) Memory available for AI models (measured)

### Total unified memory (system RAM)

Command:

```bash
sysctl -n hw.memsize
```

Result:

- **17179869184 bytes = 16 GiB total unified memory**

This is the *total* RAM shared by macOS + all apps + the GPU (unified memory architecture).

### Ollama / Metal “VRAM” budget (effective on‑GPU memory)

From `ollama serve` logs on this machine:

- **GPU backend**: Metal (`name=Metal description="Apple M2"`)
- **total**: **10.7 GiB**
- **available**: **10.7 GiB**
- Ollama enters **low VRAM mode** because it is below the 20 GiB threshold:
  - `entering low vram mode ... total vram="10.7 GiB" threshold="20.0 GiB"`

**Practical implication:** on this Mac mini, assume roughly **10–11 GiB** is the workable “fits well on GPU” budget for:

- model weights (quantized),
- KV cache (context window),
- runtime overhead (buffers, graphs, etc.).

If a model doesn’t fit inside this budget, Ollama may **offload/spill** to CPU/RAM (works, but performance typically drops a lot).

## 2) What models to use on this Mac mini (aligned to `model_stack.md`)

Your `model_stack.md` defines these roles:

- **The Architect** (Planning & Architecture)
- **The Builder** (Primary Agent – Cloud)
- **The Auditor** (Code Reviewer)
- **The Fixer** (Logic/Debug – Local)
- **The Typist** (Fast Completion – Local)

Because this machine has an effective **~10.7 GiB Metal budget**, you should generally target **7B–14B class models** in 4-bit quantization for smooth local use.

### Recommended “Mac mini friendly” mapping (7B–14B class)

| Role (from `model_stack.md`) | Use-case | Recommended local model(s) on this Mac mini | Notes (fit/speed/privacy) |
| :--- | :--- | :--- | :--- |
| **Planning & Architecture** *(The Architect)* | System design, step-by-step plans, tradeoffs | **DeepSeek‑R1 distilled 7B–14B** (Qwen-distill variants where available) | Full DeepSeek‑R1 is typically too large; distilled 14B is the realistic ceiling for “good” local reasoning on ~10.7 GiB. |
| **Primary Agent (Cloud)** *(The Builder)* | Writing production code | **Claude 3.5 Sonnet** (cloud) | Keep the “builder” in the cloud as your doc suggests; this Mac mini is better used as a private reviewer/typist. |
| **Code-Reviewer** *(The Auditor)* | Concurrency reasoning, bug finding, “prove deadlock?” | **DeepSeek‑R1 distilled 7B–14B** | Works well for local review, but watch context length: long traces + CoT can fill context quickly. |
| **Logic/Debug (Local)** *(The Fixer)* | Backtraces, template errors, “why is ptr dangling?” | **DeepSeek‑R1 distilled 7B–14B** | On this hardware, treat “Fixer” as a distilled R1, not 70B-class. Use smaller context where possible. |
| **Fast Completion (Local)** *(The Typist)* | Boilerplate, snippets, unit test scaffolding | **Qwen2.5‑Coder 7B** (fast) or **Qwen2.5‑Coder 14B** (better, slower) | **Qwen2.5‑Coder‑32B** is not a good fit on ~10.7 GiB; expect heavy offload and slowdowns. |

### “Do / Don’t” for this Mac mini

- **Do**:
  - Prefer **7B** for “instant” typing/autocomplete style prompts.
  - Use **14B** when you need noticeably better reasoning/review quality.
  - Keep prompts tight; paste only the relevant files/functions.

- **Don’t**:
  - Expect **32B** or **70B** class models to be pleasant locally on this machine.
  - Force huge context windows (e.g., 32k) unless you accept major speed/fit tradeoffs—KV cache cost grows with context.

### Context window guidance (important for R1-style reasoning)

`model_stack.md` recommends forcing a large context window for DeepSeek‑R1. On this Mac mini, that advice needs tempering:

- Larger context windows significantly increase **KV cache** memory usage.
- With an effective **~10.7 GiB** GPU budget, you will usually get the best experience using a **moderate context** (commonly 4k–8k) and keeping inputs focused.

