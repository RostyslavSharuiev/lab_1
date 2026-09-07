"""Main application entry point for the Audio Recorder CLI tool."""

import logging
import sys
from enum import IntEnum

from audio_engine import AudioEngine, AudioEngineError
from cli import parse_args
from logger import setup_logging
from plotter import Plotter, PlotterError


class ExitCode(IntEnum):
    """Standardized application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    INVALID_CONFIG = 2
    INTERRUPTED = 130


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

        audio_data = engine.record()
        saved_audio = engine.save(audio_data)

        plot_file = plotter.plot_signal(
            audio_data=audio_data,
            sample_rate=app_config.audio.sample_rate,
            audio_filename=app_config.audio.output_filename,
        )

        logger.info("Done! Audio saved to: %s", saved_audio)
        if plot_file:
            logger.info("Done! Plot image saved to: %s", plot_file)
        return ExitCode.SUCCESS

    except KeyboardInterrupt:
        logger.warning("\nRecording process aborted by user.")
        return ExitCode.INTERRUPTED
    except ValueError as err:
        logger.error("Configuration error: %s", err)
        return ExitCode.INVALID_CONFIG
    except (AudioEngineError, PlotterError) as err:
        logger.error("Application error: %s", err)
        return ExitCode.FAILURE
    except Exception as err:
        logger.critical("Unexpected failure: %s", err, exc_info=True)
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main())