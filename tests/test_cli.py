"""Unit tests for CLI argument parsing."""

from pathlib import Path
from cli import parse_args


def test_parse_args_defaults():
    app_config = parse_args([])
    assert app_config.audio.sample_rate == 48000
    assert app_config.audio.duration == 5
    assert app_config.audio.output_filename == "output"
    assert app_config.audio.output_dir == Path("records")
    assert app_config.plot.figures_dir == Path("figures")
    assert app_config.plot.enabled is True


def test_parse_args_custom_flags():
    args = [
        "-d", "3",
        "-n", "voice_memo",
        "-e", "wav",
        "-sr", "16000",
        "-o", "custom_records",
        "-fig", "custom_figures",
        "--no-show",
    ]
    app_config = parse_args(args)
    assert app_config.audio.duration == 3
    assert app_config.audio.output_filename == "voice_memo"
    assert app_config.audio.output_dir == Path("custom_records")
    assert app_config.plot.figures_dir == Path("custom_figures")
    assert app_config.plot.show is False
