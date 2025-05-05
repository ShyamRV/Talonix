
# 🎵 TALONIX

**A Python toolkit for procedural music and rhythm generation**

---

## 🎧 Overview

**Talonix** is a modular sound synthesis and rhythm generation suite designed for musicians, developers, and sound artists. It enables the creation of music loops, rhythmic patterns, and audio previews using instrument-specific MIDI and WAV files.

Whether you want to compose piano melodies, drum patterns, or lo-fi beats, Talonix provides a flexible, rule-based solution.

---

## 🏆 Key Features

### 1. Instrument Sound Generator (`instrument SG.py`)
- Generates musical melodies or drum patterns using a specified instrument.
- **Supports**: Piano, Drums, Guitar, Synth, Strings, Bass
- Random note selection from Major or Minor scales.
- Customizable BPM and duration (30s to 2 mins).
- Outputs both MIDI and WAV using FluidSynth and SoundFont.

### 2. Rhythm & Pattern Generator (`Rythm G.py`)
- A beat composer with customizable instrument layers and genre presets.
- **Styles**: Lo-Fi, Hip-Hop, Pop, EDM
- **Instruments**: Kick, Snare, Hi-Hat, Guitar, Bass, Synth, Percussion, etc.
- Full control over beat patterns, BPM, swing, fills, volume, panning, and time signatures.
- Supports stem export, MIDI output, and real-time audio previews.

---

## 📁 File Structure

```

.
├── instrument SG.py       # Instrument melody and drum pattern generator
├── Rythm G.py             # Rhythm pattern generator
├── samples/               # Folder for drum/instrument WAV samples (for rhythm engine)
├── FluidR3\_GM.sf2         # SoundFont for FluidSynth (place in project root)
├── output/                # Generated audio and MIDI files

````

---

## ⚡ How It Works

### ✅ `instrument SG.py`
- **Inputs**: Instrument name, key (C, D, etc.), scale type (Major/Minor), BPM, duration
- **Scales**: Major and Minor note dictionaries used for randomized selection
- **MIDI & Audio**: `mido` for MIDI file generation, `FluidSynth` for rendering WAV output

### ✅ `Rythm G.py`
- **Modules**: Uses `pydub`, `mido`, `numpy`, `simpleaudio`, `rich`, `argparse`, and `logging`
- **Pattern Engine**: Genre-specific configurations, complexity-driven variations
- **Audio Processing**: Loads `.wav` samples or generates synthetic tones
- **Preview & Export**: Real-time playback, WAV/MP3 export, optional stems and MIDI
- **Interactive Mode**: Prompts user if no config file is provided

---

## 📊 Setup Instructions

### 1. Install Dependencies

```bash
pip install mido midi2audio pydub numpy simpleaudio rich
````

> **Note**: For MP3 export in `Rythm G.py`, FFmpeg is required. Install it from [ffmpeg.org](https://ffmpeg.org).

---

### 2. Download SoundFont

Download `FluidR3_GM.sf2` and place it in the project root directory.

---

### 3. Sample Folder Setup

Create a `samples/` directory with subfolders:

```
samples/
  ├── kicks/
  ├── snares/
  ├── hihats/
  ├── bass/
  ├── synth/
  ├── guitar/
  ├── clap/
  ├── tambourine/
  ├── percussion/
```

> Add relevant `.wav` files to each subfolder.

---

## 📝 Usage

### Run Instrument Generator

```bash
python "instrument SG.py"
```

* Prompts for instrument, key, scale type, BPM, and duration
* Outputs MIDI and WAV files

---

### Run Rhythm Generator (Interactive Mode)

```bash
python "Rythm G.py"
```

* Specify genre, instruments, BPM, swing, and complexity interactively

---

### Run Rhythm Generator with Config

```bash
python "Rythm G.py" --config config.json --preview --export-midi --export-stems
```

* Uses parameters from a JSON config file
* Optional preview, MIDI export, and stem export

---

## 🚀 Future Updates

Stay tuned for exciting new tools and features coming to **Talonix**!
Follow the repository for updates on advanced music generation, new instrument packs, and real-time collaboration features.

---

## 🤝 Credits

Made by **Shyam**
