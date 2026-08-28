#!/usr/bin/env python3
"""
SLOP WARNING ! SLOP WARNING ! SLOP WARNING ! SLOP WARNING ! SLOP WARNING ! SLOP WARNING ! SLOP WARNING ! 
 https://claude.ai/share/1d53531a-8945-4fe9-b9e5-9be67540be4e

square_crop.py

Finds all JPG images in a source folder and, for each one, crops the
left-most N x N square (where N is the image's height, assuming the
image is wider than it is tall) and saves the result to a destination
folder.

If an image is taller than it is wide (or exactly square), the crop
is simply the top-left N x N square, where N = min(width, height).

Usage:
    python square_crop.py /path/to/source /path/to/destination
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

# Extensions we treat as "JPG"
JPG_EXTENSIONS = { ".jpg", ".jpeg" }


def find_jpgs(folder: Path):
    """Return a sorted list of JPG file paths in folder (non-recursive)."""
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in JPG_EXTENSIONS
    )


def crop_leftmost_square( img: Image.Image ) -> Image.Image:
    """Crop and return the left-most N x N square of the image,
    where N = min(width, height)."""
    width, height = img.size
    n = min( width, height )
    # Left-most square: starts at x=0, spans full height (or width if
    # the image is taller than wide, in which case it's the top square).
    left   = 0
    top    = 0
    right  = n
    bottom = n
    return img.crop( ( left, top, right, bottom ) )


def process_folder( source: Path, destination: Path ) -> None:
    source      = Path( source )
    destination = Path( destination )

    destination.mkdir( parents = True, exist_ok = True )

    jpgs = find_jpgs( source )
    if not jpgs:
        print( f"No JPG files found in '{source}'." )
        return

    print( f"Found {len(jpgs)} JPG file(s) in '{source}'." )

    for jpg_path in jpgs:
        try:
            with Image.open( jpg_path ) as img:
                width, height = img.size
                if width == height:
                    print( f"Skipping crop (already square): {jpg_path.name}" )
                cropped = crop_leftmost_square( img )

                out_path = destination / jpg_path.name
                # Preserve JPEG quality reasonably; avoids re-encoding artifacts
                # from Pillow defaults being too aggressive.
                cropped.save( out_path, quality = 95 )
                print( f"Saved: {out_path} ({cropped.size[0]}x{cropped.size[1]})" )
        except Exception as e:
            print( f"ERROR processing '{jpg_path.name}': {e}", file = sys.stderr )


def main():

    src = "/home/james/.local/share/Steam/userdata/42257567/760/remote/2133850/screenshots"
    dst = "/home/james/Pictures/BG"

    process_folder( src, dst )


if __name__ == "__main__":
    main()
