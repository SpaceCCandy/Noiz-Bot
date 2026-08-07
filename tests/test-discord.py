import time
from pypresence import Presence

# 1. Paste your Application ID here (keep it as a string with quotes)
CLIENT_ID = '1534649774555271198'

# 2. Connect to your local Discord client
RPC = Presence(CLIENT_ID)
RPC.connect()
print("Successfully connected to Discord!")

# 3. Push a status update
# 'state' is the main line, 'details' is the second line
RPC.update(
    state="Something, something?",
    details="Testing...",
    #large_image="desktop"  # Optional image key
)

print("Status updated! Check your Discord profile.")

# Keep the script running so the status stays active
try:
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("Closing connection...")
    RPC.close()