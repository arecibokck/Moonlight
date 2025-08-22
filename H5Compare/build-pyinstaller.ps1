# build-lean-executable.ps1

$ErrorActionPreference = "Stop"
$VenvDir = "venv_lean"
$PackagesFile = "packages.txt"
$ReqFile = "requirements.txt"

# 1. Install pipreqs & generate plain package list (no versions), write as UTF-8
Write-Host "Installing pipreqs in the current environment..."
pip install pipreqs

Write-Host "Generating package list (without versions) with pipreqs..."
pipreqs . --force --print | Out-File -Encoding utf8 $PackagesFile

# 2. Use inline Python to add versions from local environment and create requirements.txt
Write-Host "Generating requirements.txt with correct versions from local packages..."
python -c @"
import importlib.metadata

with open('$PackagesFile', encoding='utf-8-sig') as f:
    packages = [line.strip().split('==')[0] for line in f if line.strip()]

requirements = []
for package in packages:
    try:
        version = importlib.metadata.version(package)
        requirements.append(f'{package}=={version}')
    except importlib.metadata.PackageNotFoundError:
        requirements.append(package)

with open('$ReqFile', 'w', encoding='utf-8') as f:
    f.write('\n'.join(requirements))
"@

# 3. Create and activate new lean virtual environment
Write-Host "Creating lean virtual environment..."
python -m venv $VenvDir

Write-Host "Activating lean virtual environment..."
$VenvActivate = ".\$VenvDir\Scripts\Activate.ps1"
& $VenvActivate

# 4. Upgrade pip and install dependencies
Write-Host "Upgrading pip in lean environment..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt..."
pip install -r $ReqFile

Write-Host "Installing PyInstaller..."
pip install pyinstaller

# 5. Build executable with PyInstaller and custom options, using module entry point
Write-Host "Building executable with PyInstaller in lean environment..."
pyinstaller --name H5Compare --onefile --windowed --icon=resources/h5_icon.ico --add-data 'resources;resources' --paths=. --hidden-import=H5Compare --hidden-import=H5Compare.gui launcher.py

Write-Host "`nDone! Your lean executable is in the 'dist' folder inside $VenvDir."

# Optional: Deactivate virtual environment
deactivate