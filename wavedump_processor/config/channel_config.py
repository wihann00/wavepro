"""Channel configuration dataclass"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ChannelConfig:
    """Configuration for each channel"""
    channel_id: int
    polarity: int  # 1 for positive, -1 for negative
    baseline_samples: int = 100  # Number of samples to use for baseline
    charge_method: str = "dynamic"  # "fixed" or "dynamic"
    charge_window: Tuple[int, int] = (0, 100)  # For fixed: (start, end), for dynamic: (before_peak, after_peak)
    threshold: float = 10.0  # ADC counts above baseline for threshold crossing
    cfd_fraction: float = 0.5  # Fraction for CFD timing
    
    def __post_init__(self):
        """Validate configuration parameters"""
        if self.polarity not in [1, -1]:
            raise ValueError(f"Polarity must be 1 or -1, got {self.polarity}")
        
        if self.charge_method not in ["fixed", "dynamic"]:
            raise ValueError(f"charge_method must be 'fixed' or 'dynamic', got {self.charge_method}")
        
        if self.cfd_fraction <= 0 or self.cfd_fraction >= 1:
            raise ValueError(f"cfd_fraction must be between 0 and 1, got {self.cfd_fraction}")