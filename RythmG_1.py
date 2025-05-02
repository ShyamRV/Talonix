import os
import time
import random
import sys
import gc
import argparse

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy not installed. Synthetic tones disabled. Install with: pip install numpy")

try:
    from pydub import AudioSegment
except ImportError:
    print("⚠️ pydub not installed. Install with: pip install pydub")
    sys.exit(1)

try:
    import simpleaudio as sa
except ImportError:
    print("⚠️ simpleaudio not installed. Install with: pip install simpleaudio")
    sys.exit(1)

# Map styles to tempos (beats per minute) and patterns
STYLE_TEMPOS = {
    'hiphop': 85,
    'lofi': 70,
    'edm': 128,
    'pop': 120
}

# Define style-specific rhythm patterns (1 = play, 0 = rest)
STYLE_PATTERNS = {
    'hiphop': {
        'drums': [1, 0, 1, 0, 1, 0, 1, 0],
        'bass': [1, 0, 0, 0, 1, 0, 0, 0],
        'synth': [0, 1, 0, 1, 0, 1, 0, 1],
        'guitar': [0, 0, 1, 0, 0, 0, 1, 0]
    },
    'lofi': {
        'drums': [1, 0, 0, 0, 1, 0, 0, 0],
        'bass': [1, 0, 0, 0, 0, 0, 0, 0],
        'synth': [1, 0, 1, 0, 1, 0, 1, 0],
        'guitar': [0, 0, 0, 0, 1, 0, 0, 0]
    },
    'edm': {
        'drums': [1, 0, 1, 0, 1, 0, 1, 0],
        'bass': [1, 1, 1, 1, 1, 1, 1, 1],
        'synth': [1, 0, 0, 0, 1, 0, 0, 0],
        'guitar': [0, 0, 0, 0, 0, 0, 0, 0]
    },
    'pop': {
        'drums': [1, 0, 1, 0, 1, 0, 1, 0],
        'bass': [1, 0, 0, 0, 1, 0, 0, 0],
        'synth': [1, 0, 1, 0, 1, 0, 1, 0],
        'guitar': [0, 1, 0, 1, 0, 1, 0, 1]
    }
}

# Available instruments
AVAILABLE_INSTRUMENTS = ['drums', 'bass', 'synth', 'guitar']

# Generate a synthetic tone as a fallback
def generate_synthetic_tone(frequency=440, duration_ms=200):
    if not NUMPY_AVAILABLE:
        print("⚠️ Cannot generate synthetic tone: NumPy not installed.")
        return AudioSegment.silent(duration=duration_ms)
    sample_rate = 44100
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = np.sin(frequency * t * 2 * np.pi) * 32767
    audio = np.int16(tone).tobytes()
    return AudioSegment(audio, frame_rate=sample_rate, sample_width=2, channels=1)

# Load samples for a given instrument
def load_samples(instrument):
    folder_path = os.path.join("samples", instrument)
    print(f"📂 Loading samples for '{instrument}' from {folder_path}...")
    if not os.path.exists(folder_path):
        print(f"⚠️ No samples directory for '{instrument}'. Using synthetic tone.")
        return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]
    samples = []
    for file in os.listdir(folder_path):
        if file.endswith('.wav'):
            sample_path = os.path.join(folder_path, file)
            try:
                sample = AudioSegment.from_wav(sample_path)
                # Normalize sample properties
                try:
                    sample = sample.set_channels(1).set_frame_rate(44100).set_sample_width(2)
                except Exception as e:
                    print(f"⚠️ Failed to normalize {sample_path}: {e}. Skipping sample.")
                    continue
                samples.append(sample)
                print(f"✅ Loaded sample: {file} ({len(sample)}ms, {sample.frame_rate}Hz, {sample.channels}ch)")
            except Exception as e:
                print(f"⚠️ Failed to load {sample_path}: {e}")
    if not samples:
        print(f"⚠️ No valid samples for '{instrument}'. Using synthetic tone.")
        return [generate_synthetic_tone(frequency=200 + 100 * AVAILABLE_INSTRUMENTS.index(instrument))]
    return samples

# Randomly choose a sample from the list
def choose_sample(samples):
    return random.choice(samples) if samples else AudioSegment.silent(duration=200)

