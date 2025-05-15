'''File has been updated from text file to python file for smoother operations, eassy access and 
user convinience.'''

import os
import time
import random
import sys
import gc
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess
from difflib import get_close_matches

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not installed. Synthetic tones disabled. Install with: pip install numpy")

try:
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
    from pydub.effects import normalize
except ImportError:
    logging.error("pydub not installed. Install with: pip install pydub")
    sys.exit(1)

try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False
    logging.warning("simpleaudio not installed. Previews disabled. Install with: pip install simpleaudio")

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logging.warning("rich not installed. Using basic console output. Install with: pip install rich")

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    logging.warning("mido not installed. MIDI export disabled. Install with: pip install mido")

# Setup logging
def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("rhythm_generator.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

console = Console() if RICH_AVAILABLE else None

# Constants
SAMPLE_RATE = 44100
MIN_BPM = 20
MAX_BPM = 300
MIN_SWING = -50
MAX_SWING = 50
DEFAULT_VOLUME = 80
NOTE_TYPES = {"whole": 4, "half": 2, "quarter": 1, "eighth": 0.5, "sixteenth": 0.25, "thirty-second": 0.125}
COMPLEXITY_LEVELS = ["simple", "medium", "complex"]
TIME_SIGNATURES = ["4/4", "3/4", "6/8"]
SUBDIVISIONS = ["straight", "triplet"]

# Mapping of instrument names to sample folder names (handling plural forms)
INSTRUMENT_TO_FOLDER = {
    "kick": "kicks",
    "snare": "snares",
    "hihat": "hihats",
    "bass": "bass",
    "synth": "synth",
    "guitar": "guitar",
    "clap": "clap",
    "tambourine": "tambourine",
    "percussion": "percussion"
}

# Available instruments
AVAILABLE_INSTRUMENTS = list(INSTRUMENT_TO_FOLDER.keys())

# Default style configurations
STYLE_CONFIGS = {
    "hiphop": {
        "bpm": 85,
        "pattern": {
            "kick": [1, 0, 1, 0, 1, 0, 1, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0],
            "hihat": [1, 1, 1, 1, 1, 1, 1, 1],
            "bass": [1, 0, 0, 0, 1, 0, 0, 0],
            "synth": [0, 1, 0, 1, 0, 1, 0, 1],
            "guitar": [0, 0, 1, 0, 0, 0, 1, 0],
            "percussion": [0, 0, 0, 1, 0, 0, 0, 1]
        },
        "swing": 20,
        "complexity": "medium",
        "time_signature": "4/4"
    },
    "lofi": {
        "bpm": 70,
        "pattern": {
            "kick": [1, 0, 0, 0, 1, 0, 0, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0],
            "hihat": [1, 0, 1, 0, 1, 0, 1, 0],
            "bass": [1, 0, 0, 0, 0, 0, 0, 0],
            "synth": [1, 0, 1, 0, 1, 0, 1, 0],
            "guitar": [0, 0, 0, 0, 1, 0, 0, 0],
            "percussion": [0, 0, 0, 1, 0, 0, 0, 0]
        },
        "swing": 10,
        "complexity": "simple",
        "time_signature": "4/4"
    },
    "edm": {
        "bpm": 128,
        "pattern": {
            "kick": [1, 0, 1, 0, 1, 0, 1, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0],
            "hihat": [1, 1, 1, 1, 1, 1, 1, 1],
            "bass": [1, 1, 1, 1, 1, 1, 1, 1],
            "synth": [1, 0, 0, 0, 1, 0, 0, 0],
            "guitar": [0, 0, 0, 0, 0, 0, 0, 0],
            "percussion": [0, 0, 0, 0, 0, 0, 0, 1]
        },
        "swing": 0,
        "complexity": "complex",
        "time_signature": "4/4"
    },
    "pop": {
        "bpm": 120,
        "pattern": {
            "kick": [1, 0, 1, 0, 1, 0, 1, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0],
            "hihat": [1, 1, 1, 1, 1, 1, 1, 1],
            "bass": [1, 0, 0, 0, 1, 0, 0, 0],
            "synth": [1, 0, 1, 0, 1, 0, 1, 0],
            "guitar": [0, 1, 0, 1, 0, 1, 0, 1],
            "percussion": [0, 0, 0, 1, 0, 0, 0, 1]
        },
        "swing": 5,
        "complexity": "medium",
        "time_signature": "4/4"
    }
}

# Check for FFmpeg availability
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("FFmpeg not found. MP3 export requires FFmpeg. Install it from https://ffmpeg.org/download.html or use WAV format.")
        return False

# Generate a synthetic tone as a fallback
def generate_synthetic_tone(frequency=440, duration_ms=200):
    if not NUMPY_AVAILABLE:
        logging.warning("Cannot generate synthetic tone: NumPy not installed.")
        return AudioSegment.silent(duration=duration_ms)
    sample_rate = SAMPLE_RATE
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = np.sin(frequency * t * 2 * np.pi) * 0.5
    audio = np.int16(tone * 32767).tobytes()
    return AudioSegment(audio, frame_rate=sample_rate, sample_width=2, channels=1)

# Create a silent segment
def create_silent_segment(duration_ms):
    return AudioSegment.silent(duration=duration_ms, frame_rate=SAMPLE_RATE)

# Load samples for a given instrument
def load_samples(instrument):
    samples_dir = "samples"
    folder_name = INSTRUMENT_TO_FOLDER.get(instrument, instrument).lower()
    
    if not os.path.exists(samples_dir):
        logging.error(f"Samples directory '{samples_dir}' does not exist. Using synthetic tone for '{instrument}'.")
        return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]

    available_folders = [f.lower() for f in os.listdir(samples_dir) if os.path.isdir(os.path.join(samples_dir, f))]
    if folder_name not in available_folders:
        matches = get_close_matches(folder_name, available_folders, n=1, cutoff=0.8)
        if matches:
            corrected_folder = matches[0]
            logging.warning(f"Instrument folder '{folder_name}' not found. Using closest match '{corrected_folder}'.")
            folder_name = corrected_folder
        else:
            logging.warning(f"No samples directory for '{instrument}' (expected '{folder_name}'). Using synthetic tone.")
            return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]

    folder_path = os.path.join(samples_dir, folder_name)
    if not os.listdir(folder_path):
        logging.warning(f"Samples directory '{folder_path}' is empty. Using synthetic tone for '{instrument}'.")
        return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]

    samples = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.wav'):
            sample_path = os.path.join(folder_path, file)
            try:
                sample = AudioSegment.from_wav(sample_path)
                sample = sample.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2)
                samples.append(sample)
                logging.debug(f"Loaded sample: {file} ({len(sample)}ms) for '{instrument}'")
            except CouldntDecodeError as e:
                logging.error(f"Failed to decode {sample_path}: {e}. Skipping file.")
            except Exception as e:
                logging.error(f"Failed to load {sample_path}: {e}. Skipping file.")
    
    if not samples:
        logging.warning(f"No valid samples for '{instrument}' in '{folder_path}'. Using synthetic tone.")
        return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]
    return samples

