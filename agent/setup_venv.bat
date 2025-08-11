@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

echo Installing core dependencies first...
pip install python-dotenv requests typing-extensions

echo Installing web framework dependencies...
pip install fastapi uvicorn pydantic

echo Installing gradio (this may take a moment)...
pip install gradio

echo Installing pandas (this may take a moment)...
pip install pandas

echo Virtual environment setup complete!
echo To activate the environment, run: venv\Scripts\activate.bat
echo To run the Gradio app, run: python gradio_app.py
pause