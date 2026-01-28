# DRAFT: Hardware Recommendations for Local AI (C++ Stack)

To run the models in your "Model Stack" (**DeepSeek-R1 Distill** and **Qwen2.5-Coder-32B**) efficiently, hardware requirements depend heavily on **Quantization** (compression) and the specific model parameter size you choose.

Since you are targeting **32B** and **70B** class models, standard gaming PCs with 8GB-16GB VRAM will struggle.

### The "Sweet Spot" Recommendation
**Target:** Run **32B models** (Qwen & R1-Distill) at **4-bit quantization**.
* **Minimum VRAM:** **24 GB**
* **Best Value GPU:** Used **NVIDIA RTX 3090** (~$700) or new **RTX 4090**.

---

### Hardware Tiers for Your Stack

| Tier | Hardware Specs | What It Runs | Performance |
| :--- | :--- | :--- | :--- |
| **Entry Level**<br>*(Standard Laptop/PC)* | **GPU:** 8GB - 16GB VRAM<br>(RTX 3060/4060/4070)<br>**RAM:** 32GB System RAM | **Can NOT run 32B comfortably.**<br>Must downgrade to:<br>• *Qwen2.5-Coder-14B*<br>• *DeepSeek-R1-Distill-Qwen-14B* | **Fast** for 14B models.<br>Cannot handle the 32B models in your stack without offloading to CPU (very slow). |
| **The "Golden" Standard**<br>*(High-End Consumer)* | **GPU:** **24GB VRAM**<br>(RTX 3090 / 4090)<br>**RAM:** 64GB System RAM | **Runs 32B Models @ 4-bit.**<br>• *Qwen2.5-Coder-32B* (Typically fits fully on GPU at 4-bit, context-dependent)<br>• *DeepSeek-R1-Distill-32B* | **Fast (highly variable).**<br>Often excellent for interactive use; speed depends on engine, quant type, and context length. |
| **The Pro Workstation**<br>*(Multi‑GPU or Big Unified Memory)* | **GPU:** **2×24GB** (e.g., 2× RTX 3090/4090) or **48–80GB single GPU** (e.g., RTX 6000 Ada / data-center cards)<br>**Alt:** **Mac Studio/MBP (Apple Silicon)** with 64GB+ Unified Memory | **Runs 70B Models @ 4-bit** (with a multi‑GPU stack that supports tensor-parallel; still context-dependent), or with unified memory on Mac (slower).<br>**Note:** 32B at **FP16** needs **~64GB** just for weights, so it generally requires **80GB-class** GPUs, unified memory, or CPU offload. | **Elite (but stack-dependent).**<br>Multi‑GPU scaling depends on the inference server. NVLink is not required in many setups; what matters is tensor‑parallel support. |

### Technical Details (Why 24GB?)

1.  **Memory Math for 32B Models:**
    * A 32-billion parameter model at **FP16** (original precision) requires **~64GB VRAM**.
    * At **4-bit Quantization (Q4_K_M)**, it shrinks to **~19-20GB**.
    * **Overhead:** You also need VRAM for **KV cache** (context window), plus runtime overhead (layers, buffers, etc.). This overhead grows with **context length** and varies by engine and cache precision.
    * **Result:** A **24GB** card is a practical target for 32B @ 4-bit, but **very large contexts (e.g., 16k+) can become tight** depending on your serving stack and settings.

2.  **Mac vs. PC:**
    * **PC (NVIDIA):** Significantly faster token generation (critical for code completion). Best for the "Typist" role (Qwen).
    * **Mac (Apple Silicon):** Slower, but **Unified Memory** lets you access 96GB or 128GB of RAM as VRAM. If you want to run the massive **70B** DeepSeek-R1-Distill, a Mac Studio-class machine can be cost-effective versus building a multi‑GPU NVIDIA box (region/prices vary).

### Summary Recommendation

* **If you have a Desktop PC:** Buy a used **RTX 3090 (24GB)**. It is the cheapest way to unlock 32B models locally.
* **If you are buying a new Laptop:** Get a **MacBook Pro M3/M4 Max** with at least **64GB Unified Memory**. Do not buy a Windows laptop with an RTX 4090 Mobile (16GB) for this specific workflow, as the VRAM is too low for 32B models.
