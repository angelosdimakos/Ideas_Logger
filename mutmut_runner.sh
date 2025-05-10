#!/bin/bash

# Fail-fast behavior disabled to allow continuous mutation testing
set +e

echo "🔬 Starting mutmut mutation testing..."

# Run mutmut
# Removed 'init' command as it doesn't exist according to help output
# Removed '--safeguard-passed' option as it doesn't exist
# Removed '--no-progress' option as it doesn't exist
echo "Running mutation tests..."
mutmut run

# Capture exit code for reference
MUTMUT_EXIT_CODE=$?

# Show mutation results summary
echo "📊 Mutation Testing Results:"
# The JSON output option doesn't exist, using standard output instead
mutmut results > mutmut_results.txt
mutmut results

# Count survivors by parsing results file
SURVIVORS=$(grep "Survived" mutmut_results.txt | wc -l)
echo "⚠️  Total Surviving Mutations: $SURVIVORS"

if [ "$SURVIVORS" -gt 0 ]; then
    echo "🚨 Some mutations survived. Review the results carefully!"
else
    echo "✅ All mutations killed. Good job!"
fi

# Exit with original mutmut exit code for CI integration if needed
exit $MUTMUT_EXIT_CODE