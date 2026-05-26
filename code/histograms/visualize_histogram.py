#!/usr/bin/env python3
"""
visualize_histogram.py - Visualize histograms from tiffhist.py JSON output

Usage:
    python visualize_histogram.py <input_json> [--output <output_png>]

Options:
    --output    Path to output PNG file. If not specified, displays interactively

Examples:
    python visualize_histogram.py results.json
    python visualize_histogram.py results.json --output histogram.png
"""

import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import sys

# Define channel colors
CHANNEL_COLORS = {
    "red": "#ff0000",
    "green": "#00ff00",
    "blue": "#0000ff",
    "gray": "#808080",
    "alpha": "#80008080",  # semi-transparent purple
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "yellow": "#ffff00",
    "black": "#202020",
    "Y": "#ffff00",       # Luminance
    "Cb": "#00ffff",      # Blue-difference
    "Cr": "#ff00ff",      # Red-difference
    "L": "#808080",       # Lightness
    "a": "#00ff80",       # Green-red
    "b": "#8000ff",       # Blue-yellow
    "indexed": "#808080"  # Default for indexed colors
}

def get_channel_color(channel_name):
    """Get color for a channel, defaulting to gray if not specified"""
    channel_name = channel_name.lower()
    if channel_name in CHANNEL_COLORS:
        return CHANNEL_COLORS[channel_name]
    return "#808080"  # Default gray

def visualize_histogram(json_file, output_file=None):
    """Visualize histograms from JSON file"""

    # Load JSON data
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        return False

    # Check if data is valid
    if not data.get("success", False):
        print(f"Error in JSON data: {data.get('error', 'Unknown error')}", file=sys.stderr)
        return False

    if "histogram" not in data or not data["histogram"]:
        print("No histogram data found in JSON file", file=sys.stderr)
        return False

    # Prepare figure
    file_info = data["file_info"]
    plt.figure(figsize=(12, 8))
    plt.suptitle(f"Image Histogram: {file_info['filename']} ({file_info['width']}x{file_info['height']}, {file_info['mode']})",
                 fontsize=14, y=0.98)

    # Get histogram data
    histograms = data["histogram"]
    if not isinstance(histograms, list):
        histograms = [histograms]

    max_bins = 0
    max_count = 0

    # Find max bins and max count across all channels
    for h in histograms:
        if "histogram" in h:
            max_bins = max(max_bins, len(h["histogram"]))
            max_count = max(max_count, max(h["histogram"]))
        elif "color_histogram" in h:
            # For indexed colors, not a regular histogram
            max_count = max(max_count, max(h["color_histogram"].values()))

    # Determine layout
    n_channels = len(histograms)
    if n_channels == 1:
        n_cols = 1
        n_rows = 1
        fig_height = 6
    elif n_channels <= 3:
        n_cols = n_channels
        n_rows = 1
        fig_height = 6
    else:
        n_cols = 2
        n_rows = (n_channels + 1) // 2
        fig_height = 4 * n_rows

    plt.figure(figsize=(12, fig_height))

    # Plot each channel
    for i, h in enumerate(histograms):
        plt.subplot(n_rows, n_cols, i+1)

        if "histogram" in h:
            # Regular histogram
            color = get_channel_color(h["channel"])
            bins = len(h["histogram"])

            # Plot histogram
            plt.bar(range(bins), h["histogram"], color=color, width=1.0)

            # Add basic stats as text
            stats_text = f"Min: {h['min']}\nMax: {h['max']}\nMean: {h['mean']:.2f}"
            plt.gca().text(0.95, 0.95, stats_text,
                          transform=plt.gca().transAxes,
                          ha='right', va='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # Formatting
            plt.title(f"Channel: {h['channel'].capitalize()}")
            plt.xlabel("Intensity Value")
            plt.ylabel("Pixel Count")
            plt.xlim(0, bins)

            # Set y-axis to same scale for all subplots
            plt.ylim(0, max_count * 1.1)

        elif "color_histogram" in h:
            # Indexed/palette colors
            color_hist = h["color_histogram"]
            sorted_colors = sorted(color_hist.items())

            # Create a bar chart showing each color's frequency
            x = range(len(sorted_colors))
            heights = [v for k, v in sorted_colors]
            colors = [k for k, v in sorted_colors]

            bars = plt.bar(x, heights, color=colors, width=1.0)

            # Add some basic info
            plt.title(f"Indexed Colors: {h['palette_size']} colors, {h['unique_colors']} used")
            plt.xlabel("Color Index")
            plt.ylabel("Pixel Count")
            plt.xlim(0, len(sorted_colors))

            # Make sure we can see the dark colors
            plt.gca().set_facecolor("#f0f0f0")
            plt.grid(True, linestyle='--', alpha=0.6)

            # Add stats
            stats_text = f"Total: {h['total_pixels']} px"
            plt.gca().text(0.95, 0.95, stats_text,
                          transform=plt.gca().transAxes,
                          ha='right', va='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # Set y-axis
            max_h = max(heights) if heights else 1
            plt.ylim(0, max_h * 1.1)

    # Adjust layout
    plt.tight_layout()

    # Add some metadata at the bottom
    metadata = f"File: {os.path.abspath(json_file)} | Size: {file_info['file_size_bytes']/1024:.1f} KB"
    if 'dpi' in file_info:
        metadata += f" | DPI: {file_info['dpi']['x']}x{file_info['dpi']['y']}"

    plt.figtext(0.5, 0.01, metadata, ha='center', fontsize=9)

    # Show or save the plot
    if output_file:
        try:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved histogram to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving output file: {e}", file=sys.stderr)
            return False
    else:
        plt.show()
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Visualize histograms from tiffhist.py JSON output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json                       # Show interactively
  %(prog)s input.json --output histogram.png  # Save to file
"""
    )

    parser.add_argument(
        'input_json',
        type=str,
        help='Path to JSON file from tiffhist.py'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Path to output PNG file. If not specified, displays interactively'
    )

    args = parser.parse_args()

    if not visualize_histogram(args.input_json, args.output):
        sys.exit(1)

if __name__ == '__main__':
    main()