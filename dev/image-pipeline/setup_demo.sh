#!/bin/bash

echo "============================================================"
echo "ComfyUI Image Production Pipeline - Setup"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the image-pipeline directory"
    exit 1
fi

# Create config file if it doesn't exist
if [ ! -f "config/settings.yaml" ]; then
    echo "Creating configuration file..."
    cp config/settings.example.yaml config/settings.yaml
    echo "✓ Configuration file created: config/settings.yaml"
    echo ""
    echo "IMPORTANT: Edit config/settings.yaml to set your ComfyUI endpoint"
    echo ""
else
    echo "✓ Configuration file already exists"
    echo ""
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Run demo
echo "Running demo workflow..."
echo ""
python examples/demo_workflow.py

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "To generate real images:"
echo "1. Install and run ComfyUI: https://github.com/comfyanonymous/ComfyUI"
echo "2. Edit config/settings.yaml:"
echo "   - Set comfyui.endpoint to your ComfyUI URL"
echo "   - Set comfyui.dry_run to false"
echo "3. Edit private blocks with your content:"
echo "   - data/private/blocks/private_demo_001.json"
echo "   - data/private/blocks/negative_demo_001.json"
echo "4. Run: python examples/demo_workflow.py"
echo ""
