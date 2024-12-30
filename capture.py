import os
from datetime import datetime
import pytesseract
from PIL import ImageGrab
import pathlib

# Create Rewind directory if it doesn't exist
home_dir = str(pathlib.Path.home())
rewind_dir = os.path.join(home_dir, "Rewind")
os.makedirs(rewind_dir, exist_ok=True)

# Generate timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
image_path = os.path.join(rewind_dir, f"screenshot_{timestamp}.png")
text_path = os.path.join(rewind_dir, f"screenshot_{timestamp}.txt")

# Take screenshot
screenshot = ImageGrab.grab()
screenshot.save(image_path)

# Perform OCR
text = pytesseract.image_to_string(screenshot)

# Save OCR text
with open(text_path, "w") as f:
    f.write(text)
