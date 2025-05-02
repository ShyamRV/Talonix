import random
import time
from mido import Message, MidiFile, MidiTrack
from midi2audio import FluidSynth

# Set your SoundFont file here
SOUNDFONT_PATH = "FluidR3_GM.sf2"

INSTRUMENTS = {
    "piano": 0,
    "guitar": 24,
    "bass": 32,
    "strings": 48,
    "synth": 80,
    "drums": None  # special case for drums
}

MAJOR_SCALES = {
    "C": ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    "D": ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
    "E": ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
    "F": ['F', 'G', 'A', 'A#', 'C', 'D', 'E'],
    "G": ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
    "A": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
    "B": ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#']
}

MINOR_SCALES = {
    "C": ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#'],
    "D": ['D', 'E', 'F', 'G', 'A', 'A#', 'C'],
    "E": ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
    "F": ['F', 'G', 'G#', 'A#', 'C', 'C#', 'D#'],
    "G": ['G', 'A', 'A#', 'C', 'D', 'D#', 'F'],
    "A": ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    "B": ['B', 'C#', 'D', 'E', 'F#', 'G', 'A']
}

NOTE_TO_MIDI = {
    "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65, "F#": 66,
    "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
}

def get_user_inputs():
    print("Available Instruments:", ', '.join(INSTRUMENTS.keys()))
    instrument = input("Choose instrument: ").lower()
    while instrument not in INSTRUMENTS:
        instrument = input("Invalid instrument. Try again: ").lower()

    key = input("Enter musical key (e.g., C, D, E): ").upper()
    while key not in MAJOR_SCALES:
        key = input("Invalid key. Try again: ").upper()

    scale_type = input("Major or Minor scale? ").lower()
    while scale_type not in ['major', 'minor']:
        scale_type = input("Invalid input. Enter 'major' or 'minor': ").lower()

    bpm = int(input("Enter BPM: "))
    duration = int(input("Duration in seconds: "))

    return instrument, key, scale_type, bpm, duration

def get_scale(key, scale_type):
    return MAJOR_SCALES[key] if scale_type == "major" else MINOR_SCALES[key]

def get_midi_note(note, octave=4):
    return NOTE_TO_MIDI[note] + (octave - 4) * 12

def generate_melody(instrument, key, scale_type, bpm, duration):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    is_drum = instrument == "drums"
    channel = 9 if is_drum else 0

    if not is_drum:
        track.append(Message('program_change', program=INSTRUMENTS[instrument], time=0, channel=channel))

    scale = get_scale(key, scale_type)
    beat_time = int(60000 / bpm)
    total_beats = (duration * 1000) // beat_time

    for _ in range(int(total_beats)):
        if is_drum:
            drum_note = random.choice([35, 36, 38, 40, 42, 46])  # kick, snare, hats
            velocity = random.randint(70, 110)
            track.append(Message('note_on', note=drum_note, velocity=velocity, time=0, channel=channel))
            track.append(Message('note_off', note=drum_note, velocity=velocity, time=beat_time, channel=channel))
        else:
            note_name = random.choice(scale)
            note_midi = get_midi_note(note_name, random.randint(3, 5))
            velocity = random.randint(60, 100)
            track.append(Message('note_on', note=note_midi, velocity=velocity, time=0, channel=channel))
            track.append(Message('note_off', note=note_midi, velocity=velocity, time=beat_time, channel=channel))

    return mid

def save_as_wav(midi_file, wav_file):
    fs = FluidSynth(SOUNDFONT_PATH)
    fs.midi_to_audio(midi_file, wav_file)
    print(f"✅ WAV file saved: {wav_file}")

if __name__ == "__main__":
    instrument, key, scale_type, bpm, duration = get_user_inputs()
    midi_data = generate_melody(instrument, key, scale_type, bpm, duration)

    filename_base = f"{instrument}_{int(time.time())}"
    midi_filename = f"{filename_base}.mid"
    wav_filename = f"{filename_base}.wav"

    midi_data.save(midi_filename)
    save_as_wav(midi_filename, wav_filename)
