#!/bin/bash
# Generate agent orchestration flowchart PNG from Mermaid source.
# Requires Node.js and npx.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"

cd "$DOCS_DIR"
echo "Generating docs/agent_orchestration.png..."
npx -y @mermaid-js/mermaid-cli -i agent_orchestration.mmd -o agent_orchestration.png
echo "Done. View at docs/agent_orchestration.png"
