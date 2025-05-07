param(
    [string]$Message = "Auto-commit",
    [switch]$WithGolden
)

Write-Host "Pulling audit artifacts from latest successful CI run..."

# Check GitHub CLI presence
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is required but not installed."
    exit 1
}

# Use backtick to escape ampersand in workflow name
$workflowName = "Run Tests `& CI Audit (Dockerized)"

try {
    $run_id = gh run list --workflow "$workflowName" `
                          --limit 1 `
                          --json databaseId,status,conclusion `
                          -q '.[0].databaseId'

    if (-not $run_id) {
        Write-Warning "⚠No CI run found. Skipping artifact download."
    } else {
        Write-Host "Pulling combined audit reports..."
        gh run download $run_id --name combined-report --dir tests/fixtures
        gh run download $run_id --name ci-severity-report --dir tests/fixtures
        Write-Host "Downloaded: merged_report.json + ci_severity_report.md"

        if ($WithGolden) {
            Write-Host "Pulling golden regression fixtures..."
            gh run download $run_id --name lint-report --dir tests/fixtures
            gh run download $run_id --name docstring-summary --dir tests/fixtures
            gh run download $run_id --name refactor-audit --dir tests/fixtures
            Write-Host "Downloaded: linting_report.json, docstring_summary.json, refactor_audit.json"
        }
    }
}
catch {
    Write-Warning "⚠Artifact pull failed: $_"
}

Write-Host "Building Docker image..."
docker build -t ghcr.io/angelosdimakos/ideas_logger:latest .

Write-Host "Pushing Docker image to GHCR..."
docker push ghcr.io/angelosdimakos/ideas_logger:latest

Write-Host "Committing code changes..."
git add -A
git commit -m "$Message"
git push

Write-Host "Done."
