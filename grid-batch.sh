#!/bin/bash

while getopts f:t: flag
do
    case "${flag}" in
        f) folder=${OPTARG};;
        t) timeout=${OPTARG};;
    esac
done

sample_files=($(find "$folder" -type f -name "*.sp"))
num_samples=${#sample_files[@]}
echo $num_samples

#SBATCH -w spyder[06-12]        # Use spyder
#SBATCH -c 1                   	# Number of cores
#SBATCH -t 0-00:$timeout        # Maximum run-time in D-HH:MM
#SBATCH --mem=10G               # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o hostname_%A_%a.out   # File to which STDOUT will be written
#SBATCH -e hostname_%A_%a.err   # File to which STDERR will be written
#SBATCH --array=1-$num_sample   # Number of tasks in the array


# Get the current signal_file for this task
current_sample_file=${sample_files[($SLURM_ARRAY_TASK_ID - 1)]}


#python learn_formulas.py -f "$current_sample_file" -s 15
