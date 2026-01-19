# 🧪 Technical Test - Web Agents Developer

Hello! 👋

This technical test is designed to evaluate your skills in **React**, **Python/Backend**, and **critical thinking**. The goal is to demonstrate how you approach real problems and structure your code.

**⏱️ Estimated time**: ~2 hours
**💡 Strongly recommend using AI** (Cursor, Claude Code, ChatGPT, Copilot, etc.) - it's part of real work
**📝 Delivery format**: Git repository with descriptive commits

---

## 📋 Project Context

We're working on a **Web Agents** system that automates tasks on web applications. The system has:

- **Demo webs**: Next.js/React applications that simulate different services (cinema, books, hotels, CRM, etc.)
- **Agents**: Services that receive tasks and return sequences of actions (click, type, navigate, etc.)
- **Benchmark**: System that evaluates whether agents complete tasks correctly

Your work will be:
1. Add a new feature to a demo web (React)
2. Create a simple agent that can solve a specific task
3. Run the full benchmark against your agent

---

## 🎯 Part 1: React - New Section in Dashboard

### Objective
Add a new functional section to the dashboard of a demo web that sends events when interacted with.

### Specific Task

1. **Choose a demo web** (we recommend `web_8_autolodge` - hotel booking platform)
2. **Add a new section** to the main dashboard (`src/app/page.tsx`)
   - Must be coherent with the existing design
   - Must have functional sense (not just decorative)
   - Must be interactive (click, hover, etc.)
3. **Implement event sending** using the `logEvent()` function when interacting with the section
4. **Add the new event type** in `src/library/events.ts`

### How to Send Events

```typescript
import { EVENT_TYPES, logEvent } from "@/library/events";

// In your component
const handleClick = () => {
  logEvent(EVENT_TYPES.YOUR_NEW_EVENT, {
    source: "dashboard",
    section: "your_section",
    timestamp: new Date().toISOString(),
    // ... other relevant data
  });
};
```

### Evaluation Criteria

✅ **Design and UX**
- Visual coherence with the rest of the dashboard
- Responsive (looks good on mobile and desktop)
- Clear interactivity and visual feedback

✅ **Events**
- Event clearly defined in `EVENT_TYPES`
- Relevant and structured data in the event
- Event fires at the correct moment

### 📝 Deliverables

- Code of the new section
- New event type added

---

## 📚 Understanding Tasks and Evaluation (Important!)

Before starting Part 2, it's crucial to understand what a **Task** is and how the evaluation process works.

### What is a Task?

A **Task** is an object that contains:
- **`id`**: Unique identifier
- **`url`**: The target URL where the task should be executed
- **`prompt`**: Natural language description of what needs to be done (e.g., "Fill the form with...")
- **`tests`**: A list of validation tests that verify if the task was completed successfully

### Why are Tests Important?

The **tests** inside a Task are crucial because they define **how success is measured**. For example:
- A `CheckEventTest` verifies that a specific event was triggered with certain criteria
- The evaluation system executes your agent's actions and then runs these tests to determine if the task was successful

### How Does Evaluation Work?

The evaluation process works like this:

1. **Your agent receives a Task** (with prompt and tests)
2. **Your agent returns actions** (navigate, click, type, etc.)
3. **The system executes those actions** in a real browser
4. **The system runs the tests** from the Task to verify success
5. **You get a score** (0.0 to 1.0) based on whether the tests passed

**Key insight**: Your actions must make the tests pass. Understanding what the tests expect helps you create the right actions!

---

## 🤖 Part 2: Simple Agent

### Objective
The main objective of this part is to understand how task evaluation works. Create a simple HTTP server with an endpoint that receives a task and returns actions to solve it. For this test, you need to solve a specific task. In reality, agents should be able to solve any prompt they receive, but for this simple test, focus on solving the specific task provided.

**Note**: This part doesn't require an OpenAI API key. The test creates the task programmatically.

### Specific Task

1. **Create an HTTP server** (Flask recommended for simplicity)
2. **Implement the endpoint** `POST /solve_task` that:
   - Receives a task with structure:
     ```json
     {
       "id": "uuid",
       "url": "http://localhost:8000?seed=42",
       "prompt": "Fill the contact form with a subject equal to 'Job Position' and message contains 'I am the best developer'",
       "tests": [
         {
           "type": "CheckEventTest",
           "event_name": "CONTACT",
           "event_criteria": {
             "subject": {"operator": "equals", "value": "Job Position"},
             "message": {"operator": "contains", "value": "I am the best developer"}
           }
         }
       ]
     }
     ```
     **Note**: The URL may include a `seed` parameter (e.g., `?seed=42`). The benchmark adds this automatically when `dynamic=True`. You should use the URL as provided.
   - Returns a solution with an array of actions that will make the test pass

