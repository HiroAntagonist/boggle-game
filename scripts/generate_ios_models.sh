#!/bin/bash
# ABOUTME: Script to generate iOS Swift models from backend OpenAPI schema.
# ABOUTME: Downloads latest schema from production and generates type-safe Swift models.

set -e  # Exit on error

echo "🔄 Generating iOS models from OpenAPI schema..."

# Configuration
BACKEND_URL="${BACKEND_URL:-https://boggle-game-ar.fly.dev}"
SCHEMA_FILE="openapi.json"
OUTPUT_DIR="BoggleApp/Generated"

# Step 1: Download OpenAPI schema from backend
echo "📥 Downloading OpenAPI schema from $BACKEND_URL..."
curl -s "$BACKEND_URL/openapi.json" -o "$SCHEMA_FILE"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Failed to download OpenAPI schema"
    exit 1
fi

echo "✅ Downloaded schema ($(du -h "$SCHEMA_FILE" | cut -f1))"

# Step 2: Check if openapi-generator is installed
if ! command -v openapi-generator &> /dev/null; then
    echo "❌ openapi-generator not found"
    echo "Install with: brew install openapi-generator"
    exit 1
fi

# Step 3: Clean existing generated code (optional - be careful!)
if [ -d "$OUTPUT_DIR" ]; then
    echo "🧹 Cleaning existing generated code..."
    rm -rf "$OUTPUT_DIR"
fi

# Step 4: Generate Swift models
echo "🔨 Generating Swift models..."
openapi-generator generate \
    -i "$SCHEMA_FILE" \
    -g swift5 \
    -o "$OUTPUT_DIR" \
    --additional-properties=responseAs=Codable,useSPMFileStructure=false \
    --global-property=models,supportingFiles \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Generated Swift models in $OUTPUT_DIR"
    echo "📊 Generated $(find "$OUTPUT_DIR/Sources/OpenAPIClient/Models" -name "*.swift" 2>/dev/null | wc -l | tr -d ' ') model files"
else
    echo "❌ Failed to generate Swift models"
    exit 1
fi

# Step 5: Summary
echo ""
echo "✨ Generation complete!"
echo ""
echo "Next steps:"
echo "1. Review generated models in $OUTPUT_DIR/Sources/OpenAPIClient/Models/"
echo "2. Add model files to your Xcode project"
echo "3. Replace manual model definitions in BoggleAPI.swift"
echo ""