# Randomly choose a sample
def choose_sample(samples):
    return random.choice(samples) if samples else create_silent_segment(200)

# Apply swing to beat timing
def apply_swing(beat_idx, swing_percent, beat_duration_ms):
    if swing_percent == 0 or beat_idx % 2 == 0:
        return 0
    swing_ms = (swing_percent / 100) * (beat_duration_ms / 2)
    return swing_ms

# Apply panning
def apply_panning(audio, pan):
    if pan == 0:
        return audio
    left_gain = -pan * 12
    right_gain = pan * 12
    return audio.set_channels(2).pan(left_gain=left_gain, right_gain=right_gain)

# Apply volume adjustment (in dB)
def apply_volume(audio, volume):
    if volume == 100:
        return audio
    # Map 0-100 to -24dB to 0dB
    db_change = (volume - 100) * 0.24
    return audio + db_change

# Play a short audio segment (for preview)
def play_preview(audio_segment, timeout=2.0):
    if not SIMPLEAUDIO_AVAILABLE:
        logging.warning("simpleaudio not available. Skipping preview.")
        return
    try:
        audio_segment = audio_segment.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2)
        if not audio_segment.raw_data:
            logging.warning("Empty audio buffer. Skipping preview.")
            return
        msg = f"Playing preview (duration: {len(audio_segment)}ms)"
        logging.info(msg)
        if RICH_AVAILABLE:
            console.print(f"[bold cyan]🎵 {msg}[/bold cyan]")
        else:
            print(f"🎵 {msg}")
        play_obj = sa.play_buffer(
            audio_segment.raw_data,
            num_channels=1,
            bytes_per_sample=2,
            sample_rate=SAMPLE_RATE
        )
        start_time = time.time()
        while play_obj.is_playing() and (time.time() - start_time) < timeout:
            time.sleep(0.01)
        if play_obj.is_playing():
            play_obj.stop()
            msg = "Preview timed out."
            logging.warning(msg)
            if RICH_AVAILABLE:
                console.print("[yellow]⚠️ Preview timed out.[/yellow]")
            else:
                print(f"⚠️ {msg}")
        else:
            msg = "Preview completed."
            logging.info(msg)
            if RICH_AVAILABLE:
                console.print("[green]✅ Preview completed.[/green]")
            else:
                print(f"✅ {msg}")
        play_obj.stop()
        del play_obj
        gc.collect()
        time.sleep(0.1)
    except Exception as e:
        logging.error(f"Preview failed: {e}")
        if RICH_AVAILABLE:
            console.print(f"[red]⚠️ Preview failed: {e}[/red]")
        else:
            print(f"⚠️ Preview failed: {e}")

