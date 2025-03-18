import streamlit as st
import openai
import os

# Set your OpenAI API Key here (or use environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image(prompt, style):
    """Generates an image using OpenAI's DALL·E API."""
    response = openai.Image.create(
        prompt=f"{prompt} in {style} style",
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

# Streamlit UI
st.title("AI Image Generator - Multiple Styles")
st.write("Enter a prompt, and get images in different styles!")

# User input prompt
prompt = st.text_input("Enter your prompt:", "A futuristic city at sunset")

# Predefined styles
styles = [
    "Realistic", "Cartoon", "Cyberpunk", "Watercolor", "Sketch",
    "Pixel Art", "Fantasy", "Minimalist", "Oil Painting"
]

# Generate images when user clicks
if st.button("Generate Images"):
    if prompt:
        st.write("### Generated Images:")
        cols = st.columns(3)  # 3 images per row
        for i, style in enumerate(styles):
            image_url = generate_image(prompt, style)
            with cols[i % 3]:
                st.image(image_url, caption=f"{style} Style", use_column_width=True)
    else:
        st.warning("Please enter a prompt before generating images.")
