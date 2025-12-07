"""
Quick setup script for Blood Donation Network.
Runs all initialization steps in sequence.
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and print its output."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print('='*60)
    result = subprocess.run(command, shell=True, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"✗ Error in step: {description}")
        return False
    print(f"✓ Completed: {description}")
    return True

def main():
    """Main setup function."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   Blood Donation Network - Quick Setup Script             ║
    ║   This will set up your development environment           ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("\n⚠ Virtual environment not found!")
        create_venv = input("Do you want to create a virtual environment? (yes/no): ")
        if create_venv.lower() == 'yes':
            print("\nCreating virtual environment...")
            if not run_command('python3 -m venv venv', 'Create virtual environment'):
                sys.exit(1)
            print("\n✓ Virtual environment created!")
            print("\nPlease activate it and run this script again:")
            print("  macOS/Linux: source venv/bin/activate")
            print("  Windows: venv\\Scripts\\activate")
            sys.exit(0)
        else:
            print("Setup cancelled.")
            sys.exit(0)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠ .env file not found!")
        print("Copying .env.example to .env...")
        try:
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✓ .env file created!")
            print("\n⚠ IMPORTANT: Edit .env file with your configuration before continuing!")
            edit_env = input("Have you configured .env file? (yes/no): ")
            if edit_env.lower() != 'yes':
                print("Please configure .env file and run this script again.")
                sys.exit(0)
        except Exception as e:
            print(f"✗ Error creating .env file: {e}")
            sys.exit(1)
    
    steps = [
        ("pip install -r requirements.txt", "Install dependencies"),
        ("python init_db.py", "Initialize database"),
        ("python create_admin.py", "Create admin user"),
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n✗ Setup failed at: {description}")
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print("✓ Setup completed successfully!")
    print('='*60)
    print("\nYou can now run the application:")
    print("  python run.py")
    print("\nOr using Flask CLI:")
    print("  flask run")
    print("\nAccess the application at: http://localhost:5000")
    print('='*60)

if __name__ == '__main__':
    main()
