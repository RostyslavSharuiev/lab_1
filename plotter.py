"""Visualization module for rendering audio signal waveforms."""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from collections.abc import Callable
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from analyzer import SpectrogramData, SpectrumData
from config import PlotConfig, SpectralConfig

logger = logging.getLogger(__name__)


class PlotterError(Exception):
    """Raised when audio signal visualization fails."""


class Plotter:
    """Renders time-domain audio signal plots using Matplotlib.

    Args:
        config: Plotting configuration defining output directories and display settings.
        spectral_config: Spectral settings affecting plot axes (max frequency, dynamic range).
    """

    def __init__(self, config: PlotConfig,
        spectral_config: SpectralConfig | None = None,) -> None:
        self.config = config
        self.spectral_config = spectral_config or SpectralConfig()

    def plot_signal(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        audio_filename: str = "output.wav",
    ) -> Path | None:
        """Plot and optionally display or save the time-domain audio waveform.

        Args:
            audio_data: 1D or 2D NumPy array of audio sample values.
            sample_rate: Sampling frequency in Hz.
            audio_filename: Name of the audio file for title and plot filename.

        Returns:
            Path | None: Resolved path of saved plot image, or None if save disabled.

        Raises:
            PlotterError: If signal data is empty or plotting fails.
        """
        if not self.config.enabled:
            logger.info("Plotting is disabled by configuration.")
            return None

        if audio_data is None or audio_data.size == 0:
            raise PlotterError("Cannot plot empty audio data.")

        logger.info("Generating audio signal plot...")

        def draw(fig: Figure, ax: Axes) -> None:
            num_samples = len(audio_data)
            time_axis = np.linspace(0, num_samples / sample_rate, num_samples)
            ax.plot(time_axis, audio_data, color="#1f77b4", alpha=0.85, linewidth=1.0)
            ax.set_title(f"Audio Signal: {Path(audio_filename).name}", fontsize=12)
            ax.set_xlabel("Time (seconds)", fontsize=10)
            ax.set_ylabel("Amplitude", fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.6)

        return self._render(audio_filename, "", draw)

    def plot_spectrum(
            self,
            spectrum: SpectrumData,
            audio_filename: str = "output.wav",
    ) -> Path | None:
        """Plot the amplitude spectrum (dBFS vs. frequency) and save it as PNG.

        Returns:
            Path | None: Resolved path of saved image, or None if plotting disabled.

        Raises:
            PlotterError: If spectrum data is empty or plotting fails.
        """
        if not self.config.enabled:
            return None

        if spectrum is None or spectrum.freqs.size == 0:
            raise PlotterError("Cannot plot empty spectrum.")

        logger.info("Generating spectrum plot...")

        def draw(fig: Figure, ax: Axes) -> None:
            ax.plot(
                spectrum.freqs,
                spectrum.magnitude_db,
                color="#d62728",
                alpha=0.85,
                linewidth=0.8,
            )
            peak = float(spectrum.magnitude_db.max())
            ax.set_ylim(peak - self.spectral_config.dynamic_range_db, peak + 5)
            ax.set_xlim(0, self._max_freq(spectrum.freqs))
            ax.set_title(f"Amplitude Spectrum: {Path(audio_filename).name}", fontsize=12)
            ax.set_xlabel("Frequency (Hz)", fontsize=10)
            ax.set_ylabel("Magnitude (dBFS)", fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.6)

        return self._render(audio_filename, "_spectrum", draw)

    def plot_spectrogram(
        self,
        spectrogram: SpectrogramData,
        audio_filename: str = "output.wav",
    ) -> Path | None:
        """"Plot the spectrogram (time-frequency heatmap) and save it as PNG.

        Returns:
            Path | None: Resolved path of saved image, or None if plotting disabled.

        Raises:
            PlotterError: If spectrogram data is empty or plotting fails.
        """
        if not self.config.enabled:
            return None

        if spectrogram is None or spectrogram.power_db.size == 0:
            raise PlotterError("Cannot plot empty spectrogram.")

        logger.info("Generating spectrogram plot...")

        def draw(fig: Figure, ax: Axes) -> None:
            vmax = float(spectrogram.power_db.max())
            vmin = vmax - self.spectral_config.dynamic_range_db
            mesh = ax.pcolormesh(
                spectrogram.times,
                spectrogram.freqs,
                spectrogram.power_db,
                shading="auto",
                cmap="magma",
                vmin=vmin,
                vmax=vmax,
            )
            ax.set_ylim(0, self._max_freq(spectrogram.freqs))
            ax.set_title(f"Spectrogram: {Path(audio_filename).name}", fontsize=12)
            ax.set_xlabel("Time (seconds)", fontsize=10)
            ax.set_ylabel("Frequency (Hz)", fontsize=10)
            fig.colorbar(mesh, ax=ax, label="Power (dB)")

        return self._render(audio_filename, "_spectrogram", draw)

    def show(self) -> None:
        """Display all rendered figures at once (blocking), then release them."""
        if self.config.enabled and self.config.show and plt.get_fignums():
            plt.show()
        plt.close("all")

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _max_freq(self, freqs: np.ndarray) -> float:
        """Upper frequency limit: configured value clamped to the Nyquist frequency."""
        nyquist = float(freqs[-1])
        limit = self.spectral_config.max_freq
        return min(limit, nyquist) if limit is not None else nyquist

    def _render(
        self,
        audio_filename: str,
        suffix: str,
        draw: Callable[[Figure, Axes], None],
    ) -> Path:
        """Create a figure, draw on it, save it to disk and return the resolved path.

        The figure stays open only when interactive display is requested,
        so that `show()` can display all of them in a single call.
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        try:
            draw(fig, ax)
            fig.tight_layout()

            target_path = self.config.get_figure_path(audio_filename, suffix)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(target_path, dpi=self.config.dpi)

            resolved_path = target_path.resolve()
            logger.info("Plot image successfully saved to: %s", resolved_path)
        except Exception as err:
            plt.close(fig)
            logger.error("Failed to render plot: %s", err)
            raise PlotterError(f"Could not render plot: {err}") from err

        if not self.config.show:
            plt.close(fig)

        return resolved_path