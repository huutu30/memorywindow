param (
    [Parameter(Mandatory=$true)]
    [string]$TargetDir
)

if (-not (Test-Path $TargetDir)) {
    Write-Error "Thu muc dich khong ton tai: $TargetDir"
    exit 1
}

$sourceAgents = Join-Path $PSScriptRoot "..\AGENTS.md"
$sourceClaude = Join-Path $PSScriptRoot "..\CLAUDE.md"
$destAgents = Join-Path $TargetDir "AGENTS.md"
$destClaude = Join-Path $TargetDir "CLAUDE.md"

Copy-Item -Path $sourceAgents -Destination $destAgents -Force
Copy-Item -Path $sourceClaude -Destination $destClaude -Force

Write-Host "✅ Da dong bo thanh cong AGENTS.md va CLAUDE.md sang: $TargetDir" -ForegroundColor Green
