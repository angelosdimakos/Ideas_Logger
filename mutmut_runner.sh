#!/bin/bash

# Fail-fast behavior disabled to allow continuous mutation testing
set +e

echo "🔬 Starting mutmut mutation testing with Xvfb..."

# Check if xvfb-run is available
if ! command -v xvfb-run &> /dev/null; then
    echo "❌ xvfb-run is not installed. Please install it with:"
    echo "   sudo apt-get install xvfb (Ubuntu/Debian)"
    echo "   or equivalent for your system."
    echo "Continuing without Xvfb, GUI tests may fail..."
    USE_XVFB=0
else
    echo "✅ xvfb-run found, will use virtual display"
    USE_XVFB=1
fi

# Create backup of tests if they don't exist
if [ ! -d "tests.bak" ]; then
    echo "Creating backup of tests directory..."
    cp -r tests tests.bak
fi

# Clean up any previous test runs
if [ -f "mutmut_results.txt" ]; then
    rm mutmut_results.txt
fi

# Run mutmut with Xvfb if available
echo "Running mutation tests..."
if [ "$USE_XVFB" -eq 1 ]; then
    # Set DISPLAY environment variable to ensure tests know a display is available
    export DISPLAY=:99

    # Run with Xvfb - configure resolution and color depth as needed
    xvfb-run --server-args="-screen 0 1024x768x24" mutmut run
else
    # Run normally if Xvfb is not available
    mutmut run
fi

# Capture exit code for reference
MUTMUT_EXIT_CODE=$?

# Show mutation results summary
echo "📊 Mutation Testing Results:"
mutmut results | tee mutmut_results.txt

# Count survivors properly by checking for 'Survived' in the output
SURVIVORS=$(grep -c 'Survived:' mutmut_results.txt 2>/dev/null || echo "0")
echo "⚠️  Total Surviving Mutations: $SURVIVORS"

# Show details of surviving mutations if any
if [ "$SURVIVORS" -gt 0 ]; then
    echo "🚨 Some mutations survived. Here are the details:"
    echo "----------------------------------------"
    grep -A 3 'Survived:' mutmut_results.txt || echo "No details available"
    echo "----------------------------------------"
    echo "Run 'mutmut show <id>' to see more details about a specific mutation."
else
    echo "✅ All mutations killed. Good job!"
fi

# Exit with original mutmut exit code for CI integration if needed
exit $MUTMUT_EXIT_CODE