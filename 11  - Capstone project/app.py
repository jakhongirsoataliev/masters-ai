import streamlit as st
import pandas as pd
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import os
from dataclasses import dataclass
import plotly.express as px
import plotly.graph_objects as go
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import asyncio
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BusinessMetrics:
    total_revenue: float
    active_customers: int
    orders_today: int
    conversion_rate: float
    avg_order_value: float
    inventory_alerts: int

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "business_data.db"):
        self.db_path = db_path
        self.init_database()
        logger.info(f"Database initialized at {db_path}")
    
    def init_database(self):
        """Initialize database with sample tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                registration_date DATE,
                total_spent REAL DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE,
                amount REAL,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock_quantity INTEGER,
                last_updated DATE
            )
        ''')
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_sample_data(self, cursor):
        """Insert sample business data"""
        # Sample customers
        customers = [
            ("John Doe", "john@email.com", "2024-01-15", 1250.50, "active"),
            ("Jane Smith", "jane@email.com", "2024-02-20", 890.25, "active"),
            ("Bob Johnson", "bob@email.com", "2024-03-10", 2100.75, "premium"),
            ("Alice Brown", "alice@email.com", "2024-01-05", 650.00, "active"),
            ("Charlie Wilson", "charlie@email.com", "2024-02-28", 1850.30, "premium")
        ]
        
        cursor.executemany(
            "INSERT INTO customers (name, email, registration_date, total_spent, status) VALUES (?, ?, ?, ?, ?)",
            customers
        )
        
        # Sample products
        products = [
            ("Laptop Pro", "Electronics", 1299.99, 45, "2024-08-01"),
            ("Wireless Headphones", "Electronics", 199.99, 120, "2024-08-01"),
            ("Office Chair", "Furniture", 350.00, 25, "2024-08-01"),
            ("Coffee Maker", "Appliances", 89.99, 60, "2024-08-01"),
            ("Smartphone", "Electronics", 699.99, 15, "2024-08-01")
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, price, stock_quantity, last_updated) VALUES (?, ?, ?, ?, ?)",
            products
        )
        
        # Sample orders
        orders = [
            (1, "2024-08-01", 1299.99, "completed"),
            (2, "2024-08-02", 199.99, "completed"),
            (3, "2024-08-03", 350.00, "pending"),
            (1, "2024-08-04", 89.99, "completed"),
            (4, "2024-08-05", 699.99, "completed")
        ]
        
        cursor.executemany(
            "INSERT INTO orders (customer_id, order_date, amount, status) VALUES (?, ?, ?, ?)",
            orders
        )
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            logger.info(f"Query executed successfully: {query[:100]}...")
            return results
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []

class ExternalAPIManager:
    """Manages external API calls"""
    
    def __init__(self):
        self.base_urls = {
            "weather": "http://api.openweathermap.org/data/2.5",
            "jsonplaceholder": "https://jsonplaceholder.typicode.com"
        }
        logger.info("External API manager initialized")
    
    async def get_weather_data(self, city: str = "New York") -> Dict:
        """Get weather data from OpenWeatherMap API"""
        try:
            # Note: In production, use a real API key
            api_key = st.secrets.get("OPENWEATHER_API_KEY", "demo_key")
            url = f"{self.base_urls['weather']}/weather"
            params = {"q": city, "appid": api_key, "units": "metric"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Weather data retrieved for {city}")
                    return {
                        "city": city,
                        "temperature": data.get("main", {}).get("temp", 20),
                        "description": data.get("weather", [{}])[0].get("description", "clear sky"),
                        "humidity": data.get("main", {}).get("humidity", 50)
                    }
                else:
                    # Return mock data if API call fails
                    return {
                        "city": city,
                        "temperature": 22,
                        "description": "partly cloudy",
                        "humidity": 55
                    }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {
                "city": city,
                "temperature": 20,
                "description": "data unavailable",
                "humidity": 50
            }
    
    async def get_external_data(self, endpoint: str) -> Dict:
        """Get data from JSONPlaceholder API for testing"""
        try:
            url = f"{self.base_urls['jsonplaceholder']}/{endpoint}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"External data retrieved from {endpoint}")
                    return {"data": data[:5] if isinstance(data, list) else data}  # Limit results
        except Exception as e:
            logger.error(f"External API error: {e}")
        
        return {"data": [], "error": "Failed to fetch external data"}

class BusinessIntelligenceAgent:
    """Main AI Agent for business intelligence"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api_manager = ExternalAPIManager()
        self.setup_tools()
        self.setup_agent()
        logger.info("Business Intelligence Agent initialized")
    
    def setup_tools(self):
        """Setup tools for the agent"""
        
        def query_database(query: str) -> str:
            """Query the business database"""
            try:
                results = self.db.execute_query(query)
                logger.info(f"Database tool executed query with {len(results)} results")
                return json.dumps(results, default=str)
            except Exception as e:
                logger.error(f"Database tool error: {e}")
                return f"Error executing query: {str(e)}"
        
        def get_weather_info(city: str = "New York") -> str:
            """Get current weather information"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                weather_data = loop.run_until_complete(self.api_manager.get_weather_data(city))
                loop.close()
                logger.info(f"Weather tool executed for {city}")
                return json.dumps(weather_data)
            except Exception as e:
                logger.error(f"Weather tool error: {e}")
                return f"Error getting weather data: {str(e)}"
        
        def fetch_external_data(endpoint: str) -> str:
            """Fetch data from external APIs"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                external_data = loop.run_until_complete(self.api_manager.get_external_data(endpoint))
                loop.close()
                logger.info(f"External API tool executed for {endpoint}")
                return json.dumps(external_data, default=str)
            except Exception as e:
                logger.error(f"External API tool error: {e}")
                return f"Error fetching external data: {str(e)}"
        
        def calculate_business_metrics() -> str:
            """Calculate key business metrics"""
            try:
                # Get total revenue
                revenue_query = "SELECT SUM(amount) as total_revenue FROM orders WHERE status = 'completed'"
                revenue_result = self.db.execute_query(revenue_query)
                total_revenue = revenue_result[0]['total_revenue'] or 0
                
                # Get active customers
                customer_query = "SELECT COUNT(*) as active_customers FROM customers WHERE status IN ('active', 'premium')"
                customer_result = self.db.execute_query(customer_query)
                active_customers = customer_result[0]['active_customers']
                
                # Get today's orders
                today_query = "SELECT COUNT(*) as orders_today FROM orders WHERE date(order_date) = date('now')"
                today_result = self.db.execute_query(today_query)
                orders_today = today_result[0]['orders_today']
                
                # Calculate conversion rate (mock calculation)
                conversion_rate = min(95.5, orders_today * 10 + 65)
                
                # Calculate average order value
                avg_query = "SELECT AVG(amount) as avg_order_value FROM orders WHERE status = 'completed'"
                avg_result = self.db.execute_query(avg_query)
                avg_order_value = avg_result[0]['avg_order_value'] or 0
                
                # Get inventory alerts
                inventory_query = "SELECT COUNT(*) as low_stock FROM products WHERE stock_quantity < 20"
                inventory_result = self.db.execute_query(inventory_query)
                inventory_alerts = inventory_result[0]['low_stock']
                
                metrics = BusinessMetrics(
                    total_revenue=float(total_revenue),
                    active_customers=active_customers,
                    orders_today=orders_today,
                    conversion_rate=float(conversion_rate),
                    avg_order_value=float(avg_order_value),
                    inventory_alerts=inventory_alerts
                )
                
                logger.info("Business metrics calculated successfully")
                return json.dumps(metrics.__dict__)
                
            except Exception as e:
                logger.error(f"Business metrics calculation error: {e}")
                return f"Error calculating metrics: {str(e)}"
        
        self.tools = [
            Tool(
                name="query_database",
                description="Query the business database to get information about customers, orders, and products",
                func=query_database
            ),
            Tool(
                name="get_weather_info",
                description="Get current weather information for a specified city",
                func=get_weather_info
            ),
            Tool(
                name="fetch_external_data",
                description="Fetch data from external APIs (posts, users, todos, etc.)",
                func=fetch_external_data
            ),
            Tool(
                name="calculate_business_metrics",
                description="Calculate key business metrics like revenue, customers, conversion rates",
                func=calculate_business_metrics
            )
        ]
    
    def setup_agent(self):
        """Setup the LangChain agent"""
        try:
            # Use OpenAI API key from Streamlit secrets or environment
            api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "demo_key")
            
            if api_key == "demo_key":
                logger.warning("Using demo API key - agent responses will be simulated")
                self.llm = None
                self.agent_executor = None
                return
            
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=api_key
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful business intelligence agent. You have access to tools that can:
                1. Query the business database for customer, order, and product information
                2. Get weather information for any city
                3. Fetch external data from APIs
                4. Calculate business metrics
                
                Always use the appropriate tools to answer questions and provide data-driven insights.
                When querying the database, use proper SQL syntax.
                Be concise but informative in your responses."""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            agent = create_openai_functions_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            logger.info("LangChain agent setup completed")
            
        except Exception as e:
            logger.error(f"Agent setup error: {e}")
            self.llm = None
            self.agent_executor = None
    
    def process_query(self, query: str, chat_history: List = None) -> str:
        """Process user query through the agent"""
        try:
            if self.agent_executor is None:
                return self._simulate_agent_response(query)
            
            if chat_history is None:
                chat_history = []
            
            response = self.agent_executor.invoke({
                "input": query,
                "chat_history": chat_history
            })
            
            logger.info(f"Agent processed query: {query[:50]}...")
            return response["output"]
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return f"I encountered an error processing your query: {str(e)}"
    
    def _simulate_agent_response(self, query: str) -> str:
        """Simulate agent response when OpenAI API is not available"""
        query_lower = query.lower()
        
        if "customer" in query_lower or "user" in query_lower:
            customers = self.db.execute_query("SELECT COUNT(*) as count FROM customers")
            return f"I found {customers[0]['count']} customers in the database. Here are some insights: We have a mix of active and premium customers with varying spending patterns."
        
        elif "order" in query_lower or "sale" in query_lower:
            orders = self.db.execute_query("SELECT COUNT(*) as count, SUM(amount) as total FROM orders WHERE status = 'completed'")
            return f"I found {orders[0]['count']} completed orders with total revenue of ${orders[0]['total']:.2f}."
        
        elif "weather" in query_lower:
            return "Current weather in New York: 22°C, partly cloudy with 55% humidity. Weather conditions can affect customer shopping patterns."
        
        elif "metric" in query_lower or "kpi" in query_lower:
            # Calculate actual metrics
            metrics_tool = next(tool for tool in self.tools if tool.name == "calculate_business_metrics")
            metrics_json = metrics_tool.func()
            metrics = json.loads(metrics_json)
            return f"Key business metrics: Revenue: ${metrics['total_revenue']:.2f}, Active Customers: {metrics['active_customers']}, Orders Today: {metrics['orders_today']}, Conversion Rate: {metrics['conversion_rate']:.1f}%"
        
        else:
            return "I can help you with customer data, order information, business metrics, weather data, and external API integrations. What would you like to know?"

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AI Business Intelligence Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "agent" not in st.session_state:
        st.session_state.agent = BusinessIntelligenceAgent()
        st.session_state.chat_history = []
        st.session_state.business_metrics = None
    
    # Header
    st.title("🤖 AI Business Intelligence Agent")
    st.markdown("*Powered by LangChain, Streamlit, and Multiple Data Sources*")
    
    # Sidebar with business metrics
    with st.sidebar:
        st.header("📊 Business Dashboard")
        
        # Calculate and display business metrics
        try:
            metrics_tool = next(tool for tool in st.session_state.agent.tools if tool.name == "calculate_business_metrics")
            metrics_json = metrics_tool.func()
            metrics = json.loads(metrics_json)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Total Revenue", f"${metrics['total_revenue']:,.2f}")
                st.metric("👥 Active Customers", f"{metrics['active_customers']:,}")
                st.metric("📦 Orders Today", f"{metrics['orders_today']:,}")
            
            with col2:
                st.metric("📈 Conversion Rate", f"{metrics['conversion_rate']:.1f}%")
                st.metric("🎯 Avg Order Value", f"${metrics['avg_order_value']:,.2f}")
                st.metric("⚠️ Inventory Alerts", f"{metrics['inventory_alerts']:,}")
            
            st.session_state.business_metrics = metrics
            
        except Exception as e:
            st.error(f"Error loading business metrics: {e}")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        if st.button("📊 Show Sales Chart"):
            st.session_state.show_chart = True
        
        if st.button("🌤️ Get Weather Update"):
            st.session_state.get_weather = True
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with AI Agent")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])
        
        # User input
        if prompt := st.chat_input("Ask me about your business data, weather, or anything else..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            st.chat_message("user").write(prompt)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.agent.process_query(prompt, st.session_state.chat_history)
                st.write(response)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    with col2:
        st.header("📈 Data Visualizations")
        
        # Sales chart
        if st.session_state.get("show_chart", False) or st.button("Show Sales by Category"):
            try:
                query = """
                SELECT p.category, SUM(o.amount) as total_sales
                FROM orders o
                JOIN products p ON o.customer_id = p.id  -- Simplified join for demo
                WHERE o.status = 'completed'
                GROUP BY p.category
                """
                
                # Use sample data for visualization
                sample_data = {
                    "Electronics": 2199.97,
                    "Furniture": 350.00,
                    "Appliances": 89.99
                }
                
                df = pd.DataFrame(list(sample_data.items()), columns=['Category', 'Sales'])
                
                fig = px.pie(df, values='Sales', names='Category', title='Sales by Category')
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating chart: {e}")
        
        # Weather widget
        if st.session_state.get("get_weather", False):
            try:
                weather_tool = next(tool for tool in st.session_state.agent.tools if tool.name == "get_weather_info")
                weather_json = weather_tool.func("New York")
                weather = json.loads(weather_json)
                
                st.info(f"🌤️ Weather in {weather['city']}: {weather['temperature']}°C, {weather['description']}")
                st.session_state.get_weather = False
                
            except Exception as e:
                st.error(f"Error getting weather: {e}")
        
        # Recent activity
        st.subheader("📝 Recent Activity")
        try:
            recent_orders = st.session_state.agent.db.execute_query(
                "SELECT * FROM orders ORDER BY order_date DESC LIMIT 5"
            )
            
            if recent_orders:
                df = pd.DataFrame(recent_orders)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent orders found")
                
        except Exception as e:
            st.error(f"Error loading recent activity: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("*AI Agent logs are being written to `agent.log` for monitoring and debugging.*")

if __name__ == "__main__":
    main()
