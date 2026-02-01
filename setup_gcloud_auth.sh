#!/bin/bash
# Google Cloud Authentication Script for AdBoard AI

echo "🔑 Setting up Google Cloud Authentication..."
echo ""

# Ensure gcloud is in PATH
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

# Step 1: Authenticate with Google Cloud
echo "Step 1: Authenticating with Google Cloud..."
echo "This will open a browser window for you to log in."
echo ""
gcloud auth application-default login

# Step 2: Set the project
echo ""
echo "Step 2: Setting GCP project..."
gcloud config set project project-35087fe8-9fae-4629-b51

# Step 3: Verify
echo ""
echo "Step 3: Verifying authentication..."
if gcloud auth application-default print-access-token > /dev/null 2>&1; then
    echo "✅ Authentication successful!"
    echo ""
    echo "You're now ready to use Vertex AI Imagen for image generation."
    echo ""
    echo "Next step: Run the test pipeline:"
    echo "  cd '/Users/tomalmog/programming/Febuary 2026/Brown'"
    echo "  python test_pipeline.py"
else
    echo "❌ Authentication failed. Please try again."
    exit 1
fi
