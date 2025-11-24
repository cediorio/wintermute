# Python Audio I/O Libraries for Asyncio-Based TUI Applications

## Executive Summary

**Recommended Library: `sounddevice`**

For asyncio-based TUI frameworks like Textual, **`sounddevice`** is the clear winner. It has native asyncio support with documented examples, uses callback-based architecture that integrates well with event loops, and is actively maintained.

---

## Library Comparison

### 1. sounddevice ⭐ RECOMMENDED

**Overview:**
- Python bindings for PortAudio library
- Modern, actively maintained (last update 2024)
- Built-in asyncio support with official examples
- Works with NumPy for audio data

**Async/Await Compatibility:** ✅ EXCELLENT
- Native asyncio support with `asyncio.Queue` integration
- Official examples: `asyncio_coroutines.py` and `asyncio_generators.py`
- Uses callbacks that communicate via `loop.call_soon_threadsafe()`
- Can create async generators for streaming audio blocks

**Real-time Microphone Capture:** ✅ EXCELLENT
- `sd.InputStream` with callback-based architecture
- Non-blocking by design
- Low latency support

**Audio Playback Capabilities:** ✅ EXCELLENT
- `sd.OutputStream` for playback
- Supports simultaneous record/playback with `sd.Stream`
- Multiple audio formats via PortAudio

**Thread-Safety with Async Event Loops:** ✅ EXCELLENT
- Explicitly designed for this use case
- Callbacks run in separate threads
- Uses `loop.call_soon_threadsafe()` to safely communicate with asyncio event loop
- Proven pattern in official examples

**Installation:**
```bash
pip install sounddevice numpy
```

**Code Example - Non-blocking Microphone Recording:**
```python
import asyncio
import numpy as np
import sounddevice as sd

async def inputstream_generator(channels=1, **kwargs):
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

    stream = sd.InputStream(callback=callback, channels=channels, **kwargs)
    with stream:
        while True:
            indata, status = await q_in.get()
            yield indata, status

# Usage in Textual or other async app:
async def process_audio():
    async for audio_block, status in inputstream_generator(blocksize=1024):
        # Process audio block without blocking the UI
        rms = np.sqrt(np.mean(audio_block**2))
        print(f"Audio level: {rms}")
```

**Code Example - Non-blocking Audio Playback:**
```python
async def play_buffer(buffer, **kwargs):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        valid_frames = frame_count if remainder >= frame_count else remainder
        outdata[:valid_frames] = buffer[idx:idx + valid_frames]
        outdata[valid_frames:] = 0
        idx += valid_frames

    stream = sd.OutputStream(callback=callback, dtype=buffer.dtype,
                             channels=buffer.shape[1], **kwargs)
    with stream:
        await event.wait()

# Usage:
async def main():
    # Generate audio or load from file
    audio_data = np.sin(2 * np.pi * 440 * np.arange(44100) / 44100).reshape(-1, 1)
    await play_buffer(audio_data)
```

**Integration with Textual Example:**
```python
from textual.app import App, ComposeResult
from textual.widgets import Static
import asyncio
import sounddevice as sd

class AudioApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Audio Level: 0.0", id="level")
    
    async def on_mount(self) -> None:
        # Start audio processing in background
        asyncio.create_task(self.monitor_audio())
    
    async def monitor_audio(self):
        async for audio_block, status in inputstream_generator(blocksize=1024):
            rms = np.sqrt(np.mean(audio_block**2))
            self.query_one("#level", Static).update(f"Audio Level: {rms:.3f}")
```

**Pros:**
- ✅ Official asyncio examples and documentation
- ✅ Clean API with async/await patterns
- ✅ Well-established callback mechanism
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Active community and maintenance
- ✅ Low latency for real-time applications
- ✅ Works seamlessly with NumPy
- ✅ Proven in production applications

**Cons:**
- ⚠️ Requires NumPy (but this is likely already a dependency)
- ⚠️ Callback-based approach requires understanding of threading model
- ⚠️ Some platform-specific audio driver issues (documented in issues)

---

### 2. PyAudio

**Overview:**
- Python bindings for PortAudio (same underlying library as sounddevice)
- Older, more established library
- Last major update: 2017 (less active maintenance)

**Async/Await Compatibility:** ⚠️ POOR
- No native asyncio support
- Blocking API by default
- Callback mode exists but not designed for asyncio
- Would require manual threading/event loop integration

**Real-time Microphone Capture:** ✅ GOOD
- Callback mode available
- Blocking mode also available
- Proven reliability

**Audio Playback Capabilities:** ✅ GOOD
- Supports various formats via PortAudio
- Both blocking and callback modes

**Thread-Safety with Async Event Loops:** ⚠️ POOR
- Not designed for asyncio
- Manual integration required
- Callbacks run in separate threads without asyncio integration helpers

**Installation:**
```bash
pip install pyaudio
```

