# SQL Query Agent for E-Commerce Database

This project implements an AI-powered agent that answers questions about an SQLite e-commerce database using natural language.

## Features
- Converts natural language questions into SQL queries using OpenAI's GPT-4 Turbo.
- Queries an SQLite database (`ecommerce.db`) and retrieves relevant results.
- Interactive command-line interface for querying.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
Obtain an OpenAI API key from [OpenAI](https://openai.com/) and set it as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run the Application
```bash
python main.py
```

## Database Schema
The SQLite database (`ecommerce.db`) contains the following tables:

### `customers`
| id | name          | email           |
|----|--------------|----------------|
| 1  | Alice Johnson | alice@example.com |
| 2  | Bob Smith     | bob@example.com |

### `products`
| id | name       | price  |
|----|-----------|--------|
| 1  | Laptop    | 1200.00 |
| 2  | Smartphone | 800.00  |
| 3  | Headphones | 150.00  |

### `orders`
| id | customer_id | order_date | total_price |
|----|------------|------------|-------------|
| 1  | 1          | 2025-03-10  | 1350.00     |
| 2  | 2          | 2025-03-11  | 800.00      |

### `order_items`
| id | order_id | product_id | quantity |
|----|---------|------------|---------|
| 1  | 1       | 1          | 1       |
| 2  | 1       | 3          | 1       |
| 3  | 2       | 2          | 1       |

## Example Queries

- **User:** "How many orders were placed?"
- **Generated SQL:** `SELECT COUNT(*) FROM orders;`
- **Result:** `2`

- **User:** "What is the total revenue?"
- **Generated SQL:** `SELECT SUM(total_price) FROM orders;`
- **Result:** `2150.00`

## License
This project is open-source. Feel free to modify and improve it! 🚀
