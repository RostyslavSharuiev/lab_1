"""Unit tests for Plotter visualization module."""

import numpy as np
import pytest
from config import PlotConfig
from plotter import Plotter, PlotterError


def test_plotter_valid_data(tmp_path):
    plot_config = PlotConfig(figures_dir=tmp_path, show=False)
    plotter = Plotter(plot_config)

    t = np.linspace(0, 1, 8000)
    signal = np.sin(2 * np.pi * 440 * t)

    saved_path = plotter.plot_signal(
        audio_data=signal,
        sample_rate=8000,
        audio_filename="test_signal.wav",
    )

    assert saved_path is not None
    assert saved_path.exists()
    assert saved_path.name == "test_signal.png"
    assert saved_path.stat().st_size > 0


def test_plotter_disabled():
    plot_config = PlotConfig(enabled=False)
    plotter = Plotter(plot_config)
    signal = np.ones(100)

    saved_path = plotter.plot_signal(signal, sample_rate=8000)
    assert saved_path is None


def test_plotter_empty_data():
    plot_config = PlotConfig(show=False)
    plotter = Plotter(plot_config)
    empty_signal = np.array([])

    with pytest.raises(PlotterError, match="Cannot plot empty audio data."):
        plotter.plot_signal(empty_signal, sample_rate=8000)
