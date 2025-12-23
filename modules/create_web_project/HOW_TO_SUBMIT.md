# How to Submit Your Web to Autoppia

This is the complete guide for contributors who want to create and submit a new web project.

## 📋 Quick Summary

1. **Copy the template** from `autodining`
2. **Create your web** following the structure
3. **Create `config.yaml`** with your events and use cases
4. **Run the tests** locally to verify
5. **Submit your project** for review

---

## 🚀 Step by Step

### Step 1: Copy the Template

```bash
cd autoppia_iwa/modules/create_web_project/template/projects
cp -r autodining my_web
cd my_web
```

**Important**: Replace `my_web` with your project name (e.g., `cinema_1`, `books_2`).

### Step 2: Create Your Frontend

Your web must go in `my_web/frontend/`. The minimum required structure is:

```
my_web/frontend/
├── src/
│   ├── dynamic/              # Dynamic system (REQUIRED)
│   │   ├── v1/               # DOM structure modification
│   │   ├── v2-data/          # Data loading (optional)
│   │   ├── v3/               # Anti-scraping (IDs, classes, text)
│   │   └── shared/           # Core functions
│   ├── context/
│   │   └── SeedContext.tsx   # Seed management (REQUIRED)
│   └── library/
│       └── events.ts         # Event definitions (REQUIRED)
└── tests/                    # Tests (REQUIRED)
    ├── test-dynamic-system.js
    ├── test-events.js
    └── README.md
```

**Don't know how to implement this?** Look at the `autodining/frontend/` template as a complete reference.

### Step 3: Create config.yaml

Edit `my_web/config.yaml` with your project information:

```yaml
project:
  slug: my_web              # Unique name (no spaces, lowercase)
  name: "My Web"            # Human-readable name
  deck_id: my_web           # Must match slug
  owner: your-username      # Your GitHub username or email
  summary: "Brief description of your web"
  contact: "your@email.com"
  seed_notes: "Explain how seeds work in your web"

deployment:
  frontend_port_index: 0    # Port where it will run (0, 1, 2, etc.)
  backend_url: "${AUTOPPIA_BACKEND_URL:-http://localhost:8090}/"

events:
  - name: EVENT_1
    description: "Event description"
    fields:
      - { name: field1, type: str, source: field1 }
      - { name: field2, type: int, source: field2, optional: true }

use_cases:
  - name: "Use Case 1"
    event: EVENT_1
    description: "Use case description"
    prompts:
      - prompt: "Example prompt for the user"
        template: "Template with <placeholders>"
```

**Tip**: Copy `autodining/config.yaml` and modify it with your data.

### Step 4: Verify Locally

Before submitting, verify that everything works:

```bash
cd my_web/frontend

# Test 1: Dynamic system
node tests/test-dynamic-system.js

# Test 2: Event coverage
node tests/test-events.js
```

**Both tests must pass at 100%**. If they fail, fix the errors before submitting.

### Step 5: Submit for Review

When everything is ready:

1. **Create a PR** or **fork** the repository
2. **Include**:
   - Your complete `my_web/` folder
   - Updated `config.yaml`
   - Frontend with all required files
3. **Mention** that you have run the tests locally

---

## ✅ Checklist Before Submitting

- [ ] Copied the `autodining` template
- [ ] Implemented the frontend with the correct structure
- [ ] Created `config.yaml` with all my events and use cases
- [ ] `src/dynamic/` exists with v1, v3, shared (minimum)
- [ ] `src/context/SeedContext.tsx` exists
- [ ] `src/library/events.ts` exists with all events
- [ ] `tests/test-dynamic-system.js` exists and passes
- [ ] `tests/test-events.js` exists and passes (100% coverage)
- [ ] Ran both tests locally and they passed

---

## 📚 Resources

### Reference Template

- **Location**: `template/projects/autodining/`
- **Includes**: Complete frontend, config.yaml, test structure

### Additional Documentation

- **config.yaml schema**: `template/CONFIG_SCHEMA.md`
- **Template README**: `template/README.md`
- **Verification pipeline**: `verification/README.md`

### Structure Examples

**Minimum Dynamic System**:
```
src/dynamic/
├── v1/
│   ├── add-wrap-decoy.ts
│   └── change-order-elements.ts
├── v3/
│   ├── data/
│   │   ├── id-variants.json
│   │   ├── class-variants.json
│   │   └── text-variants.json
│   └── utils/
│       └── variant-selector.ts
└── shared/
    └── core.ts
```

**Minimum Tests**:
```
tests/
├── test-dynamic-system.js    # Must pass all tests
├── test-events.js            # Must have 100% coverage
└── README.md                 # Test documentation
```

---

## ❓ Frequently Asked Questions

### What if I don't have all the template files?

**Minimum required**:
- `config.yaml`
- `frontend/src/dynamic/` (v1, v3, shared)
- `frontend/src/context/SeedContext.tsx`
- `frontend/src/library/events.ts`
- `frontend/tests/` (both tests)

You can adapt the rest to your project.

### How do I know if my web is ready?

Run the tests:
```bash
cd my_web/frontend
node tests/test-dynamic-system.js  # Must pass
node tests/test-events.js           # Must have 100% coverage
```

If both pass, your web is ready.

### What is the dynamic system?

It's an anti-scraping system that modifies the DOM and HTML attributes based on a `seed` in the URL. **It's mandatory** for all webs.

Look at `autodining/frontend/src/dynamic/` to see how to implement it.

### Can I use another framework besides Next.js?

Yes, but you must implement:
- Dynamic system (v1, v3)
- SeedContext (or equivalent)
- Node.js tests
- Events

The template uses Next.js, but you can adapt it.

---

## 🆘 Need Help?

1. **Check the template**: `template/projects/autodining/` has everything you need
2. **Read the documentation**: `template/README.md` and `verification/README.md`
3. **Run the tests**: They will tell you exactly what's missing

---

## 📝 Key Files Summary

| File | Location | Required? | Description |
|------|----------|-----------|-------------|
| `config.yaml` | `my_web/config.yaml` | ✅ Yes | Project configuration |
| `SeedContext.tsx` | `my_web/frontend/src/context/` | ✅ Yes | Seed management |
| `events.ts` | `my_web/frontend/src/library/` | ✅ Yes | Event definitions |
| `test-dynamic-system.js` | `my_web/frontend/tests/` | ✅ Yes | Dynamic system test |
| `test-events.js` | `my_web/frontend/tests/` | ✅ Yes | Event coverage test |
| `src/dynamic/` | `my_web/frontend/src/` | ✅ Yes | Dynamic system |

---

**Last updated**: 2025-01-27
