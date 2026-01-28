# C++ AI Development: The "Golden Stack" Workflow

This guide outlines the optimal workflow for combining Anthropic's **Claude Code** (CLI) with local open-source models (**DeepSeek-R1**, **Qwen2.5**) to create a high-performance, cost-effective C++ development environment.

## 1. The Model Strategy

This hybrid approach leverages "Reasoning Models" for architecture and safety, "Frontier Models" for implementation, and "Small Models" for speed.

| Role | Recommended Model | Why & Example Task |
| :--- | :--- | :--- |
| **Planning & Architecture**<br>*(The Architect)* | **DeepSeek-R1** | **The "Thinker."** It visualizes complex system interactions before code is written, catching design flaws early.<br><br>**Example:** *"Analyze requirements for a high-frequency trading engine and output a class diagram with memory-alignment strategies."* |
| **Primary Agent (Cloud)**<br>*(The Builder)* | **Claude 3.5 Sonnet** | **The "Worker."** currently the most capable engineer for synthesizing code. It follows the R1 plan and writes clean, maintainable C++.<br><br>**Example:** *"Take the architecture plan above and implement the `OrderBook` class using `std::map`."* |
| **Code-Reviewer**<br>*(The Auditor)* | **DeepSeek-R1** | **The "Critic."** Uses Chain-of-Thought reasoning to find invisible logic bugs like race conditions that standard models miss.<br><br>**Example:** *"Review this mutex wrapper. Walk through the locking logic step-by-step to prove if a deadlock is possible."* |
| **Logic/Debug (Local)**<br>*(The Fixer)* | **DeepSeek-R1 (Distilled)**<br>*(e.g., Llama-70B)* | **The "Debugger."** Fixes segfaults or tricky template errors privately without cloud latency.<br><br>**Example:** *"Here is a GDB backtrace. Explain why the `shared_ptr` is dangling in this edge case."* |
| **Fast Completion (Local)**<br>*(The Typist)* | **Qwen2.5-Coder-32B** | **The "Speedster."** Runs locally for instantaneous boilerplate generation.<br><br>**Example:** *"Generate standard getters, setters, and the `operator<<` overload for this struct."* |

---

## 2. Environment Setup

### Prerequisites
1.  **Ollama**: Run your local models.
    *CRITICAL: DeepSeek-R1 generates long "Chain of Thought" reasoning which fills context quickly. Default Ollama context (2k-8k) is too small. Force a 32k window:*
    ```bash
    OLLAMA_NUM_CTX=32768 ollama serve
    ```
2.  **LiteLLM**: Proxy to make local models look like Anthropic's API.
    ```bash
    litellm --model ollama/deepseek-r1:latest --alias deepseek-r1 --port 8000
    ```

### Bash Configuration (`~/.bashrc` or `~/.zshrc`)

Copy the following script to your shell configuration to automate the workflow.

```bash
# --- C++ Golden Stack Configuration ---

# Configuration
# export CLAUDE_API_KEY via a secrets manager or .env file (do NOT hardcode)       # Your actual Anthropic Key
export LOCAL_PROXY_URL="[http://127.0.0.1:8000/v1](http://127.0.0.1:8000/v1)" # LiteLLM address

# 1. THE ARCHITECT (Planning) -> DeepSeek-R1
# Usage: c-plan "Create a roadmap for a thread-safe logging library"
function c-plan() {
    echo -e "\033[1;34m🤖 ARCHITECT MODE (DeepSeek-R1)\033[0m"
    echo -e "\033[0;33mTask: Drafting Requirements & Architecture...\033[0m"
    
    # Route to local proxy and inject System Prompt for planning
    ANTHROPIC_BASE_URL="$LOCAL_PROXY_URL" \
    ANTHROPIC_API_KEY="sk-dummy" \
    claude -p "ACT AS ARCHITECT. Output a strict Step-by-Step Implementation Plan. Do not write code yet. $1"
}

# 2. THE BUILDER (Coding) -> Claude 3.5 Sonnet
# Usage: c-build "Implement step 1 from the plan"
function c-build() {
    echo -e "\033[1;32m🚀 BUILDER MODE (Claude 3.5 Sonnet)\033[0m"
    echo -e "\033[0;33mTask: Writing Production Code...\033[0m"
    
    # Standard Anthropic API call
    claude "$1"
}

# 3. THE AUDITOR (Reviewing) -> DeepSeek-R1
# Usage: c-review "Check main.cpp for race conditions"
function c-review() {
    echo -e "\033[1;31m🧐 AUDITOR MODE (DeepSeek-R1)\033[0m"
    echo -e "\033[0;33mTask: Reasoning & Safety Review...\033[0m"
    
    ANTHROPIC_BASE_URL="$LOCAL_PROXY_URL" \
    ANTHROPIC_API_KEY="sk-dummy" \
    claude -p "ACT AS CODE REVIEWER. Analyze the following code/request for logic errors, memory leaks, and concurrency issues. Think step-by-step. $1"
}

# 4. THE TYPIST (Fast Completion) -> Qwen 2.5 Coder
# Note: Pipes directly to Ollama for speed
function c-fast() {
    echo -e "\033[1;36m⚡ TYPIST MODE (Qwen 2.5)\033[0m"
    echo "Processing..."
    
    echo "$1" | ollama run qwen2.5-coder:32b
}

# 5. WORKFLOW HELPER
function c-help() {
    echo "---------------------------------------------------"
    echo "C++ AI Development Stack"
    echo "---------------------------------------------------"
    echo "c-plan   : DeepSeek-R1      (Architecture/Specs)"
    echo "c-build  : Claude 3.5 Sonnet (Implementation)"
    echo "c-review : DeepSeek-R1      (Safety/Logic Check)"
    echo "c-fast   : Qwen 2.5         (Boilerplate/Snippets)"
    echo "---------------------------------------------------"
}
```

---

## 3. Practical Workflow Example

This scenario demonstrates building a **Thread-Safe Ring Buffer** using the aliases defined above.

### Step 1: The Blueprint (DeepSeek-R1)
**Goal:** Create a solid architectural plan before writing code to avoid logical pitfalls.
```bash
c-plan "I need a high-performance, thread-safe Ring Buffer in C++20. 
Requirements:
1. Lock-free single-producer/single-consumer (SPSC) support.
2. Optional mutex-based multi-producer/multi-consumer (MPMC) mode.
3. Use std::atomic for head/tail pointers.
Output a strict implementation plan with function signatures."
```

### Step 2: The Construction (Claude 3.5 Sonnet)
**Goal:** Turn the plan into high-quality production code.
```bash
c-build "Read the plan above. Implement the SPSC (Single-Producer Single-Consumer) version first. 
Use a template class `RingBuffer<T, Size>`. 
Ensure memory alignment using `alignas` to prevent false sharing."
```

### Step 3: The Audit (DeepSeek-R1)
**Goal:** Verify the tricky concurrency logic that standard models often get wrong.
```bash
c-review "Analyze the `push()` and `pop()` methods in the code above. 
Focus strictly on memory ordering (acquire/release semantics). 
Is there a potential race condition if the buffer is full?"
```

### Step 4: The Boilerplate (Qwen 2.5)
**Goal:** Quickly generate standard unit tests without wasting expensive model credits.
```bash
c-fast "Write a Google Test (gtest) file for this RingBuffer. 
Include test cases for: 
1. Full buffer
2. Empty buffer
3. Wrap-around behavior"
```
