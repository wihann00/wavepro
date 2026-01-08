# WaveDump Processor

A Python package for processing CAEN WaveDump data files and extracting PMT/MPPC parameters into ROOT ntuples.

## Package Structure

```
wavedump_processor/
├── README.md                    # This file
├── install.sh                   # Installation script
├── setup.py                     # Package setup file
├── requirements.txt             # Python dependencies
├── process_wavedump.py         # Main script
├── config_example.py           # Example configuration file
└── wavedump_processor/         # Package directory
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── channel_config.py   # ChannelConfig dataclass
    ├── processing/
    │   ├── __init__.py
    │   └── waveform_processor.py  # WaveformProcessor class
    ├── io/
    │   ├── __init__.py
    │   └── wavedump_reader.py  # WaveDumpReader class
    └── utils/
        ├── __init__.py
        ├── file_utils.py       # File finding utilities
        └── processor_utils.py  # Main processing functions
```

## Installation

### Quick Install (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd wavedump_processor
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. **Activate the virtual environment:**
```bash
source wdenv/bin/activate
```

This will:
- Create a virtual environment called `wdenv`
- Install the package and all dependencies
- Create the `wavepro` command

4. Now you can use the command:
```bash
wavepro --help
```

5. When done, deactivate the virtual environment:
```bash
deactivate
```

### Manual Installation

1. Clone or download this package
2. Create and activate a virtual environment:
```bash
python3 -m venv wdenv
source wdenv/bin/activate
```

3. Install in editable mode:
```bash
pip install -e .
```

This installs the package and all dependencies (numpy, uproot, tqdm, setuptools) and creates the `wavepro` command.

### Dependencies

The following packages will be installed automatically:
- numpy>=1.20.0
- uproot>=4.0.0
- tqdm>=4.60.0
- setuptools>=45.0.0

### Virtual Environment Notes

- The virtual environment (`wdenv`) keeps the package isolated from your system Python
- You must activate it each time: `source wdenv/bin/activate`
- Your shell prompt will show `(wdenv)` when activated
- To deactivate: `deactivate`

## Quick Start

### Single File Mode

Process a single binary file:
```bash
wavepro input.dat output.root
```

Process ASCII files (multiple wave*.txt files):
```bash
wavepro "wave*.txt" output.root --file-type ascii
```

### Batch Mode

Process all files in subdirectories:
```bash
wavepro /path/to/data/ --batch
```

With custom pattern:
```bash
wavepro /path/to/data/ --batch --pattern "run*.dat"
```

### Using Configuration Files

Use a custom configuration file:
```bash
wavepro input.dat output.root --config my_config.py
```

See `config_example.py` for configuration format.

## Command-Line Options

View all options:
```bash
wavepro --help
```

**Arguments:**
- `input`: Input file path or parent directory (for batch mode)
- `output`: Output ROOT file (not used in batch mode)

**Options:**
- `--config FILE`: Path to configuration file
- `--file-type {binary,ascii}`: Input file format (default: binary)
- `--batch`: Enable batch processing mode
- `--pattern PATTERN`: File pattern for batch mode (default: *.dat)
- `--help, -h`: Show help message

## Configuration

Create a configuration file defining your channel setup:

```python
# my_config.py
from wavedump_processor.config.channel_config import ChannelConfig

channel_configs = [
    ChannelConfig(
        channel_id=0,
        polarity=1,              # 1=positive, -1=negative
        baseline_samples=100,    # Samples for baseline calculation
        charge_method="fixed",   # "fixed" or "dynamic"
        charge_window=(0, 200),  # Integration window
        threshold=20.0,          # Threshold for timing (ADC counts)
        cfd_fraction=0.5         # CFD fraction (0-1)
    ),
    ChannelConfig(
        channel_id=1,
        polarity=1,
        charge_method="dynamic",
        charge_window=(50, 150),  # (samples_before_peak, samples_after_peak)
        threshold=15.0,
        cfd_fraction=0.3
    ),
    # Add more channels as needed
]
```

### Configuration Parameters

**ChannelConfig fields:**
- `channel_id` (int): Channel number
- `polarity` (int): Signal polarity (1 for positive, -1 for negative)
- `baseline_samples` (int): Number of samples from start of waveform for baseline calculation
- `charge_method` (str): Integration method
  - `"fixed"`: Fixed window from start
  - `"dynamic"`: Window around peak
