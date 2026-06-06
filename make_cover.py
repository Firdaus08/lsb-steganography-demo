from PIL import Image, ImageDraw
import random

# Create a 600x400 colourful image
img = Image.new("RGB", (600, 400))
draw = ImageDraw.Draw(img)

# Draw random coloured rectangles for visual variety
random.seed(42)
for _ in range(200):
    x1 = random.randint(0, 580)
    y1 = random.randint(0, 380)
    x2 = x1 + random.randint(10, 80)
    y2 = y1 + random.randint(10, 80)
    color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    draw.rectangle([x1, y1, x2, y2], fill=color)

img.save("cover.png")
print("cover.png created!")