#!/usr/bin/env python3
"""
Main script for processing CAEN WaveDump files

This script processes WaveDump binary or ASCII files and extracts
PMT/MPPC parameters into ROOT ntuples.
"""

import argparse
import os
import sys
from pathlib import Path
from tqdm import tqdm

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wavedump_processor import (
    ChannelConfig,
    process_wavedump_file,
    find_data_files
)


def create_parser():
    """Create argument parser with detailed help"""
    parser = argparse.ArgumentParser(
        description='Process CAEN WaveDump files to ROOT ntuples',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single binary file
  %(prog)s input.dat output.root
  
  # Process ASCII files
  %(prog)s "wave*.txt" output.root --file-type ascii
  
  # Batch process all files in directory
  %(prog)s /path/to/data/ --batch
  
  # Use custom configuration
  %(prog)s input.dat output.root --config my_config.py
  
  # Batch process with custom pattern
  %(prog)s /path/to/data/ --batch --pattern "run*.dat"

For more information, see README.md
        """
    )
    
    parser.add_argument('input', 
                       help='Input file path or parent directory (for batch mode)')
    parser.add_argument('output', nargs='?', default=None,
                       help='Output ROOT file (not used in batch mode)')
    parser.add_argument('--config', 
                       help='Configuration file defining channel_configs (Python format)')
    parser.add_argument('--file-type', choices=['binary', 'ascii'], default='binary',
                       help='Input file type: binary (.dat) or ascii (.txt) [default: binary]')
    parser.add_argument('--batch', action='store_true',
                       help='Batch mode: process all files in subdirectories')
    parser.add_argument('--pattern', default='*.dat',
                       help='File pattern for batch mode [default: *.dat]')
    
    return parser


def load_config(config_file):
    """Load configuration from Python file"""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config_code = f.read()
    
    local_vars = {}
    exec(config_code, {}, local_vars)
    
    if 'channel_configs' not in local_vars:
        raise ValueError("Configuration file must define 'channel_configs' variable")
    
    return local_vars['channel_configs']


def get_default_config():
    """Return default channel configuration"""
    return [
        ChannelConfig(
            channel_id=0,
            polarity=1,
            baseline_samples=100,
            charge_method="fixed",
            charge_window=(0, 200),
            threshold=20.0,
            cfd_fraction=0.5
        ),
        ChannelConfig(
            channel_id=1,
            polarity=1,
            baseline_samples=100,
            charge_method="dynamic",
            charge_window=(50, 150),
            threshold=15.0,
            cfd_fraction=0.3
        ),
        ChannelConfig(
            channel_id=2,
            polarity=-1,
            baseline_samples=100,
            charge_method="dynamic",
            charge_window=(50, 150),
            threshold=10.0,
            cfd_fraction=0.5
        ),
    ]


def process_batch(parent_dir, channel_configs, pattern, file_type):
    """Process multiple files in batch mode"""
    files_to_process = find_data_files(parent_dir, pattern, file_type)
    
    if not files_to_process:
        print(f"❌ No files found in {parent_dir} matching pattern '{pattern}'")
        return
    
    # Adjust pattern display for ASCII files
    display_pattern = pattern
    if file_type == 'ascii' and pattern == '*.dat':
        display_pattern = 'wave*.txt'
    
    print(f"\n{'='*60}")
    print(f"Batch Processing Mode")
    print(f"{'='*60}")
    print(f"Parent directory: {parent_dir}")
    print(f"Pattern: {display_pattern}")
    print(f"File type: {file_type}")
    print(f"Found {len(files_to_process)} file(s) to process")
    print(f"{'='*60}\n")
    
    total_events = 0
    successful = 0
    failed = 0
    
    # Process each file with progress bar
    for input_file, output_file in tqdm(files_to_process, desc="Processing files", unit=" file"):
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        try:
            print(f"\n📂 Processing: {input_file}")
            n_events = process_wavedump_file(input_file, output_file, channel_configs, file_type)
            total_events += n_events
            successful += 1
        except Exception as e:
            print(f"❌ ERROR processing {input_file}: {e}")
            failed += 1
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Processing Complete!")
    print(f"{'='*60}")
    print(f"✓ Successful: {successful} files")
    if failed > 0:
        print(f"✗ Failed: {failed} files")
    print(f"📊 Total events: {total_events}")
    print(f"{'='*60}\n")


def process_single(input_file, output_file, channel_configs, file_type):
    """Process single file"""
    print(f"\n{'='*60}")
    print(f"Single File Processing")
    print(f"{'='*60}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"File type: {file_type}")
    print(f"{'='*60}\n")
    
    try:
        n_events = process_wavedump_file(input_file, output_file, channel_configs, file_type)
        print(f"\n{'='*60}")
        print(f"✓ Success! Processed {n_events} events")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR: {e}")
        print(f"{'='*60}\n")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch and args.output is None:
        parser.error("output file required in single file mode")
    
    # Load configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        try:
            channel_configs = load_config(args.config)
            print(f"✓ Loaded configuration for {len(channel_configs)} channels")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            sys.exit(1)
    else:
        print("⚠ Warning: Using default configuration")
        print("  Consider creating a config file with your channel settings")
        print("  See config_example.py for reference\n")
        channel_configs = get_default_config()
    
    # Process files
    if args.batch:
        process_batch(args.input, channel_configs, args.pattern, args.file_type)
    else:
        process_single(args.input, args.output, channel_configs, args.file_type)


if __name__ == "__main__":
    main()