# Play a short audio segment (for preview)
def play_preview(audio_segment):
    try:
        if len(audio_segment) == 0:
            print("⚠️ Empty audio segment. Skipping preview.")
            return
        # Re-normalize to ensure compatibility
        audio_segment = audio_segment.set_channels(1).set_frame_rate(44100).set_sample_width(2)
        print(f"🎵 Playing preview (duration: {len(audio_segment)}ms, channels: {audio_segment.channels}, sample_rate: {audio_segment.frame_rate}, raw_data: {len(audio_segment.raw_data)} bytes)")
        play_obj = sa.play_buffer(
            audio_segment.raw_data,
            num_channels=audio_segment.channels,
            bytes_per_sample=audio_segment.sample_width,
            sample_rate=audio_segment.frame_rate
        )
        play_obj.wait_done()
        play_obj.stop()
        del play_obj
        gc.collect()
        print("✅ Preview completed.")
    except Exception as e:
        print(f"⚠️ Preview failed: {e}. Continuing without preview.")

# Generate the rhythm loop
def generate_rhythm(style, instruments, randomize=False, preview=False):
    print(f"\n🎶 Generating rhythm | Style: {style} | Instruments: {instruments} | Randomize: {randomize}")

    # Validate style
    if style not in STYLE_TEMPOS:
        print(f"⚠️ Invalid style '{style}'. Defaulting to 'pop'.")
        style = 'pop'

    # Tempo & Beat
    tempo = STYLE_TEMPOS[style]
    beat_duration_ms = int(60000 / tempo)
    print(f"🎛️ Tempo set at {tempo} BPM | Beat duration: {beat_duration_ms}ms")

    # Get style-specific pattern
    pattern_length = 8
    instrument_patterns = STYLE_PATTERNS[style]
    print(f"📋 Base pattern for {style}: {instrument_patterns}")
    if randomize:
        instrument_patterns = {
            inst: [random.choice([0, 1]) if random.random() < 0.7 else pattern[i]
                   for i in range(pattern_length)]
            for inst, pattern in instrument_patterns.items()
        }
        # Ensure at least one drum hit to avoid silent loop
        if 'drums' in instruments:
            instrument_patterns['drums'][0] = 1
        print(f"📋 Randomized pattern: {instrument_patterns}")

    # Load samples
    instrument_samples = {}
    for inst in instruments:
        samples = load_samples(inst)
        if samples:
            instrument_samples[inst] = samples
        else:
            print(f"⚠️ No samples for '{inst}'. Skipping instrument.")

    if not instrument_samples:
        print("⚠️ No valid instruments with samples. Generating silent loop.")
        return AudioSegment.silent(duration=pattern_length * beat_duration_ms)

    # Create the rhythm loop
    beat_layers = []
    for beat_idx in range(pattern_length):
        beat_layer = AudioSegment.silent(duration=beat_duration_ms).set_channels(1).set_frame_rate(44100).set_sample_width(2)
        has_content = False
        for instrument in instrument_samples:
            if instrument in instrument_patterns and instrument_patterns[instrument][beat_idx]:
                sample = choose_sample(instrument_samples[instrument])
                print(f"🥁 Adding {instrument} to beat {beat_idx + 1} (sample: {len(sample)}ms)")
                if len(sample) < beat_duration_ms:
                    sample = sample + AudioSegment.silent(duration=beat_duration_ms - len(sample))
                elif len(sample) > beat_duration_ms:
                    sample = sample[:beat_duration_ms]
                try:
                    beat_layer = beat_layer.overlay(sample)
                    has_content = True
                except Exception as e:
                    print(f"⚠️ Failed to overlay {instrument} sample: {e}. Skipping.")
        # Re-normalize beat_layer
        try:
            beat_layer = beat_layer.set_channels(1).set_frame_rate(44100).set_sample_width(2)
            print(f"🔊 Beat {beat_idx + 1} duration: {len(beat_layer)}ms, has_content: {has_content}, raw_data: {len(beat_layer.raw_data)} bytes")
        except Exception as e:
            print(f"⚠️ Failed to normalize beat {beat_idx + 1}: {e}. Using silent beat.")
            beat_layer = AudioSegment.silent(duration=beat_duration_ms).set_channels(1).set_frame_rate(44100).set_sample_width(2)
            has_content = False
        if preview and has_content:
            print(f"🔍 Previewing beat {beat_idx + 1}...")
            print(f"📊 Pre-preview beat_layer raw_data: {len(beat_layer.raw_data)} bytes")
            play_preview(beat_layer)
            print(f"📊 Post-preview beat_layer raw_data: {len(beat_layer.raw_data)} bytes")
        try:
            beat_layers.append(beat_layer)
            print(f"✅ Stored beat {beat_idx + 1} for concatenation")
        except Exception as e:
            print(f"⚠️ Failed to store beat {beat_idx + 1}: {e}. Using silent beat.")
            beat_layers.append(AudioSegment.silent(duration=beat_duration_ms).set_channels(1).set_frame_rate(44100).set_sample_width(2))

    # Concatenate all beat layers
    try:
        loop = AudioSegment.silent(duration=0).set_channels(1).set_frame_rate(44100).set_sample_width(2)
        for idx, beat_layer in enumerate(beat_layers, 1):
            loop = loop + beat_layer
            print(f"✅ Appended beat {idx} to loop (loop duration: {len(loop)}ms)")
        print(f"✅ Generated loop duration: {len(loop)}ms")
    except Exception as e:
        print(f"⚠️ Failed to concatenate loop: {e}. Generating partial loop.")
        loop = AudioSegment.silent(duration=pattern_length * beat_duration_ms).set_channels(1).set_frame_rate(44100).set_sample_width(2)
        for idx, beat_layer in enumerate(beat_layers, 1):
            try:
                loop = loop + beat_layer
                print(f"✅ Appended beat {idx} to partial loop (loop duration: {len(loop)}ms)")
            except:
                loop = loop + AudioSegment.silent(duration=beat_duration_ms).set_channels(1).set_frame_rate(44100).set_sample_width(2)
                print(f"⚠️ Skipped beat {idx} in partial loop")
        print(f"✅ Generated partial loop duration: {len(loop)}ms")

    return loop