# Extend base pattern
def extend_base_pattern(base_pattern, pattern_length):
    if len(base_pattern) >= pattern_length:
        return base_pattern[:pattern_length]
    extended = base_pattern * (pattern_length // len(base_pattern)) + base_pattern[:pattern_length % len(base_pattern)]
    return extended

# Generate a rhythm pattern
def generate_pattern(complexity, pattern_length, base_pattern, fill_frequency=0.2):
    base_pattern = extend_base_pattern(base_pattern, pattern_length)
    if complexity == "simple":
        pattern = [1 if random.random() < 0.3 else 0 for _ in range(pattern_length)]
    elif complexity == "medium":
        pattern = [base_pattern[i] if random.random() < 0.7 else random.choice([0, 1]) for i in range(pattern_length)]
        pattern[0] = 1
        pattern[pattern_length // 2] = 1
    else:
        pattern = [base_pattern[i] if random.random() < 0.5 else random.choice([0, 1]) for i in range(pattern_length)]
        for i in range(pattern_length - 1, 0, -int(1 / fill_frequency)):
            pattern[i] = 1
    pattern[0] = 1
    return pattern

# Generate MIDI file
def generate_midi(instrument_patterns, pattern_length, bpm, note_type, subdivision, output_filename):
    if not MIDO_AVAILABLE:
        logging.warning("mido not installed. Skipping MIDI export.")
        return
    try:
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)
        ticks_per_beat = midi.ticks_per_beat
        tempo = mido.bpm2tempo(bpm)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        note_duration = int(ticks_per_beat * NOTE_TYPES[note_type] * (2/3 if subdivision == "triplet" else 1))
        
        # Track the last event time to ensure proper timing
        last_time = 0
        events = []
        for inst, pattern in instrument_patterns.items():
            midi_note = 36 + AVAILABLE_INSTRUMENTS.index(inst)
            for i, hit in enumerate(pattern):
                if hit:
                    start_time = i * note_duration
                    events.append((start_time, mido.Message('note_on', note=midi_note, velocity=100)))
                    events.append((start_time + note_duration, mido.Message('note_off', note=midi_note, velocity=0)))
        
        # Sort events by time
        events.sort(key=lambda x: x[0])
        for event_time, msg in events:
            delta_time = event_time - last_time
            msg.time = delta_time
            track.append(msg)
            last_time = event_time

        midi.save(output_filename)
        msg = f"MIDI exported as: {output_filename}"
        logging.info(msg)
        if RICH_AVAILABLE:
            console.print(f"[green]✅ {msg}[/green]")
        else:
            print(f"✅ {msg}")
    except Exception as e:
        logging.error(f"MIDI export failed: {e}")
        if RICH_AVAILABLE:
            console.print(f"[red]⚠️ MIDI export failed: {e}[/red]")
        else:
            print(f"⚠️ MIDI export failed: {e}")

# Generate the rhythm loop
def generate_rhythm(style, instruments, bpm, note_type, swing, complexity, volumes, pattern_length, time_signature, subdivision, fill_frequency, master_volume, pan_settings, loop_repeats, preview=False):
    logging.info(f"Generating rhythm | Style: {style} | BPM: {bpm} | Instruments: {instruments}")
    
    # Display configuration
    config_lines = [
        f"Style: {style}",
        f"Instruments: {', '.join(instruments)}",
        f"BPM: {bpm}",
        f"Note Type: {note_type}",
        f"Swing: {swing}%",
        f"Complexity: {complexity}",
        f"Pattern Length: {pattern_length}",
        f"Time Signature: {time_signature}",
        f"Subdivision: {subdivision}"
    ]
    if RICH_AVAILABLE:
        table = Table(title="Rhythm Configuration")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        for line in config_lines:
            param, value = line.split(": ", 1)
            table.add_row(param, value)
        console.print(table)
    else:
        print("\nRhythm Configuration:")
        for line in config_lines:
            print(line)

    # Validate inputs
    if style not in STYLE_CONFIGS:
        logging.warning(f"Invalid style '{style}'. Defaulting to 'pop'.")
        style = 'pop'
    if bpm < MIN_BPM or bpm > MAX_BPM:
        logging.warning(f"BPM {bpm} out of range. Setting to {STYLE_CONFIGS[style]['bpm']}.")
        bpm = STYLE_CONFIGS[style]['bpm']
    if note_type not in NOTE_TYPES:
        logging.warning(f"Invalid note type '{note_type}'. Defaulting to 'quarter'.")
        note_type = 'quarter'
    if swing < MIN_SWING or swing > MAX_SWING:
        logging.warning(f"Swing {swing}% out of range. Setting to 0.")
        swing = 0
    if complexity not in COMPLEXITY_LEVELS:
        logging.warning(f"Invalid complexity '{complexity}'. Defaulting to 'medium'.")
        complexity = 'medium'
    if pattern_length < 4 or pattern_length > 16:
        logging.warning(f"Pattern length {pattern_length} out of range. Setting to 8.")
        pattern_length = 8
    if time_signature not in TIME_SIGNATURES:
        logging.warning(f"Invalid time signature '{time_signature}'. Defaulting to '4/4'.")
        time_signature = '4/4'
    if subdivision not in SUBDIVISIONS:
        logging.warning(f"Invalid subdivision '{subdivision}'. Defaulting to 'straight'.")
        subdivision = 'straight'

    # Calculate beat duration
    beat_duration_ms = int(60000 / bpm * NOTE_TYPES[note_type])
    if subdivision == "triplet":
        beat_duration_ms = int(beat_duration_ms * 2 / 3)
    msg = f"Tempo: {bpm} BPM | Beat duration: {beat_duration_ms}ms"
    logging.info(msg)
    if RICH_AVAILABLE:
        console.print(f"[bold]{msg}[/bold]")
    else:
        print(msg)

    # Get style-specific pattern
    base_patterns = STYLE_CONFIGS[style]["pattern"]
    instrument_patterns = {}
    for inst in instruments:
        base_pattern = base_patterns.get(inst, [0] * 8)
        instrument_patterns[inst] = generate_pattern(complexity, pattern_length, base_pattern, fill_frequency)
    msg = f"Patterns: {instrument_patterns}"
    logging.info(msg)
    if RICH_AVAILABLE:
        console.print(f"[bold]{msg}[/bold]")
    else:
        print(msg)

    # Load samples
    instrument_samples = {}
    for inst in list(instruments):  # Create a copy to allow modification
        samples = load_samples(inst)
        if samples:
            instrument_samples[inst] = samples
        else:
            instruments.remove(inst)
    if not instrument_samples:
        logging.error("No valid instruments. Generating silent loop.")
        return create_silent_segment(pattern_length * beat_duration_ms * loop_repeats), {}

    # Create the rhythm loop
    beat_layers = []
    instrument_stems = {inst: create_silent_segment(0) for inst in instruments}
    for beat_idx in range(pattern_length):
        beat_layer = create_silent_segment(beat_duration_ms)
        has_content = False
        for instrument in instrument_samples:
            if instrument in instrument_patterns and instrument_patterns[instrument][beat_idx]:
                sample = choose_sample(instrument_samples[instrument])
                volume = volumes.get(instrument, DEFAULT_VOLUME)
                sample = apply_volume(sample, volume)
                pan = pan_settings.get(instrument, 0)
                sample = apply_panning(sample, pan)
                if len(sample) < beat_duration_ms:
                    sample = sample + create_silent_segment(beat_duration_ms - len(sample))
                elif len(sample) > beat_duration_ms:
                    sample = sample[:beat_duration_ms]
                try:
                    beat_layer = beat_layer.overlay(sample, gain_during_overlay=-6)  # Prevent clipping
                    stem_segment = create_silent_segment(beat_duration_ms)
                    stem_segment = stem_segment.overlay(sample)
                    instrument_stems[instrument] = instrument_stems[instrument] + stem_segment
                    has_content = True
                    msg = f"Adding {instrument} to beat {beat_idx + 1} (volume: {volume}%, pan: {pan})"
                    logging.info(msg)
                    if RICH_AVAILABLE:
                        console.print(f"[bold]🥁 {msg}[/bold]")
                    else:
                        print(f"🥁 {msg}")
                except Exception as e:
                    logging.error(f"Failed to overlay {instrument}: {e}")
                    if RICH_AVAILABLE:
                        console.print(f"[red]⚠️ Failed to overlay {instrument}: {e}[/red]")
                    else:
                        print(f"⚠️ Failed to overlay {instrument}: {e}")
        try:
            beat_layer = normalize(beat_layer.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2))
            msg = f"Beat {beat_idx + 1}: {len(beat_layer)}ms, has_content: {has_content}"
            logging.info(msg)
            if RICH_AVAILABLE:
                console.print(f"[cyan]🔊 {msg}[/cyan]")
            else:
                print(f"🔊 {msg}")
        except Exception as e:
            logging.error(f"Failed to normalize beat {beat_idx + 1}: {e}")
            beat_layer = create_silent_segment(beat_duration_ms)
            has_content = False
        if preview and has_content:
            play_preview(beat_layer)
        beat_layers.append(beat_layer)
        del beat_layer
        gc.collect()

    # Concatenate and repeat loop
    loop = create_silent_segment(0)
    for _ in range(loop_repeats):
        for beat_layer in beat_layers:
            loop = loop + beat_layer
    loop = apply_volume(loop, master_volume)
    expected_duration = pattern_length * beat_duration_ms * loop_repeats
    if len(loop) < expected_duration:
        loop = loop + create_silent_segment(expected_duration - len(loop))
    msg = f"Generated loop duration: {len(loop)}ms"
    logging.info(msg)
    if RICH_AVAILABLE:
        console.print(f"[green]✅ {msg}[/green]")
    else:
        print(f"✅ {msg}")
    return loop, instrument_stems, instrument_patterns

