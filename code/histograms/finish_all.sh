#!/bin/bash

# run from the root of the repo
ROOT=$(git rev-parse --show-toplevel)
cd $ROOT

# list all jobs
echo datalad slurm-finish --list-open-jobs
datalad slurm-finish --list-open-jobs

# finish all with one command
echo datalad slurm-finish
datalad slurm-finish