3. **Your task**: Return an array of actions that will successfully complete the task

4. **Test your agent**: Once implemented, test it using the provided test script

### Test Your Agent

1. **Deploy the movies web and web server**:
   ```bash
   cd autoppia_webs_demo
   ./scripts/setup.sh --demo=autocinema --web_port=8000
   ```

   **Important**: This script automatically deploys:
   - The autocinema demo web (port 8000)
   - The webs_server backend (port 8090)
   - PostgreSQL database for events

   If any of these fails, events won't be saved and the test will fail!

2. **Start your agent** on a port (expected in configs: `127.0.0.1:7000`)

3. **Run the test script**:
   ```bash
   cd autoppia_iwa
   python -m autoppia_iwa.entrypoints.technical_test_agent.test_contact_task
   ```

4. **Verify the result**:
   - The agent should successfully complete the task
   - The evaluation should return a success (score = 1.0)
   - The script will show detailed results

### Important Notes

- **You need to investigate** the action format by looking at the codebase
- The action structure is part of what you need to discover
- For this simple test, you can hardcode the actions for the specific task
- Include reasonable waits between actions so the UI can react

### 📝 Deliverables

- Instructions on how to run it
- Example of request/response

---

## 📊 Part 3: Run Benchmark Against Your Agent

### Objective
Run the full benchmark against web1 (autocinema) to see how your agent performs on multiple tasks. You need to understand how the benchmark works.

**Important**:
- You **MUST** have an OpenAI API key configured in `.env` for this part (see "Configure Environment Variables" section)
- Read the benchmark documentation in `autoppia_iwa/autoppia_iwa/entrypoints/benchmark/README.md` to understand how the benchmark works

### Run Full Benchmark

Run the full benchmark against web1 (autocinema). The benchmark will test your agent against multiple use cases, for example:
- `LOGIN` - Login tasks
- `FILM_DETAIL` - View film details tasks
- And many other use cases...

1. **Make sure your agent is running** on a port

2. **Run the benchmark**:
   ```bash
   cd autoppia_iwa
   python -m autoppia_iwa.entrypoints.technical_test_agent.run_benchmark
   ```

3. **Analyze the results**:
   - The benchmark will test your agent against multiple tasks from web1
   - **Expected behavior**: As your agent is not prepared for all tasks, most should fail. This is expected and shows how a specialized agent behaves.

---

## 🎁 Bonus (Optional but Valued)

If you have extra time, you can:

1. **Improve the React section**:
   - Add animations
   - Make it more interactive
   - Add more events

2. **Improve the agent**:
   - Automatically detect task types
   - Handle different form structures
   - Add retry logic

3. **Understanding the system**:
   - What is "dynamic" mode in the benchmark? Why was something like this implemented?

---

## 📦 Initial Setup

### Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.10+
- Docker and Docker Compose
- Git

### Installation

```bash
# 1. Clone repositories
git clone <repo_autoppia_webs_demo>
git clone <repo_autoppia_iwa>

# 2. Install web demo dependencies
cd autoppia_webs_demo/web_8_autolodge
npm install  # or pnpm install

# 3. Install Python dependencies
cd ../../autoppia_iwa
pip install -r requirements.txt
```

### Verify everything works

```bash
# Start demo web
cd autoppia_webs_demo
./scripts/setup.sh --demo=autocinema --web_port=8000

# Verify it's running
curl http://localhost:8000
curl http://localhost:8090/health  # webs_server
```

### Configure Environment Variables

**Required for Part 3 only**: The benchmark requires an OpenAI API key to generate tasks dynamically. Parts 1 and 2 don't need this.

Create a `.env` file in the `autoppia_iwa` directory:

```bash
cd autoppia_iwa
cat > .env << EOF
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
DEMO_WEBS_ENDPOINT=http://localhost
EOF
```

**Configuration:**
- `LLM_PROVIDER=openai` - Use OpenAI to generate tasks
- `OPENAI_API_KEY` - Your OpenAI API key (required for Part 3)
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `DEMO_WEBS_ENDPOINT` - Base URL for demo webs (default: http://localhost)

---

## 🚀 Good Luck!
This test is designed to be challenging but achievable. We don’t expect perfection — we want to see how you think, adapt, and get things done.

Remember:

- If your agent doesn’t work, don’t panic — debugging is the job 🐛

- Use whatever tools help you move faster (yes, AI is absolutely fine) 🤖

- Monster helps, but too much Monster leads to commits at 3am and questions like “who wrote this code?” 🧃😵‍💫

  Have fun with it. We care much more about your process than a perfect result.
---