# Export rhythm, stems, and MIDI
def export_rhythm(loop, instrument_stems, instrument_patterns, style, bpm, note_type, pattern_length, output_format, export_stems, export_midi, project_name, loop_repeats, subdivision):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{project_name}_{style}_{timestamp}.{output_format}")
    
    if output_format == "mp3" and not check_ffmpeg():
        output_format = "wav"
        output_filename = output_filename.replace(".mp3", ".wav")

    try:
        loop = normalize(loop.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2))
        loop.export(output_filename, format=output_format)
        msg = f"Rhythm exported as: {output_filename}"
        logging.info(msg)
        if RICH_AVAILABLE:
            console.print(f"[green]✅ {msg}[/green]")
        else:
            print(f"✅ {msg}")
    except Exception as e:
        logging.error(f"Export failed: {e}")
        if RICH_AVAILABLE:
            console.print(f"[red]⚠️ Export failed: {e}[/red]")
        else:
            print(f"⚠️ Export failed: {e}")
        return

    if export_stems:
        for inst, stem in instrument_stems.items():
            stem_filename = os.path.join(output_dir, f"{project_name}_{style}_{inst}_{timestamp}.{output_format}")
            try:
                stem = normalize(stem.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2))
                stem = stem * loop_repeats
                stem.export(stem_filename, format=output_format)
                msg = f"Stem exported as: {stem_filename}"
                logging.info(msg)
                if RICH_AVAILABLE:
                    console.print(f"[green]✅ {msg}[/green]")
                else:
                    print(f"✅ {msg}")
            except Exception as e:
                logging.error(f"Stem export failed for {inst}: {e}")
                if RICH_AVAILABLE:
                    console.print(f"[red]⚠️ Stem export failed for {inst}: {e}[/red]")
                else:
                    print(f"⚠️ Stem export failed for {inst}: {e}")

    if export_midi:
        midi_filename = os.path.join(output_dir, f"{project_name}_{style}_{timestamp}.mid")
        generate_midi(instrument_patterns, pattern_length, bpm, note_type, subdivision, midi_filename)

    if SIMPLEAUDIO_AVAILABLE:
        try:
            play_preview(loop, timeout=10.0)
        except Exception as e:
            logging.error(f"Playback failed: {e}")
            if RICH_AVAILABLE:
                console.print(f"[red]⚠️ Playback failed: {e}[/red]")
            else:
                print(f"⚠️ Playback failed: {e}")

