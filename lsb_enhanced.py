"""
WQE7003 Group Assignment — Defense Sub-Group
File: lsb_enhanced.py
Description: Enhanced LSB steganography with:
             1. AES-128 encryption (CBC mode)
             2. Pseudo-random pixel selection using key as PRNG seed
Member:  D3
Dependencies: pip install Pillow pycryptodome
"""

import sys
import random
import hashlib
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def prepare_key(raw_key):
    return hashlib.sha256(raw_key.encode()).digest()[:16]


def aes_encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
    return cipher.iv + ciphertext


def aes_decrypt(data, key):
    iv = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode("utf-8")


def get_random_positions(num_bits, total_slots, seed):
    rng = random.Random(seed)
    positions = list(range(total_slots))
    rng.shuffle(positions)
    return positions[:num_bits]


def key_to_seed(key):
    return int.from_bytes(key, "big")


def bytes_to_bits(data):
    return "".join(format(byte, "08b") for byte in data)


def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def embed(cover_path, message, output_path, raw_key):
    key = prepare_key(raw_key)
    seed = key_to_seed(key)

    ciphertext = aes_encrypt(message, key)
    length_header = len(ciphertext).to_bytes(4, "big")
    payload = length_header + ciphertext
    bits = bytes_to_bits(payload)

    img = Image.open(cover_path).convert("RGB")
    pixels = list(img.getdata())
    total_slots = len(pixels) * 3

    if len(bits) > total_slots:
        raise ValueError("Message too large: {} bits needed, {} slots available.".format(
            len(bits), total_slots))

    positions = get_random_positions(len(bits), total_slots, seed)

    flat = []
    for pixel in pixels:
        flat.extend(pixel)

    for bit_index, slot in enumerate(positions):
        flat[slot] = (flat[slot] & 0b11111110) | int(bits[bit_index])

    new_pixels = [tuple(flat[i:i+3]) for i in range(0, len(flat), 3)]
    img.putdata(new_pixels)
    img.save(output_path)

    print("[EMBED ENHANCED] Stego image saved to '{}'".format(output_path))
    print("  AES ciphertext size : {} bytes".format(len(ciphertext)))
    print("  Bits embedded       : {}".format(len(bits)))
    print("  Capacity used       : {:.2f}%".format(100 * len(bits) / total_slots))
    print("  Pixel order         : pseudo-random (seed from key)")


def extract(stego_path, raw_key):
    key = prepare_key(raw_key)
    seed = key_to_seed(key)

    img = Image.open(stego_path).convert("RGB")
    pixels = list(img.getdata())
    total_slots = len(pixels) * 3

    flat = []
    for pixel in pixels:
        flat.extend(pixel)

    header_positions = get_random_positions(32, total_slots, seed)
    header_bits = "".join(str(flat[pos] & 1) for pos in header_positions)
    payload_length = int.from_bytes(bits_to_bytes(header_bits), "big")

    total_bits_needed = 32 + payload_length * 8
    all_positions = get_random_positions(total_bits_needed, total_slots, seed)
    all_bits = "".join(str(flat[pos] & 1) for pos in all_positions)

    ciphertext_bits = all_bits[32:]
    ciphertext = bits_to_bytes(ciphertext_bits)

    message = aes_decrypt(ciphertext, key)
    print("[EXTRACT ENHANCED] Hidden message: {!r}".format(message))
    return message


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  embed:   python lsb_enhanced.py embed <cover.png> <message> <output.png> <key>")
        print("  extract: python lsb_enhanced.py extract <stego.png> <key>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "embed":
        if len(sys.argv) != 6:
            print("embed requires: <cover.png> <message> <output.png> <key>")
            sys.exit(1)
        embed(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif mode == "extract":
        if len(sys.argv) != 4:
            print("extract requires: <stego.png> <key>")
            sys.exit(1)
        extract(sys.argv[2], sys.argv[3])

    else:
        print("Unknown mode '{}'. Use 'embed' or 'extract'.".format(sys.argv[1]))
        sys.exit(1)
