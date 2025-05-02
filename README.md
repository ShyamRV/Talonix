# Talonix 🎵

**An AI-powered Python toolkit for realistic music and rhythm generation**

---

## 🎧 Overview

**Talonix** is a modular sound synthesis and rhythm generation suite designed for musicians, developers, and sound artists. It allows you to generate music loops, rhythmic patterns, and audio previews using instrument-specific MIDI and WAV files. Whether you want to compose piano loops, guitar riffs, or lo-fi beats, Talonix is the ideal tool.

---

## 🏆 Key Features

### 1. Instrument Sound Generator (`instrument SG.py`)

Generates musical melodies using a specified or randomized instrument.

* 👉 Supports: Piano, Drums, Guitar, Synth, Strings, Bass.
* 🔄 Random key & scale selection (Major/Minor).
* ⏱ Customizable BPM and duration (30s to 2 mins).
* 🎤 Outputs both MIDI and WAV using FluidSynth and SoundFont.

### 2. Rhythm & Pattern Generator (`Rythm G.py`)

A beat composer with customizable instrument layers, randomness, and genre presets.

* 🎶 Styles: Lo-Fi, Hip-Hop, Pop, EDM.
* 🎙 Instruments: Kick, Snare, Hi-Hat, Guitar, Bass, Synth, etc.
* 🎵 Full control over beat patterns, BPM, swing, fills, volume, panning, and time signatures.
* 🔹 Supports stem export, MIDI output, and real-time previews.

---

## 📁 Files Structure

```
.
├── instrument SG.py       # Instrument melody generator
├── Rythm G.py             # Rhythm pattern generator
├── samples/               # Folder for drum/instrument WAV samples (for rhythm engine)
├── FluidR3_GM.sf2         # SoundFont for FluidSynth (place in project root)
├── output/                # Generated audio and MIDI files
```

---

## ⚡ How It Works (Code Explanation)

### ✅ `instrument SG.py`

* **Inputs:** Instrument name, key (C, D, etc.), scale type, BPM, and duration.
* **Scales:** Defined in `MAJOR_SCALES` and `MINOR_SCALES` dictionaries.
* **Melody:** Notes chosen from scale, converted to MIDI using `NOTE_TO_MIDI`.
* **MIDI:** Uses `mido` to generate a sequence, `FluidSynth` to render as WAV.

### ✅ `Rythm G.py`

* **Modules:** Uses `pydub`, `mido`, `numpy`, `simpleaudio`, `rich`, `argparse`, and `logging`.
* **Pattern Engine:** Reads instrument-to-folder mapping, generates beat patterns based on genre config.
* **Preview:** Optional real-time loop playback using `simpleaudio`.
* **Export:** Exports WAV/MP3 + optional stems and MIDI.
* **Interactive Mode:** Allows user prompts for BPM, instruments, volume, etc., if not using config.

---

## 📊 Setup Instructions

### 1. Install Dependencies

```bash
pip install mido midi2audio pydub numpy simpleaudio rich
```

### 2. Download SoundFont

Place your `.sf2` SoundFont file (e.g., FluidR3\_GM.sf2) in the root directory.
[Download FluidR3\_GM.sf2](https://member.keymusician.com/Member/FluidR3_GM/index.html)

### 3. Sample Folder Setup (for Rhythm Generator)

Create `samples/` with subfolders:

```
samples/
  ├── kicks/
  ├── snares/
  ├── hihats/
  ├── bass/
  └── synth/
```

Add `.wav` files in each.

---

## 📝 Usage

### Run Instrument Generator:

```bash
python "instrument SG.py"
```

* Generates a random or chosen melody in MIDI + WAV format.

### Run Rhythm Generator (Interactive):

```bash
python "Rythm G.py"
```

* You can specify instruments, BPM, style, etc. interactively.

### Run Rhythm Generator with Config:

```bash
python "Rythm G.py" --config config.json --preview --export-midi --export-stems
```

---

## 🙏 Credits

Made with ❤️ by Shyam.

---
