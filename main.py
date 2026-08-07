import os
import pyautogui
import time
from pypresence import Presence
from PIL import Image
from dotenv import load_dotenv
from google import genai
from datetime import datetime

# Constants
CLIENT_ID = '1534649774555271198'
CAPTURE_DELAY = 120
IMG_CONTEXT = 3

status = "idle"
recent_screenshots = []

# Connecting to discord
RPC = Presence(CLIENT_ID)
RPC.connect()
print("Successfully connected to Discord!")

# Gets the secert Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

prompt = """
### ROLE
You are an ultra-precise activity classifier for a Discord status bot. Your job is to analyze 1 to 3 chronological screenshots of a user's desktop screen and determine their primary activity.

### CONTEXT
You are receiving the most recent desktop screenshots taken in order. 
- Use the visual timeline across images to resolve ambiguities (e.g., searching Google while VS Code was open in the previous frame = STEM).

### CATEGORIES
Select EXACTLY ONE category key from the list below:
1. "GAMES" -> Roblox, Minecraft, Fortnite, Steam games, active gameplay.
2. "STUDY" -> Google Classroom, docs/essays, slides, educational platforms, reading research.
3. "DOOM_SCROLLING" -> Instagram Reels, YouTube, TikTok, social media feeds, non-educational videos.
4. "STEM" -> Writing code (VS Code, terminal), CAD/3D modeling (Blender), digital art programs, game engines (Godot, Roblox Studio).
5. "MEETING" -> Active video/audio calls on Zoom, Google Meets, or Discord (check bottom-left call indicators).
6. "IDLE" -> Blank desktop, screensaver, using social media to causally communicate, or when the most recent screenshots are completely identical with no user movement.

### RULES
- OUTPUT CONSTRAINTS: Respond with ONLY the exact category key name (e.g., STEM, GAMES, STUDY). Do NOT include category numbers, markdown formatting, explanations, or quotes.
- - DISCORD: Check the bottom left for active voice call indicators. If in an active call, classify as MEETING (unless actively coding, which takes priority as STEM). If Discord is just open on screen without an active call, do not mark as MEETING.
- VIDEOS: Check what kind of video the user is watching. Only if it's not educational it falls under doom scrolling. Otherwise mark it under what the video mostly matches.

### OUTPUT
[CATEGORY_KEY]
"""

try:
    while True:
        screenshot = pyautogui.screenshot()
        screenshot.save("curr_screen.png")
        img = Image.open("curr_screen.png")
        recent_screenshots.append(img) # Adding it to the recent stuff

        if len(recent_screenshots) > IMG_CONTEXT:
            recent_screenshots.pop(0) # Get rid of last one

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[*recent_screenshots, prompt]
        )

        ai_text = response.text

        if "STEM" in ai_text:
            status = "doing STEM stuff ⭐"
        elif "Games" in ai_text:
            status = "gaming 👾"
        elif "Study montage" in ai_text:
            status = "studying 📖"
        elif "Doom Scrolling" in ai_text:
            status = "Doom Scrolling 💀"
        elif "Meeting" in ai_text:
            status = "in a meeting 💻"
        else:
            status = "idle 🌙"
        
        RPC.update(
        state=status,
        details="Currently...",
        #large_image="desktop"  # Optional image key
        )  

        # Grab the exact current date and time
        now = datetime.now()

        # Format it nicely (Hours:Minutes:Seconds)
        time_string = now.strftime("%H:%M:%S")

        print(f"Current Time: {time_string}")
        print("Current status:" + status)

        time.sleep(CAPTURE_DELAY)
        #print("Response[" + interaction.output_text + "]")
except KeyboardInterrupt:
    print("Closing connection...")
    RPC.close()