"""File finding utilities for batch processing"""

from pathlib import Path
from typing import List, Tuple


def find_data_files(parent_dir: str, pattern: str = '*.dat', file_type: str = 'binary') -> List[Tuple[str, str]]:
    """
    Find all data files in subdirectories
    
    Args:
        parent_dir: Parent directory to search
        pattern: File pattern to match
        file_type: 'binary' or 'ascii'
    
    Returns:
        List of tuples: (input_file_path, suggested_output_path)
    """
    parent_path = Path(parent_dir)
    files = []
    
    if file_type == 'binary':
        # Find all .dat files in subdirectories
        for dat_file in parent_path.rglob(pattern):
            # Create output path: replace .dat with .root, maintain directory structure
            rel_path = dat_file.relative_to(parent_path)
            output_path = parent_path / rel_path.with_suffix('.root')
            files.append((str(dat_file), str(output_path)))
    else:  # ascii
        # Find directories containing wave*.txt files
        dirs_with_data = set()
        for txt_file in parent_path.rglob('wave*.txt'):
            dirs_with_data.add(txt_file.parent)
        
        for data_dir in sorted(dirs_with_data):
            # Use the directory as input (pattern will be applied)
            pattern_path = str(data_dir / 'wave*.txt')
            output_path = data_dir / 'output.root'
            files.append((pattern_path, str(output_path)))
    
    return files