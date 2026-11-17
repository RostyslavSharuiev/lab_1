"""Signal processing module for threshold-based audio trimming."""

import logging
import numpy as np

from config import ProcessingConfig

logger = logging.getLogger(__name__)


class SignalProcessingError(Exception):
    """Raised when audio signal processing fails."""


class SignalProcessor:
    """Performs threshold-based silence trimming on audio waveforms.

    Args:
        config: Processing configuration defining the amplitude threshold.
    """

    def __init__(self, config: ProcessingConfig) -> None:
        self.config = config

    def trim_silence(self, audio_data: np.ndarray) -> np.ndarray:
        """Trim leading and trailing silence using an amplitude threshold.

        Args:
            audio_data: 1D or 2D NumPy array of audio sample values.

        Returns:
            np.ndarray: Trimmed audio signal array.

        Raises:
            SignalProcessingError: If input audio data is empty or invalid.
        """
        if audio_data is None or audio_data.size == 0:
            raise SignalProcessingError("Cannot process empty audio data.")

        logger.info(
            "Trimming leading and trailing silence with threshold=%.4f...",
            self.config.threshold,
        )

        try:
            # Calculate absolute amplitude envelope across channels if 2D
            if audio_data.ndim > 1:
                amplitude = np.max(np.abs(audio_data), axis=1)
            else:
                amplitude = np.abs(audio_data)

            above_threshold_indices = np.where(amplitude > self.config.threshold)[0]

            if above_threshold_indices.size == 0:
                logger.warning(
                    "No samples exceeded threshold %.4f. Returning original signal.",
                    self.config.threshold,
                )
                return audio_data.copy()

            start_idx = int(above_threshold_indices[0])
            end_idx = int(above_threshold_indices[-1]) + 1

            trimmed_data = audio_data[start_idx:end_idx]

            logger.info(
                "Trimming complete: kept samples [%d:%d] (%d -> %d samples).",
                start_idx,
                end_idx,
                len(audio_data),
                len(trimmed_data),
            )
            return trimmed_data

        except Exception as err:
            logger.error("Failed to trim audio signal: %s", err)
            raise SignalProcessingError(f"Signal trimming failed: {err}") from err