- `charge_window` (tuple):
  - For fixed: (start_sample, end_sample)
  - For dynamic: (samples_before_peak, samples_after_peak)
- `threshold` (float): Threshold in ADC counts above baseline for leading edge timing
- `cfd_fraction` (float): Fraction of peak height for CFD timing (typically 0.3-0.5)

## Output Format

The output ROOT file contains a TTree named `events` with the following branches:

**Event-level branches:**
- `event_number`: Event counter
- `trigger_time`: Trigger time tag
- `board_id`: Digitizer board ID

**Per-channel branches** (for each configured channel N):
- `chN_baseline_mean`: Baseline mean (ADC counts)
- `chN_baseline_rms`: Baseline RMS (ADC counts)
- `chN_peak_height`: Peak height above baseline (ADC counts)
- `chN_peak_time`: Peak time (sample number)
- `chN_charge`: Integrated charge (ADC counts × samples)
- `chN_threshold_time`: Leading edge threshold crossing time (sample number, -1 if not found)
- `chN_cfd_time`: CFD crossing time (sample number, -1 if not found)

Missing channels in an event are filled with -999.0.

## File Format Support

### Binary Format (.dat)
- Single file containing all channels
- CAEN WaveDump native binary format
- More compact file size
- Faster processing

### ASCII Format (.txt)
- Separate files per channel (wave0.txt, wave1.txt, etc.)
- Human-readable but larger files
- Must specify pattern matching all channel files

## Examples

### Example 1: Process single PMT run
```bash
wavepro data/run001.dat output/run001.root --config pmt_config.py
```

### Example 2: Batch process all runs
```bash
wavepro data/ --batch --config pmt_config.py
```

### Example 3: Process ASCII files
```bash
wavepro "data/run001/wave*.txt" output/run001.root --file-type ascii
```

### Example 4: Batch process with custom pattern
```bash
wavepro data/ --batch --pattern "run_2024*.dat"
```

## Progress Tracking

The processor displays progress bars during execution:
- File-level progress in batch mode
- Event-level progress within each file
- Real-time event counting
- Clear status indicators (✓ for success, ❌ for errors)

## Troubleshooting

**No files found in batch mode:**
- Check that the pattern matches your files
- Ensure you're pointing to the correct parent directory
- For ASCII, make sure wave*.txt files exist in subdirectories

**Import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Ensure the package structure is intact with all `__init__.py` files

**Memory issues with large files:**
- The processor reads events sequentially, so memory usage should be manageable
- If issues persist, consider processing files individually rather than in batch

**"channel_configs not defined" error:**
- Make sure your config file defines the `channel_configs` variable
- Check that the import statement is correct: `from wavedump_processor.config.channel_config import ChannelConfig`

## Performance Notes

- Binary files process faster than ASCII
- Processing speed: ~1000-10000 events/second depending on hardware
- Batch mode processes files sequentially
- For parallel processing on clusters, use SLURM (coming soon)

## Analyzed Parameters

For each waveform, the processor extracts:

1. **Baseline**: Mean and RMS from first N samples
2. **Peak Finding**: Maximum value and position after polarity correction
3. **Charge Integration**: Sum of ADC values in specified window
4. **Leading Edge Time**: Threshold crossing with linear interpolation
5. **CFD Time**: Constant Fraction Discriminator timing
6. **Peak Time**: Sample position of maximum value

All timing values use linear interpolation for sub-sample precision.

## Future Features

- ✅ Binary and ASCII file support
- ✅ Batch processing
- ✅ Progress bars
- ✅ Configurable channel parameters
- 🚧 SLURM job submission for cluster parallelization
- 🚧 Additional pulse parameters (rise time, fall time)
- 🚧 Pulse shape discrimination
- 🚧 Real-time monitoring dashboard
- 🚧 Automated quality checks

## Contributing

Suggestions and contributions are welcome! Please test thoroughly before submitting changes.

## License

[Specify your license here]

## Contact

For issues, questions, or contributions, please contact [your contact information].

---

**Version**: 1.0.0  
**Last Updated**: 2025