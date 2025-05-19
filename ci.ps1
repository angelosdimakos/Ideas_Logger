param(
    [string]$Message = "Auto-commit",
    [switch]$WithGolden,
    [string]$VersionPrefix = "v" # Default version prefix
)

Write-Host "Pulling audit artifacts from latest successful CI run..."

# Check GitHub CLI presence
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is required but not installed."
    exit 1
}

# Workflow and paths
$workflowName = "Run Tests & CI Audit with Documentation"
$artifactsDir = ".\artifacts"

# Get current date/time for versioning
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$version = "$VersionPrefix$timestamp"
$versionedDir = Join-Path $artifactsDir $version

# Ensure artifacts directory exists
if (-not (Test-Path $artifactsDir)) {
    Write-Host "Creating artifacts directory..."
    New-Item -ItemType Directory -Path $artifactsDir | Out-Null
}

# Create versioned directory for this run
Write-Host "Creating versioned artifacts directory: $versionedDir"
New-Item -ItemType Directory -Path $versionedDir | Out-Null

# Create a latest symlink/directory for easy access to most recent artifacts
$latestDir = Join-Path $artifactsDir "latest"
if (Test-Path $latestDir) {
    Write-Host "Removing previous 'latest' directory..."
    Remove-Item $latestDir -Force -Recurse
}
New-Item -ItemType Directory -Path $latestDir | Out-Null

try {
    $run_id = gh run list --workflow "$workflowName" `
                          --limit 1 `
                          --json databaseId,status,conclusion `
                          -q '.[0].databaseId'

    if (-not $run_id) {
        Write-Warning "No CI run found. Skipping artifact download."
    } else {
        # Document which run_id we're using
        "$run_id" | Out-File -FilePath (Join-Path $versionedDir "run_id.txt")

        Write-Host "Pulling core audit reports..."
        gh run download $run_id --name combined-report --dir $versionedDir
        gh run download $run_id --name ci-severity-report --dir $versionedDir
        Write-Host "Downloaded: merged_report.json, ci_severity_report.md"

        # Always pull test discovery
        Write-Host "Pulling test discovery report..."
        gh run download $run_id --name test-report --dir $versionedDir
        Write-Host "Downloaded: test_report.json"

        # Pull coverage reports if available
        Write-Host "Pulling coverage reports..."
        gh run download $run_id --name coverage-reports --dir $versionedDir

        # Pull final strictness report
        Write-Host "Pulling final strictness report..."
        gh run download $run_id --name final-strictness-report --dir $versionedDir

        if ($WithGolden) {
            Write-Host "Pulling golden regression fixtures..."
            gh run download $run_id --name lint-report --dir $versionedDir
            gh run download $run_id --name docstring-summary --dir $versionedDir
            gh run download $run_id --name refactor-audit --dir $versionedDir
            Write-Host "Downloaded: linting_report.json, docstring_summary.json, refactor_audit.json"
        }

        # Create "latest" directory with copies of current version
        Write-Host "Creating 'latest' reference copy..."
        Copy-Item -Path "$versionedDir\*" -Destination $latestDir -Force -Recurse

        # Create version history file
        $historyFile = Join-Path $artifactsDir "version_history.csv"
        if (-not (Test-Path $historyFile)) {
            "Version,Timestamp,RunID" | Out-File -FilePath $historyFile
        }
        "$version,$timestamp,$run_id" | Out-File -FilePath $historyFile -Append

        Write-Host "Artifacts downloaded and versioned as: $version"
    }
}
catch {
    Write-Warning "Artifact pull failed: $_"
}

# Continue with the rest of your script if needed
Write-Host "Building Docker image..."
docker build -t ghcr.io/angelosdimakos/ideas_logger:latest .

Write-Host "Pushing Docker image to GHCR..."
docker push ghcr.io/angelosdimakos/ideas_logger:latest

Write-Host "Committing code changes..."
git add -A
git commit -m "$Message"
git push

Write-Host "Compressing latest reports..."

$latestStrictness = Join-Path $latestDir "final_strictness_report.json"
$latestMerged = Join-Path $latestDir "merged_report.json"

$compressedStrictness = Join-Path $artifactsDir "final_strictness_report.comp.json"
$compressedMerged = Join-Path $artifactsDir "merged_report.comp.json"

# Check if the source files exist before attempting to compress
if (Test-Path $latestStrictness) {
    Write-Host "Compressing strictness report..."
    try {
        $strictnessResult = python scripts/refactor/compressor/strictness_report_squeezer.py compress `
           $latestStrictness `
           $compressedStrictness

        if (Test-Path $compressedStrictness) {
            Write-Host "Successfully compressed strictness report to: $compressedStrictness"
        } else {
            Write-Warning "Compression command executed but output file was not created: $compressedStrictness"
        }
    } catch {
        Write-Warning "Error compressing strictness report: $_"
    }
} else {
    Write-Warning "Source strictness report not found: $latestStrictness"
}

if (Test-Path $latestMerged) {
    Write-Host "Compressing merged report..."
    try {
        $mergedResult = python scripts/refactor/compressor/merged_report_squeezer.py compress `
           $latestMerged `
           $compressedMerged

        if (Test-Path $compressedMerged) {
            Write-Host "Successfully compressed merged report to: $compressedMerged"
        } else {
            Write-Warning "Compression command executed but output file was not created: $compressedMerged"
        }
    } catch {
        Write-Warning "Error compressing merged report: $_"
    }
} else {
    Write-Warning "Source merged report not found: $latestMerged"
}

Write-Host "Compression completed. Compressed reports should be saved to root artifacts directory."

Write-Host "Done."