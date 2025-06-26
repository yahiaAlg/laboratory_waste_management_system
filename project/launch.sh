#!/bin/bash

# Django Project Launcher Script
# Usage: ./launch.sh [command]
# Commands: setup, run, migrate, shell, test, reset

PROJECT_NAME="Django Business Management System"
PYTHON_CMD="python"
MANAGE_PY="manage.py"
VENV_DIR="venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $PROJECT_NAME${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python -m venv $VENV_DIR
        print_status "Virtual environment created."
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        source $VENV_DIR/bin/activate 2>/dev/null || source $VENV_DIR/Scripts/activate 2>/dev/null
        print_status "Virtual environment activated."
    else
        print_error "Virtual environment not found!"
        exit 1
    fi
}

# Install requirements
install_requirements() {
    if [ -f "requirements.txt" ]; then
        print_status "Installing requirements..."
        pip install -r requirements.txt
        print_status "Requirements installed successfully."
    else
        print_warning "requirements.txt not found. Skipping dependency installation."
    fi
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."
    $PYTHON_CMD $MANAGE_PY makemigrations
    $PYTHON_CMD $MANAGE_PY migrate
    print_status "Migrations completed."
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    $PYTHON_CMD $MANAGE_PY collectstatic --noinput
    print_status "Static files collected."
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    $PYTHON_CMD $MANAGE_PY createsuperuser
}

# Setup project
setup_project() {
    print_header
    print_status "Setting up Django project..."
    
    check_venv
    activate_venv
    install_requirements
    run_migrations
    
    # Run custom management commands if they exist
    if [ -f "apps/dashboard/management/commands/populate_db.py" ]; then
        print_status "Populating database with initial data..."
        $PYTHON_CMD $MANAGE_PY populate_db
    fi
    
    if [ -f "apps/customers/management/commands/populate_cities.py" ]; then
        print_status "Populating cities data..."
        $PYTHON_CMD $MANAGE_PY populate_cities
    fi
    
    collect_static
    
    echo
    print_status "Setup completed! You can now run the development server."
    print_status "Use: ./launch.sh run"
}

# Run development server
run_server() {
    print_header
    activate_venv
    print_status "Starting Django development server..."
    print_status "Server will be available at: http://127.0.0.1:8000"
    print_status "Admin panel: http://127.0.0.1:8000/admin"
    echo
    $PYTHON_CMD $MANAGE_PY runserver
}

# Run Django shell
run_shell() {
    activate_venv
    print_status "Starting Django shell..."
    $PYTHON_CMD $MANAGE_PY shell
}

# Run tests
run_tests() {
    activate_venv
    print_status "Running tests..."
    $PYTHON_CMD $MANAGE_PY test
}

# Reset database
reset_database() {
    print_warning "This will delete your database and all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        activate_venv
        print_status "Removing database..."
        rm -f db.sqlite3
        print_status "Removing migration files..."
        find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
        find . -path "*/migrations/*.pyc" -delete
        run_migrations
        print_status "Database reset completed."
    else
        print_status "Database reset cancelled."
    fi
}

# Show help
show_help() {
    print_header
    echo "Available commands:"
    echo "  setup    - Initial project setup (install deps, migrate, populate data)"
    echo "  run      - Start development server"
    echo "  migrate  - Run database migrations"
    echo "  shell    - Open Django shell"
    echo "  test     - Run tests"
    echo "  reset    - Reset database (WARNING: destructive)"
    echo "  help     - Show this help message"
    echo
    echo "Usage: ./launch.sh [command]"
    echo "If no command is provided, 'run' is used by default."
}

# Main script logic
case "${1:-run}" in
    "setup")
        setup_project
        ;;
    "run")
        run_server
        ;;
    "migrate")
        activate_venv
        run_migrations
        ;;
    "shell")
        run_shell
        ;;
    "test")
        run_tests
        ;;
    "reset")
        reset_database
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac