#!/usr/bin/env python3
"""
GreenLens Local Setup Script
Helps set up the local development environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

# def create_virtual_environment():
#     """Create a virtual environment"""
#     venv_path = Path(".venv")
#     if venv_path.exists():
#         print("✅ Virtual environment already exists")
#         return True
    
    # return run_command("python -m venv .venv", "Creating virtual environment")

# def activate_venv_command():
#     """Get the command to activate virtual environment"""
#     if platform.system() == "Windows":
#         return ".venv\\Scripts\\activate"
#     else:
#         return "source .venv/bin/activate"

# def install_requirements():
#     """Install Python requirements"""
#     pip_cmd = ".venv/Scripts/pip" if platform.system() == "Windows" else ".venv/bin/pip"
#     return run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python packages")

# def create_env_file():
#     """Create .env file for environment variables"""
#     env_file = Path(".env")
#     if env_file.exists():
#         print("✅ .env file already exists")
#         return True
    
#     env_content = """# GreenLens Environment Variables
# # Get your API keys and add them here

# # Google Gemini AI API Key
# GEMINI_API_KEY=your_gemini_api_key_here

# # Weather API Key (from weatherapi.com)
# WEATHER_API_KEY=your_weather_api_key_here

# # Optional: Set debug mode
# DEBUG=True
# """
    
#     try:
#         with open(env_file, "w") as f:
#             f.write(env_content)
#         print("✅ Created .env file template")
#         print("⚠️  Please edit .env file and add your API keys!")
#         return True
#     except Exception as e:
#         print(f"❌ Error creating .env file: {e}")
#         return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads", "outputs", "static/outputs", 
        "attached_assets", "models", "services", "utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")
    return True

def check_model_file():
    """Check if the model file exists"""
    model_path = Path("attached_assets/efficientnet_greenlens.pth")
    if model_path.exists():
        print("✅ Model file found")
        return True
    else:
        print("⚠️  Model file not found at attached_assets/efficientnet_greenlens_1751538188206.pth")
        print("   Please place your fine-tuned model file in the attached_assets directory")
        return False

def main():
    """Main setup function"""
    print("🌱 GreenLens Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create necessary directories
    create_directories()
    
    # Check model file
    check_model_file()
    
    # Create virtual environment
    # if not create_virtual_environment():
    #     return
    
    # # Install requirements
    # if not install_requirements():
    #     return
    
    # # Create .env file
    # create_env_file()
    
    # print("\n" + "=" * 50)
    # print("🎉 Setup Complete!")
    # print("=" * 50)
    # print(f"📝 Next steps:")
    # print(f"1. Activate virtual environment: {activate_venv_command()}")
    # print(f"2. Edit .env file and add your API keys")
    # print(f"3. Place your model file in attached_assets/")
    print(f"4. Run the application: python main.py")
    print(f"5. Open http://127.0.0.1:5000 in your browser")

if __name__ == "__main__":
    main()
