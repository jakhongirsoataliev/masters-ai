import openai

# Initialize OpenAI API key
openai.api_key = 'OPENAI_API_KEY'

def get_openai_response(query):
    try:
        response = openai.Completion.create(
          engine="gpt-4o",
          prompt=query,
          max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        raise Exception(f"Error in OpenAI API call: {str(e)}")