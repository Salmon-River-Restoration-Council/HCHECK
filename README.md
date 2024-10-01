# HCHECK HOBO Temperature Anomaly Flagger

Version 0.5.15

This tool processes HOBOWare exported CSV files containing temperature data to detect and flag anomalies using PyQt5 for the graphical user interface.

## Features

- Process multiple CSV files in a directory
- Detect and flag temperature anomalies based on user-defined thresholds
- Option to add headers to processed files
- Generate Excel output files with or without headers
- Produce a summary of detected anomalies

## Requirements

- Python 3.6+
- PyQt5
- pandas
- openpyxl

## Installation and Usage

### Linux Users

1. Clone this repository, or download the zip:
   ```
   git clone https://github.com/yourusername/hcheck.git
   ```
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

Run the script using Python:

```python
python hcheck.py
```

### Windows Users

Download the zip, unzip, and run the batch file:

1. Ensure you have Python 3.6 or later installed. If not, the batch file will guide you to download it.
2. Double-click on `run_hcheck.bat`.
3. If it's your first time running the script, the batch file will set up a virtual environment and install the required packages. This may take a few minutes.
4. The script will then run automatically.

Note: If you encounter any issues, please ensure that you have the latest version of Python installed and that it's added to your system's PATH.

### Nix Users (Linux, Windows WSL, MacOS)

This project includes a Nix flake for easy development and execution in Nix environments. For more information about Nix and how to use it, please refer to the [official Nix documentation](https://nixos.org/manual/nix/stable/).

1. Ensure you have Nix installed with flakes enabled.
2. To enter a development shell:
   ```
   nix develop
   ```
3. To run the application:
   ```
   nix run
   ```
4. To build the application:
   ```
   nix build
   ```

Note: The first time you run these commands, Nix will download and build all dependencies, which may take some time.

### TODO

- [ ] Write more comprehensive documentation
- [x] Add nix environment
- [ ] Package into executables for windows and macos
- [ ] Update to Qt6

