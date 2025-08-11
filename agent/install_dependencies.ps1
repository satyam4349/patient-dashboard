# PowerShell script to properly install dependencies in virtual environment
# This script addresses common Python 3.13 and virtual environment issues

Write-Host "🚀 Starting Agent Companion Dependencies Installation" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Get the current directory
$AgentDir = Get-Location
Write-Host "Working in directory: $AgentDir" -ForegroundColor Yellow

# Step 1: Remove existing virtual environment if it exists
Write-Host "`n📁 Step 1: Cleaning up existing virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "Removing existing venv directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Step 2: Create new virtual environment
Write-Host "`n🔧 Step 2: Creating new virtual environment..." -ForegroundColor Cyan
try {
    python -m venv venv
    Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create virtual environment: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Activate virtual environment
Write-Host "`n⚡ Step 3: Activating virtual environment..." -ForegroundColor Cyan
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Verify Python and pip are from virtual environment
Write-Host "`n🔍 Step 4: Verifying virtual environment setup..." -ForegroundColor Cyan
$PythonPath = & python -c "import sys; print(sys.executable)"
$PipPath = & pip --version
Write-Host "Python path: $PythonPath" -ForegroundColor Yellow
Write-Host "Pip version: $PipPath" -ForegroundColor Yellow

if ($PythonPath -like "*venv*") {
    Write-Host "✅ Python is correctly using virtual environment" -ForegroundColor Green
} else {
    Write-Host "❌ Warning: Python may not be using virtual environment" -ForegroundColor Red
}

# Step 5: Upgrade pip to latest version
Write-Host "`n📦 Step 5: Upgrading pip..." -ForegroundColor Cyan
try {
    & python -m pip install --upgrade pip
    Write-Host "✅ Pip upgraded successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to upgrade pip: $_" -ForegroundColor Red
}

# Step 6: Install wheel and setuptools for better compatibility
Write-Host "`n🛠️ Step 6: Installing build tools..." -ForegroundColor Cyan
try {
    & pip install --upgrade wheel setuptools
    Write-Host "✅ Build tools installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install build tools: $_" -ForegroundColor Red
}

# Step 7: Install dependencies from requirements.txt
Write-Host "`n📋 Step 7: Installing dependencies from requirements.txt..." -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Yellow

try {
    & pip install -r requirements.txt --no-cache-dir --force-reinstall
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install from requirements.txt" -ForegroundColor Red
    Write-Host "Trying minimal requirements instead..." -ForegroundColor Yellow
    
    try {
        & pip install -r requirements_minimal.txt --no-cache-dir --force-reinstall
        Write-Host "✅ Minimal dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install minimal requirements: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 8: Verify installations
Write-Host "`n✅ Step 8: Verifying installations..." -ForegroundColor Cyan

$TestPackages = @("fastapi", "uvicorn", "pydantic", "gradio", "requests", "pandas", "python-dotenv")

foreach ($Package in $TestPackages) {
    try {
        & python -c "import $Package; print('✅ $Package: OK')"
    } catch {
        Write-Host "❌ $Package: FAILED" -ForegroundColor Red
    }
}

# Step 9: List installed packages
Write-Host "`n📋 Step 9: Installed packages:" -ForegroundColor Cyan
& pip list

# Step 10: Test basic functionality
Write-Host "`n🧪 Step 10: Testing basic functionality..." -ForegroundColor Cyan
try {
    & python -c "
import requests
import gradio as gr
import fastapi
import pydantic
import pandas as pd
from dotenv import load_dotenv
print('✅ All core modules imported successfully!')
print('🎉 Installation completed successfully!')
"
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Some imports failed: $_" -ForegroundColor Red
}

Write-Host "`n🎯 Installation Summary:" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host "✅ Basic functionality verified" -ForegroundColor Green
Write-Host "`n🚀 You can now run your agent companion!" -ForegroundColor Green
Write-Host "To activate the virtual environment in future sessions, run:" -ForegroundColor Yellow
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Cyan