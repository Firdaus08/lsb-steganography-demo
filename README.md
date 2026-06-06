# WQE7003 — Image LSB Steganography
### Cryptography and Information Hiding | Group Assignment 2025/26

---

## 📁 Project Files

| File | Who Uses It | Purpose |
|------|-------------|---------|
| `demo_runner.py` | Everyone | **Start here.** Guided step-by-step demo session |
| `lsb_baseline.py` | Defense D1 | Plain LSB embed and extract (no encryption) |
| `lsb_enhanced.py` | Defense D3 | Enhanced LSB: AES-128 + random pixel scatter |
| `lsb_attacks.py` | Attack A1, A2 | All passive and active attack tools |
| `README.md` | Everyone | This file |

---

## ⚡ Quick Start (Recommended)

### Step 1 — Install dependencies
```bash
pip install Pillow pycryptodome numpy scipy matplotlib colorama
```
> `colorama` is optional — it adds colour to terminal output on Windows.

### Step 2 — Run the guided demo
```bash
python demo_runner.py
```

That's it. The demo runner will:
- Ask you to start a new session
- Walk you through **8 steps** one by one
- Save **every output file** in a dedicated folder (`Demo_1/`, `Demo_2/`, etc.)
- At the end, print a summary of every file created and what it is

---

## 🗂️ Demo Session Folders

Every time you run `demo_runner.py` and start a new session, a new folder is created:

```
Demo_1/
├── cover.png                        ← original cover image
├── stego_baseline.png               ← baseline stego (plain LSB)
├── stego_enhanced.png               ← enhanced stego (AES + scatter)
├── stego_baseline_lsb_plane.png     ← LSB plane analysis image
├── stego_enhanced_lsb_plane.png     ← LSB plane analysis image
├── stego_baseline_histogram.png     ← histogram chart
├── stego_enhanced_histogram.png     ← histogram chart
├── attacked_jpeg.jpg                ← JPEG compression attack result
├── attacked_noisy.png               ← Gaussian noise attack result
└── attacked_cropped.png             ← cropping attack result

Demo_2/
└── ... (separate run, different message/key/cover)
```

This means you can run the demo 5 times and compare `Demo_1/` vs `Demo_2/` without anything getting overwritten.

---

## 🔍 Manual Commands (Advanced)

If you want to run individual steps yourself instead of using the demo runner, use the commands below. Replace `Demo_1/` with your actual folder path.

---

### 🛡️ DEFENSE — Baseline LSB (`lsb_baseline.py`)

#### Embed a message
```bash
python lsb_baseline.py embed <cover_image> "<secret_message>" <output_image>
```
**Example:**
```bash
python lsb_baseline.py embed Demo_1/cover.png "Hello World" Demo_1/stego_baseline.png
```
**What it does:**
Converts the message to binary. Replaces the least significant bit (LSB) of each pixel channel (R, G, B) with message bits, going left-to-right, top-to-bottom. Saves as PNG (lossless).

---

#### Extract a message
```bash
python lsb_baseline.py extract <stego_image>
```
**Example:**
```bash
python lsb_baseline.py extract Demo_1/stego_baseline.png
```
**What it does:**
Reads LSBs from pixels sequentially, converts bits back to characters, and stops when it finds the end delimiter `$$END$$`. Prints the recovered message.

---

### 🛡️ DEFENSE — Enhanced LSB (`lsb_enhanced.py`)

#### Embed with AES encryption + random scatter
```bash
python lsb_enhanced.py embed <cover_image> "<secret_message>" <output_image> <key>
```
**Example:**
```bash
python lsb_enhanced.py embed Demo_1/cover.png "Hello World" Demo_1/stego_enhanced.png mySecretKey
```
**What it does:**
1. Derives a 16-byte AES key from `<key>` using SHA-256
2. Encrypts the message with AES-128 in CBC mode (random IV each time)
3. Uses the key to seed a PRNG and generate a shuffled list of pixel positions
4. Embeds the ciphertext bits at those random positions (not sequentially)
5. Saves as PNG

**Key point:** The receiver MUST use the same `<key>` to extract. Without it, extraction is impossible.

---

#### Extract with AES decryption
```bash
python lsb_enhanced.py extract <stego_image> <key>
```
**Example:**
```bash
python lsb_enhanced.py extract Demo_1/stego_enhanced.png mySecretKey
```
**What it does:**
Regenerates the same random pixel positions from the key, reads bits in that order, then AES-decrypts the assembled ciphertext to recover the original message.

---

### ⚔️ ATTACK — All Attack Tools (`lsb_attacks.py`)

#### Passive Attack — Run all detection tests
```bash
python lsb_attacks.py passive <image> [output_folder]
```
**Example:**
```bash
python lsb_attacks.py passive Demo_1/stego_baseline.png Demo_1/
python lsb_attacks.py passive Demo_1/stego_enhanced.png Demo_1/
```
**What it does:** Runs 4 tests and saves image outputs to `output_folder`:

