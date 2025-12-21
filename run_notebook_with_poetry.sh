#!/bin/bash

# Run Jupyter notebook using Poetry environment (RECOMMENDED)
# Fast startup, uses existing Poetry dependencies

echo "Starting Jupyter notebook with Poetry environment..."
echo ""
echo "Jupyter will be available at: http://localhost:8888"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
poetry run jupyter notebook