**Code Example (Manual Integration Required):**
```python
import asyncio
import pyaudio

# Would require manual threading integration
def callback(in_data, frame_count, time_info, status):
    # This runs in a separate thread
    # Need to manually use loop.call_soon_threadsafe()
    # No built-in pattern like sounddevice
    pass
```

**Pros:**
- ✅ Very stable and battle-tested
- ✅ Extensive documentation
- ✅ Wide platform support

**Cons:**
- ❌ No asyncio support out of the box
- ❌ Less active development
- ❌ Would require significant custom integration code
- ❌ Older API design

---

### 3. python-soundfile (soundfile)

**Overview:**
- Library for reading/writing audio files (not for real-time I/O)
- Based on libsndfile
- Uses CFFI and NumPy

**Async/Await Compatibility:** ❌ NOT APPLICABLE
- File I/O library, not for streams
- Could use with asyncio file operations
- But not designed for real-time audio

**Real-time Microphone Capture:** ❌ NO
- Not designed for this purpose
- File-based I/O only

**Audio Playback Capabilities:** ❌ NO
- Can read/write files but not play them
- Would need another library (like sounddevice) for playback

**Thread-Safety with Async Event Loops:** ⚠️ LIMITED
- File I/O can be made async
- But not relevant for real-time audio

**Installation:**
```bash
pip install soundfile
```

**Use Case:**
```python
import soundfile as sf

# Read audio file
data, samplerate = sf.read('audio.wav')

# Write audio file
sf.write('output.flac', data, samplerate)
```

**Pros:**
- ✅ Excellent for file I/O
- ✅ Supports many formats (WAV, FLAC, OGG, etc.)
- ✅ Clean API

**Cons:**
- ❌ Not for real-time streaming
- ❌ No microphone/speaker access
- ❌ Would need to combine with sounddevice for real-time use

**Note:** `soundfile` is often used **together** with `sounddevice`:
```python
import sounddevice as sd
import soundfile as sf

# Read file with soundfile
data, samplerate = sf.read('input.wav')

# Play with sounddevice
sd.play(data, samplerate)
sd.wait()
```

---

## Recommendation Summary

### For Wintermute TUI Application:

**Primary Library: `sounddevice`**
- Use for all real-time audio I/O (microphone, playback)
- Has proven asyncio integration patterns
- Non-blocking by design
- Perfect fit for Textual's async architecture

**Secondary Library: `soundfile` (optional)**
- Use only if you need to read/write audio files
- Complements sounddevice nicely
- Not required for basic audio capture/playback

**Avoid: `pyaudio`**
- No asyncio support
- Would require extensive custom integration
- Older codebase with less active development

---

## Integration Best Practices

### 1. Use Callbacks with asyncio.Queue Pattern
```python
async def audio_stream_generator(channels=1, blocksize=1024):
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    
    def callback(indata, frames, time, status):
        # Called from audio thread
        loop.call_soon_threadsafe(q.put_nowait, indata.copy())
    
    stream = sd.InputStream(
        callback=callback,
        channels=channels,
        blocksize=blocksize
    )
    
    with stream:
        while True:
            data = await q.get()
            yield data
```

### 2. Handle Cleanup Properly
```python
class AudioManager:
    def __init__(self):
        self.stream = None
        self.running = False
    
    async def start(self):
        self.running = True
        # ... start stream
    
    async def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
```

### 3. Use Background Tasks in Textual
```python
class MyApp(App):
    async def on_mount(self):
        # Start audio processing in background
        self.audio_task = asyncio.create_task(self.process_audio())
    
    async def on_unmount(self):
        # Cancel task on shutdown
        if hasattr(self, 'audio_task'):
            self.audio_task.cancel()
            try:
                await self.audio_task
            except asyncio.CancelledError:
                pass
```

### 4. Error Handling
```python
async def safe_audio_stream():
    try:
        async for audio_block, status in inputstream_generator():
            if status:
                print(f"Audio status: {status}")
            # Process audio
    except Exception as e:
        print(f"Audio error: {e}")
        # Attempt recovery or notify user
```

---

## Potential Issues to Watch Out For

### 1. Audio Buffer Underruns/Overruns
**Problem:** If processing takes too long, audio may glitch
**Solution:** 
- Use appropriate blocksize (1024-2048 frames typical)
- Keep processing minimal in callback
- Offload heavy processing to separate tasks

### 2. Thread Safety
**Problem:** Callbacks run in audio thread, not main asyncio thread
**Solution:** 
- Always use `loop.call_soon_threadsafe()`
- Never access UI directly from callback
- Use queues to pass data to main thread

### 3. Resource Cleanup
**Problem:** Streams may not close properly on crashes
**Solution:**
- Use context managers (`with` statements)
- Implement proper shutdown in app lifecycle
- Handle cancellation in tasks

### 4. Platform-Specific Issues
**Problem:** Different audio backends on different platforms
**Solution:**
- Test on all target platforms
- Handle device selection gracefully
- Provide fallback options
- Check issues on GitHub for known platform problems

