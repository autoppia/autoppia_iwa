# Scripts Directory

Helper scripts for development, testing, and operations.

## 📁 Scripts Overview

| Script                               | Purpose                      | When to Use               |
| ------------------------------------ | ---------------------------- | ------------------------- |
| `wait_for_services_and_run_tests.sh` | Wait + run integration tests | Development testing       |
| `train_ppo_agent.py`                 | Train RL agent with PPO      | RL training               |
| `run_demo_web_proxy.py`              | Run mutation proxy           | Dynamic mutations testing |
| `port_forward.py`                    | TCP port forwarding          | Network utilities         |
| `fetch_service_runs.py`              | Fetch data from service      | Data collection           |

---

## 🔧 Scripts Detail

### **wait_for_services_and_run_tests.sh**

**Purpose:** Waits for services to be ready, then runs integration test suite.

**What it does:**

1. Checks if webs_server is running (port 8090)
2. Checks if demo webs are running (ports 8001, 8002)
3. Waits up to 30 seconds for each service
4. Runs: test_all_projects, test_seed_guard, test_constraint_generation

**Usage:**

```bash
./scripts/wait_for_services_and_run_tests.sh
```

**Prerequisites:**

```bash
# Start webs_server
cd autoppia_webs_demo && docker-compose up webs_server

# Start demo webs
cd autoppia_webs_demo && ./scripts/setup.sh --demo=autocinema
```

---

### **train_ppo_agent.py**

**Purpose:** Quick-start wrapper for training PPO (Proximal Policy Optimization) agent.

**What it does:**

- Trains RL agent using PPO algorithm
- Optionally uses Behavior Cloning (BC) warm-start
- Loads reward model for shaping
- Saves checkpoints during training

**Usage:**

```bash
# Basic PPO training
python scripts/train_ppo_agent.py

# With BC warm-start
python scripts/train_ppo_agent.py --with-bc

# Custom config
python scripts/train_ppo_agent.py --config path/to/config.yaml
```

**Output:** Training logs and model checkpoints

---

### **run_demo_web_proxy.py**

**Purpose:** Runs dynamic mutation proxies for demo webs (D1/D3/D4 system).

**What it does:**

- Starts reverse proxy that intercepts HTML
- Applies D1 (structure), D3 (attributes), D4 (overlays) mutations
- One proxy process per web project
- Deterministic based on seed

**Usage:**

```bash
# Run proxy for specific project
python scripts/run_demo_web_proxy.py --project autocinema

# List configured projects
python scripts/run_demo_web_proxy.py --list

# Custom config
python scripts/run_demo_web_proxy.py --config path/to/proxy_config.json
```

**When to use:** Testing dynamic mutations outside of Playwright.

---

### **port_forward.py**

**Purpose:** Simple TCP port forwarder for network tunneling.

**What it does:**

- Forwards traffic from local port to remote host:port
- Useful when Docker container ports don't match expected ports
- Lightweight alternative to SSH tunneling

**Usage:**

```bash
# Forward local 8001 to remote server
python scripts/port_forward.py --listen-port 8001 --target-host 84.247.180.192 --target-port 8001
```

**Example use case:**

```bash
# Access remote demo web locally
python scripts/port_forward.py \
  --listen-host 127.0.0.1 \
  --listen-port 8001 \
  --target-host remote-server.com \
  --target-port 8001

# Now http://localhost:8001 → remote-server.com:8001
```

---

### **fetch_service_runs.py**

**Purpose:** Fetch evaluation run data from a remote service API.

**What it does:**

- Calls REST endpoint to get Task/Solution/Result JSONs
- Downloads evaluation data from production
- Saves to local directory for analysis

**Usage:**

```bash
# Fetch from service
python scripts/fetch_service_runs.py \
  --base_url http://service.example.com \
  --token YOUR_TOKEN \
  --limit 100 \
  --out inputs/reward_model/raw_runs
```

**Output:** JSON files with evaluation data for RM training.

---

## 🎯 Common Workflows

### **Development Testing**

```bash
# 1. Start services
cd autoppia_webs_demo && docker-compose up -d

# 2. Run tests
./scripts/wait_for_services_and_run_tests.sh
```

### **RL Training**

```bash
# Train PPO agent
python scripts/train_ppo_agent.py --with-bc
```

### **Testing Mutations**

```bash
# Start mutation proxy
python scripts/run_demo_web_proxy.py --project autocinema

# Access via proxy
curl http://localhost:8200/?seed=42
```

---

## 📝 Adding New Scripts

When adding scripts:

1. Make them executable: `chmod +x script_name.sh` or `chmod +x script_name.py`
2. Add descriptive header comments (docstring or comments)
3. Document usage in this README
4. Use clear, descriptive names
5. Add argument parser with `--help` support
