#!/usr/bin/python
"""
CLI entry point for the DSpace SAF builder.

Usage:
    python dspace-csv-safbuilder.py /path/to/input/file.csv
"""

import os
import sys

from dspacearchive import DspaceArchive


def main():
    if len(sys.argv) != 2:
        print("Usage: dspace-csv-safbuilder.py /path/to/input/file.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"Error: file not found: {input_file}")
        sys.exit(1)

    output_path = os.path.join(os.path.dirname(os.path.abspath(input_file)), "SimpleArchiveFormat")
    print(f"Building archive from: {input_file}")
    DspaceArchive(input_file).write(output_path)
    print(f"Archive written to: {output_path}")


if __name__ == "__main__":
    main()
