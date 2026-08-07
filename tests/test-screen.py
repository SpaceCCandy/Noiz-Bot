import pyautogui
import time

print("Taking screenshot in 3 seconds... switch to whatever you're working on!")
time.sleep(3)

# 1. Take the screenshot
screenshot = pyautogui.screenshot()

# 2. Save it locally
screenshot.save("current_screen.png")

print("Saved screenshot as 'current_screen.png'! Go check your project folder.")