"""
Example configuration file for WaveDump processor

Copy this file and modify for your specific setup.
"""

from wavedump_processor.config.channel_config import ChannelConfig

# Define your channel configurations
channel_configs = [
    # Channel 0: Signal generator trigger (positive polarity)
    ChannelConfig(
        channel_id=0,
        polarity=1,
        baseline_samples=100,
        charge_method="fixed",
        charge_window=(0, 200),
        threshold=100.0,
        cfd_fraction=0.5
    ),
    
    # Channel 1: MPPC (positive polarity)
    ChannelConfig(
        channel_id=1,
        polarity=1,
        baseline_samples=100,
        charge_method="dynamic",
        charge_window=(50, 150),  # 50 samples before peak, 150 after
        threshold=100.0,
        cfd_fraction=0.3
    ),
    
    # Channel 2: PMT (negative polarity)
    ChannelConfig(
        channel_id=2,
        polarity=-1,
        baseline_samples=100,
        charge_method="dynamic",
        charge_window=(50, 150),
        threshold=5.0,
        cfd_fraction=0.5
    ),
    
    # Add more channels as needed
]