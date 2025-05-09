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

# Workflow and paths
$workflowName = "Run Tests `& CI Audit (Dockerized)"
$artifactsDir = "/artifacts"

# Ensure artifacts directory exists and is cleaned
if (Test-Path $artifactsDir) {
    Write-Host "Cleaning downloaded artifacts in $artifactsDir..."
    Remove-Item "$artifactsDir\*" -Recurse -Force
} else {
    Write-Host "Creating artifacts directory..."
    New-Item -ItemType Directory -Path $artifactsDir | Out-Null
}

try {
    $run_id = gh run list --workflow "$workflowName" `
                          --limit 1 `
                          --json databaseId,status,conclusion `
                          -q '.[0].databaseId'

    if (-not $run_id) {
        Write-Warning "No CI run found. Skipping artifact download."
    } else {
        Write-Host "Pulling core audit reports..."
        gh run download $run_id --name combined-report --dir $artifactsDir
        gh run download $run_id --name ci-severity-report --dir $artifactsDir
        Write-Host "Downloaded: merged_report.json, ci_severity_report.md"

        # Always pull strictness-mapping
        Write-Host "Pulling strictness mapping report..."
        gh run download $run_id --name strictness-mapping --dir $artifactsDir
        Write-Host "Downloaded: strictness_mapping.json"

        if ($WithGolden) {
            Write-Host "Pulling golden regression fixtures..."
            gh run download $run_id --name lint-report --dir $artifactsDir
            gh run download $run_id --name docstring-summary --dir $artifactsDir
            gh run download $run_id --name refactor-audit --dir $artifactsDir
            Write-Host "Downloaded: linting_report.json, docstring_summary.json, refactor_audit.json"
        }
    }
}
catch {
    Write-Warning "Artifact pull failed: $_"
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
