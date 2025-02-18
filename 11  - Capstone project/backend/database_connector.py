from sqlalchemy import create_engine
import pandas as pd

DATABASE_URI = 'sqlite:///musics.db'

def fetch_music_details(query):
    engine = create_engine(DATABASE_URI)
    with engine.connect() as connection:
        result = pd.read_sql_query(query, con=connection)
    return result