# Run this as compare.py to view all images side by side
from PIL import Image
import matplotlib.pyplot as plt

imgs = {
    "Original cover": "cover.png",
    "Baseline stego": "output_baseline.png",
    "Enhanced stego": "output_enhanced.png",
    "LSB plane (baseline)": "lsb_plane.png",
}

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, (title, path) in zip(axes, imgs.items()):
    ax.imshow(Image.open(path))
    ax.set_title(title)
    ax.axis("off")

plt.tight_layout()
plt.savefig("comparison.png", dpi=100)
plt.show()
print("Saved comparison.png")