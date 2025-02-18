import streamlit as st
from backend.database_connector import fetch_music_details
from backend.api_interaction import send_data_to_api, fetch_data_from_api
from backend.log_manager import info_log, error_log
from backend.openai_integration import get_openai_response

st.title('Music Information System')

# Chat-like interface for OpenAI
query_input = st.text_input("Ask me anything about music:")

if query_input:
    if st.button("Get Answer"):
        try:
            response = get_openai_response(query_input)
            st.write(response)
            info_log("Response provided successfully.")
        except Exception as e:
            st.error("Failed to fetch response.")
            error_log(f"Failed to fetch response: {e}")
    
# Send data feature (kept the same for example)
if st.button("Send data"):
    api_url = "https://api.openai.com/v1/chat/completions"
    data_to_send = {"key": "value"}
    try:
        status_code, response = send_data_to_api(api_url, data_to_send)
        if status_code == 200:
            st.success("Data sent successfully.")
            info_log("Data sent to API successfully.")
        else:
            st.error("Failed to send data.")
            error_log("Failed to send data.")
    except Exception as e:
        st.error("Failed to interact with API.")
        error_log(f"API interaction failed: {e}")

# Display music data
st.sidebar.header("Sample Music Data")
music_data = fetch_music_details("SELECT * FROM musics LIMIT 5")
st.sidebar.write(music_data)