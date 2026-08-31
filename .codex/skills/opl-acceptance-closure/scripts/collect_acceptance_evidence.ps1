param(
    [Parameter(Mandatory = $true)]
    [int]$AlignmentPr,

    [Parameter(Mandatory = $true)]
    [string[]]$FocusedTests,

    [string]$Repository = "F:\OpenProjectLab",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
Set-Location $Repository

$VenvScripts = Join-Path $Repository ".venv\Scripts"
$Python = Join-Path $VenvScripts "python.exe"
$env:PATH = "$VenvScripts;$env:PATH"

function Show-Command([string]$Command) {
    Write-Host ""
    Write-Host ">>> $Command" -ForegroundColor Cyan
}

function Assert-NativeSuccess([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Virtual-environment Python not found: $Python"
}
if ((git branch --show-current) -ne "main") {
    throw "Evidence collection requires main."
}
if (git status --porcelain) {
    git status --short
    throw "Evidence collection requires a clean working tree."
}

Show-Command "gh auth status --hostname github.com"
gh auth status --hostname github.com
Assert-NativeSuccess "GitHub authentication"

Show-Command "gh auth setup-git"
gh auth setup-git
Assert-NativeSuccess "GitHub Git credential setup"

Show-Command "gh pr view $AlignmentPr --json number,title,state,mergedAt,mergeCommit,url"
$Pr = gh pr view $AlignmentPr `
    --json number,title,state,mergedAt,mergeCommit,url |
    ConvertFrom-Json
Assert-NativeSuccess "Alignment PR lookup"
if ($Pr.state -ne "MERGED" -or -not $Pr.mergeCommit.oid) {
    throw "Alignment PR is not confirmed as merged."
}

Show-Command "gh pr checks $AlignmentPr"
gh pr checks $AlignmentPr
Assert-NativeSuccess "Alignment PR required CI"

Show-Command "git -c url.https://github.com/.insteadOf=git@github.com: pull --ff-only origin main"
git -c "url.https://github.com/.insteadOf=git@github.com:" pull --ff-only origin main
Assert-NativeSuccess "Authenticated HTTPS main synchronization"

$Head = git rev-parse HEAD
$OriginMain = git rev-parse origin/main
if ($Head -ne $OriginMain -or $Head -ne $Pr.mergeCommit.oid) {
    throw "Main identity does not match the alignment PR merge commit."
}

Show-Command "& `"$Python`" -m pytest $($FocusedTests -join ' ') -q --no-cov"
$TestOutput = @(& $Python -m pytest @FocusedTests -q --no-cov 2>&1)
$TestExit = $LASTEXITCODE
$TestOutput | ForEach-Object { Write-Host $_ }
if ($TestExit -ne 0) {
    throw "Post-merge focused verification failed with exit code $TestExit"
}

$Summary = @($TestOutput | Where-Object {
    $_ -match "\bpassed\b" -and $_ -notmatch "collected"
} | Select-Object -Last 1)
if ($Summary.Count -ne 1) {
    throw "The focused pytest summary could not be resolved exactly once."
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $env:TEMP (
        "opl-acceptance-evidence-pr-$AlignmentPr.json"
    )
}

$Evidence = [ordered]@{
    collected_at = (Get-Date).ToString("o")
    repository = git remote get-url origin
    branch = git branch --show-current
    head = $Head
    origin_main = $OriginMain
    working_tree_clean = -not [bool](git status --porcelain)
    alignment_pr = $Pr
    focused_tests = $FocusedTests
    focused_summary = [string]$Summary[0]
    focused_exit_code = $TestExit
}

[IO.File]::WriteAllText(
    $OutputPath,
    ($Evidence | ConvertTo-Json -Depth 8),
    [Text.UTF8Encoding]::new($false)
)

Write-Host ""
Write-Host "ACCEPTANCE EVIDENCE READY" -ForegroundColor Green
Write-Host $OutputPath
$Evidence | ConvertTo-Json -Depth 8
