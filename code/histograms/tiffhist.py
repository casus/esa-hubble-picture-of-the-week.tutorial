#!/usr/bin/env python3
"""
tiffhist.py - Compute histogram of TIFF images

Usage:
    python tiffhist.py <input_file> [--channel <channel_name>]

Options:
    --channel    Compute histogram for specific channel only
                 (e.g., red, green, blue, gray, etc. or "all")

Examples:
    python tiffhist.py image.tif --channel red
    python tiffhist.py image.tif --channel green
"""

import sys
import os
import json
import argparse
import numpy as np
from pathlib import Path
from fractions import Fraction
from PIL import Image


def fraction_to_float(value):
    """Convert Fraction to float for JSON serialization."""
    if value is None:
        return 0.0
    if isinstance(value, Fraction):
        return float(value)
    return float(value)


def compute_histogram(data: np.ndarray, bins: int = 256) -> list:
    """Compute histogram for a single channel."""
    hist, _ = np.histogram(data, bins=bins, range=(0, 255))
    return hist.tolist()


def get_available_channels(img: Image.Image) -> list:
    """Return list of available channels for the image mode."""
    mode = img.mode
    
    if mode == '1':
        return ['gray']
    elif mode == 'L':
        return ['gray']
    elif mode == 'RGB':
        return ['red', 'green', 'blue']
    elif mode == 'RGBA':
        return ['red', 'green', 'blue', 'alpha']
    elif mode == 'CMYK':
        return ['cyan', 'magenta', 'yellow', 'black']
    elif mode == 'YCbCr':
        return ['Y', 'Cb', 'Cr']
    elif mode == 'LAB':
        return ['L', 'a', 'b']
    elif mode == 'P':
        return ['index']
    elif mode in ('I', 'I;16'):
        return ['gray']
    else:
        return []


def print_available_channels(channels: list, file_path: str, mode: str):
    """Print available channels to stderr."""
    sys.stderr.write(f"File: {file_path}\n")
    sys.stderr.write(f"Image mode: {mode}\n")
    sys.stderr.write(f"Available channels: {', '.join(channels)}\n")
    sys.stderr.write(f"\nUsage: python tiffhist.py <file> --channel <channel_name>\n")
    sys.stderr.write(f"\nExample: python tiffhist.py {file_path} --channel {channels[0]}\n\n")


def validate_channel(channel_name: str, available_channels: list) -> bool:
    """Check if channel name is valid (case-insensitive)."""
    if channel_name is None:
        return False
    channel_lower = channel_name.lower()
    for channel in available_channels:
        if channel.lower() == channel_lower:
            return True
    return False


def get_channel_index(channel_name: str, available_channels: list) -> int:
    """Get the index of a channel name (case-insensitive)."""
    channel_lower = channel_name.lower()
    for i, channel in enumerate(available_channels):
        if channel.lower() == channel_lower:
            return i
    return -1


def compute_histogram_grayscale(data: np.ndarray) -> dict:
    """Compute histogram for grayscale (L) or binary (1) image."""
    histogram = compute_histogram(data)
    
    result = {
        "channel": "gray",
        "bins": 256,
        "histogram": histogram,
        "min": int(data.min()),
        "max": int(data.max()),
        "mean": round(float(data.mean()), 2),
        "total_pixels": int(data.size)
    }
    
    return result


def compute_channel_histogram(data: np.ndarray, channel_name: str) -> dict:
    """Compute histogram for a specific channel in RGB/RGBA/CMYK/etc."""
    channel_name = channel_name.lower()
    
    # Map channel name to index
    channel_map = {
        # RGB
        'red': 0, 'r': 0,
        'green': 1, 'g': 1,
        'blue': 2, 'b': 2,
        # RGBA
        'alpha': 3, 'a': 3,
        # CMYK
        'cyan': 0, 'c': 0,
        'magenta': 1, 'm': 1,
        'yellow': 2, 'y': 2,
        'black': 3, 'k': 3,
        # YCbCr
        'y': 0, 'cb': 1, 'cr': 2,
        # LAB
        'l': 0, 'a': 1, 'b': 2,
    }
    
    idx = channel_map.get(channel_name, 0)
    channel_data = data[:, :, idx]
    histogram = compute_histogram(channel_data)
    
    result = {
        "channel": channel_name,
        "bins": 256,
        "histogram": histogram,
        "min": int(channel_data.min()),
        "max": int(channel_data.max()),
        "mean": round(float(channel_data.mean()), 2),
        "total_pixels": int(channel_data.size)
    }
    
    return result


