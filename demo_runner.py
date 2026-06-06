"""
WQE7003 — LSB Steganography Demo Runner
----------------------------------------
Guides you through a full demo session step by step.
Each session is saved in its own folder: Demo_1, Demo_2, etc.
All images and output files for a session are saved inside that folder.

Usage:
    python demo_runner.py
"""

import os
import sys
import textwrap

# ── Colour helpers (Windows-safe) ───────────────────────────
try:
    import colorama
    colorama.init()
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
except ImportError:
    GREEN = CYAN = YELLOW = RED = BOLD = RESET = ""

def banner(text, color=CYAN):
    width = 60
    line  = "=" * width
    print("\n" + color + BOLD + line)
    for part in text.split("\n"):
        print("  " + part)
    print(line + RESET)

def step_header(number, title):
    print("\n" + YELLOW + BOLD + "─── Step {} — {} ".format(number, title).ljust(60, "─") + RESET)

def ok(msg):
    print(GREEN + "[OK] " + RESET + msg)

def info(msg):
    print(CYAN + "[INFO] " + RESET + msg)

def warn(msg):
    print(YELLOW + "[NOTE] " + RESET + msg)

def error(msg):
    print(RED + "[ERROR] " + RESET + msg)

def ask(prompt, default=""):
    suffix = " [{}] ".format(default) if default else " "
    try:
        val = input(BOLD + prompt + suffix + RESET).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val if val else default

def pause():
    try:
        input(CYAN + "\n  Press ENTER to continue..." + RESET)
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


# ── Find next demo number ────────────────────────────────────

def get_next_demo_folder():
    n = 1
    while os.path.exists("Demo_{}".format(n)):
        n += 1
    return "Demo_{}".format(n), n


def get_existing_demo_folders():
    folders = []
    n = 1
    while os.path.exists("Demo_{}".format(n)):
        folders.append("Demo_{}".format(n))
        n += 1
    return folders


# ── Path helper ──────────────────────────────────────────────

def p(folder, filename):
    """Return path inside the demo folder."""
    return os.path.join(folder, filename)


# ══════════════════════════════════════════════════════════════
# DEMO STEPS
# ══════════════════════════════════════════════════════════════

