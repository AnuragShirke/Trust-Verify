from PIL import Image
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "news-trust-visualizer", "public")

# Load the 32x32 PNG favicon
favicon_path = os.path.join(output_dir, "favicon.png")
img = Image.open(favicon_path)

# Create ICO file path
ico_path = os.path.join(output_dir, "favicon.ico")

# Save as ICO
img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
print(f"ICO file created at {ico_path}")