### 5. Latency Considerations
**Problem:** Too much latency for real-time applications
**Solution:**
- Adjust blocksize (smaller = lower latency, more CPU)
- Set appropriate `latency` parameter
- Use 'low' or 'high' latency hints: `sd.default.latency = 'low'`

---

## Example Implementation for Wintermute

```python
# wintermute/services/audio_service.py

import asyncio
import numpy as np
import sounddevice as sd
from typing import AsyncGenerator, Optional

class AudioService:
    """
    Non-blocking audio service for Wintermute TUI.
    Integrates seamlessly with Textual's async architecture.
    """
    
    def __init__(
        self,
        samplerate: int = 16000,  # Good for speech
        channels: int = 1,
        blocksize: int = 1024,
    ):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream: Optional[sd.InputStream] = None
        self._queue: Optional[asyncio.Queue] = None
    
    async def record_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """
        Async generator that yields audio blocks from microphone.
        
        Usage:
            async for audio_block in audio_service.record_stream():
                # Process audio without blocking UI
                process(audio_block)
        """
        self._queue = asyncio.Queue(maxsize=10)
        loop = asyncio.get_event_loop()
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            try:
                loop.call_soon_threadsafe(
                    self._queue.put_nowait,
                    indata.copy()
                )
            except asyncio.QueueFull:
                # Drop frame if queue is full
                pass
        
        self.stream = sd.InputStream(
            callback=callback,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
        )
        
        try:
            with self.stream:
                while True:
                    audio_block = await self._queue.get()
                    yield audio_block
        finally:
            self.stream = None
            self._queue = None
    
    async def play_audio(self, audio_data: np.ndarray) -> None:
        """
        Play audio data without blocking.
        
        Args:
            audio_data: NumPy array of audio samples
        """
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        idx = 0
        
        def callback(outdata, frames, time, status):
            nonlocal idx
            if status:
                print(f"Playback status: {status}")
            
            remainder = len(audio_data) - idx
            if remainder == 0:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop
            
            chunk = min(remainder, frames)
            outdata[:chunk] = audio_data[idx:idx + chunk].reshape(-1, self.channels)
            if chunk < frames:
                outdata[chunk:] = 0
            idx += chunk
        
        stream = sd.OutputStream(
            callback=callback,
            channels=self.channels,
            samplerate=self.samplerate,
            dtype=audio_data.dtype,
        )
        
        with stream:
            await event.wait()
    
    def get_devices(self) -> list:
        """Get list of available audio devices."""
        return sd.query_devices()
    
    def set_device(self, device_id: int) -> None:
        """Set default audio device."""
        sd.default.device = device_id


# Example usage in Textual app:

from textual.app import App
from textual.widgets import Static

class WintermuteApp(App):
    def compose(self):
        yield Static("Audio Level: 0.0", id="level")
    
    async def on_mount(self):
        self.audio_service = AudioService()
        self.audio_task = asyncio.create_task(self.monitor_audio())
    
    async def monitor_audio(self):
        try:
            async for audio_block in self.audio_service.record_stream():
                # Calculate RMS level
                rms = np.sqrt(np.mean(audio_block ** 2))
                
                # Update UI (Textual handles thread safety)
                self.query_one("#level", Static).update(
                    f"Audio Level: {rms:.3f}"
                )
        except asyncio.CancelledError:
            pass  # Clean shutdown
    
    async def on_unmount(self):
        if hasattr(self, 'audio_task'):
            self.audio_task.cancel()
            try:
                await self.audio_task
            except asyncio.CancelledError:
                pass
```

---

## Additional Resources

### sounddevice Documentation
- Main docs: https://python-sounddevice.readthedocs.io/
- Asyncio examples: https://python-sounddevice.readthedocs.io/en/latest/examples.html#using-a-stream-in-an-asyncio-coroutine
- GitHub: https://github.com/spatialaudio/python-sounddevice

### Community Discussions
- GitHub Issues with asyncio tag: Multiple users successfully using sounddevice with asyncio
- Active community with responsive maintainers
- Regular updates and bug fixes

### Related Libraries
- PortAudio: http://www.portaudio.com/ (underlying C library)
- NumPy: https://numpy.org/ (required for audio data handling)
- Textual: https://textual.textualize.io/ (asyncio-based TUI framework)

---

## Conclusion

For building audio features into Wintermute (or any asyncio-based TUI application), **sounddevice is the clear choice**. It provides:

1. ✅ Native asyncio integration with proven patterns
2. ✅ Non-blocking architecture perfect for TUI apps
3. ✅ Active maintenance and community support
4. ✅ Official examples demonstrating asyncio usage
5. ✅ Low latency for real-time applications
6. ✅ Clean, modern API

The library is specifically designed for the exact use case Wintermute requires: real-time audio I/O in an async Python application without blocking the UI thread.

**Do NOT use:**
- PyAudio: No asyncio support, would require extensive custom code
- soundfile: Not designed for real-time streaming (file I/O only)

**Optional complement:**
- soundfile: If you need to read/write audio files in addition to real-time I/O
