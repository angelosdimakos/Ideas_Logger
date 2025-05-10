#!/bin/bash

# Fail-fast behavior disabled to allow continuous mutation testing
set +e

echo "🔬 Starting mutmut mutation testing..."

# Initialize mutmut database if needed
mutmut init || true

# Run mutmut and continue even if failures occur
mutmut run --safeguard-passed --no-progress --tests-dir tests

# Capture exit code for reference
MUTMUT_EXIT_CODE=$?

# Show mutation results summary
echo "📊 Mutation Testing Results:"
mutmut results --json > mutmut_results.json
mutmut results

# Optional: Highlight surviving mutations clearly
SURVIVORS=$(mutmut results | grep "SURVIVED" | wc -l)
echo "⚠️  Total Surviving Mutations: $SURVIVORS"

if [ "$SURVIVORS" -gt 0 ]; then
    echo "🚨 Some mutations survived. Review the results carefully!"
else
    echo "✅ All mutations killed. Good job!"
fi

# Exit with original mutmut exit code for CI integration if needed
exit $MUTMUT_EXIT_CODE
