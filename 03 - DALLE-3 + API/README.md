# AI Image Generator - Multiple Styles

This is a **Streamlit app** that generates 9 different images based on a user prompt using OpenAI's DALL·E API in various artistic styles.

## Features
✅ Enter a text prompt  
✅ Generates images in 9 different predefined styles (Realistic, Cartoon, Cyberpunk, etc.)  
✅ Uses OpenAI's **DALL·E** for AI-based image generation  
✅ Displays and saves images automatically

---

## Installation & Setup

### 1. Install Dependencies
Ensure you have Python installed, then install the required libraries:

```bash
pip install streamlit openai
```

### 2. Set Up OpenAI API Key
You'll need an OpenAI API key to access DALL·E. Set it up as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

(Windows users can use `set OPENAI_API_KEY="your-api-key"`)

Alternatively, you can hardcode it inside `image_gen_app.py` line 6:

```python
openai.api_key = "your-api-key"
```

### 3. Run the App
Start the Streamlit app using:

```bash
streamlit run image_gen_app.py
```

This will open a **web interface** in your browser.

---

## Usage
1. Enter a **text prompt** (e.g., "A futuristic city at sunset").
2. Click **"Generate Images"**.
3. The app will display **9 different images** in various artistic styles.
4. Right-click an image to **save** it if needed.

---

## Available Styles
- Realistic
- Cartoon
- Cyberpunk
- Watercolor
- Sketch
- Pixel Art
- Fantasy
- Minimalist
- Oil Painting

---

## License
This project is open-source. Feel free to modify and improve it! 🚀
