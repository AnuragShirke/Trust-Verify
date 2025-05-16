from PIL import Image
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Input and output paths with absolute paths
input_path = os.path.join(current_dir, "ChatGPT Image May 10, 2025, 09_10_18 PM.png")
output_dir = os.path.join(current_dir, "news-trust-visualizer", "public")
output_path = os.path.join(output_dir, "favicon.png")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Input path: {input_path}")
print(f"Output path: {output_path}")

# Open the original image
original_image = Image.open(input_path)

# Create a backup of the original image
backup_path = os.path.join(output_dir, "favicon_original.png")
original_image.save(backup_path)
print(f"Original image backed up to {backup_path}")

# Resize to 32x32 (standard favicon size)
resized_image = original_image.resize((32, 32), Image.LANCZOS)

# Save the resized image
resized_image.save(output_path)
print(f"Resized image saved to {output_path}")

# Create additional sizes for better browser compatibility
favicon_sizes = [16, 48, 64, 128, 256]
for size in favicon_sizes:
    size_path = os.path.join(output_dir, f"favicon-{size}x{size}.png")
    resized = original_image.resize((size, size), Image.LANCZOS)
    resized.save(size_path)
    print(f"Created {size}x{size} favicon at {size_path}")

print("Favicon resizing complete!")
