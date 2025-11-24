"""Tests for AudioService."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from wintermute.services.audio_service import AudioService


class TestAudioService:
    """Test suite for AudioService."""

    @pytest.fixture
    def audio_service(self) -> AudioService:
        """Create an AudioService instance for testing."""
        return AudioService(samplerate=16000, channels=1, blocksize=1024)

    def test_initialization(self, audio_service: AudioService) -> None:
        """Test AudioService initializes with correct parameters."""
        assert audio_service.samplerate == 16000
        assert audio_service.channels == 1
        assert audio_service.blocksize == 1024

    @pytest.mark.asyncio
    async def test_record_audio_returns_numpy_array(self, audio_service: AudioService) -> None:
        """Test record_audio returns a numpy array of audio samples."""
        # Mock sounddevice.InputStream
        mock_audio_data = np.random.rand(16000, 1).astype(np.float32)

        with patch("wintermute.services.audio_service.sd.InputStream") as mock_stream:
            # Setup mock to simulate audio recording
            mock_stream_instance = MagicMock()
            mock_stream.return_value.__enter__.return_value = mock_stream_instance

            # Mock the callback to provide audio data
            def mock_callback(callback, **kwargs):
                # Simulate providing audio chunks
                loop = asyncio.get_event_loop()
                for i in range(0, len(mock_audio_data), 1024):
                    chunk = mock_audio_data[i : i + 1024]
                    loop.call_soon_threadsafe(lambda c=chunk: callback(c, len(c), None, None))
                return mock_stream_instance

            mock_stream.side_effect = mock_callback

            # Record for 1 second
            audio = await audio_service.record_audio(duration=1.0)

            assert isinstance(audio, np.ndarray)
            assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_play_audio_with_valid_data(self, audio_service: AudioService) -> None:
        """Test play_audio successfully plays audio data."""
        audio_data = np.random.rand(24000).astype(np.float32)

        with patch("wintermute.services.audio_service.sd.OutputStream") as mock_stream:
            mock_stream_instance = MagicMock()
            mock_stream.return_value.__enter__.return_value = mock_stream_instance

            # Should complete without error
            await audio_service.play_audio(audio_data, samplerate=24000)

            # Verify OutputStream was called
            mock_stream.assert_called_once()

    def test_get_devices_returns_list(self, audio_service: AudioService) -> None:
        """Test get_devices returns a list of audio devices."""
        with patch("wintermute.services.audio_service.sd.query_devices") as mock_query:
            mock_query.return_value = [
                {"name": "Device 1", "max_input_channels": 2},
                {"name": "Device 2", "max_input_channels": 1},
            ]

            devices = audio_service.get_devices()

            assert isinstance(devices, list)
            assert len(devices) == 2
            mock_query.assert_called_once()

    def test_set_device(self, audio_service: AudioService) -> None:
        """Test set_device sets the default audio device."""
        with patch("wintermute.services.audio_service.sd") as mock_sd:
            mock_sd.default = MagicMock()

            audio_service.set_device(1)

            # Verify default device was set
            assert mock_sd.default.device == 1
