#!/usr/bin/env python3
"""Profile the 04_merger_and_excel.py script to establish performance baseline."""

import cProfile
import pstats
from pathlib import Path
import sys

# Import the main function from 04 script
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

def run_profiling():
    """Run profiling on 04_merger_and_excel.py script."""
    
    # Import the script's main function
    script_module = import_module('04_merger_and_excel')
    
    # Profile the execution
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run the script
    script_module.main()
    
    profiler.disable()
    
    # Create output directory
    output_dir = Path('!local-notes/profiling')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save stats sorted by cumulative time
    stats_time = pstats.Stats(profiler)
    stats_time.sort_stats('cumulative')
    
    with open(output_dir / '01-baseline-by-time.txt', 'w') as f:
        stats_time.stream = f
        f.write("=" * 80 + "\n")
        f.write("PROFILING REPORT - SORTED BY CUMULATIVE TIME\n")
        f.write("=" * 80 + "\n\n")
        stats_time.print_stats()
    
    # Save stats sorted by call count
    stats_calls = pstats.Stats(profiler)
    stats_calls.sort_stats('ncalls')
    
    with open(output_dir / '01-baseline-by-calls.txt', 'w') as f:
        stats_calls.stream = f
        f.write("=" * 80 + "\n")
        f.write("PROFILING REPORT - SORTED BY CALL COUNT\n")
        f.write("=" * 80 + "\n\n")
        stats_calls.print_stats()
    
    print("\n" + "=" * 80)
    print("Profiling complete!")
    print("=" * 80)
    print(f"Reports saved to: {output_dir}")
    print(f"  - 01-baseline-by-time.txt  (sorted by execution time)")
    print(f"  - 01-baseline-by-calls.txt (sorted by call count)")
    print("=" * 80)

if __name__ == '__main__':
    run_profiling()
