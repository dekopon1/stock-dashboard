# Locate git executable
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    $candidates = @(
        'C:\Program Files\Git\cmd\git.exe',
        'C:\Program Files (x86)\Git\cmd\git.exe'
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { $gitCmd = @{ Path = $p }; break }
    }
}

if (-not $gitCmd) {
    Write-Output "git executable not found on PATH or standard Program Files locations. Aborting."
    exit 1
}

$gitPath = $gitCmd.Path
Write-Output "Using git: $gitPath"
& $gitPath --version

Set-Location -Path "C:\Users\stecarter\OneDrive - Microsoft\Desktop\Vibe Code Playground"

# Initialize repo and commit
& $gitPath init
& $gitPath checkout -b main
& $gitPath add .
$commitResult = & $gitPath commit -m "Initial commit: stock dashboard" 2>&1
Write-Output $commitResult

# Try creating GitHub repo if gh CLI is available
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Output "Found gh CLI; creating remote repo and pushing..."
    gh repo create stock-dashboard --public --source=. --remote=origin --push --confirm
} else {
    Write-Output "gh CLI not found; skipping remote creation. You can push manually later."
}
