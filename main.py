"""Main application entry point for the Audio Recorder CLI tool."""

import logging
import sys
from enum import IntEnum
from pathlib import Path

import numpy as np

from analyzer import AnalyzerError, SpectralAnalyzer
from audio_engine import AudioEngine, AudioEngineError
from cli import parse_args
from logger import setup_logging
from plotter import Plotter, PlotterError
from processor import AudioProcessor, ProcessorError

class ExitCode(IntEnum):
    """Standardized application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    INVALID_CONFIG = 2
    INTERRUPTED = 130


def build_plots(
        plotter: Plotter,
        analyzer: SpectralAnalyzer,
        audio_data: np.ndarray,
        sample_rate: int,
        name: str,
) -> dict[str, Path | None]:
    """Build waveform, spectrum and spectrogram plots for a single signal.

    Returns:
        dict: Mapping of plot kind to the saved image path (None if plotting disabled).
    """
    if not plotter.config.enabled:
        return {}

    spectrum = analyzer.compute_spectrum(audio_data, sample_rate)
    spectrogram = analyzer.compute_spectrogram(audio_data, sample_rate)

    return {
        "waveform": plotter.plot_signal(audio_data, sample_rate, name),
        "spectrum": plotter.plot_spectrum(spectrum, name),
        "spectrogram": plotter.plot_spectrogram(spectrogram, name),
    }


def main() -> int:
    """Run the audio recorder application pipeline.

    Returns:
        int: Process exit code.
    """
    setup_logging()
    logger = logging.getLogger("main")

    try:
        app_config = parse_args()
        engine = AudioEngine(app_config.audio)
        plotter = Plotter(app_config.plot)
        analyzer = SpectralAnalyzer(app_config.spectral)

        processor = AudioProcessor(app_config.processing.threshold)
        suffix = app_config.processing.suffix
        name = app_config.audio.output_filename
        fs = app_config.audio.sample_rate

        # 1. Запис і збереження оригіналу
        audio_data = engine.record()
        saved_original = engine.save(audio_data)

        # 2. Обробка (обрізання початку та кінця за порогом)
        processed_data = processor.trim_silence(audio_data)
        saved_processed = engine.save(
            processed_data, app_config.audio.file_path_with_suffix(suffix)
        )

        # 3. Графіки обох сигналів
        plots_original = build_plots(plotter, analyzer, audio_data, fs, name)
        plots_processed = build_plots(
            plotter, analyzer, processed_data, fs, f"{name}{suffix}"
        )

        logger.info("Original audio saved to: %s", saved_original)
        logger.info("Processed audio saved to: %s", saved_processed)
        for kind, path in plots_original.items():
            if path:
                logger.info("Original %s plot saved to: %s", kind, path)
        for kind, path in plots_processed.items():
            if path:
                logger.info("Processed %s plot saved to: %s", kind, path)
        plotter.show()
        return ExitCode.SUCCESS

    except KeyboardInterrupt:
        logger.warning("\nRecording process aborted by user.")
        return ExitCode.INTERRUPTED
    except ValueError as err:
        logger.error("Configuration error: %s", err)
        return ExitCode.INVALID_CONFIG
    except (AudioEngineError, PlotterError, ProcessorError) as err:
        logger.error("Application error: %s", err)
        return ExitCode.FAILURE
    except Exception as err:
        logger.critical("Unexpected failure: %s", err, exc_info=True)
        return ExitCode.FAILURE

if __name__ == "__main__":
    sys.exit(main())