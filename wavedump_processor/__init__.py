"""
WaveDump Processor Package

A package for processing CAEN WaveDump data files and extracting
PMT/MPPC parameters into ROOT ntuples.
"""

__version__ = "1.0.0"
__author__ = "Wi Han Ng"

from .config.channel_config import ChannelConfig
from .processing.waveform_processor import WaveformProcessor
from .io.wavedump_reader import WaveDumpReader
from .utils.processor_utils import process_wavedump_file
from .utils.file_utils import find_data_files

__all__ = [
    'ChannelConfig',
    'WaveformProcessor',
    'WaveDumpReader',
    'process_wavedump_file',
    'find_data_files',
]