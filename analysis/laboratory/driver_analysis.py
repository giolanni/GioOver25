"""Compatibility entry point for the Laboratory driver analysis.

The implementation lives in driver_analysis_fixed so missing experimental
fields (especially restart-after-break fields) do not discard whole matches.
"""
from .driver_analysis_fixed import *
from .driver_analysis_fixed import main

if __name__ == "__main__":
    raise SystemExit(main())
