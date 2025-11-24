# Voice Interaction Proof-of-Concept

This document explains how to test the voice interaction proof-of-concept (POC) that combines:
- **sounddevice** - Audio I/O
- **Moonshine AI** - Speech-to-Text (STT)
- **Kokoro** - Text-to-Speech (TTS)

## Prerequisites

### 1. Install espeak-ng

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install espeak-ng
```

**On macOS:**
```bash
brew install espeak-ng
```

**On Windows:**
Download and install from: https://github.com/espeak-ng/espeak-ng/releases

### 2. Install Python Dependencies

```bash
# Install voice interaction packages
pip install sounddevice numpy soundfile useful-moonshine-onnx kokoro

# Optional: Install with misaki language support
# pip install 'misaki[ja]'  # Japanese
# pip install 'misaki[zh]'  # Chinese
```

## Running the POC

### Basic Usage

```bash
python voice_poc.py
```

### What the POC Does

The script will:

1. **Initialize** Kokoro TTS pipeline
2. **List** all available audio devices on your system
3. **Test 1: Record and Transcribe**
   - Records 5 seconds of audio from your microphone
   - Shows a progress bar during recording
   - Transcribes the audio using Moonshine AI
   - Displays the transcription
4. **Test 2: Synthesize and Play**
   - Generates a response using your transcription
   - Synthesizes speech using Kokoro TTS
   - Plays the synthesized audio through your speakers

### Expected Output

```
============================================================
Voice Interaction Proof-of-Concept
Moonshine STT + Kokoro TTS + sounddevice
============================================================
Initializing Kokoro TTS pipeline...
✓ Kokoro TTS initialized

=== Available Audio Devices ===
[0] Built-in Microphone
    Max input channels: 2
    Max output channels: 0
    Default samplerate: 44100.0
[1] Built-in Output
    Max input channels: 0
    Max output channels: 2
    Default samplerate: 44100.0

============================================================
TEST 1: Record speech and transcribe
============================================================

🎤 Recording for 5.0 seconds...
   Speak now!
   [==============================] 100%
✓ Recording complete

🧠 Transcribing with Moonshine AI...
✓ Transcription: "Hello, this is a test"

============================================================
TEST 2: Synthesize and play response
============================================================

🗣️  Synthesizing speech: "You said: Hello, this is a test. This is a test of the Kokoro text to speech system."
✓ Generated 89472 samples at 24kHz

🔊 Playing audio...
✓ Playback complete

============================================================
✓ Proof-of-concept complete!
============================================================

All components are working correctly:
  ✓ sounddevice - audio I/O
  ✓ Moonshine - speech-to-text
  ✓ Kokoro - text-to-speech

Ready to integrate into Wintermute TUI!
```

## Troubleshooting

### Issue: No audio devices found
**Solution:** Make sure your microphone and speakers are properly connected and recognized by your OS.

### Issue: Import errors
**Solution:** Install missing dependencies:
```bash
pip install sounddevice numpy soundfile useful-moonshine-onnx kokoro
```

### Issue: espeak-ng not found
**Solution:** Install espeak-ng system package (see Prerequisites above).

### Issue: Poor transcription quality
**Solution:** 
- Speak clearly and close to the microphone
- Reduce background noise
- The POC uses the `tiny` Moonshine model for speed; you can try `base` for better accuracy

### Issue: Audio device errors on Linux
**Solution:** You may need to install additional audio libraries:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Issue: Playback stuttering
**Solution:** Try adjusting the blocksize parameter (default is 1024):
```python
poc = VoiceInteractionPOC(blocksize=2048)
```

## Customization

You can modify the POC script to test different configurations:

### Change Recording Duration
```python
audio_data = await poc.record_audio(duration=10.0)  # 10 seconds
```

### Use Different Moonshine Model
```python
# In transcribe_audio method, change:
transcriptions = moonshine_onnx.transcribe(
    tmp_path,
    'moonshine/base'  # Better accuracy, slower
)
```

### Use Different Kokoro Voice
```python
# In VoiceInteractionPOC.__init__, change:
generator = self.tts_pipeline(
    text,
    voice='af_sky',    # Try: af_heart, af_sky, am_adam, etc.
    speed=1.2          # Adjust speed (0.5 to 2.0)
)
```

Available Kokoro voices:
- `af_heart` - Female voice (warm)
- `af_sky` - Female voice (bright)
- `am_adam` - Male voice (deep)
- `am_michael` - Male voice (neutral)
- And more...

### Change Sample Rate
```python
poc = VoiceInteractionPOC(
    samplerate=22050,  # Higher quality for STT
    channels=1,
    blocksize=1024
)
```

## Next Steps

Once the POC works successfully:

1. ✅ Verify all components integrate correctly
2. Design the voice UI for Wintermute TUI
3. Create `AudioService` class following TDD approach
4. Create `VoiceClient` service for STT/TTS
5. Add voice interaction keybindings to Wintermute
6. Implement visual indicators (recording, speaking, etc.)

## Architecture Notes

The POC demonstrates the key integration patterns:

1. **Async Audio Recording**: Uses `asyncio.Queue` with `loop.call_soon_threadsafe()` to safely pass audio from the audio callback thread to the asyncio event loop.

2. **Non-blocking Playback**: Audio playback uses callbacks so it doesn't block the main thread/event loop.

3. **STT Integration**: Moonshine accepts file paths, so we use temporary files (in production, we could optimize this).

4. **TTS Integration**: Kokoro returns generators, allowing for streaming synthesis if needed.

These patterns will translate directly into the Wintermute TUI implementation with Textual.
