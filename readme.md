# Infinite Web Arena (IWA)

## Chutes LLM Integration

You can use [Chutes](https://chutes.ai) as your LLM backend, replacing OpenAI. Chutes provides OpenAI-compatible endpoints with your own models and API keys.

### Configuration

Set the following environment variables in your `.env` file or environment:

```
LLM_PROVIDER=chutes
CHUTES_BASE_URL=https://your-username-your-chute.chutes.ai/v1
CHUTES_API_KEY=cpk_your_api_key_here
CHUTES_MODEL=meta-llama/Llama-3.1-8B-Instruct
CHUTES_MAX_TOKENS=2048
CHUTES_TEMPERATURE=0.7
CHUTES_USE_BEARER=False  # Set to True if your API key must be sent as Bearer token
```

- `CHUTES_BASE_URL` should be the base URL of your deployed Chute (ending with `/v1`).
- `CHUTES_API_KEY` is your Chutes API key (see Chutes dashboard).
- `CHUTES_MODEL` is the model name deployed in your Chute.
- `CHUTES_USE_BEARER` (optional): If True, sends the API key as `Authorization: Bearer ...` header. Otherwise, uses `X-API-Key`.

### Usage

Once configured, all LLM calls will use your Chutes deployment. No code changes are needed—just set the environment variables and run your application or tests.

For more information on deploying a Chute, see [Chutes documentation](https://docs.chutes.ai/).

## Synthetic Evaluation Benchmark for Web Agents

Welcome to **Infinite Web Arena (IWA)**, a revolutionary **autonomous web agent evaluation framework** that transcends traditional benchmarking limitations. Unlike existing benchmarks that rely on human-curated datasets and manual validation, IWA creates an **infinitely scalable evaluation environment** through **generative AI** and **synthetic data**. This automation enables continuous testing against novel web scenarios without human bottlenecks, ensuring comprehensive evaluation of web agents' capabilities.

---

## Core Features

### 🔄 Dynamic Web Generation

- Meta-programming and LLMs create infinite variants of websites
- Continuously introduces new challenges that prevent memorization
- Ensures agents face realistic, evolving scenarios

### 🤖 Automated Task & Test Generation

- LLMs autonomously produce tasks and corresponding tests
- No dependency on human task designers
- Generates validation criteria before execution

### 🌐 Browser Execution & Analysis

- Launches real browser instances for authentic web interaction
- Records and analyzes every agent action and DOM state
- Captures complete interaction flow for evaluation
- Enables deep inspection of agent decision-making

### 📊 Smart Evaluation System

- Combines predefined tests with LLM-based analysis
- Evaluates success through both quantitative and qualitative metrics
- Leverages the key insight that verifying a task is simpler than performing it
- Provides granular scoring across multiple success criteria

<br>

## 🔍 The Key to Validation: Tests

The strength of IWA lies in its holistic testing methodology. By managing both frontend and backend environments, we can evaluate web agent behavior across multiple layers, ensuring a comprehensive assessment of their capabilities. Directly integrating GenAI into web agent validation introduces a circular dependency, as it requires the validation logic to surpass the intelligence of the agents being tested. The solution is to distill the problem to its core and anchor it to a logical combination of predefined "conditions" or "events." Ultimately, success is determined by a logical function of these conditions, which, when true, unambiguously defines success in the task.

### 🖥️ Frontend Tests

- **DOM Analysis**: Inspect HTML structure changes and state transitions
- **Network Activity**: Monitor API calls and data exchanges
- **Visual Verification**: Compare screenshots and UI states
- **Browser Events**: Track JavaScript execution and user interactions

### ⚙️ Backend Tests

* **Event Tracking**: Capture backend event emissions
* **State Validation**: Verify database and system changes
* **Process Flow**: Confirm complete business logic execution
* **Custom Events**: Leverage controlled environment for deep inspection

---

### 🌍 Real-World Applications

While validation occurs in controlled environments, agents develop skills directly applicable to production websites:

- Navigate complex DOM structures
- Handle dynamic content loading
- Process real-world UI patterns
- Adapt to varying website architectures

---

## 💡 Example Use Case

Consider a typical e-commerce task:

### 1️⃣ Task Generation

```
Task: "Buy a red dress for less than $10"
Tests: Verify Purchase() event with parameters
      (item: "red dress", price < $10)
```

### 2️⃣ Agent Execution

- Navigate site
- Search for product
- Apply filters
- Complete purchase

### 3️⃣ Validation

* Verify correct item selection
* Check price constraints
* Confirm purchase completion

---

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run setup script:

   ```bash
   bash setup.sh
   ```

📖 For a detailed guide, check out the [Setup Guide](docs/guides/setup.md).

---

## 🧪 Running the Benchmark

The benchmark evaluates different agents against generated tasks, tests, and websites. Configure and execute with ease:

### 🛠️ Configuration Variables (in `benchmark.py`)

| Variable                     | Description                       | Example                  |
| ---------------------------- | --------------------------------- | ------------------------ |
| `PROJECTS_TO_RUN`            | List of demo projects to evaluate | `[demo_web_projects[0]]` |
| `PROMPT_PER_USE_CASE_CONST`  | Prompts per use case              | `1`                      |
| `PLOT_BENCHMARK_RESULTS`     | Plot result graphs                | `False`                  |
| `SAVE_EVALUATION_RESULTS`    | Save result JSONs                 | `False`                  |
| `USE_CACHED_TASKS_CONST`     | Use pre-generated tasks           | `False`                  |
| `USE_CACHED_SOLUTIONS_CONST` | Use precomputed agent solutions   | `False`                  |
| `EVALUATE_REAL_TASKS_CONST`  | Evaluate on real web URLs         | `False`                  |
| `RETURN_EVALUATION_GIF`      | Record UI interactions as GIF     | `True`                   |
| `LOG_FILE`                   | Benchmark log file path           | `"benchmark.log"`        |

### ⚙️ Example Agent Configuration

Edit the `AGENTS` list to define which agents to test:

```python
AGENTS = [
    ApifiedWebAgent(id="2", name="OpenAICUA", host="127.0.0.1", port=5005, timeout=300),
    # ApifiedWebAgent(id="3", name="AnthropicCUA", port=5010, ...)
]
```

Ensure all services are up before starting.

### ▶️ Run the Benchmark

```bash
python benchmark.py
```

### 📁 Outputs

* **GIFs**: Saved in `recordings/<agent_name>/<task_id>.gif`
* **Logs**: Stored in `benchmark.log`
* **Metrics** (optional): JSONs and plots in `config.output_dir`

### 🧹 Reset Cache (Optional)

```bash
rm -rf ~/.autoppia_cache/tasks/
rm -rf ~/.autoppia_cache/solutions/
```

---

## 📜 License

© 2024 Autoppia. All rights reserved.

---

