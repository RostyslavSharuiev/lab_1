"""Unit tests for AudioConfig and PlotConfig models."""

from pathlib import Path
import pytest

from config import AudioConfig, PlotConfig


def test_default_audio_config():
    config = AudioConfig()
    assert config.sample_rate == 48000
    assert config.duration == 5
    assert config.output_filename == "output"
    assert config.output_extension == "wav"
    assert config.output_dir == Path("records")
    assert config.file_path == Path("records/output.wav")


def test_audio_config_custom_values():
    config = AudioConfig(
        sample_rate=44100,
        duration=10,
        output_filename="my_recording",
        output_extension=".flac",
        output_dir=Path("/tmp/audio"),
    )
    assert config.sample_rate == 44100
    assert config.duration == 10
    assert config.output_filename == "my_recording"
    assert config.output_extension == "flac"
    assert config.file_path == Path("/tmp/audio/my_recording.flac")


def test_default_plot_config():
    config = PlotConfig()
    assert config.figures_dir == Path("figures")
    assert config.enabled is True
    assert config.show is True
    assert config.get_figure_path("my_sound.wav") == Path("figures/my_sound.png")


def test_invalid_sample_rate():
    with pytest.raises(ValueError, match="Sample rate must be positive"):
        AudioConfig(sample_rate=-1)


def test_invalid_duration():
    with pytest.raises(ValueError, match="Duration must be positive"):
        AudioConfig(duration=0)
