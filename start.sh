#!/bin/bash
set -e

# Colours
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

cd "$(dirname "$0")"

# Check Python executable
PYTHON_CMD="python3"
if [ -f "./.venv/bin/python" ]; then
    PYTHON_CMD="./.venv/bin/python"
fi

# Check uvicorn
if ! $PYTHON_CMD -c "import uvicorn" 2>/dev/null; then
    echo "ERROR: uvicorn is not installed in $PYTHON_CMD environment."
    exit 1
fi

echo -e "${BLUE}Starting FastAPI Backend on port 8000...${NC}"
$PYTHON_CMD -m uvicorn engine.api.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
sleep 2

echo -e "${BLUE}Starting Frontend static server on port 5173...${NC}"
$PYTHON_CMD -m http.server 5173 --directory frontend &
FRONTEND_PID=$!


echo ""
echo -e "${GREEN}=========================================================${NC}"
echo -e "${GREEN} Labour Market Intelligence Engine${NC}"
echo -e "${GREEN}=========================================================${NC}"
echo -e " Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e " API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e " Frontend UI:  ${BLUE}http://localhost:5173${NC}"
echo -e "${GREEN}=========================================================${NC}"
echo " Press Ctrl+C to stop all services."
echo ""

wait $BACKEND_PID $FRONTEND_PID
