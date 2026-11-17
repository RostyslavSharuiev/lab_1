"""Main application entry point for the Audio Recorder and Processor CLI tool."""

import logging
import sys
from enum import IntEnum

from audio_engine import AudioEngine, AudioEngineError
from cli import parse_args
from logger import setup_logging
from plotter import Plotter, PlotterError
from processor import SignalProcessingError, SignalProcessor


class ExitCode(IntEnum):
    """Standardized application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    INVALID_CONFIG = 2
    INTERRUPTED = 130


def main() -> int:
    """Run the audio recorder and signal processing pipeline.

    Returns:
        int: Process exit code.
    """
    setup_logging()
    logger = logging.getLogger("main")

    try:
        app_config = parse_args()
        engine = AudioEngine(app_config.audio)
        processor = SignalProcessor(app_config.processing)
        plotter = Plotter(app_config.plot)

        # 1. Record and persist original audio + plot
        original_audio = engine.record()
        saved_original = engine.save(original_audio, suffix="original")
        original_plot = plotter.plot_signal(
            audio_data=original_audio,
            sample_rate=app_config.audio.sample_rate,
            audio_filename=saved_original.name,
        )

        # 2. Trim silence via threshold method and persist processed audio + plot
        processed_audio = processor.trim_silence(original_audio)
        saved_processed = engine.save(processed_audio, suffix="processed")
        processed_plot = plotter.plot_signal(
            audio_data=processed_audio,
            sample_rate=app_config.audio.sample_rate,
            audio_filename=saved_processed.name,
        )

        logger.info("Done! Original audio saved to: %s", saved_original)
        if original_plot:
            logger.info("Done! Original plot saved to: %s", original_plot)

        logger.info("Done! Processed audio saved to: %s", saved_processed)
        if processed_plot:
            logger.info("Done! Processed plot saved to: %s", processed_plot)

        return ExitCode.SUCCESS

    except KeyboardInterrupt:
        logger.warning("\nRecording process aborted by user.")
        return ExitCode.INTERRUPTED
    except ValueError as err:
        logger.error("Configuration error: %s", err)
        return ExitCode.INVALID_CONFIG
    except (AudioEngineError, SignalProcessingError, PlotterError) as err:
        logger.error("Application error: %s", err)
        return ExitCode.FAILURE
    except Exception as err:
        logger.critical("Unexpected failure: %s", err, exc_info=True)
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main())