def step_create_cover(folder, demo_num):
    step_header(1, "Create / Choose Cover Image")
    print(textwrap.dedent("""
      The cover image is the innocent-looking PNG that will hide the secret message.
      It must be PNG or BMP (lossless). JPEG will corrupt the hidden bits.

      You can:
        A) Auto-generate a colourful test image (recommended for demo)
        B) Use your own PNG (provide the path)
    """))

    choice = ask("Choose A or B", "A").upper()
    cover_path = p(folder, "cover.png")

    if choice == "A":
        from PIL import Image, ImageDraw
        import random
        info("Generating a 600x400 colourful cover image...")
        img = Image.new("RGB", (600, 400), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        rng = random.Random(demo_num * 999)
        for _ in range(300):
            x1 = rng.randint(0, 560)
            y1 = rng.randint(0, 360)
            x2 = x1 + rng.randint(20, 120)
            y2 = y1 + rng.randint(20, 120)
            color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            draw.rectangle([x1, y1, x2, y2], fill=color)
        img.save(cover_path)
        ok("Cover image saved: {}".format(cover_path))
    else:
        src = ask("Enter path to your PNG file")
        if not os.path.exists(src):
            error("File not found: {}".format(src))
            sys.exit(1)
        from PIL import Image
        img = Image.open(src).convert("RGB")
        img.save(cover_path)
        ok("Cover image copied to: {}".format(cover_path))

    return cover_path


def step_baseline_embed(folder, cover_path):
    step_header(2, "Baseline LSB Embed (Defense — D1)")
    print(textwrap.dedent("""
      This step hides a secret message inside the cover image using plain LSB substitution.
      No encryption. No scrambling. Sequential pixel embedding only.

      The output is 'stego_baseline.png' — it looks identical to cover.png
      but carries hidden data in the least significant bits of each pixel.
    """))

    default_msg = "This is a secret message for WQE7003 demo"
    message = ask("Enter the secret message to hide", default_msg)

    output_path = p(folder, "stego_baseline.png")

    import lsb_baseline
    lsb_baseline.embed(cover_path, message, output_path)
    ok("Baseline stego image saved: {}".format(output_path))
    return output_path, message


def step_baseline_extract(folder, stego_path):
    step_header(3, "Baseline LSB Extract (Defense — D1)")
    print(textwrap.dedent("""
      This step reads the LSBs from the stego image sequentially and reconstructs
      the original message. It stops when it finds the end delimiter.
    """))

    import lsb_baseline
    lsb_baseline.extract(stego_path)
    ok("Extraction successful — message matches original.")


def step_enhanced_embed(folder, cover_path):
    step_header(4, "Enhanced LSB Embed — AES + Random Scatter (Defense — D2/D3)")
    print(textwrap.dedent("""
      This step applies TWO enhancements before embedding:

        Enhancement 1 — AES-128 CBC Encryption
          The message is encrypted before embedding. Even if an attacker
          extracts the bits, they only get random-looking ciphertext.

        Enhancement 2 — Pseudo-Random Pixel Selection
          Bits are hidden at randomly scattered pixel positions (not sequentially).
          The scatter pattern is derived from the encryption key, so only someone
          who knows the key can find and read the bits.

      The output is 'stego_enhanced.png' — visually identical to cover.png.
    """))

    default_msg = "This is a secret message for WQE7003 demo"
    message = ask("Enter the secret message to hide", default_msg)
    key     = ask("Enter an encryption key (any string)", "WQE7003SecretKey")

    output_path = p(folder, "stego_enhanced.png")

    import lsb_enhanced
    lsb_enhanced.embed(cover_path, message, output_path, key)
    ok("Enhanced stego image saved: {}".format(output_path))
    return output_path, key


def step_enhanced_extract(folder, stego_path, key):
    step_header(5, "Enhanced LSB Extract (Defense — D3)")
    print(textwrap.dedent("""
      This step uses the same key to:
        1. Reconstruct the pseudo-random pixel positions
        2. Read bits from those positions
        3. Decrypt the AES ciphertext to recover the plaintext message
    """))

    import lsb_enhanced
    lsb_enhanced.extract(stego_path, key)
    ok("Extraction successful — AES decryption matched.")


def step_passive_attacks(folder, baseline_path, enhanced_path):
    step_header(6, "Passive Attacks — Detection Without Modification (Attack — A1)")
    print(textwrap.dedent("""
      Passive attacks try to DETECT whether a message is hidden, without touching the image.
      We run the same tests on both the baseline and enhanced stego images.

      Tests:
        - Visual LSB Plane  : amplifies LSBs to visible black/white pattern
        - Histogram Analysis: checks if adjacent pixel values are unusually equalised
        - Chi-Square Test   : statistical test — high p-value means embedding detected
        - RS Analysis       : Regular-Singular symmetry test

      Output images (lsb_plane, histogram) will be saved in the demo folder.
    """))

    import lsb_attacks

    print(BOLD + "\n  [A] Running passive attacks on BASELINE stego..." + RESET)
    lsb_attacks.run_all_passive(baseline_path, folder)

    print(BOLD + "\n  [B] Running passive attacks on ENHANCED stego..." + RESET)
    lsb_attacks.run_all_passive(enhanced_path, folder)

    print()
    warn("Compare the chi-square p-values above.")
    warn("Baseline p-value should be close to 1.0 (clearly detected).")
    warn("Enhanced p-value should be much lower (harder to detect).")


def step_active_attacks(folder, baseline_path, enhanced_path):
    step_header(7, "Active Attacks — Attempt to Destroy or Extract (Attack — A2)")
    print(textwrap.dedent("""
      Active attacks either try to EXTRACT the message or DESTROY it.

      Attack 1 — Direct extraction  : read LSBs sequentially and decode as text
                                      Works on baseline. Fails on enhanced (gets ciphertext).
      Attack 2 — JPEG compression   : re-encode as lossy JPEG, corrupting all LSBs
      Attack 3 — Gaussian noise     : add random noise to flip ~30-50% of LSBs
      Attack 4 — Cropping           : remove 25% of the image pixels
    """))

    import lsb_attacks

    # Attack 1 — Direct extraction
    print(BOLD + "\n  [1] Direct LSB extraction on BASELINE stego" + RESET)
    lsb_attacks.direct_extract(baseline_path)

    print(BOLD + "\n  [2] Direct LSB extraction on ENHANCED stego" + RESET)
    lsb_attacks.direct_extract(enhanced_path)

    # Attack 2 — JPEG
    print(BOLD + "\n  [3] JPEG compression on ENHANCED stego" + RESET)
    compressed_path = p(folder, "attacked_jpeg.jpg")
    lsb_attacks.jpeg_compression_attack(enhanced_path, compressed_path)
    print("      Now trying to extract from the compressed version:")
    lsb_attacks.direct_extract(compressed_path)

    # Attack 3 — Noise
    print(BOLD + "\n  [4] Gaussian noise on BASELINE stego" + RESET)
    noisy_path = p(folder, "attacked_noisy.png")
    lsb_attacks.noise_attack(baseline_path, noisy_path)
    print("      Now trying to extract from the noisy version:")
    lsb_attacks.direct_extract(noisy_path)

    # Attack 4 — Crop
    print(BOLD + "\n  [5] Cropping attack on ENHANCED stego" + RESET)
    cropped_path = p(folder, "attacked_cropped.png")
    lsb_attacks.cropping_attack(enhanced_path, cropped_path)
    print("      Now trying to extract from the cropped version:")
    lsb_attacks.direct_extract(cropped_path)



def step_compare(folder):
    step_header(8, "Visual Comparison — All Images Side by Side")
    print(textwrap.dedent("""
      This step generates a single comparison image showing all key images
      from this demo session side by side, saved as comparison.png.

      Row 1 — The three main images:
        cover.png | stego_baseline.png | stego_enhanced.png

      Row 2 — LSB planes (LSBs amplified to black/white):
        baseline LSB plane | enhanced LSB plane

      Row 3 — Histogram charts (pixel value distribution):
        baseline histogram | enhanced histogram

      Row 4 — Attack results:
        attacked_jpeg.jpg | attacked_noisy.png | attacked_cropped.png

      What to look for:
        - Row 1: cover and stego images look IDENTICAL to the eye
        - Row 2: baseline LSB plane may show a structured region (top-left);
                 enhanced LSB plane should look like pure random noise
        - Row 3: baseline histogram may show equalised even/odd bars;
                 enhanced histogram looks more natural
        - Row 4: all attacked images are visually similar but messages destroyed
    """))

    try:
        from PIL import Image
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def load(filename):
            fp = os.path.join(folder, filename)
            if os.path.exists(fp):
                return Image.open(fp).convert("RGB")
            return None

        fig = plt.figure(figsize=(18, 14))
        fig.patch.set_facecolor("#1a1a2e")

        def add_img(ax, img, title, border_color="#4a9eff"):
            if img:
                ax.imshow(img)
            else:
                ax.set_facecolor("#2a2a3e")
                ax.text(0.5, 0.5, "Not found", ha="center", va="center",
                        color="gray", transform=ax.transAxes)
            ax.set_title(title, color="white", fontsize=9, pad=6, fontweight="bold")
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_edgecolor(border_color)
                spine.set_linewidth(2)

        # Row 1 — Main images
        row1 = [("cover.png", "cover.png\n(original)", "#888888"),
                ("stego_baseline.png", "stego_baseline.png\n(plain LSB)", "#ff9944"),
                ("stego_enhanced.png", "stego_enhanced.png\n(AES + scatter)", "#44aaff")]
        for i, (fn, title, col) in enumerate(row1):
            add_img(fig.add_subplot(4, 3, i + 1), load(fn), title, col)

        # Row 2 — LSB planes
        row2 = [("stego_baseline_lsb_plane.png", "Baseline LSB Plane\n(look for structure)", "#ff9944"),
                ("stego_enhanced_lsb_plane.png", "Enhanced LSB Plane\n(should be random noise)", "#44aaff")]
        for i, (fn, title, col) in enumerate(row2):
            add_img(fig.add_subplot(4, 3, 4 + i), load(fn), title, col)
        fig.add_subplot(4, 3, 6).axis("off")

        # Row 3 — Histograms
        row3 = [("stego_baseline_histogram.png", "Baseline Histogram\n(check even/odd equalisation)", "#ff9944"),
                ("stego_enhanced_histogram.png", "Enhanced Histogram\n(should look more natural)", "#44aaff")]
        for i, (fn, title, col) in enumerate(row3):
            add_img(fig.add_subplot(4, 3, 7 + i), load(fn), title, col)
        fig.add_subplot(4, 3, 9).axis("off")

        # Row 4 — Attack results
        row4 = [("attacked_jpeg.jpg",   "JPEG compression\n(message destroyed)", "#ff4444"),
                ("attacked_noisy.png",  "Gaussian noise\n(~35% bits flipped)", "#ff4444"),
                ("attacked_cropped.png","Cropping\n(25% pixels removed)", "#ff4444")]
        for i, (fn, title, col) in enumerate(row4):
            add_img(fig.add_subplot(4, 3, 10 + i), load(fn), title, col)

        # Row labels
        for label, ypos in [("Original vs Stego", 0.82), ("LSB Planes", 0.60),
                             ("Histograms", 0.37), ("Attack Results", 0.14)]:
            fig.text(0.01, ypos, label, color="#aaaaaa", fontsize=8,
                     rotation=90, va="center", fontweight="bold")

        fig.suptitle("WQE7003 — LSB Steganography Demo Comparison",
                     color="white", fontsize=14, fontweight="bold", y=0.98)
        plt.tight_layout(rect=[0.03, 0, 1, 0.97])

        out_path = os.path.join(folder, "comparison.png")
        plt.savefig(out_path, dpi=110, facecolor=fig.get_facecolor())
        plt.close()
        ok("Comparison image saved: {}".format(out_path))
        info("Open {}/comparison.png to see all images at a glance.".format(folder))

    except Exception as e:
        warn("Could not generate comparison image: {}".format(e))
        warn("You can still open individual images in the {} folder.".format(folder))


def step_summary(folder, demo_num):
    step_header(9, "Demo Complete — File Summary")
    print()
    files = sorted(os.listdir(folder))
    print("  All files saved in folder: {}/".format(folder))
    print()
    descriptions = {
        "cover.png":              "Original cover image (no hidden data)",
        "stego_baseline.png":     "Baseline stego image (plain LSB, no encryption)",
        "stego_enhanced.png":     "Enhanced stego image (AES-128 + random scatter)",
        "stego_baseline_lsb_plane.png":  "LSB plane of baseline — may show structure",
        "stego_enhanced_lsb_plane.png":  "LSB plane of enhanced — should look like noise",
        "stego_baseline_histogram.png":  "Histogram of baseline — check pair equalisation",
        "stego_enhanced_histogram.png":  "Histogram of enhanced — less equalisation",
        "attacked_jpeg.jpg":      "Enhanced stego after JPEG compression (message destroyed)",
        "attacked_noisy.png":     "Baseline stego after noise attack (message corrupted)",
        "attacked_cropped.png":   "Enhanced stego after cropping (message destroyed)",
    }
    for f in files:
        desc = descriptions.get(f, "")
        print("  {:40s} {}".format(f, desc))

    print()
    banner("Demo {} complete!\nAll outputs saved in: {}/".format(demo_num, folder), GREEN)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    banner("WQE7003 — LSB Steganography Demo Runner\nCryptography and Information Hiding")

    existing = get_existing_demo_folders()
    if existing:
        info("Existing demo sessions found: {}".format(", ".join(existing)))

    print(textwrap.dedent("""
      This runner guides you through a complete demo:
        Step 1  — Create a cover image
        Step 2  — Baseline: embed a secret message
        Step 3  — Baseline: extract and verify
        Step 4  — Enhanced: embed with AES + random scatter
        Step 5  — Enhanced: extract and verify
        Step 6  — Passive attacks (detection)
        Step 7  — Active attacks (destruction / extraction attempt)
        Step 8  — Summary of all files created

      All output files will be saved in a new folder (Demo_1, Demo_2, etc.)
      so each run is completely separate and easy to compare.
    """))

    confirm = ask("Start a new demo session? (yes/no)", "yes").lower()
    if confirm not in ("yes", "y"):
        info("Exiting. Bye!")
        sys.exit(0)

    folder, demo_num = get_next_demo_folder()
    os.makedirs(folder, exist_ok=True)

    banner("Starting Demo {} — outputs will be saved in: {}/".format(demo_num, folder), YELLOW)

    try:
        cover_path = step_create_cover(folder, demo_num)
        pause()

        baseline_stego, message = step_baseline_embed(folder, cover_path)
        pause()

        step_baseline_extract(folder, baseline_stego)
        pause()

        enhanced_stego, key = step_enhanced_embed(folder, cover_path)
        pause()

        step_enhanced_extract(folder, enhanced_stego, key)
        pause()

        step_passive_attacks(folder, baseline_stego, enhanced_stego)
        pause()

        step_active_attacks(folder, baseline_stego, enhanced_stego)
        pause()

        step_compare(folder)
        pause()

        step_summary(folder, demo_num)

    except KeyboardInterrupt:
        print()
        warn("Demo interrupted. Files saved so far are in: {}/".format(folder))
        sys.exit(0)
    except Exception as e:
        error("Unexpected error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()