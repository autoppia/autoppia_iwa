#!/bin/bash
# Wait for Services and Run Tests
#
# This script waits for required services to be ready (webs_server, demo webs)
# and then runs the integration test suite to verify the system works correctly.
#
# Usage: ./scripts/wait_for_services_and_run_tests.sh
#
# Required services:
# - webs_server (port 8090)
# - autocinema (port 8001)
# - autobooks (port 8002)

echo "🔍 Verificando servicios..."

# Función para esperar a un servicio
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -n "   Esperando $name..."

    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo " ✅ OK!"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done

    echo " ❌ TIMEOUT después de ${max_attempts}s"
    return 1
}

# Esperar servicios
echo ""
wait_for_service "webs_server (puerto 8090)" "http://localhost:8090/health"
wait_for_service "autocinema (puerto 8001)" "http://localhost:8001/"
wait_for_service "autobooks (puerto 8002)" "http://localhost:8002/"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 EJECUTANDO TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Verificar todos los proyectos
echo "1️⃣ Test: Verificar todos los proyectos están actualizados"
python3 tests/integration/test_all_projects.py
echo ""

# Test 2: Seed Guard
echo "2️⃣ Test: Seed Guard (validación de NavigateActions)"
python3 tests/integration/test_seed_guard.py
echo ""

# Test 3: Constraint Generation (requiere servicios levantados)
echo "3️⃣ Test: Generación de Constraints"
python3 tests/integration/test_constraint_generation.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TODOS LOS TESTS COMPLETADOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
