# Scripts Directory

Helper scripts for development and testing.

## 📁 Scripts

### **wait_for_services_and_run_tests.sh**
Waits for required services to be ready, then runs integration tests.

**What it does:**
1. Checks if webs_server is running (port 8090)
2. Checks if demo webs are running (ports 8001, 8002)
3. Waits up to 30 seconds for each service
4. Runs integration test suite

**Usage:**
```bash
./scripts/wait_for_services_and_run_tests.sh
```

**Before running:**
```bash
# Start webs_server
cd autoppia_webs_demo
docker-compose up webs_server

# Start demo webs
./scripts/setup.sh --demo=autocinema
./scripts/setup.sh --demo=autobooks
```

---

### **Other Scripts** (if present)

Check this directory for additional utility scripts:
- Deployment helpers
- Data processing
- Service management
- Testing utilities

---

## 📝 Adding New Scripts

When adding scripts:
1. Make them executable: `chmod +x script_name.sh`
2. Add descriptive header comments
3. Document usage in this README
4. Use clear, descriptive names
