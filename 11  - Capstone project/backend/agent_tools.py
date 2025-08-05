"""
Advanced tools for the AI agent with enhanced functionality
"""
import json
import logging
import sqlite3
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SalesAnalysis:
    total_revenue: float
    revenue_growth: float
    best_selling_product: str
    top_customer: str
    avg_order_value: float
    conversion_rate: float

@dataclass
class InventoryAlert:
    product_name: str
    current_stock: int
    min_level: int
    days_until_stockout: int
    recommended_order_quantity: int

class AdvancedAnalyticsTool:
    """Advanced analytics tool for business intelligence"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info("Advanced Analytics Tool initialized")
    
    def get_sales_analysis(self, days: int = 30) -> str:
        """Perform comprehensive sales analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Total revenue for period
            cursor.execute("""
                SELECT SUM(total_amount) as revenue
                FROM orders 
                WHERE order_date >= ? AND order_date <= ? AND status = 'completed'
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            current_revenue = cursor.fetchone()[0] or 0
            
            # Revenue for previous period (for growth calculation)
            prev_start = start_date - timedelta(days=days)
            cursor.execute("""
                SELECT SUM(total_amount) as revenue
                FROM orders 
                WHERE order_date >= ? AND order_date < ? AND status = 'completed'
            """, (prev_start.strftime("%Y-%m-%d"), start_date.strftime("%Y-%m-%d")))
            
            prev_revenue = cursor.fetchone()[0] or 1
            revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
            
            # Best selling product
            cursor.execute("""
                SELECT p.name, SUM(oi.quantity) as total_sold
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.order_date >= ? AND o.order_date <= ? AND o.status = 'completed'
                GROUP BY p.name
                ORDER BY total_sold DESC
                LIMIT 1
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            best_product = cursor.fetchone()
            best_selling_product = best_product[0] if best_product else "No sales"
            
            # Top customer
            cursor.execute("""
                SELECT c.name, SUM(o.total_amount) as total_spent
                FROM customers c
                JOIN orders o ON c.id = o.customer_id
                WHERE o.order_date >= ? AND o.order_date <= ? AND o.status = 'completed'
                GROUP BY c.name
                ORDER BY total_spent DESC
                LIMIT 1
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            top_customer_data = cursor.fetchone()
            top_customer = top_customer_data[0] if top_customer_data else "No customers"
            
            # Average order value
            cursor.execute("""
                SELECT AVG(total_amount) as avg_order
                FROM orders 
                WHERE order_date >= ? AND order_date <= ? AND status = 'completed'
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            avg_order_value = cursor.fetchone()[0] or 0
            
            # Conversion rate (orders/total customers * 100)
            cursor.execute("SELECT COUNT(*) FROM customers WHERE status IN ('active', 'premium')")
            total_customers = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT customer_id) 
                FROM orders 
                WHERE order_date >= ? AND order_date <= ?
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            active_customers = cursor.fetchone()[0] or 0
            conversion_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0
            
            conn.close()
            
            analysis = SalesAnalysis(
                total_revenue=float(current_revenue),
                revenue_growth=float(revenue_growth),
                best_selling_product=best_selling_product,
                top_customer=top_customer,
                avg_order_value=float(avg_order_value),
                conversion_rate=float(conversion_rate)
            )
            
            logger.info(f"Sales analysis completed for {days} days")
            return json.dumps(analysis.__dict__, default=str)
            
        except Exception as e:
            logger.error(f"Sales analysis error: {e}")
            return f"Error performing sales analysis: {str(e)}"
    
    def get_inventory_alerts(self) -> str:
        """Get inventory alerts for low stock items"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get products with low stock
            cursor.execute("""
                SELECT p.name, p.stock_quantity, p.min_stock_level, p.id
                FROM products p
                WHERE p.stock_quantity <= p.min_stock_level
                ORDER BY (p.stock_quantity - p.min_stock_level) ASC
            """)
            
            low_stock_products = cursor.fetchall()
            alerts = []
            
            for product_name, current_stock, min_level, product_id in low_stock_products:
                # Calculate average daily sales for this product
                cursor.execute("""
                    SELECT AVG(daily_sales) as avg_daily_sales
                    FROM (
                        SELECT DATE(o.order_date) as sale_date, SUM(oi.quantity) as daily_sales
                        FROM order_items oi
                        JOIN orders o ON oi.order_id = o.id
                        WHERE oi.product_id = ? AND o.status = 'completed'
                        AND o.order_date >= date('now', '-30 days')
                        GROUP BY DATE(o.order_date)
                    )
                """, (product_id,))
                
                avg_daily_sales = cursor.fetchone()[0] or 1
                days_until_stockout = max(1, int(current_stock / avg_daily_sales))
                recommended_order_quantity = max(min_level * 2, int(avg_daily_sales * 30))
                
                alert = InventoryAlert(
                    product_name=product_name,
                    current_stock=current_stock,
                    min_level=min_level,
                    days_until_stockout=days_until_stockout,
                    recommended_order_quantity=recommended_order_quantity
                )
                alerts.append(alert.__dict__)
            
            conn.close()
            logger.info(f"Generated {len(alerts)} inventory alerts")
            return json.dumps(alerts, default=str)
            
        except Exception as e:
            logger.error(f"Inventory alerts error: {e}")
            return f"Error generating inventory alerts: {str(e)}"
    
    def get_customer_segmentation(self) -> str:
        """Perform customer segmentation analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    c.name,
                    c.total_spent,
                    COUNT(o.id) as order_count,
                    AVG(o.total_amount) as avg_order_value,
                    MAX(o.order_date) as last_order_date,
                    c.status
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
                GROUP BY c.id, c.name, c.total_spent, c.status
                ORDER BY c.total_spent DESC
            """)
            
            customers = cursor.fetchall()
            segments = {
                "high_value": [],
                "medium_value": [],
                "low_value": [],
                "at_risk": []
            }
            
            for customer_data in customers:
                name, total_spent, order_count, avg_order, last_order, status = customer_data
                
                # Calculate days since last order
                if last_order:
                    last_order_date = datetime.strptime(last_order, "%Y-%m-%d")
                    days_since_last_order = (datetime.now() - last_order_date).days
                else:
                    days_since_last_order = 999
                
                # Segment customers
                if total_spent > 2000 and days_since_last_order < 30:
                    segments["high_value"].append({
                        "name": name,
                        "total_spent": total_spent,
                        "order_count": order_count,
                        "days_since_last_order": days_since_last_order
                    })
                elif total_spent > 1000 and days_since_last_order < 60:
                    segments["medium_value"].append({
                        "name": name,
                        "total_spent": total_spent,
                        "order_count": order_count,
                        "days_since_last_order": days_since_last_order
                    })
                elif days_since_last_order > 90:
                    segments["at_risk"].append({
                        "name": name,
                        "total_spent": total_spent,
                        "order_count": order_count,
                        "days_since_last_order": days_since_last_order
                    })
                else:
                    segments["low_value"].append({
                        "name": name,
                        "total_spent": total_spent,
                        "order_count": order_count,
                        "days_since_last_order": days_since_last_order
                    })
            
            conn.close()
            logger.info("Customer segmentation analysis completed")
            return json.dumps(segments, default=str)
            
        except Exception as e:
            logger.error(f"Customer segmentation error: {e}")
            return f"Error performing customer segmentation: {str(e)}"

class ExternalIntegrationTool:
    """Tool for external API integrations"""
    
    def __init__(self):
        self.session = None
        logger.info("External Integration Tool initialized")
    
    async def get_market_data(self, symbol: str = "AAPL") -> str:
        """Get stock market data (mock implementation)"""
        try:
            # Mock market data since we don't have a real API key
            mock_data = {
                "symbol": symbol,
                "price": 175.50 + (hash(symbol) % 20 - 10),  # Semi-random price
                "change": (hash(symbol) % 10 - 5) / 10,
                "volume": 50000000 + (hash(symbol) % 10000000),
                "market_cap": "2.8T",
                "pe_ratio": 28.5,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Market data retrieved for {symbol}")
            return json.dumps(mock_data)
            
        except Exception as e:
            logger.error(f"Market data error: {e}")
            return f"Error fetching market data: {str(e)}"
    
    async def get_economic_indicators(self) -> str:
        """Get economic indicators (mock implementation)"""
        try:
            # Mock economic data
            indicators = {
                "inflation_rate": 3.2,
                "unemployment_rate": 4.1,
                "gdp_growth": 2.8,
                "interest_rate": 5.25,
                "consumer_confidence": 102.3,
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info("Economic indicators retrieved")
            return json.dumps(indicators)
            
        except Exception as e:
            logger.error(f"Economic indicators error: {e}")
            return f"Error fetching economic indicators: {str(e)}"
    
    async def send_notification(self, message: str, channel: str = "email") -> str:
        """Send notification through external service (mock implementation)"""
        try:
            notification_data = {
                "id": f"notif_{datetime.now().timestamp()}",
                "message": message,
                "channel": channel,
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Notification sent via {channel}: {message[:50]}...")
            return json.dumps(notification_data)
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
            return f"Error sending notification: {str(e)}"

class PredictiveAnalyticsTool:
    """Tool for predictive analytics and forecasting"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info("Predictive Analytics Tool initialized")
    
    def forecast_sales(self, days_ahead: int = 30) -> str:
        """Forecast sales for the next period"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get historical daily sales data
            query = """
                SELECT DATE(order_date) as sale_date, SUM(total_amount) as daily_revenue
                FROM orders 
                WHERE status = 'completed' AND order_date >= date('now', '-90 days')
                GROUP BY DATE(order_date)
                ORDER BY sale_date
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) < 7:
                return json.dumps({
                    "forecast": [],
                    "error": "Insufficient historical data for forecasting"
                })
            
            # Simple moving average forecast
            daily_revenues = df['daily_revenue'].values
            window_size = min(7, len(daily_revenues) // 2)
            
            # Calculate moving average
            moving_avg = np.convolve(daily_revenues, np.ones(window_size)/window_size, mode='valid')[-1]
            
            # Add some trend analysis
            recent_avg = np.mean(daily_revenues[-window_size:])
            older_avg = np.mean(daily_revenues[-2*window_size:-window_size])
            trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            
            # Generate forecast
            forecast_data = []
            current_date = datetime.now()
            
            for i in range(days_ahead):
                forecast_date = current_date + timedelta(days=i+1)
                # Apply trend and some seasonality (weekend effect)
                weekday_factor = 0.8 if forecast_date.weekday() >= 5 else 1.0
                predicted_revenue = moving_avg * (1 + trend * (i/30)) * weekday_factor
                
                forecast_data.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "predicted_revenue": round(predicted_revenue, 2),
                    "confidence": max(0.6, 0.9 - (i/days_ahead) * 0.3)  # Decreasing confidence
                })
            
            total_forecast = sum(item["predicted_revenue"] for item in forecast_data)
            
            result = {
                "forecast_period_days": days_ahead,
                "total_predicted_revenue": round(total_forecast, 2),
                "daily_forecasts": forecast_data[:10],  # Limit to first 10 days
                "trend_direction": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                "confidence_level": "medium"
            }
            
            logger.info(f"Sales forecast generated for {days_ahead} days")
            return json.dumps(result, default=str)
            
        except Exception as e:
            logger.error(f"Sales forecast error: {e}")
            return f"Error generating sales forecast: {str(e)}"
    
    def predict_customer_churn(self) -> str:
        """Predict customers at risk of churning"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT 
                    c.id,
                    c.name,
                    c.total_spent,
                    COUNT(o.id) as order_count,
                    MAX(o.order_date) as last_order_date,
                    AVG(o.total_amount) as avg_order_value
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
                WHERE c.status IN ('active', 'premium')
                GROUP BY c.id, c.name, c.total_spent
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            churn_predictions = []
            
            for _, customer in df.iterrows():
                # Calculate days since last order
                if pd.isna(customer['last_order_date']):
                    days_since_last_order = 999
                else:
                    last_order = datetime.strptime(customer['last_order_date'], "%Y-%m-%d")
                    days_since_last_order = (datetime.now() - last_order).days
                
                # Simple churn prediction based on recency and order history
                churn_score = 0
                
                # Recency factor
                if days_since_last_order > 90:
                    churn_score += 0.4
                elif days_since_last_order > 60:
                    churn_score += 0.2
                
                # Order frequency factor
                if customer['order_count'] < 2:
                    churn_score += 0.3
                elif customer['order_count'] < 5:
                    churn_score += 0.1
                
                # Spending factor
                if customer['total_spent'] < 500:
                    churn_score += 0.2
                
                # Random factor for realism
                churn_score += (hash(customer['name']) % 100) / 1000
                
                if churn_score > 0.5:  # High risk threshold
                    churn_predictions.append({
                        "customer_name": customer['name'],
                        "churn_probability": round(min(churn_score, 0.95), 3),
                        "risk_level": "high" if churn_score > 0.7 else "medium",
                        "days_since_last_order": days_since_last_order,
                        "total_spent": customer['total_spent'],
                        "recommended_action": "Send personalized offer" if churn_score > 0.7 else "Follow up email"
                    })
            
            # Sort by churn probability
            churn_predictions.sort(key=lambda x: x['churn_probability'], reverse=True)
            
            result = {
                "total_at_risk_customers": len(churn_predictions),
                "high_risk_count": len([c for c in churn_predictions if c['risk_level'] == 'high']),
                "predictions": churn_predictions[:10]  # Top 10 at-risk customers
            }
            
            logger.info(f"Churn prediction completed for {len(churn_predictions)} at-risk customers")
            return json.dumps(result, default=str)
            
        except Exception as e:
            logger.error(f"Churn prediction error: {e}")
            return f"Error predicting customer churn: {str(e)}"