| Test | What it detects |
|------|----------------|
| **Visual LSB Plane** | Structured patterns in the LSB layer (visible structure = embedding) |
| **Histogram Analysis** | Even/odd pixel value pair equalisation (equalised pairs = embedding) |
| **Chi-Square Test** | Statistical test — high p-value (> 0.05) = likely stego detected |
| **RS Analysis** | R ≈ R_neg symmetry = likely stego detected |

**What to look for:**
- Baseline stego: chi-square p-value will be close to **1.0** (clearly detected)
- Enhanced stego: chi-square p-value will be much lower (harder to detect)

---

#### Active Attack 1 — Direct LSB Extraction
```bash
python lsb_attacks.py extract <image>
```
**Example:**
```bash
python lsb_attacks.py extract Demo_1/stego_baseline.png
python lsb_attacks.py extract Demo_1/stego_enhanced.png
```
**What it does:**
Reads LSBs sequentially and tries to decode them as a text message.
- On **baseline**: recovers the plaintext message ✅
- On **enhanced**: gets garbled ciphertext bytes ❌ (AES encrypted + wrong pixel order)

---

#### Active Attack 2 — JPEG Compression
```bash
python lsb_attacks.py compress <image> <output.jpg>
```
**Example:**
```bash
python lsb_attacks.py compress Demo_1/stego_enhanced.png Demo_1/attacked_jpeg.jpg
```
**What it does:**
Re-saves the image as JPEG (lossy). JPEG's DCT quantisation modifies pixel values, overwriting the carefully placed LSBs. The message is destroyed completely. Works on both baseline and enhanced.

**Verify destruction:**
```bash
python lsb_attacks.py extract Demo_1/attacked_jpeg.jpg
```

---

#### Active Attack 3 — Gaussian Noise
```bash
python lsb_attacks.py noise <image> <output.png>
```
**Example:**
```bash
python lsb_attacks.py noise Demo_1/stego_baseline.png Demo_1/attacked_noisy.png
```
**What it does:**
Adds Gaussian random noise (sigma=2.0) to every pixel. This randomly flips approximately 30–50% of all LSBs, corrupting a large fraction of the hidden bits. Without error correction, even 1% corruption makes recovery impossible.

---

#### Active Attack 4 — Cropping
```bash
python lsb_attacks.py crop <image> <output.png>
```
**Example:**
```bash
python lsb_attacks.py crop Demo_1/stego_enhanced.png Demo_1/attacked_cropped.png
```
**What it does:**
Removes 25% of the image (keeps top-left 75% × 75% area).
- On **baseline**: the message might partially survive if it was short (bits are at the start)
- On **enhanced**: message is destroyed because bits are scattered everywhere

---

## 💡 Key Concepts Explained

### What is LSB steganography?
Every pixel in a PNG image has 3 colour channels: Red, Green, Blue — each stored as a number from 0 to 255. Changing the last bit (least significant bit) of 200 to 201 is a difference of only 1 — completely invisible to the eye. LSB steganography hides one bit of the secret message in each pixel channel's last bit.

### What is the Enhancement?

**Problem with baseline:**
If you just embed bits left-to-right, an attacker can:
1. Read all the LSBs in order and get the message immediately
2. Run a chi-square test and detect that something is hidden

**Enhancement 1 — AES-128 Encryption:**
The message is encrypted *before* embedding. Even if an attacker reads all the LSBs, they only get random-looking ciphertext. Without the key, they cannot read the message.

**Enhancement 2 — Random Pixel Scatter:**
Instead of hiding bits in pixels 1, 2, 3, 4... the program hides them in pixels 47, 891, 23, 1204... (a random order derived from the key). The attacker does not know which pixels to read, and the chi-square test sees no localised pattern.

### Why do JPEG/Noise/Crop attacks work on both versions?
These attacks do not need to *find* the hidden bits — they destroy the entire image's LSB layer blindly. Both versions use the same fragile LSB layer, so both are equally vulnerable. A truly robust scheme would use spread-spectrum embedding or error-correcting codes.

---

## 🗓️ Timeline

| Week | Task |
|------|------|
| 7–8 | D1 builds baseline, A1/A2 study attack theory |
| 9–10 | D2/D3 build enhanced version, A1/A2 attack the baseline |
| 11–12 | A1/A2 attack the enhanced version, D4/A3 write reports |
| 13 | Combined group presentation |

---

## 📋 Marking Criteria Reminder

| Sub-group | Criterion | Marks |
|-----------|-----------|-------|
| Defense | Selected technique and implementation | 3 |
| Defense | Enhancements / Modifications | 4 |
| Defense | Justification / Usefulness | 4 |
| Defense | Code Demonstrations | 2 |
| Attack | Attack Plan | 4 |
| Attack | Justification / Usefulness | 4 |
| Attack | Findings of Attacks | 3 |
| Attack | Code Demonstrations | 2 |
| All | Presentation and Q&A (individual) | 4 |
| **Total** | | **30** |
