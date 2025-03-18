import sqlite3
import openai
import json
import os

def create_connection(db_file):
    """ Create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def execute_query(conn, query):
    """ Execute SQL query and fetch results """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        return f"Error: {str(e)}"

def ask_llm(question, api_key):
    """ Query OpenAI API to generate SQL based on natural language question """
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL assistant that helps users query a database."},
            {"role": "user", "content": f"Convert this into an SQL query: {question}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

def main():
    db_file = "ecommerce.db"  # SQLite database file
    api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
    
    if not api_key:
        print("Error: OpenAI API key is missing. Set OPENAI_API_KEY as an environment variable.")
        return
    
    conn = create_connection(db_file)
    if conn is None:
        print("Error: Cannot connect to database.")
        return
    
    while True:
        user_input = input("Ask a question about the database (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        
        sql_query = ask_llm(user_input, api_key)
        print(f"Generated SQL Query: {sql_query}")
        
        results = execute_query(conn, sql_query)
        print("Query Results:", results)
    
    conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()