#!/usr/bin/env bash
set -e

echo "========================================================"
echo "🚀 Setting up Daily Tech & AI Briefing Agent"
echo "========================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if python3 works
if python3 -c "import sys; sys.exit(0)" 2>/dev/null; then
    PYTHON_CMD="python3"
    echo "✓ Detected working Python: $($PYTHON_CMD --version)"
elif command -v uv >/dev/null 2>&1; then
    PYTHON_CMD="uv run python"
    echo "✓ Detected uv (Astral Python manager)"
else
    echo "⚠️ System Python requires Apple Developer Tools or standalone Python."
    echo "Installing 'uv' (ultrafast standalone Python manager, no admin rights needed)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv >/dev/null 2>&1; then
        PYTHON_CMD="uv run python"
        echo "✓ uv installed successfully!"
    else
        echo "❌ Please install Python from https://www.python.org/downloads/ or run 'xcode-select --install'"
        exit 1
    fi
fi

echo ""
echo "Creating .env if not present..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file. Please edit it with your email & API keys."
fi

echo ""
echo "========================================================"
echo "🎉 Setup complete!"
echo "To generate today's briefing preview in your browser, run:"
echo "    $PYTHON_CMD run.py --preview"
echo ""
echo "To schedule daily 10:00 AM delivery, run:"
echo "    $PYTHON_CMD run.py --install-schedule"
echo "========================================================"
