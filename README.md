# 🎙️ Audio Recorder CLI

A production-grade, cross-platform Python command-line utility for recording audio from a microphone, saving WAV audio files, and rendering signal waveform plots.

Built with Python 3.12+, `sounddevice`, `matplotlib`, `numpy`, and managed with `uv`.

---

## ✨ Features

- 🎤 **Microphone Recording**: Audio capture via `sounddevice`.
- 📊 **Signal Visualization**: Automatic waveform plotting saved as PNG images (`figures/`).
- 📂 **Isolated Directories**: Audio files are stored in `records/` and plots in `figures/` by default.
- ⚙️ **Configurable Parameters**: Custom duration, sample rate, output filename, extension, output directories, and toggleable plotting.
- 🔒 **Clean Domain Architecture**: Separated `AudioConfig` and `PlotConfig` models aggregated in `AppConfig`.
- 📝 **Structured Logging**: Context-aware log messages with timestamps and module names.
- 🛡️ **Robust Error Handling**: Standardized exit codes (`ExitCode`) for CLI automation.
- 🧪 **Unit Tested**: Full test suite covering CLI parsing, domain configs, audio saving, and plot rendering using `pytest`.

---

## 📋 Prerequisites

- **Python**: `>= 3.12`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`

---

## 🚀 Quick Start

### 1. Install Dependencies

Using `uv`:
```bash
uv sync
```

---

## 💻 Usage

### Basic Recording (Default: 5 seconds, 48000 Hz)

```bash
uv run python main.py
```
*Saves audio to `records/output.wav` and plot to `figures/output.png`.*

### Custom Recording

Record 10 seconds of audio to `records/voice_memo.wav` and save plot to `figures/voice_memo.png`:

```bash
uv run python main.py -d 10 -n voice_memo -sr 44100
```

### CLI Arguments Reference

#### Audio Settings
| Flag  | Long Flag       | Default   | Description                                     |
|-------|-----------------|-----------|-------------------------------------------------|
| `-d`  | `--duration`    | `5`       | Recording duration in seconds                   |
| `-n`  | `--name`        | `output`  | Output filename (without extension)             |
| `-e`  | `--ext`         | `wav`     | Output file extension                           |
| `-sr` | `--sample-rate` | `48000`   | Audio sample rate in Hz (e.g. `44100`, `48000`) |
| `-o`  | `--output-dir`  | `records` | Target directory path for audio recordings      |

#### Visualization Settings
| Flag   | Long Flag       | Default   | Description                                        |
|--------|-----------------|-----------|----------------------------------------------------|
| `-fig` | `--figures-dir` | `figures` | Target directory path for plot images              |
|        | `--no-plot`     | `False`   | Disable waveform signal plotting                   |
|        | `--no-show`     | `False`   | Disable interactive GUI window display of the plot |

---

## 🧪 Running Tests

To run the unit tests with `pytest`:

```bash
uv run pytest
```

---

## 📁 Project Structure

```text
PythonProject/
├── audio_engine.py   # Audio recording & file saving engine
├── cli.py            # CLI argument parser (Audio Settings & Visualization Settings)
├── config.py         # Domain models: AudioConfig, PlotConfig, AppConfig
├── logger.py         # Logging configuration setup
├── main.py           # Application pipeline orchestration & exit codes
├── plotter.py        # Signal waveform visualization engine
├── pyproject.toml    # Project metadata, dependencies, & tool configs
├── tests/            # Unit tests
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_plotter.py
├── records/          # Default directory for recorded WAV files
└── figures/          # Default directory for rendered plot PNG images
```

---

## 📄 Exit Codes

| Code  | Name             | Description                               |
|-------|------------------|-------------------------------------------|
| `0`   | `SUCCESS`        | Successful execution                      |
| `1`   | `FAILURE`        | Audio hardware, file IO, or plotter error |
| `2`   | `INVALID_CONFIG` | Invalid configuration or CLI arguments    |
| `130` | `INTERRUPTED`    | Interrupted by user (`Ctrl+C`)            |
