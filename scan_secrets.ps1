$ErrorActionPreference = 'SilentlyContinue'

Write-Host "=== SECRET SCAN ===" -ForegroundColor Cyan

$files = Get-ChildItem -Path "." -Include "*.py" -Recurse |
    Where-Object { $_.FullName -notmatch "jarvis_env|jarvis_env_312|__pycache__" }

$patterns = "AIzaSy", "iiiswouajpvqjtbp", "Dip@123", "token_urlsafe", "r2EDEcL3thsmBCUVT8Ct"
$found = 0

foreach ($pat in $patterns) {
    $hits = $files | Select-String -Pattern $pat -SimpleMatch
    foreach ($h in $hits) {
        Write-Host "  FOUND '$pat': $($h.Filename) line $($h.LineNumber)" -ForegroundColor Red
        $found++
    }
}

if ($found -eq 0) {
    Write-Host "  CLEAN: No hardcoded secrets found in .py files." -ForegroundColor Green
} else {
    Write-Host "  TOTAL ISSUES: $found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== GITIGNORE CHECK ===" -ForegroundColor Cyan

$gi = Get-Content ".gitignore" -Raw
$required = @(".env", ".streamlit/secrets.toml", "__pycache__", "*.pyc")
foreach ($entry in $required) {
    if ($gi -match [regex]::Escape($entry)) {
        Write-Host "  OK : '$entry'" -ForegroundColor Green
    } else {
        Write-Host "  MISSING : '$entry'" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== PRINT LEAK SCAN ===" -ForegroundColor Cyan

$printHits = $files | Select-String -Pattern "print\(f?[`"'].*(?i)(password|token|key|secret)" -AllMatches
foreach ($h in $printHits) {
    Write-Host "  LEAK: $($h.Filename) line $($h.LineNumber): $($h.Line.Trim())" -ForegroundColor Yellow
}
if (-not $printHits) {
    Write-Host "  CLEAN: No secret-printing found." -ForegroundColor Green
}
