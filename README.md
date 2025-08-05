# AI Business Intelligence Agent

A sophisticated AI-powered business intelligence agent built with Python ≤ 3.12, Streamlit, and LangChain. This agent can query databases, call external APIs, provide business insights, and make predictions using multiple tools and data sources.

## 🌟 Features

### Functional Requirements ✅
- **Database Integration**: Queries SQLite database without exposing full schema to LLM
- **External API Integration**: Multiple 3rd party API integrations (Weather, Market Data, etc.)
- **Business Intelligence Dashboard**: Real-time metrics and visualizations
- **Advanced Analytics**: Sales forecasting, customer segmentation, inventory alerts
- **Console Logging**: Comprehensive logging system for monitoring and debugging

### Non-Functional Requirements ✅
- **Python ≤ 3.12**: Compatible with Python 3.8 to 3.12
- **Streamlit UI**: Modern web interface with business dashboard
- **Multiple Tools**: 6+ different function calling tools for the AI agent
- **Complete Documentation**: Installation instructions and usage guide

## 🏗️ Architecture

```
├── main.py                 # Main Streamlit application
├── database_init.py        # Database setup and sample data
├── agent_tools.py          # Advanced analytics tools
├── config.py              # Configuration management
├── requirements.txt        # Python dependencies
├── data/                  # Database and data files
├── logs/                  # Application logs
└── .streamlit/            # Streamlit configuration
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 to 3.12
- pip package manager
- Git (for cloning the repository)

### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone <your-repository-url>
cd ai-business-intelligence-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Initialize Project Structure

```bash
# Run the configuration setup
python config.py
```

This will create:
- Required directories (`data/`, `logs/`, `.streamlit/`)
- Sample configuration files
- Environment templates

### Step 4: Setup Environment Variables

#### Option A: Using Streamlit Secrets (Recommended)

Create `.streamlit/secrets.toml`:

```toml
# OpenAI API Key (required for full functionality)
OPENAI_API_KEY = "your_openai_api_key_here"

# OpenWeatherMap API Key (optional)
OPENWEATHER_API_KEY = "your_openweather_api_key_here"

[database]
path = "data/business_data.db"
backup_enabled = true
```

#### Option B: Using Environment Variables

Create `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

### Step 5: Initialize Database

```bash
# Create database with sample business data
python database_init.py
```

This creates a SQLite database with:
- 8 customers with realistic profiles
- 12 products across multiple categories
- 150+ orders with order items
- 5 suppliers
- Inventory transaction logs

### Step 6: Run the Application

```bash
# Start the Streamlit application
streamlit run main.py
```

The application will be available at: `http://localhost:8501`

## 🎯 Usage

### AI Agent Capabilities

The agent includes **6+ different tools**:

1. **Database Query Tool**: Query business database for customers, orders, products
2. **Weather API Tool**: Get real-time weather information
3. **External Data Tool**: Fetch data from external APIs
4. **Business Metrics Calculator**: Calculate KPIs and performance metrics
5. **Sales Analytics Tool**: Advanced sales analysis and reporting
6. **Inventory Management Tool**: Stock alerts and inventory insights
7. **Customer Segmentation Tool**: Analyze and segment customer base
8. **Predictive Analytics Tool**: Sales forecasting and churn prediction

### Example Queries

Try asking the agent:

```
# Database Queries
"Show me the top 5 customers by total spending"
"What products are running low in stock?"
"How many orders were placed this month?"

# Analytics
"Analyze sales performance for the last 30 days"
"Which customers are at risk of churning?"
"Forecast sales for the next month"

# External Data
"What's the weather like in New York?"
"Get me some external market data"

# Business Intelligence
"Calculate key business metrics"
"Show me inventory alerts"
"Segment our customers by value"
```

### Business Dashboard

The sidebar displays real-time business metrics:
- 💰 Total Revenue
- 👥 Active Customers  
- 📦 Orders Today
- 📈 Conversion Rate
- 🎯 Average Order Value
- ⚠️ Inventory Alerts

### Data Visualizations

The right panel shows:
- Sales by category (pie chart)
- Recent activity table
- Weather widget
- Performance trends

## 🔧 Configuration

### Database Configuration

Edit `config.json` to customize database settings:

```json
{
  "database": {
    "path": "data/business_data.db",
    "backup_enabled": true,
    "backup_interval_hours": 24
  }
}
```

### API Settings

Configure AI model and external APIs:

```json
{
  "api": {
    "openai_model": "gpt-3.5-turbo",
    "max_tokens": 2000,
    "temperature": 0.1,
    "timeout": 30
  }
}
```

### Logging

Logs are written to:
- `logs/agent.log` - Application logs
- Console output - Real-time logging

Configure logging in `config.json`:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_rotation": true,
    "max_file_size_mb": 10
  }
}
```

## 🧪 Development

### Adding New Tools

1. Create your tool function in `agent_tools.py`:

```python
def my_custom_tool(parameter: str) -> str:
    """Description of what the tool does"""
    try:
        # Tool implementation
        result = {"data": "processed"}
        logger.info("Custom tool executed successfully")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Custom tool error: {e}")
        return f"Error: {str(e)}"
```

2. Add it to the agent's tools list in `main.py`:

```python
Tool(
    name="my_custom_tool",
    description="Description for the AI agent",
    func=my_custom_tool
)
```

### Database Schema

The database includes these tables:
- `customers` - Customer information and profiles
- `products` - Product catalog with inventory
- `orders` - Order headers
- `order_items` - Detailed order line items
- `suppliers` - Supplier information
- `inventory_logs` - Stock movement history

### Extending External APIs

Add new API integrations in `agent_tools.py`:

```python
async def call_new_api(self, params: dict) -> dict:
    """Call a new external API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
```

## 🚨 Troubleshooting

### Common Issues

1. **"No OpenAI API Key"**
   - Add your API key to `.streamlit/secrets.toml`
   - The agent will work in demo mode without it

2. **Database Errors**
   - Run `python database_init.py` to recreate the database
   - Check file permissions in the `data/` directory

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8-3.12)

4. **Streamlit Port Issues**
   - Use a different port: `streamlit run main.py --server.port 8502`

### Logs and Debugging

Check logs for detailed error information:
- View `logs/agent.log` for application logs
- Enable debug mode in `config.json`
- Check console output for real-time logging

## 📝 API Keys

### Required APIs
- **OpenAI**: For AI agent functionality
  - Get key: https://platform.openai.com/api-keys
  - Free tier available

### Optional APIs
- **OpenWeatherMap**: For weather data
  - Get key: https://openweathermap.org/api
  - Free tier: 1000 calls/day

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `logs/agent.log`
3. Open an issue on GitHub
4. Check configuration in `config.json`

## 🎉 Demo

The application includes sample data for immediate testing:
- 8 realistic customers
- 12 products across categories
- 150+ sample orders
- Inventory and supplier data

Start exploring right away with queries like:
- "Show me sales analytics"
- "Which customers spent the most?"
- "What's our inventory status?"

---

**Built with ❤️ using Python, Streamlit, LangChain, and modern AI technologies.**
