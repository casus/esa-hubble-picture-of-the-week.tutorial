#!/bin/bash

# If no arguments provided, find all pot*.tif files and call this script with each one
if [ $# -eq 0 ]; then
    find . -name "pot*.tif" -print0 | while IFS= read -r -d '' file; do
        dir=`dirname $file`
        echo \"Scheduling: $dir\"
        $0 $dir
    done
    exit 0
fi

# Process single file (one argument)
echo "    Processing: $1"
cd $1
ROOT=$(git rev-parse --show-toplevel)
datalad slurm-schedule -i $PWD -o $PWD sbatch $ROOT/code/histograms/slurm.sh