# Export and play the final rhythm
def export_and_play(loop, style, preview=False):
    timestamp = int(time.time())
    output_filename = f"rhythm_{style}_{timestamp}.wav"
    try:
        loop = loop.set_channels(1).set_frame_rate(44100).set_sample_width(2)
        loop.export(output_filename, format="wav")
        print(f"\n✅ Rhythm exported as: {output_filename}")
    except Exception as e:
        print(f"⚠️ Export failed: {e}. Check if FFmpeg is installed.")
        return

    if preview:
        print("🔊 Playing final rhythm...")
        try:
            play_obj = sa.play_buffer(
                loop.raw_data,
                num_channels=loop.channels,
                bytes_per_sample=loop.sample_width,
                sample_rate=loop.frame_rate
            )
            play_obj.wait_done()
            play_obj.stop()
            del play_obj
            gc.collect()
            print("✅ Final playback completed.")
        except Exception as e:
            print(f"⚠️ Playback failed: {e}. WAV file is still available.")

# Main interactive function
def main():
    parser = argparse.ArgumentParser(description="Rhythm & Pattern Generator")
    parser.add_argument('--preview', action='store_true', help="Enable beat and final rhythm previews")
    args = parser.parse_args()

    print("🎵 Welcome to the Ultimate Rhythm & Pattern Generator 🎵")
    print("Available styles:", ", ".join(STYLE_TEMPOS.keys()))
    print("Available instruments:", ", ".join(AVAILABLE_INSTRUMENTS))

    style = input("Choose a style (pop/hiphop/lofi/edm): ").lower().strip()
    instr_input = input("Enter instruments (comma-separated, e.g., drums, guitar): ").lower().strip()
    instruments = [i.strip() for i in instr_input.split(',') if i.strip()]
    valid_instruments = [i for i in instruments if i in AVAILABLE_INSTRUMENTS]
    if not valid_instruments:
        print("⚠️ No valid instruments selected. Using default: drums.")
        valid_instruments = ['drums']
    else:
        print(f"✅ Selected instruments: {valid_instruments}")

    randomize = input("Randomize beat drops and patterns? (y/n): ").lower().strip() == 'y'
    rhythm_loop = generate_rhythm(style, valid_instruments, randomize, preview=args.preview)
    if len(rhythm_loop) == 0:
        print("⚠️ Generated loop is empty. Check sample files or dependencies.")
        return
    export_and_play(rhythm_loop, style, preview=args.preview)

if __name__ == '__main__':
    main()