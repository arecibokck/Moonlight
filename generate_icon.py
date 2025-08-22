# generate_h5_icon_centered_preview.py
from PIL import Image, ImageDraw, ImageFont

# Icon sizes to include in .ico file
icon_sizes = [16, 32, 48, 64, 128, 256]

# Base high-resolution canvas
base_size = 512
img = Image.new("RGBA", (base_size, base_size), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("bahnschrift.ttf", int(base_size * 0.8))
except:
    font = ImageFont.load_default()

# Text
text_h = "h"
text_5 = "5"

# Get bounding boxes for accurate centering
bbox_h = font.getbbox(text_h)
bbox_5 = font.getbbox(text_5)
w_h, h_h = bbox_h[2]-bbox_h[0], bbox_h[3]-bbox_h[1]
w_5, h_5 = bbox_5[2]-bbox_5[0], bbox_5[3]-bbox_5[1]

# Center positions
center_x = base_size / 2
center_y = base_size / 2

# Offset h slightly upward
offset_y_h = -base_size * 0.05

# Calculate top-left coordinates for centered placement
x_h = center_x - w_h / 2
y_h = center_y - h_h / 2 + offset_y_h
x_5 = center_x - w_5 / 2
y_5 = center_y - h_5 / 2

x_h -= 90
x_5 += 90
y_h -= 100
y_5 += 10

# Draw texts
draw.text((x_5, y_5), text_5, font=font, fill=(0,0,0,255))  # draw 5 first (behind)
draw.text((x_h, y_h), text_h, font=font, fill=(0,0,0,255))  # draw h on top

# --- Preview the icon ---
img.show()  # opens default image viewer

# Ask user to approve
approve = input("Do you want to save this as h5_icon.ico? (y/n): ").strip().lower()
if approve == "y":
    # Resize for all icon sizes
    icon_images = [img.resize((s, s), Image.LANCZOS) for s in icon_sizes]

    # Save as multi-resolution .ico
    icon_images[0].save("h5_icon.ico", format="ICO", sizes=[(s,s) for s in icon_sizes])
    print("h5_icon.ico generated with centered h and 5!")
else:
    print("Icon generation canceled.")
