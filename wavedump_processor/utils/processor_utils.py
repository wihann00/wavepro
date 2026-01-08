"""Main processing functions"""

import numpy as np
import uproot
from typing import List
from tqdm import tqdm
from ..config.channel_config import ChannelConfig
from ..processing.waveform_processor import WaveformProcessor
from ..io.wavedump_reader import WaveDumpReader


def process_wavedump_file(input_file: str, output_file: str, channel_configs: List[ChannelConfig], 
                          file_type: str = 'binary') -> int:
    """
    Process WaveDump file and create ROOT ntuple
    
    Args:
        input_file: Path to input file
        output_file: Path to output ROOT file
        channel_configs: List of channel configurations
        file_type: 'binary' or 'ascii'
    
    Returns:
        Number of events processed
    """
    
    # Create processors for each channel
    processors = {config.channel_id: WaveformProcessor(config) for config in channel_configs}
    
    # Initialize data dictionary for ROOT tree
    # data = {
    #     'event_number': [],
    #     'trigger_time': [],
    #     'board_id': [],
    # }

    full_data = {}

    # Add branches for each configured channel
    for config in channel_configs:
        ch = config.channel_id

        channel_data = {}

        # channel_data = {
        #     'event_number': [],
        #     'trigger_time': [],
        #     'board_id': [],
        #     }

        channel_data[f'ch{ch}_baseline_mean'] = []
        channel_data[f'ch{ch}_baseline_rms'] = []
        channel_data[f'ch{ch}_peak_height'] = []
        channel_data[f'ch{ch}_peak_time'] = []
        channel_data[f'ch{ch}_charge'] = []
        channel_data[f'ch{ch}_threshold_time'] = []
        channel_data[f'ch{ch}_cfd_time'] = []

        full_data[f'ch{ch}'] = channel_data
    
    # Read and process events
    reader = WaveDumpReader(input_file, file_type=file_type)
    event_count = 0
    
    # Create progress bar
    pbar = tqdm(desc="Processing events", unit=" events", dynamic_ncols=True)
    
    while True:
        event = reader.read_event()
        if event is None:
            break
        
        # Process each channel
        for config in channel_configs:
            ch = config.channel_id
            
            if ch in event['channels']:

                # Store event-level info
                # full_data[f'ch{ch}']['event_number'].append(event['event_counter'])
                # full_data[f'ch{ch}']['trigger_time'].append(event['trigger_time_tag'])
                # full_data[f'ch{ch}']['board_id'].append(event['board_id'])

                waveform = event['channels'][ch]
                params = processors[ch].process_waveform(waveform)

                full_data[f'ch{ch}'][f'ch{ch}_baseline_mean'].append(params['baseline_mean'])
                full_data[f'ch{ch}'][f'ch{ch}_baseline_rms'].append(params['baseline_rms'])
                full_data[f'ch{ch}'][f'ch{ch}_peak_height'].append(params['peak_height'])
                full_data[f'ch{ch}'][f'ch{ch}_peak_time'].append(params['peak_time'])
                full_data[f'ch{ch}'][f'ch{ch}_charge'].append(params['charge'])
                full_data[f'ch{ch}'][f'ch{ch}_threshold_time'].append(params['threshold_time'])
                full_data[f'ch{ch}'][f'ch{ch}_cfd_time'].append(params['cfd_time'])
            else:
                # Channel not present in this event
                full_data[f'ch{ch}'][f'ch{ch}_baseline_mean'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_baseline_rms'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_peak_height'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_peak_time'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_charge'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_threshold_time'].append(-999.0)
                full_data[f'ch{ch}'][f'ch{ch}_cfd_time'].append(-999.0)
        
        event_count += 1
        pbar.update(1)
    
    pbar.close()
    reader.close()
    
    # Convert to numpy arrays with proper dtypes
    for key in channel_data:
        if key == 'event_number' or key == 'board_id':
            channel_data[key] = np.array(channel_data[key], dtype=np.int32)
        elif key == 'trigger_time':
            channel_data[key] = np.array(channel_data[key], dtype=np.uint32)
        else:
            channel_data[key] = np.array(channel_data[key], dtype=np.float64)
    
    # Write to ROOT file with explicit TTree creation (fixes uproot warning)
    print(f"Writing {event_count} events to {output_file}...")
    with uproot.recreate(output_file) as root_file:
        # Create TTree explicitly with branch specifications
        # root_file["events"] = {key: channel_data[key] for key in channel_data}

        for config in channel_configs:
            ch = config.channel_id
            channel_data = full_data[f'ch{ch}']

            root_file[f"Tree_ch{ch}"] = {key: channel_data[key] for key in channel_data}
    
    print(f"✓ Completed: {event_count} events processed")
    return event_count