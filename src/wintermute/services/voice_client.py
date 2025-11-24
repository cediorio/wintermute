"""Voice client for speech-to-text and text-to-speech operations."""

import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

try:
    import moonshine_onnx
    from kokoro import KPipeline

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


class VoiceClient:
    """
    Client for voice interactions using Moonshine (STT) and Kokoro (TTS).

    Handles transcription of audio to text and synthesis of text to speech.
    """

    def __init__(
        self,
        stt_model: str = "moonshine/tiny",
        tts_lang_code: str = "a",  # 'a' = American English
        tts_voice: str = "af_heart",
        tts_speed: float = 1.0,
    ):
        """
        Initialize VoiceClient.

        Args:
            stt_model: Moonshine model to use for STT ('moonshine/tiny' or 'moonshine/base').
            tts_lang_code: Language code for Kokoro TTS.
            tts_voice: Voice to use for TTS.
            tts_speed: Speech speed (0.5 to 2.0).

        Raises:
            ImportError: If voice dependencies are not installed.
        """
        if not VOICE_AVAILABLE:
            raise ImportError(
                "Voice dependencies not installed. "
                "Install with: pip install sounddevice numpy useful-moonshine-onnx "
                "kokoro soundfile"
            )

        self.stt_model = stt_model
        self.tts_lang_code = tts_lang_code
        self.tts_voice = tts_voice
        self.tts_speed = tts_speed

        # Initialize TTS pipeline
        self._tts_pipeline: Optional[KPipeline] = None

    @property
    def tts_pipeline(self) -> KPipeline:
        """Lazy-load TTS pipeline."""
        if self._tts_pipeline is None:
            self._tts_pipeline = KPipeline(lang_code=self.tts_lang_code)
        return self._tts_pipeline

    def transcribe(self, audio_data: np.ndarray, samplerate: int = 16000) -> str:
        """
        Transcribe audio to text using Moonshine AI.

        Args:
            audio_data: NumPy array of audio samples.
            samplerate: Sample rate of the audio.

        Returns:
            Transcribed text.
        """
        # Moonshine works with file paths, so save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            sf.write(tmp_path, audio_data, samplerate)

        try:
            # Transcribe using Moonshine
            transcriptions = moonshine_onnx.transcribe(tmp_path, self.stt_model)
            text = " ".join(transcriptions)
            return text
        finally:
            # Clean up temp file
            tmp_path.unlink()

    async def synthesize(self, text: str) -> np.ndarray:
        """
        Synthesize speech from text using Kokoro TTS.

        Args:
            text: Text to synthesize.

        Returns:
            NumPy array of audio samples at 24kHz.
        """
        # Generate speech using Kokoro
        generator = self.tts_pipeline(text, voice=self.tts_voice, speed=self.tts_speed)

        # Collect all audio segments
        audio_segments = []
        for _graphemes, _phonemes, audio in generator:
            audio_segments.append(audio)

        # Concatenate segments
        if audio_segments:
            full_audio = np.concatenate(audio_segments, axis=0)
            return full_audio
        else:
            # Return silence if no audio generated
            return np.array([], dtype=np.float32)
