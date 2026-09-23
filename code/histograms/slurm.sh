#!/bin/bash -l

#SBATCH --partition=rome
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=2G
#SBATCH --time=0:10:00

# Either use from this location if it is scheduled without modifications. 
# Or copy to a subdir, modify specifics there, then schedule from there.

module load 2025
module load Python/3.13.5-GCCcore-14.3.0

# get ROOT of the datalad repository
ROOT=../..
source $HOME/venv/bin/activate

echo "Processing $DIR"

# parallel command
srun $ROOT/code/histograms/tiffhist.py -c all pot*.tif -o histogram.json

# post-processing
$ROOT/code/histograms/visualize_histogram.py histogram.json -o histogram.png

# modify README.md
if ! grep -q "# Histogram" README.md; then
    echo -e '\n\n# Histogram\n\n![histogram.png](histogram.png)\n' >>README.md
fi

