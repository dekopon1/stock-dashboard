# Locate gh executable
$ghCmd = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghCmd) {
    $found = Get-ChildItem 'C:\Program Files' -Recurse -Filter gh.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $ghCmd = @{ Path = $found.FullName } }
}

if (-not $ghCmd) {
    Write-Output "gh (GitHub CLI) not found on this machine. Please install and authenticate with 'gh auth login'."
    exit 1
}

$ghPath = $ghCmd.Path
Write-Output "Using gh: $ghPath"
& $ghPath --version

# Check authentication
$auth = & $ghPath auth status 2>&1
Write-Output $auth
if ($auth -notmatch 'Logged in to') {
    Write-Output "gh is not authenticated. Please run: gh auth login --web and re-run this script."
    exit 1
}

# Create repo and push
Set-Location -Path "C:\Users\stecarter\OneDrive - Microsoft\Desktop\Vibe Code Playground"
Write-Output "Creating repo 'stock-dashboard' and pushing..."
$create = & $ghPath repo create stock-dashboard --public --source=. --remote=origin --push --confirm 2>&1
Write-Output $create
