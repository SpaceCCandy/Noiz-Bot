import os
import pyautogui
import time
from PIL import Image
from pypresence import Presence
import pystray
from pystray import Menu as menu, MenuItem as item
from dotenv import load_dotenv
from google import genai
from datetime import datetime
import threading

# Constants
CLIENT_ID = '1534649774555271198'
CAPTURE_DELAY = 120 # 2 mins
IMG_CONTEXT = 3

status = "idle"
is_running = True
capturing = False
recent_screenshots = []
image_path = "assets/Nozi-Bot.png"
icon_image = Image.open(image_path)

#Getting examples
EXAMPLES_CONFIG = [
    {"image": "Examples\\Example1.png", "target": "[idle]: Not in meeting(No meeting indication on the bottom left profile, or a clear meeting window), the user is idle, and just casually texting with friends."},
    {"image": "Examples\\Example2.png", "target": "[Meeting]: The user is currently in a discord call indicated by the call window in discord, and a voice connecting pop up on the bottom left above the user profile."},
    {"image": "Examples\\Example3.png", "target": "[IDLE]: User is casually chatting on Discord. An embedded YouTube link card inside a chat thread does NOT count as DOOM_SCROLLING unless youtube.com or a fullscreen video player is active."},
    {"image": "Examples\\Example4.png", "target": "[STEM]: User is actively planning and designing program architecture in Canva for a software project. Planning software logic or system flow falls under STEM."}
]

few_shots = [
    item 
    for example in EXAMPLES_CONFIG 
    for item in (Image.open(example["image"]), f"EXAMPLE RESPONSE -> {example['target']}")
]

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
2. "STUDY" -> Google Classroom, writing docs/essays, slides, educational platforms, reading research.
3. "DOOM_SCROLLING" -> Instagram Reels, TikTok, active scrolling on YouTube feeds, watching non-educational videos full-screen or in a browser.
4. "STEM" -> Writing code (VS Code, terminal), CAD/3D modeling (Blender), digital art programs, game engines (Godot, Roblox Studio).
5. "MEETING" -> Active video/audio calls on Zoom, Google Meets.
6. "IDLE" -> Blank desktop, screensaver, casual messaging/text chat in Discord, reading DMs, or when the most recent screenshots are completely identical with no user movement.

### RULES
- ACTIVE WINDOW PRIORITY: Classify based ONLY on the user's primary focused window. If VS Code, a code editor, terminal, or browser IDE is open and active, classify as STEM immediately—even if Discord, Spotify, or other apps are visible in the background.
- DISCORD & IDLE RULE: Casual messaging, reading DMs, looking at images shared in chat (e.g., weather forecast cards, meme photos, text messages), or lingering in Discord servers with no voice call active MUST be classified as IDLE.
- DISCORD MEETING STRICT RULE: Do NOT classify as MEETING just because Discord is open on screen or a chat is named after a group call. Only classify as MEETING if the user is in an active voice channel/call (check bottom-left call status) or the main focused window is a video/voice call interface.
- DOOM_SCROLLING STRICT BOUNDARY: Do NOT classify Discord chats as DOOM_SCROLLING just because an image or video link thumbnail is visible inside a text chat thread. Reserve DOOM_SCROLLING strictly for active scrolling on social media feeds or watching videos in a dedicated browser/video player.
- VIDEOS: Check what kind of video the user is watching. Only if it is non-educational does it fall under DOOM_SCROLLING. Educational tutorials, coding streams, or research videos fall under the matching productive category (e.g., STEM or STUDY).
- REPETITIVE / STATIC SCREEN RULE: Compare the screenshots in the timeline. If the 2 or 3 most recent screenshots are visually identical with no noticeable movement, cursor changes, or new content, classify immediately as IDLE—regardless of what app is open on the screen (e.g., sitting on a coding screen or document without typing/moving counts as IDLE).

### OUTPUT FORMAT
[CATEGORY_KEY]: Short description explaining why this category was chosen based on the primary active window.
"""
#- OUTPUT CONSTRAINTS: Respond with ONLY the exact category key name (e.g., STEM, GAMES, STUDY). Do NOT include category numbers, markdown formatting, explanations, or quotes.

def init():
    global RPC, capTotal, gameCount, studyCount, doomCount, stemCount, meetingCount

    # Connecting to discord
    RPC = Presence(CLIENT_ID)
    RPC.connect()
    print("> Successfully connected to Discord!")

    # Every increase in 1 means 2 mins
    with open("data.txt") as f:
        capTotal = int(f.readline().strip())
        gameCount = int(f.readline().strip())
        studyCount = int(f.readline().strip())
        doomCount = int(f.readline().strip())
        stemCount = int(f.readline().strip())
        meetingCount = int(f.readline().strip())

def start_capture():
    global capTotal, gameCount, studyCount, doomCount, stemCount, meetingCount
    print("> Start capture")

    try:
        while capturing:
            screenshot = pyautogui.screenshot()  # Takes the screenshot
            capTotal += 1
            screenshot.save("curr_screen.png")
            img = Image.open("curr_screen.png")
            recent_screenshots.append(img)  # Adding it to the recent stuff

            if len(recent_screenshots) > IMG_CONTEXT:
                recent_screenshots.pop(0)  # Get rid of oldest one

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[prompt, *few_shots, *recent_screenshots]
            )

            ai_text = response.text
            category_key = ai_text.split(":")[0].strip().replace("[", "").replace("]", "")

            if "STEM" in category_key:
                status = "doing STEM stuff ⭐"
                stemCount += 1
            elif "GAMES" in category_key:
                status = "gaming 👾"
                gameCount += 1
            elif "STUDY" in category_key:
                status = "studying 📖"
                studyCount += 1
            elif "DOOM_SCROLLING" in category_key:
                status = "Doom Scrolling 💀"
                doomCount += 1
            elif "MEETING" in category_key:
                status = "in a meeting 💻"
                meetingCount += 1
            else:
                status = "idle 🌙"

            # If Stop was clicked while Gemini was thinking, don't overwrite the cleared status
            if not capturing:
                break

            RPC.update(
                state=status,
                details="(testing) Currently...",
            )

            time_string = datetime.now().strftime("%H:%M:%S")
            print(f"Current Time: {time_string}")
            print("Current status:" + status)
            print("Response: " + ai_text)

            # Sleep 1 second at a time so Stop takes effect quickly
            for _ in range(CAPTURE_DELAY):
                if not capturing:
                    break
                time.sleep(1)
    except Exception as e:
        print(f"> Capture error: {e}")

capture_thread = None

def start_cap():
    global capturing, capture_thread
    capturing = True
    if capture_thread is None or not capture_thread.is_alive():
        capture_thread = threading.Thread(target=start_capture, daemon=True)
        capture_thread.start()

def stop_capture():
    global capturing
    capturing = False
    RPC.clear()
    print("> Status cleared.")

def on_quit(icon, item):
    global is_running, capturing
    is_running = False
    capturing = False
    icon.stop()

    with open("data.txt", "w") as f:
        f.write(str(capTotal) + "\n")
        f.write(str(gameCount) + "\n")
        f.write(str(studyCount) + "\n")
        f.write(str(doomCount) + "\n")
        f.write(str(stemCount) + "\n")
        f.write(str(meetingCount) + "\n")

    RPC.close()
    print("> Program finished")

init()

icon = pystray.Icon(
    'Nozi-Bot',
    icon=icon_image,
    menu=pystray.Menu(pystray.MenuItem("Start", start_cap),
                      pystray.MenuItem("Stop", stop_capture),
                      pystray.MenuItem("Exit", on_quit))
    )

icon.run()