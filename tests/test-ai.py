import os
import pyautogui
from PIL import Image
from dotenv import load_dotenv
from google import genai

# Gets the secert Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)

screenshot = pyautogui.screenshot()
# Images for testing only
screenshot.save("curr_screen.png")
img = Image.open("curr_screen.png")

my_file = client.files.upload(file="../curr_screen.png")

prompt = """
Analyze this screen capture. Classify the primary user activity into EXACTLY ONE of these 4 categories:
1. Games
2. Study montage
3. Doom Scrolling
4. STEM
...
"""

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input=[
        {"type": "text", "text": prompt},
        {
            "type": "image",
            "uri": my_file.uri,
            "mime_type": my_file.mime_type
        }
    ]
)

print("Response[" + interaction.output_text + "]")

# print(response.text.strip())