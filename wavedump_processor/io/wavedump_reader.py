"""Reader for CAEN WaveDump files (binary and ASCII)"""

import numpy as np
import struct
import glob
import os
import re
from typing import Optional, Dict


class WaveDumpReader:
    """Read CAEN WaveDump files (binary or ASCII)"""
    
    def __init__(self, filename: str, file_type: str = 'binary'):
        """
        Initialize reader
        
        Args:
            filename: Path to file (for binary) or pattern for ASCII (e.g., 'wave*.txt')
            file_type: 'binary' or 'ascii'
        """
        self.filename = filename
        self.file_type = file_type.lower()
        
        if self.file_type == 'binary':
            self.file = open(filename, 'rb')
            # Get file size for progress tracking
            self.file.seek(0, 2)  # Seek to end
            self.file_size = self.file.tell()
            self.file.seek(0)  # Back to start
            self.read_event = self._read_binary_event
        elif self.file_type == 'ascii':
            self._setup_ascii_reader(filename)
            self.read_event = self._read_ascii_event
        else:
            raise ValueError(f"Unknown file type: {file_type}. Use 'binary' or 'ascii'")
    
    def get_progress(self) -> float:
        """Get current reading progress (0.0 to 1.0) for binary files"""
        if self.file_type == 'binary':
            current_pos = self.file.tell()
            return current_pos / self.file_size if self.file_size > 0 else 0.0
        else:
            # ASCII progress tracking would require counting lines first
            return 0.0
    
    def _setup_ascii_reader(self, pattern: str):
        """Setup ASCII file reader by finding all channel files"""
        # Get directory and pattern
        directory = os.path.dirname(pattern) or '.'
        base_pattern = os.path.basename(pattern)
        
        # Find all matching files
        search_pattern = os.path.join(directory, base_pattern)
        files = sorted(glob.glob(search_pattern))
        
        if not files:
            raise FileNotFoundError(f"No files found matching pattern: {search_pattern}")
        
        # Open all channel files
        self.ascii_files = {}
        for filepath in files:
            # Extract channel number from filename (e.g., wave0.txt -> 0)
            basename = os.path.basename(filepath)
            match = re.search(r'(\d+)', basename)
            if match:
                ch_num = int(match.group(1))
                self.ascii_files[ch_num] = open(filepath, 'r')
        
        print(f"Found {len(self.ascii_files)} ASCII channel files: {list(self.ascii_files.keys())}")
        self.ascii_event_counter = 0
    
    def _read_binary_event(self) -> Optional[Dict]:
        """Read a single event from binary file"""
        try:
            # Read event header (4 words = 16 bytes)
            header = self.file.read(16)
            if len(header) < 16:
                return None
            
            # Parse header
            event_size = struct.unpack('I', header[0:4])[0]
            board_id = struct.unpack('I', header[4:8])[0]
            pattern = struct.unpack('I', header[8:12])[0]
            channel_mask = struct.unpack('I', header[12:16])[0]
            
            # Read event counter and trigger time tag
            event_info = self.file.read(8)
            event_counter = struct.unpack('I', event_info[0:4])[0]
            trigger_time_tag = struct.unpack('I', event_info[4:8])[0]
            
            # Determine which channels are active
            active_channels = []
            for ch in range(8):  # DT5730 has 8 channels
                if channel_mask & (1 << ch):
                    active_channels.append(ch)
            
            # Read channel data
            channels_data = {}
            for ch in active_channels:
                # Read channel size (in words)
                ch_size_bytes = self.file.read(4)
                ch_size = struct.unpack('I', ch_size_bytes)[0]
                
                # Number of samples (each sample is 2 bytes for 14-bit ADC)
                n_samples = (ch_size - 2) * 2  # Subtract header, multiply by 2 for 16-bit words
                
                # Read waveform data
                waveform_bytes = self.file.read(n_samples * 2)
                waveform = np.frombuffer(waveform_bytes, dtype=np.uint16)
                
                # Mask to 14-bit (DT5730 is 14-bit)
                waveform = waveform & 0x3FFF
                
                channels_data[ch] = waveform
            
            return {
                'event_counter': event_counter,
                'trigger_time_tag': trigger_time_tag,
                'board_id': board_id,
                'channels': channels_data
            }
            
        except Exception as e:
            print(f"Error reading binary event: {e}")
            return None
    
    def _parse_int(self, value_str: str) -> int:
        """Parse integer that might be in hex (0xXXXX) or decimal format"""
        value_str = value_str.strip()
        if value_str.startswith('0x') or value_str.startswith('0X'):
            return int(value_str, 16)
        else:
            return int(value_str)
    
    def _read_ascii_event(self) -> Optional[Dict]:
        """Read a single event from ASCII files (one per channel)"""
        channels_data = {}
        event_counter = self.ascii_event_counter
        trigger_time_tag = 0
        
        try:
            for ch, f in self.ascii_files.items():
                # Read header line (Record Length:)
                line = f.readline()
                if not line:
                    return None  # EOF
                
                # Read BoardID line
                line = f.readline()
                if not line:
                    return None
                
                # Read Channel line
                line = f.readline()
                
                # Read Event Number line
                line = f.readline()
                
                # Read Pattern line
                line = f.readline()
                
                # Read Trigger Time Tag line
                line = f.readline()
                trigger_time_tag = self._parse_int(line.split(':')[1])
                
                # Read DC offset line
                line = f.readline()
                
                # Read empty line
                f.readline()
                
                # Read waveform data
                waveform = []
                while True:
                    line = f.readline()
                    if not line or line.strip() == '':
                        break
                    try:
                        value = self._parse_int(line)
                        waveform.append(value)
                    except ValueError:
                        break
                
                channels_data[ch] = np.array(waveform, dtype=np.uint16)
            
            self.ascii_event_counter += 1
            
            return {
                'event_counter': event_counter,
                'trigger_time_tag': trigger_time_tag,
                'board_id': 0,  # Not available in ASCII
                'channels': channels_data
            }
            
        except Exception as e:
            print(f"Error reading ASCII event: {e}")
            return None
    
    def close(self):
        """Close all open files"""
        if self.file_type == 'binary':
            self.file.close()
        elif self.file_type == 'ascii':
            for f in self.ascii_files.values():
                f.close()