"""
WQE7003 Group Assignment — Defense Sub-Group
File: lsb_baseline.py
Description: Baseline LSB (Least Significant Bit) steganography
             — sequential pixel embedding, no encryption.
Member:  D1
"""

from PIL import Image
import sys
import os

DELIMITER = "$$END$$"


def text_to_bits(text):
    return "".join(format(ord(ch), "08b") for ch in text)


def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(b, 2)) for b in chars if len(b) == 8)


def embed(cover_path, message, output_path):
    img = Image.open(cover_path).convert("RGB")
    pixels = list(img.getdata())

    payload = message + DELIMITER
    bits = text_to_bits(payload)

    max_bits = len(pixels) * 3
    if len(bits) > max_bits:
        raise ValueError(
            "Message too long: need {} bits but image only holds {} bits.".format(len(bits), max_bits)
        )

    bit_index = 0
    new_pixels = []

    for pixel in pixels:
        r, g, b = pixel
        channels = [r, g, b]
        new_channels = []
        for value in channels:
            if bit_index < len(bits):
                new_value = (value & 0b11111110) | int(bits[bit_index])
                bit_index += 1
            else:
                new_value = value
            new_channels.append(new_value)
        new_pixels.append(tuple(new_channels))

    img.putdata(new_pixels)
    img.save(output_path)
    print("[EMBED] Message hidden in '{}'".format(output_path))
    print("        Bits used: {} / {} ({:.2f}% capacity)".format(
        len(bits), max_bits, 100 * len(bits) / max_bits))


def extract(stego_path):
    img = Image.open(stego_path).convert("RGB")
    pixels = list(img.getdata())

    bits = ""
    for pixel in pixels:
        for value in pixel:
            bits += str(value & 1)

    text = bits_to_text(bits)
    if DELIMITER in text:
        message = text.split(DELIMITER)[0]
        print("[EXTRACT] Hidden message: {!r}".format(message))
        return message
    else:
        raise ValueError("No hidden message found (delimiter not detected).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  embed:   python lsb_baseline.py embed <cover.png> <message> <output.png>")
        print("  extract: python lsb_baseline.py extract <stego.png>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "embed":
        if len(sys.argv) != 5:
            print("embed requires: <cover.png> <message> <output.png>")
            sys.exit(1)
        embed(sys.argv[2], sys.argv[3], sys.argv[4])

    elif mode == "extract":
        if len(sys.argv) != 3:
            print("extract requires: <stego.png>")
            sys.exit(1)
        extract(sys.argv[2])

    else:
        print("Unknown mode '{}'. Use 'embed' or 'extract'.".format(sys.argv[1]))
        sys.exit(1)
