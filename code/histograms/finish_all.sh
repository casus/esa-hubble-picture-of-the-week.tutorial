#!/bin/bash

# run from the root of the repo
ROOT=$(git rev-parse --show-toplevel)
cd $ROOT

# list all jobs
datalad slurm-finish --list-open-jobs

# finish all with one command
datalad slurm-finish
