$ErrorActionPreference = 'Stop'
$venv = Join-Path $PSScriptRoot '.venv'
if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    python -m venv $venv
    if ($LASTEXITCODE) { throw 'Install Python 3 with Tk support first.' }
}
$pythonExe = Join-Path $venv 'Scripts\python.exe'
& $pythonExe -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE) { throw 'Could not install dashboard requirements.' }
Start-Process -FilePath $pythonExe -ArgumentList @((Join-Path $PSScriptRoot 'robot_dashboard.py')) -WindowStyle Normal
