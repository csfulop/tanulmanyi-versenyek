#!/bin/bash

# Run Jupyter notebook locally using Kaggle's Docker image (20GB)
# This ensures the exact same environment as Kaggle's platform

echo "Starting Jupyter notebook in Kaggle Docker environment..."
echo ""
echo "⚠️  Note: First run will download 20GB Docker image"
echo ""
echo "Mounting:"
echo "  - data/kaggle/ → /kaggle/input/tanulmanyi-versenyek/"
echo "  - notebooks/ → /kaggle/working/"
echo ""
echo "Jupyter will be available at: http://localhost:8888"
echo ""

docker run -it --rm \
  -p 8888:8888 \
  -v "$(pwd)/data/kaggle":/kaggle/input/tanulmanyi-versenyek \
  -v "$(pwd)/notebooks":/kaggle/working \
  kaggle/python \
  jupyter notebook \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password=''
