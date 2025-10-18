#!/usr/bin/env python3
"""
Setup script for YouTube Comment Section Analyzer
This script helps set up the application for first-time use
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🎬 YouTube Comment Section Analyzer - Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    print("\n📦 Checking backend dependencies...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found in backend directory")
        return False
    
    try:
        # Try to import key dependencies
        import flask
        import sqlalchemy
        print("✅ Backend dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r backend/requirements.txt")
        return False

def check_environment_file():
    """Check if .env file exists and is configured"""
    print("\n🔧 Checking environment configuration...")
    env_file = Path("backend/.env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Create backend/.env with your API keys:")
        print("   YOUTUBE_API_KEY=your_youtube_api_key")
        print("   OPENAI_API_KEY=your_openai_api_key")
        return False
    
    # Check if API keys are set
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_youtube_api_key" in content or "your_openai_api_key" in content:
            print("⚠️  .env file exists but contains placeholder values")
            print("💡 Update backend/.env with your actual API keys")
            return False
    
    print("✅ Environment file is configured")
    return True

def check_database():
    """Check if database is initialized"""
    print("\n🗄️  Checking database...")
    try:
        # Try to import and check database
        sys.path.append("backend")
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'videos' in tables and 'comments' in tables:
                print("✅ Database is initialized")
                return True
            else:
                print("⚠️  Database tables not found")
                print("💡 Run: python -c \"from app import create_app, db; create_app().app_context().push(); db.create_all()\"")
                return False
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def start_servers():
    """Start both backend and frontend servers"""
    print("\n🚀 Starting servers...")
    print("📝 Instructions:")
    print("   1. Open a new terminal and run: cd backend && python run.py")
    print("   2. Open another terminal and run: python start_server.py")
    print("   3. Open your browser to: http://localhost:8080")
    print()

def main():
    print_header()
    
    # Check all requirements
    checks = [
        check_python_version(),
        check_backend_dependencies(),
        check_environment_file(),
        check_database()
    ]
    
    print("\n" + "=" * 60)
    
    if all(checks):
        print("🎉 Setup complete! All checks passed.")
        print("\n🚀 Ready to start the application:")
        start_servers()
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        print("\n📚 For detailed setup instructions, see README.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
