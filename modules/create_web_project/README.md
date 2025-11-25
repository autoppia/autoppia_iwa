# Create Web Project - Tools for Building New Web Projects

This directory contains all tools for **creating and validating** new web projects for IWA.

## 📁 Structure

```
modules/create_web_project/
├── template/          # 📝 Template for community contributions
│   └── projects/
│       └── autodining/    # Complete reference implementation
│
└── verification/      # ✅ Automated validation pipeline (8 phases)
    ├── cli/
    └── phases/
```

---

## 🎯 Purpose

### **`template/` - For Contributors** 👥

When someone wants to add a new web project to IWA, they:
1. Copy `template/projects/autodining/`
2. Customize `config.yaml` with their events/use cases
3. Implement their frontend following the structure
4. Submit for review

### **`verification/` - For Autoppia Team** 🔍

Automated pipeline that validates submissions:
- Generates Python modules from config.yaml
- Runs 8 verification phases
- Ensures quality and compatibility
- Auto-approves or provides feedback

---

## 🌐 Complete Template Structure

The autodining template includes **ALL** features of production webs:

### **Dynamic System (v1/v2/v3)** ✅

```
src/
├── dynamic/
│   ├── v1-layouts/          # Layout variants (10 layouts)
│   │   ├── layouts.ts
│   │   └── index.ts
│   ├── v2-data/             # Data loading with seeds
│   │   ├── data-provider.ts
│   │   └── index.ts
│   └── v3-dynamic/          # Anti-scraping (IDs, classes, text)
│       ├── data/
│       │   ├── semantic-ids.json
│       │   ├── class-variants.json
│       │   └── text-variants.json
│       ├── hooks/
│       │   └── useV3Attributes.ts
│       └── utils/
│           ├── id-generator.ts
│           ├── text-selector.ts
│           └── class-selector.ts
```

### **Seed System** ✅

```
src/
├── shared/
│   ├── seed-resolver.ts     # Calls /seeds/resolve endpoint
│   ├── seeded-loader.ts     # Loads data with seeds
│   └── data-generator.ts    # Generates test data
├── context/
│   └── SeedContext.tsx      # Manages seed state
└── hooks/
    └── useSeedRouter.ts     # Router with seed preservation
```

### **Core Features** ✅

```
src/
├── app/                     # Pages (Next.js 13+ app router)
├── components/              # UI components
├── library/
│   ├── events.ts           # Event logging helpers
│   ├── dataset.ts          # Data management
│   └── utils.ts            # Utilities
└── context/
    └── SeedContext.tsx     # Seed management
```

---

## 🚀 Workflow

### **1. Contributor Creates Project**

```bash
# Copy template
cp -r modules/create_web_project/template/projects/autodining \
      modules/create_web_project/template/projects/my_project

# Customize
cd modules/create_web_project/template/projects/my_project
# Edit config.yaml with events/use cases
# Implement frontend/src/
# Update docker-compose.yml
```

### **2. Autoppia Validates**

```bash
# Generate Python module
python -m modules.create_web_project.verification generate-module \
  modules/create_web_project/template/projects/my_project/config.yaml

# Run verification (8 phases)
python -m modules.create_web_project.verification verify my_project \
  --deck path/to/deck.json

# Result:
✅ All phases pass → Project approved
❌ Phase fails → Feedback provided
```

### **3. Integration**

If approved:
- Python module added to `src/demo_webs/projects/`
- Frontend deployed to production
- Available in benchmarks

---

## 📊 What Makes a Complete Template?

### **Must Have (Production Features):**

✅ **Seed System:**
- `SeedContext.tsx` - State management
- `seed-resolver.ts` - Calls `/seeds/resolve`
- `SeedLink.tsx` - Link with seed preservation
- `useSeedRouter.ts` - Router with seed preservation

✅ **Dynamic System (v1/v2/v3):**
- `v1-layouts/` - 10 layout variants
- `v2-data/` - Data loading with seeds
- `v3-dynamic/` - Anti-scraping (IDs, classes, text variants)

✅ **Core:**
- Event logging (`library/events.ts`)
- Data management (`library/dataset.ts`)
- Backend integration (`api/log-event/route.ts`)

✅ **Configuration:**
- `config.yaml` - Complete event/use case definitions
- `docker-compose.yml` - Reproducible deployment
- `README.md` - Documentation

---

## 🔧 Differences from Real Webs

The template is a **reference implementation** that includes:
- ✅ All v1/v2/v3 infrastructure
- ✅ Complete seed system
- ✅ Production-ready structure
- ⚠️ Generic constraint generators (contributors customize)
- ⚠️ Basic dataset (contributors replace with real data)

Real webs like `autocinema` have:
- ✅ Custom constraint logic
- ✅ Large datasets (hundreds of items)
- ✅ Complex UI components
- ✅ Advanced features

---

## 📝 Quick Reference

| Component | Template | Real Webs | Purpose |
|-----------|----------|-----------|---------|
| dynamic/ | ✅ Complete | ✅ Complete | v1/v2/v3 system |
| seed-resolver.ts | ✅ Yes | ✅ Yes | Seed resolution |
| SeedContext | ✅ Yes | ✅ Yes | Seed management |
| Events | ✅ Basic | ✅ Custom | Backend logging |
| Constraints | ⚠️ Generic | ✅ Custom | Task generation |
| Dataset | ⚠️ Small | ✅ Large | Content |

---

## 🎯 Summary

**`modules/web_projects/`** is the complete system for:
1. **Creating** new web projects (template/)
2. **Validating** submissions (verification/)

Contributors use the template, which now includes **ALL production features** including the complete v1/v2/v3 dynamic system. The verification pipeline ensures quality before integration.
