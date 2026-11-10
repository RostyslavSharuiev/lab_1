"""Spectral analysis module: amplitude spectrum (FFT) and spectrogram (STFT)."""

import logging
from dataclasses import dataclass

import numpy as np
from scipy.signal import get_window, spectrogram

from config import SpectralConfig

logger = logging.getLogger(__name__)

# Protects log10 from zero values (-240 dB floor for amplitude, -120 dB for power).
_EPS = 1e-12


class AnalyzerError(Exception):
    """Raised when spectral analysis fails."""


@dataclass(frozen=True)
class SpectrumData:
    """One-sided amplitude spectrum of the whole signal.

    Attributes:
        freqs: Frequency axis in Hz, shape (F,).
        magnitude_db: Amplitude in dBFS (0 dB = sine with amplitude 1.0), shape (F,).
    """

    freqs: np.ndarray
    magnitude_db: np.ndarray


@dataclass(frozen=True)
class SpectrogramData:
    """Time-frequency representation of the signal.

    Attributes:
        freqs: Frequency axis in Hz, shape (F,).
        times: Time axis in seconds (centres of segments), shape (T,).
        power_db: Power in dB, shape (F, T).
    """

    freqs: np.ndarray
    times: np.ndarray
    power_db: np.ndarray


class SpectralAnalyzer:
    """Computes spectrum and spectrogram of a recorded signal.

    Args:
        config: Spectral analysis configuration (window, segment length, overlap).
    """

    def __init__(self, config: SpectralConfig) -> None:
        self.config = config

    @staticmethod
    def _to_mono(audio_data: np.ndarray) -> np.ndarray:
        """Validate input and convert (samples x channels) or 1D data to 1D float64."""
        if audio_data is None or audio_data.size == 0:
            raise AnalyzerError("Cannot analyze empty audio data.")

        signal = np.asarray(audio_data, dtype=np.float64)
        if signal.ndim > 1:
            signal = signal.mean(axis=1)

        if signal.size < 2:
            raise AnalyzerError("Signal is too short for spectral analysis.")

        return signal

    def compute_spectrum(self, audio_data: np.ndarray, sample_rate: int) -> SpectrumData:
        """Compute the one-sided amplitude spectrum of the entire signal via FFT.

        Args:
            audio_data: Audio samples (samples x channels or 1D).
            sample_rate: Sampling frequency in Hz.

        Returns:
            SpectrumData: Frequency axis and amplitude in dBFS.

        Raises:
            AnalyzerError: If the input is empty/too short or the FFT fails.
        """
        signal = self._to_mono(audio_data)

        try:
            window = get_window(self.config.window, signal.size)
            fft_values = np.fft.rfft(signal * window)

            # Factor 2 compensates for discarded negative frequencies; division by
            # sum(window) compensates window gain, so a sine of amplitude A shows A.
            magnitude = 2.0 * np.abs(fft_values) / window.sum()
            magnitude_db = 20.0 * np.log10(np.maximum(magnitude, _EPS))
            freqs = np.fft.rfftfreq(signal.size, d=1.0 / sample_rate)
        except Exception as err:
            logger.error("Failed to compute spectrum: %s", err)
            raise AnalyzerError(f"Could not compute spectrum: {err}") from err

        logger.info(
            "Spectrum computed: %d bins, resolution %.2f Hz.",
            freqs.size,
            sample_rate / signal.size,
        )
        return SpectrumData(freqs=freqs, magnitude_db=magnitude_db)

    def compute_spectrogram(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> SpectrogramData:
        """Compute the spectrogram of the signal via short-time Fourier transform.

        Args:
            audio_data: Audio samples (samples x channels or 1D).
            sample_rate: Sampling frequency in Hz.

        Returns:
            SpectrogramData: Frequency axis, time axis and power matrix in dB.

        Raises:
            AnalyzerError: If the input is empty/too short or the STFT fails.
        """
        signal = self._to_mono(audio_data)

        nperseg = self.config.nperseg
        if nperseg > signal.size:
            logger.warning(
                "Signal (%d samples) is shorter than window (%d); window reduced.",
                signal.size,
                nperseg,
            )
            nperseg = signal.size
        noverlap = min(self.config.noverlap, nperseg - 1)

        try:
            freqs, times, power = spectrogram(
                signal,
                fs=sample_rate,
                window=self.config.window,
                nperseg=nperseg,
                noverlap=noverlap,
                scaling="spectrum",
                mode="psd",
            )
            power_db = 10.0 * np.log10(np.maximum(power, _EPS))
        except Exception as err:
            logger.error("Failed to compute spectrogram: %s", err)
            raise AnalyzerError(f"Could not compute spectrogram: {err}") from err

        logger.info(
            "Spectrogram computed: %d freq bins x %d time frames.",
            freqs.size,
            times.size,
        )
        return SpectrogramData(freqs=freqs, times=times, power_db=power_db)