# Django Project Launcher Script for PowerShell
# Usage: .\launch.ps1 [command]
# Commands: setup, run, migrate, shell, test, reset

param(
    [string]$Command = "run"
)

$ProjectName = "Django Business Management System"
$PythonCmd = "python"
$ManagePy = "manage.py"
$VenvDir = "venv"

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Header {
    Write-Host "================================" -ForegroundColor Blue
    Write-Host " $ProjectName" -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
}

# Check if virtual environment exists
function Test-VirtualEnvironment {
    if (-not (Test-Path $VenvDir)) {
        Write-Warning "Virtual environment not found. Creating one..."
        & $PythonCmd -m venv $VenvDir
        Write-Status "Virtual environment created."
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    if (Test-Path $VenvDir) {
        if (Test-Path "$VenvDir\Scripts\Activate.ps1") {
            & "$VenvDir\Scripts\Activate.ps1"
        } else {
            Write-Error "Virtual environment activation script not found!"
            exit 1
        }
        Write-Status "Virtual environment activated."
    } else {
        Write-Error "Virtual environment not found!"
        exit 1
    }
}

# Install requirements
function Install-Requirements {
    if (Test-Path "requirements.txt") {
        Write-Status "Installing requirements..."
        pip install -r requirements.txt
        Write-Status "Requirements installed successfully."
    } else {
        Write-Warning "requirements.txt not found. Skipping dependency installation."
    }
}

# Run migrations
function Invoke-Migrations {
    Write-Status "Running database migrations..."
    & $PythonCmd $ManagePy makemigrations
    & $PythonCmd $ManagePy migrate
    Write-Status "Migrations completed."
}

# Collect static files
function Invoke-CollectStatic {
    Write-Status "Collecting static files..."
    & $PythonCmd $ManagePy collectstatic --noinput
    Write-Status "Static files collected."
}

# Setup project
function Initialize-Project {
    Write-Header
    Write-Status "Setting up Django project..."
    
    Test-VirtualEnvironment
    Enable-VirtualEnvironment
    Install-Requirements
    Invoke-Migrations
    
    # Run custom management commands if they exist
    if (Test-Path "apps\dashboard\management\commands\populate_db.py") {
        Write-Status "Populating database with initial data..."
        & $PythonCmd $ManagePy populate_db
    }
    
    if (Test-Path "apps\customers\management\commands\populate_cities.py") {
        Write-Status "Populating cities data..."
        & $PythonCmd $ManagePy populate_cities
    }
    if (Test-Path "apps\authentication\management\commands\create_superuser.py") {
        Write-Status "create admin user..."
        & $PythonCmd $ManagePy create_superuser
    }
    
    Invoke-CollectStatic
    
    Write-Host ""
    Write-Status "Setup completed! You can now run the development server."
    Write-Status "Use: .\launch.ps1 run"
}

# Run development server
function Start-DevelopmentServer {
    Write-Header
    Enable-VirtualEnvironment
    Write-Status "Starting Django development server..."
    Write-Status "Server will be available at: http://127.0.0.1:8000"
    Write-Status "Admin panel: http://127.0.0.1:8000/admin"
    Write-Host ""
    & $PythonCmd $ManagePy runserver
}

# Run Django shell
function Start-DjangoShell {
    Enable-VirtualEnvironment
    Write-Status "Starting Django shell..."
    & $PythonCmd $ManagePy shell
}

# Run tests
function Invoke-Tests {
    Enable-VirtualEnvironment
    Write-Status "Running tests..."
    & $PythonCmd $ManagePy test
}

# Reset database
function Reset-Database {
    Write-Warning "This will delete your database and all data!"
    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Enable-VirtualEnvironment
        Write-Status "Removing database..."
        if (Test-Path "db.sqlite3") {
            Remove-Item "db.sqlite3" -Force
        }
        Write-Status "Removing migration files..."
        Get-ChildItem -Path . -Recurse -Filter "*.py" | Where-Object { 
            $_.FullName -like "*\migrations\*" -and $_.Name -ne "__init__.py"
        } | Remove-Item -Force
        Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Where-Object { 
            $_.FullName -like "*\migrations\*"
        } | Remove-Item -Force
        Invoke-Migrations
        Write-Status "Database reset completed."
    } else {
        Write-Status "Database reset cancelled."
    }
}

# Show help
function Show-Help {
    Write-Header
    Write-Host "Available commands:"
    Write-Host "  setup    - Initial project setup (install deps, migrate, populate data)"
    Write-Host "  run      - Start development server"
    Write-Host "  migrate  - Run database migrations"
    Write-Host "  shell    - Open Django shell"
    Write-Host "  test     - Run tests"
    Write-Host "  reset    - Reset database (WARNING: destructive)"
    Write-Host "  help     - Show this help message"
    Write-Host ""
    Write-Host "Usage: .\launch.ps1 [command]"
    Write-Host "If no command is provided, 'run' is used by default."
}

# Main script logic
switch ($Command.ToLower()) {
    "setup" {
        Initialize-Project
    }
    "run" {
        Start-DevelopmentServer
    }
    "migrate" {
        Enable-VirtualEnvironment
        Invoke-Migrations
    }
    "shell" {
        Start-DjangoShell
    }
    "test" {
        Invoke-Tests
    }
    "reset" {
        Reset-Database
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}