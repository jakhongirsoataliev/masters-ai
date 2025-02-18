# masters-ai

# Music Information System

This application is designed to assist users in retrieving detailed information about music from a database, interact with external systems via APIs, and utilize OpenAI's language model for processing natural language queries.

## Features

- **Natural Language Query Processing**: Powered by OpenAI's GPT model.
- **Database Interactions**: Retrieve music-related data from a specified database.
- **API Interactions**: Send and fetch data to/from third-party systems.
- **Live Business Data**: Display music data on a user interface built with Streamlit.

## Installation

### Prerequisites

- Python 3.7 or higher (compatible with <= Python 3.12 as per the requirements).
- pip for installing Python packages.
- An OpenAI API key.
- A suitable SQL database (example given with SQLite).

### Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repository/music-information-system.git
   cd music-information-system
   ```
2. **Install Dependencies**:

    Using a virtual environment is recommended:
    ```bash
   python -m venv env
    source env/bin/activate  # Unix/MacOS
    env\Scripts\activate  # Windows

    pip install -r backend/requirements.txt
    ```
3. **Environment Configuration**:

   directly place your key in backend/openai_integration.py

**Running the Application**

Launch the Streamlit application:

```bash
streamlit run app.py
```
Access the app through your web browser at the address shown in your terminal (usually http://localhost:8501).

