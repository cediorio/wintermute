#!/usr/bin/env python3
"""
Simple demo of Moonshine STT working with sounddevice.
This demonstrates the core voice input functionality.

Requirements:
    pip install sounddevice numpy useful-moonshine-onnx soundfile
"""

import asyncio
import sys
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import moonshine_onnx


async def record_audio(duration: float = 5.0, samplerate: int = 16000) -> np.ndarray:
    """Record audio from microphone."""
    print(f"\n🎤 Recording for {duration} seconds...")
    print("   Speak now!")
    
    recorded_chunks = []
    total_frames = int(duration * samplerate)
    frames_recorded = 0
    
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    
    def callback(indata, frames, time_info, status):
        if status:
            print(f"   Status: {status}")
        loop.call_soon_threadsafe(queue.put_nowait, indata.copy())
    
    stream = sd.InputStream(
        callback=callback,
        channels=1,
        samplerate=samplerate,
        blocksize=1024,
    )
    
    with stream:
        while frames_recorded < total_frames:
            try:
                chunk = await asyncio.wait_for(queue.get(), timeout=1.0)
                recorded_chunks.append(chunk)
                frames_recorded += len(chunk)
                
                # Progress bar
                progress = frames_recorded / total_frames
                bars = int(progress * 30)
                print(f"\r   [{'=' * bars}{' ' * (30 - bars)}] {progress:.0%}", end="")
                
            except asyncio.TimeoutError:
                break
    
    print("\n✓ Recording complete")
    return np.concatenate(recorded_chunks, axis=0)


def transcribe_audio(audio_data: np.ndarray, samplerate: int = 16000) -> str:
    """Transcribe audio using Moonshine AI."""
    print("\n🧠 Transcribing with Moonshine AI...")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        sf.write(tmp_path, audio_data, samplerate)
    
    try:
        transcriptions = moonshine_onnx.transcribe(tmp_path, 'moonshine/tiny')
        text = ' '.join(transcriptions)
        print(f"✓ Transcription: \"{text}\"")
        return text
    finally:
        tmp_path.unlink()


async def main():
    """Run the demo."""
    print("=" * 60)
    print("Moonshine STT Demo")
    print("Speech-to-Text with sounddevice")
    print("=" * 60)
    
    # Show available audio devices
    print("\n=== Available Audio Devices ===")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"[{i}] {device['name']} (input)")
    print()
    
    # Record and transcribe
    try:
        audio_data = await record_audio(duration=5.0)
        transcription = transcribe_audio(audio_data)
        
        print("\n" + "=" * 60)
        print("✓ Demo complete!")
        print("=" * 60)
        print(f"\nYou said: \"{transcription}\"")
        print("\nCore components working:")
        print("  ✓ sounddevice - non-blocking audio recording")
        print("  ✓ Moonshine - fast speech-to-text")
        print("\nThis proves the voice input pipeline is ready!")
        print("\nNote: Kokoro TTS requires additional setup.")
        print("      For now, STT is fully functional.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
