"""
Configuration and environment setup for the AI Agent
"""
import os
from pathlib import Path
from typing import Dict, Any
import json
import logging

class Config:
    """Configuration management"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        self.config_file = self.base_dir / "config.json"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.settings = self.load_config()
        
        # Setup logging
        self.setup_logging()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "database": {
                "path": str(self.data_dir / "business_data.db"),
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "api": {
                "openai_model": "gpt-3.5-turbo",
                "max_tokens": 2000,
                "temperature": 0.1,
                "timeout": 30
            },
            "external_apis": {
                "weather": {
                    "base_url": "http://api.openweathermap.org/data/2.5",
                    "timeout": 10
                },
                "market_data": {
                    "enabled": False,
                    "mock_mode": True
                }
            },
            "agent": {
                "max_iterations": 10,
                "verbose": True,
                "return_intermediate_steps": True
            },
            "ui": {
                "page_title": "AI Business Intelligence Agent",
                "theme": "dark",
                "show_metrics_sidebar": True,
                "auto_refresh_interval": 300
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_rotation": True,
                "max_file_size_mb": 10
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config file: {e}, using defaults")
        else:
            # Create default config file
            self.save_config(default_config)
        
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.settings["logging"]["level"])
        log_format = self.settings["logging"]["format"]
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(self.logs_dir / "agent.log"),
                logging.StreamHandler()
            ]
        )
        
        # Set library log levels to reduce noise
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    def get_database_path(self) -> str:
        """Get database file path"""
        return self.settings["database"]["path"]
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.settings["api"]
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.settings["ui"]

# Environment setup functions
def setup_environment():
    """Setup environment variables and validate dependencies"""
    
    # Check for required environment variables
    required_env_vars = {
        "OPENAI_API_KEY": "OpenAI API key for LLM functionality",
        "OPENWEATHER_API_KEY": "OpenWeatherMap API key (optional, will use mock data if not provided)"
    }
    
    missing_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var) and var not in ["OPENWEATHER_API_KEY"]:  # Weather API is optional
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nTo set environment variables:")
        print("1. Create a .env file in the project root")
        print("2. Add your API keys:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        print("   OPENWEATHER_API_KEY=your_weather_api_key_here")
        print("\nOr set them in Streamlit secrets:")
        print("1. Create .streamlit/secrets.toml")
        print("2. Add:")
        print('   OPENAI_API_KEY = "your_openai_api_key_here"')
        print('   OPENWEATHER_API_KEY = "your_weather_api_key_here"')
    
    return len(missing_vars) == 0

def validate_dependencies():
    """Validate that all required dependencies are installed"""
    
    required_packages = [
        ("streamlit", "1.28.0"),
        ("pandas", "2.0.0"),
        ("plotly", "5.15.0"),
        ("langchain", "0.1.0"),
        ("langchain_openai", "0.1.0"),
        ("openai", "1.0.0"),
        ("httpx", "0.24.0"),
        ("numpy", "1.24.0")
    ]
    
    missing_packages = []
    
    for package, min_version in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(f"{package}>={min_version}")
    
    if missing_packages:
        print("⚠️  Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_sample_secrets_file():
    """Create a sample secrets.toml file for Streamlit"""
    
    secrets_dir = Path(".streamlit")
    secrets_file = secrets_dir / "secrets.toml"
    
    secrets_dir.mkdir(exist_ok=True)
    
    if not secrets_file.exists():
        sample_content = '''# Streamlit secrets configuration
# Copy this file and add your actual API keys

# OpenAI API Key (required for full functionality)
OPENAI_API_KEY = "your_openai_api_key_here"

# OpenWeatherMap API Key (optional, will use mock data if not provided)
OPENWEATHER_API_KEY = "your_openweather_api_key_here"

# Database settings
[database]
path = "data/business_data.db"
backup_enabled = true

# Agent settings
[agent]
max_iterations = 10
verbose = true
'''
        
        try:
            with open(secrets_file, 'w') as f:
                f.write(sample_content)
            print(f"✅ Created sample secrets file: {secrets_file}")
            print("Please edit it with your actual API keys")
        except Exception as e:
            print(f"❌ Error creating secrets file: {e}")

def initialize_project():
    """Initialize the project structure and configuration"""
    
    print("🚀 Initializing AI Business Intelligence Agent...")
    
    # Validate dependencies
    if not validate_dependencies():
        print("❌ Dependency validation failed")
        return False
    
    # Setup environment
    env_ok = setup_environment()
    
    # Create configuration
    config = Config()
    print(f"✅ Configuration loaded from: {config.config_file}")
    
    # Create sample secrets file
    create_sample_secrets_file()
    
    # Create project structure
    project_structure = {
        "data": "Database and data files",
        "logs": "Application logs",
        ".streamlit": "Streamlit configuration",
        "assets": "Static assets (images, etc.)"
    }
    
    for directory, description in project_structure.items():
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}/ - {description}")
    
    # Create .env template
    env_template = Path(".env.template")
    if not env_template.exists():
        with open(env_template, 'w') as f:
            f.write("""# Environment variables template
# Copy this to .env and fill in your actual values

# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Development settings
DEBUG=false
LOG_LEVEL=INFO
""")
        print("✅ Created .env template file")
    
    print("\n🎉 Project initialization complete!")
    
    if not env_ok:
        print("\n⚠️  Note: Some environment variables are missing.")
        print("The agent will work with limited functionality until API keys are provided.")
    
    print("\nNext steps:")
    print("1. Add your API keys to .streamlit/secrets.toml or .env")
    print("2. Run: python database_init.py (to setup sample data)")
    print("3. Run: streamlit run main.py")
    
    return True

if __name__ == "__main__":
    initialize_project()