def compute_histogram_rgb(data: np.ndarray) -> list:
    """Compute histogram for RGB image."""
    channels = ['red', 'green', 'blue']
    results = []
    
    for i, channel_name in enumerate(channels):
        channel_data = data[:, :, i]
        histogram = compute_histogram(channel_data)
        
        results.append({
            "channel": channel_name,
            "bins": 256,
            "histogram": histogram,
            "min": int(channel_data.min()),
            "max": int(channel_data.max()),
            "mean": round(float(channel_data.mean()), 2),
            "total_pixels": int(channel_data.size)
        })
    
    return results


def compute_histogram_rgba(data: np.ndarray) -> list:
    """Compute histogram for RGBA image."""
    channels = ['red', 'green', 'blue', 'alpha']
    results = []
    
    for i, channel_name in enumerate(channels):
        channel_data = data[:, :, i]
        histogram = compute_histogram(channel_data)
        
        results.append({
            "channel": channel_name,
            "bins": 256,
            "histogram": histogram,
            "min": int(channel_data.min()),
            "max": int(channel_data.min()) if channel_name == 'alpha' else int(channel_data.max()),
            "mean": round(float(channel_data.mean()), 2),
            "total_pixels": int(channel_data.size)
        })
    
    return results


def compute_histogram_cmyk(data: np.ndarray) -> list:
    """Compute histogram for CMYK image."""
    channels = ['cyan', 'magenta', 'yellow', 'black']
    results = []
    
    for i, channel_name in enumerate(channels):
        channel_data = data[:, :, i]
        histogram = compute_histogram(channel_data)
        
        results.append({
            "channel": channel_name,
            "bins": 256,
            "histogram": histogram,
            "min": int(channel_data.min()),
            "max": int(channel_data.max()),
            "mean": round(float(channel_data.mean()), 2),
            "total_pixels": int(channel_data.size)
        })
    
    return results


def get_file_info(img: Image.Image, file_path: str) -> dict:
    """Get basic file information."""
    file_size = os.path.getsize(file_path)
    
    info = {
        "filename": os.path.basename(file_path),
        "file_path": os.path.abspath(file_path),
        "width": img.size[0],
        "height": img.size[1],
        "mode": img.mode,
        "format": img.format if hasattr(img, 'format') else "TIFF",
        "file_size_bytes": file_size
    }
    
    # Add DPI if available (convert Fraction to float)
    try:
        dpi = img.info.get('dpi', None)
        if dpi:
            info["dpi"] = {
                "x": round(fraction_to_float(dpi[0]), 1),
                "y": round(fraction_to_float(dpi[1]), 1)
            }
    except (KeyError, TypeError, IndexError):
        pass
    
    # Total pixels
    info["total_pixels"] = img.size[0] * img.size[1]
    
    return info


