#!/bin/bash
#
#SBATCH -w spyder20        		# Use spyder
#SBATCH -c 1                   	# Number of cores
#SBATCH -N 1                    # Ensure that all cores are on one machine
#SBATCH -t 0-00:10              # Maximum run-time in D-HH:MM
#SBATCH --mem=10G               # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o hostname_%A_%a.out   # File to which STDOUT will be written
#SBATCH -e hostname_%A_%a.err   # File to which STDERR will be written
#SBATCH --array=1-48            # Number of tasks in the array


folder="test_suite" # specify the folder on which to run on

# Get the list of sample files
sample_files=($(find "$folder" -type f -name "*.sp"))

# Print the sample files
echo "Sample files:"
for sample_file in "${sample_files[@]}"; do
	echo "  $sample_file"
done

# Get the current signal_file for this task
current_sample_file=${sample_files[($SLURM_ARRAY_TASK_ID - 1)]}

#Print current sample file
echo "Current sample file: $current_sample_file"

python learn_formulas.py -f "$current_sample_file" -s 5
