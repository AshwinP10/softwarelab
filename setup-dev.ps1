<#
setup-dev.ps1

Windows PowerShell helper to create a backend virtual environment and install dependencies,
and install frontend npm packages. It does NOT commit secrets. Use the -Start switch to
optionally launch the backend and frontend in new PowerShell windows.

Usage examples:
  .\setup-dev.ps1            # install deps
  .\setup-dev.ps1 -Start    # install deps, then open new windows to run backend and frontend
#>

param(
    [switch]$Start
)

Set-StrictMode -Version Latest

function Run-InApi {
    Push-Location -Path "$(Join-Path $PSScriptRoot 'api')"
    if (-Not (Test-Path .venv)) {
        Write-Output "Creating Python virtualenv in ./api/.venv"
        python -m venv .venv
    } else {
        Write-Output "Using existing ./api/.venv"
    }
    Write-Output "Activating backend venv and installing Python requirements..."
    . .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r requirements.txt
    Pop-Location
}

function Run-InFrontend {
    Push-Location -Path "$(Join-Path $PSScriptRoot 'frontend')"
    Write-Output "Installing frontend npm packages..."
    npm install
    Pop-Location
}

try {
    Run-InApi
    Run-InFrontend
    Write-Output "Dependencies installed. See README for how to run servers."

    if ($Start) {
        Write-Output "Opening new PowerShell windows to start backend and frontend..."
        Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd '$PSScriptRoot\api'; . .\.venv\Scripts\Activate.ps1; python app.py" -WindowStyle Normal
        Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal
    }
} catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    exit 1
}
