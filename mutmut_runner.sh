#!/bin/bash

# Fail-fast behavior disabled to allow continuous mutation testing
set +e

echo "🔬 Starting mutmut mutation testing..."

# Create backup of tests if they don't exist
if [ ! -d "tests.bak" ]; then
    echo "Creating backup of tests directory..."
    cp -r tests tests.bak
fi

# Clean up any previous test runs
if [ -f "mutmut_results.txt" ]; then
    rm mutmut_results.txt
fi

# Run mutmut with options it actually supports
echo "Running mutation tests..."
mutmut run

# Capture exit code for reference
MUTMUT_EXIT_CODE=$?

# Show mutation results summary
echo "📊 Mutation Testing Results:"
mutmut results | tee mutmut_results.txt

# Count survivors properly by checking for 'Survived' in the output
SURVIVORS=$(grep -c 'Survived:' mutmut_results.txt || echo "0")
echo "⚠️  Total Surviving Mutations: $SURVIVORS"

# Fix bug in comparison - ensure SURVIVORS is treated as a number
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