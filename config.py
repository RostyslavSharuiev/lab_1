"""Configuration models for Audio Engine and Plotter visualization."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AudioConfig:
    """Configuration settings specifically for audio recording and audio file persistence.

    Attributes:
        sample_rate: Audio sampling frequency in Hz (e.g., 44100, 48000).
        duration: Duration of recording in seconds.
        output_filename: Output file name without extension.
        output_extension: Audio file format extension (default: 'wav').
        output_dir: Directory where the recorded audio file will be saved.
    """

    sample_rate: int = 8000
    duration: int = 5
    output_filename: str = "output"
    output_extension: str = "wav"
    output_dir: Path = field(default_factory=lambda: Path("records"))

    def __post_init__(self) -> None:
        """Validate audio configuration parameters."""
        if self.sample_rate <= 0:
            raise ValueError(f"Sample rate must be positive, got {self.sample_rate}")

        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")

        if not self.output_filename.strip():
            raise ValueError("Output filename cannot be empty")

        cleaned_ext = self.output_extension.lstrip(".")

        if not cleaned_ext:
            raise ValueError("Output extension cannot be empty")

        object.__setattr__(self, "output_extension", cleaned_ext)

    @property
    def file_path(self) -> Path:
        """Return the fully resolved file path for the recorded audio."""
        return self.output_dir / f"{self.output_filename}.{self.output_extension}"

    def file_path_with_suffix(self, suffix: str) -> Path:
        """Return output file path with a suffix added to the file name."""
        return self.output_dir / f"{self.output_filename}{suffix}.{self.output_extension}"

@dataclass(frozen=True)
class PlotConfig:
    """Configuration settings specifically for signal visualization and plot image output.

    Attributes:
        figures_dir: Directory where plot images will be saved.
        enabled: Whether signal plotting is enabled.
        show: Whether to display interactive plot GUI window.
        dpi: Dots per inch resolution for saved plot images.
    """

    figures_dir: Path = field(default_factory=lambda: Path("figures"))
    enabled: bool = True
    show: bool = True
    dpi: int = 300

    def get_figure_path(self, audio_filename: str, suffix: str= "") -> Path:
        """Return target PNG file path for a given audio filename stem."""
        stem = Path(audio_filename).stem
        return self.figures_dir / f"{stem}{suffix}.png"

@dataclass(frozen=True)
class SpectralConfig:
    """Configuration for spectrum and spectrogram analysis.

    Attributes:
        window: Window function name understood by scipy.signal.get_window.
        nperseg: Length of one STFT segment (window) in samples for the spectrogram.
        overlap: Fraction of overlap between neighbouring segments, in [0, 1).
        dynamic_range_db: Displayed dynamic range below the peak, in dB.
        max_freq: Upper frequency limit of the plots in Hz (None = Nyquist frequency).
    """

    window: str = "hann"
    nperseg: int = 1024
    overlap: float = 0.5
    dynamic_range_db: float = 80.0
    max_freq: float | None = None

    def __post_init__(self) -> None:
        if self.nperseg < 2:
            raise ValueError(f"Window size must be at least 2 samples, got {self.nperseg}")

        if not 0 <= self.overlap < 1:
            raise ValueError(f"Overlap must be in range [0, 1), got {self.overlap}")

        if self.dynamic_range_db <= 0:
            raise ValueError(
                f"Dynamic range must be positive, got {self.dynamic_range_db}"
            )

        if self.max_freq is not None and self.max_freq <= 0:
            raise ValueError(f"Max frequency must be positive, got {self.max_freq}")

    @property
    def noverlap(self) -> int:
        """Number of overlapping samples between neighbouring segments."""
        return int(self.nperseg * self.overlap)


@dataclass(frozen=True)
class ProcessingConfig:
    """Configuration for threshold-based trimming.

    Attributes:
        threshold: Amplitude threshold in range (0, 1).
        suffix: Suffix added to the name of processed files.
    """

    threshold: float = 0.01
    suffix: str = "_processed"

    def __post_init__(self) -> None:
        if not 0 < self.threshold < 1:
            raise ValueError(f"Threshold must be in range (0, 1), got {self.threshold}")


@dataclass(frozen=True)
class AppConfig:
    """Aggregate configuration holding domain-specific configs."""

    audio: AudioConfig
    plot: PlotConfig
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    spectral: SpectralConfig = field(default_factory=SpectralConfig)