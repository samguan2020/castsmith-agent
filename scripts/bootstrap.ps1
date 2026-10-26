param(
    [string]$Python = "python",
    [string]$EngineRepository = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
& $Python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 'Python 3.11+ is required')"
if ($LASTEXITCODE -ne 0) { throw "A working Python 3.11+ interpreter is required." }
Get-Command git -ErrorAction Stop | Out-Null

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $Python -m venv (Join-Path $root ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the virtual environment." }
}

$requirements = Join-Path $root "requirements.txt"
if ($EngineRepository) {
    # Install the same pinned commit from an existing clone, not its working tree.
    $pin = ((Get-Content $requirements | Where-Object { $_ -like "castsmith @*" }) -replace "^.*@", "").Trim()
    $source = (Resolve-Path $EngineRepository).Path
    $uri = ([System.Uri]$source).AbsoluteUri
    & $venvPython -m pip install "castsmith @ git+$uri@$pin"
} else {
    & $venvPython -m pip install -r $requirements
}
if ($LASTEXITCODE -ne 0) {
    throw "Engine installation failed. Verify repository access and Git authentication; do not paste tokens."
}

& $venvPython (Join-Path $PSScriptRoot "studio.py") init
if ($LASTEXITCODE -ne 0) { throw "Workspace initialization failed." }
& $venvPython (Join-Path $PSScriptRoot "studio.py") doctor
if ($LASTEXITCODE -ne 0) { throw "Core installation checks failed." }
Write-Host "Installed. Edit .env locally, open this folder in VS Code, and select CastSmith Studio."