def compute_histogram_tiff(file_path: str, channel: str = None) -> dict:
    """Compute histogram for a TIFF file."""
    result = {
        "success": False,
        "error": None
    }

    if "all" == channel:
        channel= None

    try:
        with Image.open(file_path) as img:
            result["file_info"] = get_file_info(img, file_path)
            
            available_channels = get_available_channels(img)
            result["available_channels"] = available_channels
            
            # Validate channel if specified
            requested_channel = None
            if channel is not None:
                if not validate_channel(channel, available_channels):
                    print_available_channels(available_channels, file_path, img.mode)
                    result["error"] = f"Invalid channel '{channel}'. Available: {available_channels}"
                    return result
                requested_channel = channel

            # Convert to numpy array
            data = np.array(img)
            
            # Compute histogram based on mode and requested channel
            mode = img.mode
            
            if mode == '1' or mode == 'L':
                # Grayscale
                result["histogram"] = [compute_histogram_grayscale(data)]
                result["mode_description"] = "8-bit grayscale"
                
            elif mode == 'RGB':
                # RGB color
                if requested_channel:
                    idx = get_channel_index(requested_channel, available_channels)
                    result["histogram"] = [compute_channel_histogram(data, requested_channel)]
                else:
                    result["histogram"] = compute_histogram_rgb(data)
                result["mode_description"] = "24-bit RGB color"
                
            elif mode == 'RGBA':
                # RGB with alpha
                if requested_channel:
                    result["histogram"] = [compute_channel_histogram(data, requested_channel)]
                else:
                    result["histogram"] = compute_histogram_rgba(data)
                result["mode_description"] = "32-bit RGB with alpha"
                
            elif mode == 'CMYK':
                # CMYK color
                if requested_channel:
                    result["histogram"] = [compute_channel_histogram(data, requested_channel)]
                else:
                    result["histogram"] = compute_histogram_cmyk(data)
                result["mode_description"] = "CMYK color"
                
            elif mode == 'P':
                # Palette (indexed) color
                palette = img.getpalette()
                if palette:
                    unique, counts = np.unique(data, return_counts=True)
                    
                    color_histogram = {}
                    for idx, count in zip(unique, counts):
                        if idx < len(palette) // 3:
                            r = palette[idx * 3]
                            g = palette[idx * 3 + 1]
                            b = palette[idx * 3 + 2]
                            color_key = f"#{r:02x}{g:02x}{b:02x}"
                            color_histogram[color_key] = int(count)
                    
                    result["histogram"] = [{
                        "channel": "indexed",
                        "palette_size": len(palette) // 3,
                        "unique_colors": len(unique),
                        "color_histogram": color_histogram,
                        "total_pixels": int(data.size)
                    }]
                else:
                    result["histogram"] = [compute_histogram_grayscale(data)]
                result["mode_description"] = "Indexed/palette color"
                
            elif mode == 'I' or mode == 'I;16':
                # 16-bit integer
                data_normalized = np.clip(data, 0, 255).astype(np.uint8)
                result["histogram"] = [compute_histogram_grayscale(data_normalized)]
                result["mode_description"] = "16-bit integer (normalized)"
                
            else:
                # Fallback
                if data.ndim == 3:
                    if requested_channel:
                        result["histogram"] = [compute_channel_histogram(data, requested_channel)]
                    else:
                        result["histogram"] = compute_histogram_rgb(data)
                else:
                    result["histogram"] = [compute_histogram_grayscale(data)]
                result["mode_description"] = f"Unknown mode '{mode}' (converted)"
            
            result["success"] = True
            
    except Exception as e:
        result["error"] = str(e)
        result["histogram"] = []
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Compute histogram of TIFF images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.tif                    # All channels
  %(prog)s image.tif --channel red      # Red channel only
  %(prog)s image.tif -c green           # Green channel only (short form)
  %(prog)s image.tif --channel blue     # Blue channel only
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the input TIFF file'
    )
    
    parser.add_argument(
        '-c', '--channel',
        type=str,
        default="all",
        help='Compute histogram for specific channel only (e.g., red, green, blue, all)'
    )
    
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation (default: 2, use 0 for compact)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Path to output JSON file. If not specified, results are printed to stdout'
    )

    args = parser.parse_args()
    
    file_path = args.input_file
    
    # Validate input file
    if not os.path.exists(file_path):
        error_result = {
            "success": False,
            "error": f"File not found: {file_path}",
            "filename": file_path
        }
        output_json = json.dumps(error_result, indent=args.indent)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
        else:
            print(output_json)
        sys.exit(1)
    
    # Compute histogram
    result = compute_histogram_tiff(file_path, args.channel)

    # Prepare JSON output
    if args.indent == 0:
        output_json = json.dumps(result, separators=(',', ':'))
    else:
        output_json = json.dumps(result, indent=args.indent)

    # Write output based on arguments
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
            if not result["success"]:
                sys.exit(1)
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Failed to write output file: {str(e)}",
                "original_result": result
            }
            print(json.dumps(error_result, indent=args.indent), file=sys.stderr)
            sys.exit(1)
    else:
        # Standard stdout output
        print(output_json)
        if not result["success"]:
            sys.exit(1)

if __name__ == '__main__':
    main()