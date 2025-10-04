gemini_key = "AIzaSyAf_l8_rqVtsr4z5FXSS4ucyE0M8fW2R9k"

from google import genai

client = genai.Client(api_key=gemini_key)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)