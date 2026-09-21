from PIL import Image
import pystray

image_path = "assets/Nozi-Bot.png"
icon_image = Image.open(image_path)

# Creating the ICON
icon = pystray.Icon(
    'test_name',
    icon=icon_image,
    title="My Bot"
)

# Running the ICON in the system Tray
icon.run()