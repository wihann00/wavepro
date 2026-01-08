"""Waveform processing class for extracting PMT parameters"""

import numpy as np
from typing import Tuple, Optional
from ..config.channel_config import ChannelConfig


class WaveformProcessor:
    """Process individual waveforms to extract PMT parameters"""
    
    def __init__(self, config: ChannelConfig):
        self.config = config
    
    def calculate_baseline(self, waveform: np.ndarray) -> Tuple[float, float]:
        """Calculate baseline mean and RMS from first N samples"""
        baseline_region = waveform[:self.config.baseline_samples]
        mean = np.mean(baseline_region)
        rms = np.std(baseline_region)
        return mean, rms
    
    def correct_polarity(self, waveform: np.ndarray, baseline: float) -> np.ndarray:
        """Correct waveform for polarity and baseline"""
        corrected = (waveform - baseline) * self.config.polarity
        return corrected
    
    def find_peak(self, waveform: np.ndarray) -> Tuple[int, float]:
        """Find peak position and height"""
        peak_idx = np.argmax(waveform)
        peak_height = waveform[peak_idx]
        return peak_idx, peak_height
    
    def calculate_charge(self, waveform: np.ndarray, peak_idx: int) -> float:
        """Calculate integrated charge"""

        waveform_units = 1e-3
        charge_units = 1e12
        impedance = 50
        sample_rate = 500e6

        charge_constant = waveform_units * charge_units / (impedance * sample_rate)

        if self.config.charge_method == "fixed":
            start, end = self.config.charge_window
            integration_region = waveform[start:end]
        else:  # dynamic
            before, after = self.config.charge_window
            start = max(0, peak_idx - before)
            end = min(len(waveform), peak_idx + after)
            integration_region = waveform[start:end]
        
        charge = np.sum(integration_region)*charge_constant
        return charge
    
    def find_threshold_crossing(self, waveform: np.ndarray) -> Optional[float]:
        """Find leading edge threshold crossing time using linear interpolation"""
        threshold = self.config.threshold
        
        # Find first crossing
        above_threshold = waveform > threshold
        if not np.any(above_threshold):
            return None
        
        crossing_idx = np.where(above_threshold)[0][0]
        
        if crossing_idx == 0:
            return 0.0
        
        # Linear interpolation between points
        y1, y2 = waveform[crossing_idx - 1], waveform[crossing_idx]
        x1, x2 = crossing_idx - 1, crossing_idx
        
        # Interpolate to find exact crossing point
        crossing_time = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)
        return crossing_time
    
    def find_cfd_time(self, waveform: np.ndarray, peak_height: float) -> Optional[float]:
        """Find constant fraction discriminator crossing time"""
        threshold = peak_height * self.config.cfd_fraction
        
        # Find crossing before peak
        above_threshold = waveform > threshold
        if not np.any(above_threshold):
            return None
        
        crossing_idx = np.where(above_threshold)[0][0]
        
        if crossing_idx == 0:
            return 0.0
        
        # Linear interpolation
        y1, y2 = waveform[crossing_idx - 1], waveform[crossing_idx]
        x1, x2 = crossing_idx - 1, crossing_idx
        
        cfd_time = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)
        return cfd_time
    
    def process_waveform(self, waveform: np.ndarray) -> dict:
        """Process a single waveform and extract all parameters"""
        # Calculate baseline
        baseline_mean, baseline_rms = self.calculate_baseline(waveform)
        
        # Correct for polarity and baseline
        corrected_wf = self.correct_polarity(waveform, baseline_mean)
        
        # Find peak
        peak_idx, peak_height = self.find_peak(corrected_wf)
        
        # Calculate charge
        charge = self.calculate_charge(corrected_wf, peak_idx)
        
        # Find timing markers
        threshold_time = self.find_threshold_crossing(corrected_wf)
        cfd_time = self.find_cfd_time(corrected_wf, peak_height)
        
        return {
            'baseline_mean': baseline_mean,
            'baseline_rms': baseline_rms,
            'peak_height': peak_height,
            'peak_time': float(peak_idx),
            'charge': charge,
            'threshold_time': threshold_time if threshold_time is not None else -1.0,
            'cfd_time': cfd_time if cfd_time is not None else -1.0,
        }