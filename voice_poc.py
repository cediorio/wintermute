#!/usr/bin/env python3
"""
Proof-of-concept for voice interaction using:
- sounddevice for audio I/O
- Moonshine AI for speech-to-text (STT)
- Kokoro for text-to-speech (TTS)

This is a simple test script to verify all components work together
before integrating into the Wintermute TUI.

Usage:
    python voice_poc.py

Requirements:
    pip install sounddevice numpy useful-moonshine-onnx kokoro soundfile
    apt-get install espeak-ng  # or brew install espeak on macOS
"""

import asyncio
import sys
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

try:
    import moonshine_onnx
except ImportError:
    print("ERROR: moonshine_onnx not installed")
    print("Install with: pip install useful-moonshine-onnx")
    sys.exit(1)

try:
    from kokoro import KPipeline
except ImportError:
    print("ERROR: kokoro not installed")
    print("Install with: pip install kokoro")
    sys.exit(1)


class VoiceInteractionPOC:
    """Simple proof-of-concept for voice interaction."""

    def __init__(
        self,
        samplerate: int = 16000,  # Moonshine prefers 16kHz
        channels: int = 1,
        blocksize: int = 1024,
    ):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.recording = False
        self.recorded_chunks = []

        # Initialize Kokoro TTS pipeline
        print("Initializing Kokoro TTS pipeline...")
        self.tts_pipeline = KPipeline(lang_code='a')  # 'a' = American English
        print("✓ Kokoro TTS initialized")

    def get_audio_devices(self):
        """List available audio devices."""
        print("\n=== Available Audio Devices ===")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"[{i}] {device['name']}")
            print(f"    Max input channels: {device['max_input_channels']}")
            print(f"    Max output channels: {device['max_output_channels']}")
            print(f"    Default samplerate: {device['default_samplerate']}")
        print()

    async def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """
        Record audio from microphone for specified duration.

        Args:
            duration: Recording duration in seconds

        Returns:
            NumPy array of audio samples
        """
        print(f"\n🎤 Recording for {duration} seconds...")
        print("   Speak now!")

        self.recorded_chunks = []
        self.recording = True

        # Calculate total frames needed
        total_frames = int(duration * self.samplerate)
        frames_recorded = 0

        # Setup async queue for audio data
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            if status:
                print(f"   Audio status: {status}")
            if self.recording:
                loop.call_soon_threadsafe(queue.put_nowait, indata.copy())

        # Start recording
        stream = sd.InputStream(
            callback=callback,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
        )

        with stream:
            while frames_recorded < total_frames:
                try:
                    chunk = await asyncio.wait_for(queue.get(), timeout=1.0)
                    self.recorded_chunks.append(chunk)
                    frames_recorded += len(chunk)

                    # Show progress
                    progress = frames_recorded / total_frames
                    bars = int(progress * 30)
                    print(f"\r   [{'=' * bars}{' ' * (30 - bars)}] {progress:.0%}", end="")

                except asyncio.TimeoutError:
                    print("\n   Warning: Audio timeout")
                    break

        print("\n✓ Recording complete")

        # Concatenate all chunks
        audio_data = np.concatenate(self.recorded_chunks, axis=0)
        return audio_data

    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio using Moonshine AI.

        Args:
            audio_data: NumPy array of audio samples

        Returns:
            Transcribed text
        """
        print("\n🧠 Transcribing with Moonshine AI...")

        # Moonshine expects audio in specific format
        # Save to temporary file (Moonshine works with file paths)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            # Write audio to temp file
            sf.write(tmp_path, audio_data, self.samplerate)

        try:
            # Transcribe using Moonshine
            # Returns list of transcriptions (one per segment)
            transcriptions = moonshine_onnx.transcribe(
                tmp_path,
                'moonshine/tiny'  # Use tiny model for speed
            )

            # Join all transcriptions
            text = ' '.join(transcriptions)
            print(f"✓ Transcription: \"{text}\"")
            return text

        finally:
            # Clean up temp file
            tmp_path.unlink()

    async def synthesize_speech(self, text: str) -> np.ndarray:
        """
        Synthesize speech using Kokoro TTS.

        Args:
            text: Text to synthesize

        Returns:
            NumPy array of audio samples at 24kHz (Kokoro's native rate)
        """
        print(f"\n🗣️  Synthesizing speech: \"{text}\"")

        # Generate speech using Kokoro
        # Kokoro returns generator of (graphemes, phonemes, audio) tuples
        generator = self.tts_pipeline(
            text,
            voice='af_heart',  # Female voice
            speed=1.0
        )

        # Kokoro generates in segments, collect them all
        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_segments.append(audio)

        # Concatenate all segments
        if audio_segments:
            full_audio = np.concatenate(audio_segments, axis=0)
            print(f"✓ Generated {len(full_audio)} samples at 24kHz")
            return full_audio
        else:
            print("⚠ No audio generated")
            return np.array([])

    async def play_audio(self, audio_data: np.ndarray, samplerate: int = 24000) -> None:
        """
        Play audio through speakers.

        Args:
            audio_data: NumPy array of audio samples
            samplerate: Sample rate of audio (Kokoro uses 24kHz)
        """
        print("\n🔊 Playing audio...")

        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        idx = 0

        def callback(outdata, frames, time_info, status):
            nonlocal idx
            if status:
                print(f"   Playback status: {status}")

            remainder = len(audio_data) - idx
            if remainder == 0:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop

            chunk_size = min(remainder, frames)
            # Kokoro outputs mono, expand to match channels if needed
            if audio_data.ndim == 1:
                outdata[:chunk_size] = audio_data[idx:idx + chunk_size].reshape(-1, 1)
            else:
                outdata[:chunk_size] = audio_data[idx:idx + chunk_size]

            if chunk_size < frames:
                outdata[chunk_size:] = 0
            idx += chunk_size

        stream = sd.OutputStream(
            callback=callback,
            channels=1,  # Mono output
            samplerate=samplerate,
            dtype=audio_data.dtype,
        )

        with stream:
            await event.wait()

        print("✓ Playback complete")


async def main():
    """Main proof-of-concept demonstration."""
    print("=" * 60)
    print("Voice Interaction Proof-of-Concept")
    print("Moonshine STT + Kokoro TTS + sounddevice")
    print("=" * 60)

    # Initialize
    poc = VoiceInteractionPOC()

    # Show available audio devices
    poc.get_audio_devices()

    # Test 1: Record and transcribe
    print("\n" + "=" * 60)
    print("TEST 1: Record speech and transcribe")
    print("=" * 60)

    try:
        audio_data = await poc.record_audio(duration=5.0)
        transcription = poc.transcribe_audio(audio_data)
    except Exception as e:
        print(f"❌ Error in recording/transcription: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 2: Synthesize and play response
    print("\n" + "=" * 60)
    print("TEST 2: Synthesize and play response")
    print("=" * 60)

    # Create a response based on transcription
    if transcription.strip():
        response = f"You said: {transcription}. This is a test of the Kokoro text to speech system."
    else:
        response = "I didn't catch that. Could you please repeat?"

    try:
        speech_audio = await poc.synthesize_speech(response)
        if len(speech_audio) > 0:
            await poc.play_audio(speech_audio, samplerate=24000)
    except Exception as e:
        print(f"❌ Error in synthesis/playback: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✓ Proof-of-concept complete!")
    print("=" * 60)
    print("\nAll components are working correctly:")
    print("  ✓ sounddevice - audio I/O")
    print("  ✓ Moonshine - speech-to-text")
    print("  ✓ Kokoro - text-to-speech")
    print("\nReady to integrate into Wintermute TUI!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