# Main interactive function
def main():
    parser = argparse.ArgumentParser(description="Quantum Love Rhythm Generator")
    parser.add_argument('--config', type=str, help="Path to JSON config file")
    parser.add_argument('--preview', action='store_true', help="Enable previews")
    parser.add_argument('--export-stems', action='store_true', help="Export stems")
    parser.add_argument('--export-midi', action='store_true', help="Export MIDI")
    parser.add_argument('--output-format', choices=['wav', 'mp3'], default='wav', help="Output format")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(args.debug)

    # Default config
    config = {
        "style": "pop",
        "instruments": ["kick", "snare", "hihat", "percussion"],
        "bpm": 120,
        "note_type": "quarter",
        "swing": 0,
        "complexity": "medium",
        "volumes": {"kick": 90, "snare": 80, "hihat": 70, "percussion": 75},
        "pattern_length": 8,
        "time_signature": "4/4",
        "subdivision": "straight",
        "fill_frequency": 0.2,
        "master_volume": 100,
        "pan_settings": {"kick": 0, "snare": 0.3, "hihat": -0.3, "percussion": 0.1},
        "loop_repeats": 1,
        "project_name": "quantum_love"
    }

    # Load config from file
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config.update(json.load(f))
            msg = f"Loaded config from {args.config}"
            logging.info(msg)
            if RICH_AVAILABLE:
                console.print(f"[green]✅ {msg}[/green]")
            else:
                print(f"✅ {msg}")
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            if RICH_AVAILABLE:
                console.print(f"[red]⚠️ Failed to load config: {e}. Using defaults.[/red]")
            else:
                print(f"⚠️ Failed to load config: {e}. Using defaults.")

    # Interactive input
    if not args.config:
        msg = "🎵 Quantum Love Rhythm Generator 🎵"
        if RICH_AVAILABLE:
            console.print(f"[bold magenta]{msg}[/bold magenta]")
        else:
            print(msg)
        print(f"Available styles: {', '.join(STYLE_CONFIGS.keys())}")
        print(f"Available instruments: {', '.join(AVAILABLE_INSTRUMENTS)}")
        print(f"Available note types: {', '.join(NOTE_TYPES.keys())}")
        print(f"Available time signatures: {', '.join(TIME_SIGNATURES)}")
        print(f"Available subdivisions: {', '.join(SUBDIVISIONS)}")

        def get_valid_input(prompt, default, validator, type_cast, error_msg="Invalid input. Please try again."):
            while True:
                value = input(f"{prompt} [{default}]: ").strip() or default
                try:
                    if validator(value):
                        return type_cast(value)
                    print(error_msg)
                except ValueError:
                    print(f"Invalid input. Please enter a valid value.")

        config["style"] = get_valid_input(
            "Choose a style",
            config["style"],
            lambda x: x in STYLE_CONFIGS,
            str,
            "Invalid style. Choose from: " + ", ".join(STYLE_CONFIGS.keys())
        )
        config["instruments"] = get_valid_input(
            "Enter instruments (comma-separated)",
            ",".join(config["instruments"]),
            lambda x: x.strip() and all(i.strip() in AVAILABLE_INSTRUMENTS for i in x.split(',')),
            lambda x: [i.strip() for i in x.split(',')],
            "Invalid instruments. Choose from: " + ", ".join(AVAILABLE_INSTRUMENTS)
        )
        config["bpm"] = get_valid_input(
            f"Enter BPM ({MIN_BPM}-{MAX_BPM})",
            config["bpm"],
            lambda x: MIN_BPM <= int(x) <= MAX_BPM,
            int,
            f"BPM must be between {MIN_BPM} and {MAX_BPM}."
        )
        config["note_type"] = get_valid_input(
            "Choose note type",
            config["note_type"],
            lambda x: x in NOTE_TYPES,
            str,
            "Invalid note type. Choose from: " + ", ".join(NOTE_TYPES.keys())
        )
        config["swing"] = get_valid_input(
            f"Enter swing percentage ({MIN_SWING}-{MAX_SWING})",
            config["swing"],
            lambda x: MIN_SWING <= int(x) <= MAX_SWING,
            int,
            f"Swing must be between {MIN_SWING} and {MAX_SWING}."
        )
        config["complexity"] = get_valid_input(
            "Choose complexity",
            config["complexity"],
            lambda x: x in COMPLEXITY_LEVELS,
            str,
            "Invalid complexity. Choose from: " + ", ".join(COMPLEXITY_LEVELS)
        )
        config["pattern_length"] = get_valid_input(
            "Enter pattern length (4-16)",
            config["pattern_length"],
            lambda x: 4 <= int(x) <= 16,
            int,
            "Pattern length must be between 4 and 16."
        )
        config["time_signature"] = get_valid_input(
            "Choose time signature",
            config["time_signature"],
            lambda x: x in TIME_SIGNATURES,
            str,
            "Invalid time signature. Choose from: " + ", ".join(TIME_SIGNATURES)
        )
        config["subdivision"] = get_valid_input(
            "Choose subdivision",
            config["subdivision"],
            lambda x: x in SUBDIVISIONS,
            str,
            "Invalid subdivision. Choose from: " + ", ".join(SUBDIVISIONS)
        )
        config["fill_frequency"] = get_valid_input(
            "Enter fill frequency (0.0-1.0)",
            config["fill_frequency"],
            lambda x: 0.0 <= float(x) <= 1.0,
            float,
            "Fill frequency must be between 0.0 and 1.0."
        )
        config["master_volume"] = get_valid_input(
            "Enter master volume (0-100)",
            config["master_volume"],
            lambda x: 0 <= int(x) <= 100,
            int,
            "Master volume must be between 0 and 100."
        )
        config["loop_repeats"] = get_valid_input(
            "Enter loop repeats (1-10)",
            config["loop_repeats"],
            lambda x: 1 <= int(x) <= 10,
            int,
            "Loop repeats must be between 1 and 10."
        )
        config["project_name"] = get_valid_input(
            "Enter project name",
            config["project_name"],
            lambda x: x.strip() and not any(c in x for c in r'<>:"/\|?*'),
            str,
            "Invalid project name. Avoid special characters like <>:\"/\\|?*"
        )
        config["volumes"] = {}
        config["pan_settings"] = {}
        for inst in config["instruments"]:
            config["volumes"][inst] = get_valid_input(
                f"Enter volume for {inst} (0-100)",
                config["volumes"].get(inst, DEFAULT_VOLUME),
                lambda x: 0 <= int(x) <= 100,
                int,
                "Volume must be between 0 and 100."
            )
            config["pan_settings"][inst] = get_valid_input(
                f"Enter pan for {inst} (-1.0 to 1.0)",
                config["pan_settings"].get(inst, 0),
                lambda x: -1.0 <= float(x) <= 1.0,
                float,
                "Pan must be between -1.0 and 1.0."
            )

    # Validate instruments
    config["instruments"] = [i for i in config["instruments"] if i in AVAILABLE_INSTRUMENTS]
    if not config["instruments"]:
        logging.warning("No valid instruments. Using default: kick, snare.")
        config["instruments"] = ["kick", "snare"]
        config["volumes"] = {inst: DEFAULT_VOLUME for inst in config["instruments"]}
        config["pan_settings"] = {inst: 0 for inst in config["instruments"]}
    msg = f"Selected instruments: {config['instruments']}"
    logging.info(msg)
    if RICH_AVAILABLE:
        console.print(f"[green]✅ {msg}[/green]")
    else:
        print(f"✅ {msg}")

    # Generate and export rhythm
    loop, stems, patterns = generate_rhythm(
        style=config["style"],
        instruments=config["instruments"],
        bpm=config["bpm"],
        note_type=config["note_type"],
        swing=config["swing"],
        complexity=config["complexity"],
        volumes=config["volumes"],
        pattern_length=config["pattern_length"],
        time_signature=config["time_signature"],
        subdivision=config["subdivision"],
        fill_frequency=config["fill_frequency"],
        master_volume=config["master_volume"],
        pan_settings=config["pan_settings"],
        loop_repeats=config["loop_repeats"],
        preview=args.preview
    )
    if len(loop) == 0:
        logging.error("Generated loop is empty. Check sample files and dependencies.")
        return
    export_rhythm(
        loop,
        stems,
        patterns,
        config["style"],
        config["bpm"],
        config["note_type"],
        config["pattern_length"],
        output_format=args.output_format,
        export_stems=args.export_stems,
        export_midi=args.export_midi,
        project_name=config["project_name"],
        loop_repeats=config["loop_repeats"],
        subdivision=config["subdivision"]
    )

if __name__ == '__main__':
    main()
