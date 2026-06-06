"""
WQE7003 Group Assignment — Attack Sub-Group
File: lsb_attacks.py
Description: Passive and active attack tools targeting LSB steganography.

  PASSIVE ATTACKS:
    1. Visual LSB plane inspection
    2. Histogram analysis
    3. Chi-square test
    4. RS Analysis

  ACTIVE ATTACKS:
    5. Direct LSB extraction
    6. JPEG compression attack
    7. Gaussian noise attack
    8. Cropping attack

Members: A1 (passive), A2 (active), A3 (report & demo)
Dependencies: pip install Pillow numpy scipy matplotlib
"""

import sys
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2


DELIMITER = "$$END$$"


# ── Passive 1: Visual LSB Plane ─────────────────────────────

def visual_lsb_plane(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    r, g, b = img.split()
    r_arr = np.array(r)
    lsb_plane = (r_arr & 1) * 255
    lsb_img = Image.fromarray(lsb_plane.astype(np.uint8), mode="L")
    lsb_img.save(output_path)
    print("[PASSIVE-1] LSB plane saved to '{}'".format(output_path))
    print("  Inspect: structured patterns = likely embedding; pure noise = clean or enhanced")


# ── Passive 2: Histogram Analysis ───────────────────────────

def histogram_analysis(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    r_arr = np.array(img)[:, :, 0].flatten()
    plt.figure(figsize=(12, 4))
    plt.hist(r_arr, bins=256, range=(0, 255), color="steelblue", alpha=0.8)
    plt.title("Red channel histogram — check even/odd value equalisation")
    plt.xlabel("Pixel value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    print("[PASSIVE-2] Histogram saved to '{}'".format(output_path))
    print("  Natural image: uneven distribution. Stego image: values 2k approx 2k+1")


# ── Passive 3: Chi-Square Test ───────────────────────────────

def chi_square_test(image_path):
    img = Image.open(image_path).convert("RGB")
    r_arr = np.array(img)[:, :, 0].flatten()
    hist, _ = np.histogram(r_arr, bins=256, range=(0, 256))

    chi_stat = 0.0
    df = 0

    for k in range(0, 255, 2):
        observed_even = hist[k]
        observed_odd  = hist[k + 1]
        expected = (observed_even + observed_odd) / 2.0
        if expected > 0:
            chi_stat += ((observed_even - expected) ** 2) / expected
            chi_stat += ((observed_odd  - expected) ** 2) / expected
            df += 1

    p_value = chi2.sf(chi_stat, df=df)
    print("[PASSIVE-3] Chi-square test on '{}'".format(image_path))
    print("  Chi-square statistic : {:.2f}".format(chi_stat))
    print("  Degrees of freedom   : {}".format(df))
    print("  p-value              : {:.6f}".format(p_value))
    if p_value > 0.05:
        print("  VERDICT              : LIKELY STEGO (p > 0.05 — pairs are equalised)")
    else:
        print("  VERDICT              : Likely CLEAN (p <= 0.05 — distribution looks natural)")
    return p_value


# ── Passive 4: RS Analysis ───────────────────────────────────

def rs_analysis(image_path):
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.int16)
    h, w = arr.shape
    block_size = 4

    def noise(block):
        return np.sum(np.abs(np.diff(block)))

    def flip_lsb(block):
        return block ^ 1

    def flip_neg(block):
        flipped = block.copy()
        flipped[block % 2 == 0] -= 1
        flipped[block % 2 == 1] += 1
        return flipped

    R = S = R_neg = S_neg = total = 0

    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = arr[i:i+block_size, j:j+block_size].flatten().copy()
            f  = noise(flip_lsb(block))
            fn = noise(flip_neg(block))
            n  = noise(block)
            if   f > n: R += 1
            elif f < n: S += 1
            if   fn > n: R_neg += 1
            elif fn < n: S_neg += 1
            total += 1

    if total == 0:
        print("[PASSIVE-4] RS Analysis: image too small.")
        return

    r  = R     / total
    s  = S     / total
    rn = R_neg / total
    sn = S_neg / total

    print("[PASSIVE-4] RS Analysis on '{}'".format(image_path))
    print("  R={:.4f}  S={:.4f}  R_neg={:.4f}  S_neg={:.4f}".format(r, s, rn, sn))
    if abs(r - rn) < 0.02 and abs(s - sn) < 0.02:
        print("  VERDICT : R approx R_neg and S approx S_neg => LIKELY STEGO")
    else:
        print("  VERDICT : Asymmetric distribution => Likely CLEAN image")


# ── Active 5: Direct LSB Extraction ─────────────────────────

def direct_extract(stego_path):
    img = Image.open(stego_path).convert("RGB")
    pixels = list(img.getdata())

    bits = ""
    for pixel in pixels:
        for value in pixel:
            bits += str(value & 1)

    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    text = "".join(chr(int(b, 2)) for b in chars if len(b) == 8)

    print("[ACTIVE-5] Direct LSB extraction from '{}'".format(stego_path))
    if DELIMITER in text:
        msg = text.split(DELIMITER)[0]
        print("  SUCCESS - message recovered: {!r}".format(msg))
    else:
        printable = "".join(c if 32 <= ord(c) < 127 else "." for c in text[:200])
        print("  FAILED - no delimiter found. First 200 chars (. = non-printable):")
        print("  {}".format(printable))
        print("  (Expected for AES-enhanced version — output is encrypted ciphertext.)")


# ── Active 6: JPEG Compression ───────────────────────────────

def jpeg_compression_attack(image_path, output_path, quality=75):
    img = Image.open(image_path).convert("RGB")
    img.save(output_path, format="JPEG", quality=quality)
    print("[ACTIVE-6] JPEG compression attack (quality={})".format(quality))
    print("  Input : {}".format(image_path))
    print("  Output: {}".format(output_path))
    print("  Effect: LSBs overwritten by JPEG quantisation — message destroyed.")


# ── Active 7: Gaussian Noise ─────────────────────────────────

def noise_attack(image_path, output_path, sigma=2.0):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)

    noise_arr = np.random.normal(0, sigma, arr.shape)
    noisy = np.clip(arr + noise_arr, 0, 255).astype(np.uint8)

    noisy_img = Image.fromarray(noisy, mode="RGB")
    noisy_img.save(output_path)

    original_lsb = arr.astype(np.uint8) & 1
    noisy_lsb    = noisy & 1
    flip_rate = np.mean(original_lsb != noisy_lsb)

    print("[ACTIVE-7] Gaussian noise attack (sigma={})".format(sigma))
    print("  Output         : '{}'".format(output_path))
    print("  Estimated LSB flip rate: {:.1f}%".format(flip_rate * 100))
    print("  Effect: ~{:.0f}% of hidden bits corrupted.".format(flip_rate * 100))


# ── Active 8: Cropping ───────────────────────────────────────

def cropping_attack(image_path, output_path, keep_fraction=0.75):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    new_w = int(w * keep_fraction)
    new_h = int(h * keep_fraction)
    cropped = img.crop((0, 0, new_w, new_h))
    cropped.save(output_path)

    removed_pct = (1 - keep_fraction ** 2) * 100
    print("[ACTIVE-8] Cropping attack (keep {:.0f}% of area)".format(keep_fraction * 100))
    print("  Original size : {}x{}".format(w, h))
    print("  Cropped size  : {}x{}".format(new_w, new_h))
    print("  Pixels removed: ~{:.0f}%".format(removed_pct))
    print("  Output        : '{}'".format(output_path))


# ── Run all passive ───────────────────────────────────────────

def run_all_passive(image_path, out_dir="."):
    base = os.path.splitext(os.path.basename(image_path))[0]
    print("=" * 60)
    print("PASSIVE ATTACK SUITE on: {}".format(image_path))
    print("=" * 60)
    visual_lsb_plane(image_path, os.path.join(out_dir, "{}_lsb_plane.png".format(base)))
    print()
    histogram_analysis(image_path, os.path.join(out_dir, "{}_histogram.png".format(base)))
    print()
    chi_square_test(image_path)
    print()
    rs_analysis(image_path)
    print("=" * 60)


# ── CLI ───────────────────────────────────────────────────────

USAGE = """
Commands:
  passive  <image> [output_dir]          Run all passive detection tests
  extract  <image>                       Attempt direct LSB extraction
  compress <image> <output.jpg>          JPEG compression attack
  noise    <image> <output.png>          Gaussian noise attack
  crop     <image> <output.png>          Cropping attack
"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    img = sys.argv[2]

    if cmd == "passive":
        out_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(img) or "."
        run_all_passive(img, out_dir)

    elif cmd == "extract":
        direct_extract(img)

    elif cmd == "compress":
        out = sys.argv[3] if len(sys.argv) > 3 else "compressed.jpg"
        jpeg_compression_attack(img, out)

    elif cmd == "noise":
        out = sys.argv[3] if len(sys.argv) > 3 else "noisy.png"
        noise_attack(img, out)

    elif cmd == "crop":
        out = sys.argv[3] if len(sys.argv) > 3 else "cropped.png"
        cropping_attack(img, out)

    else:
        print("Unknown command '{}'".format(cmd))
        print(USAGE)
        sys.exit(1)
