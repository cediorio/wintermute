"""Audio I/O service using sounddevice for non-blocking audio operations."""

import asyncio
from typing import AsyncGenerator, Optional

import numpy as np
import sounddevice as sd


class AudioService:
    """
    Non-blocking audio service for recording and playback.

    Integrates seamlessly with Textual's async architecture using
    the loop.call_soon_threadsafe() pattern.
    """

    def __init__(
        self,
        samplerate: int = 16000,
        channels: int = 1,
        blocksize: int = 1024,
    ):
        """
        Initialize AudioService.

        Args:
            samplerate: Sample rate for audio I/O (Hz).
            channels: Number of audio channels (1=mono, 2=stereo).
            blocksize: Size of audio blocks for processing.
        """
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream: Optional[sd.InputStream] = None
        self._queue: Optional[asyncio.Queue] = None

    async def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """
        Record audio from microphone for specified duration.

        Args:
            duration: Recording duration in seconds.

        Returns:
            NumPy array of audio samples.
        """
        recorded_chunks = []
        total_frames = int(duration * self.samplerate)
        frames_recorded = 0

        # Setup async queue for audio data
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            # Safely pass data from audio thread to async event loop
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
                    recorded_chunks.append(chunk)
                    frames_recorded += len(chunk)
                except asyncio.TimeoutError:
                    break

        # Concatenate all chunks
        audio_data = np.concatenate(recorded_chunks, axis=0)
        return audio_data

    async def record_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """
        Async generator that yields audio blocks from microphone.

        Usage:
            async for audio_block in audio_service.record_stream():
                # Process audio without blocking UI
                process(audio_block)

        Yields:
            NumPy arrays of audio samples.
        """
        self._queue = asyncio.Queue(maxsize=10)
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            try:
                loop.call_soon_threadsafe(self._queue.put_nowait, indata.copy())
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

    async def play_audio(self, audio_data: np.ndarray, samplerate: int = 24000) -> None:
        """
        Play audio data without blocking.

        Args:
            audio_data: NumPy array of audio samples.
            samplerate: Sample rate of audio (Kokoro uses 24kHz).
        """
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        idx = 0

        def callback(outdata, frames, time_info, status):
            nonlocal idx
            if status:
                print(f"Playback status: {status}")

            remainder = len(audio_data) - idx
            if remainder == 0:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop

            chunk_size = min(remainder, frames)
            # Handle mono/stereo output
            if audio_data.ndim == 1:
                outdata[:chunk_size] = audio_data[idx : idx + chunk_size].reshape(-1, 1)
            else:
                outdata[:chunk_size] = audio_data[idx : idx + chunk_size]

            if chunk_size < frames:
                outdata[chunk_size:] = 0
            idx += chunk_size

        stream = sd.OutputStream(
            callback=callback,
            channels=self.channels,
            samplerate=samplerate,
            dtype=audio_data.dtype,
        )

        with stream:
            await event.wait()

    def get_devices(self) -> list:
        """
        Get list of available audio devices.

        Returns:
            List of device dictionaries.
        """
        return sd.query_devices()

    def set_device(self, device_id: int) -> None:
        """
        Set default audio device.

        Args:
            device_id: ID of the device to use.
        """
        sd.default.device = device_id
