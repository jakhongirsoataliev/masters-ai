# .env.template
# Copy this file to .env and fill in your actual values

# Required: OpenAI API Key for AI agent functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional: OpenWeatherMap API Key for weather data
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Development settings
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development

# Database settings
DB_PATH=data/business_data.db
DB_BACKUP_ENABLED=true

# API settings
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=2000
TEMPERATURE=0.1

# External API timeouts (seconds)
API_TIMEOUT=30
WEATHER_API_TIMEOUT=10
