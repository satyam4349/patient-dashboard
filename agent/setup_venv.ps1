# PowerShell script to set up virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing requirements..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Virtual environment setup complete!" -ForegroundColor Green
Write-Host "To activate the environment, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "To run the Gradio app, run: python gradio_app.py" -ForegroundColor Yellow