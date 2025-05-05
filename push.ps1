param(
    [string]$Message = "Auto-commit"
)

Write-Host "Building Docker image..."
docker build -t ghcr.io/angelosdimakos/ideas_logger:latest .

Write-Host "Pushing Docker image to GHCR..."
docker push ghcr.io/angelosdimakos/ideas_logger:latest

Write-Host "Committing changes..."
git add -A
git commit -m "$Message"
git push

Write-Host "Done. Docker image pushed and code committed."
