#!/bin/bash
# This script demonstrates how to sweep a parameter on 2 hosts
# and access/view all resulting data from the same web page
#
# It's recommended that you setup password-less ssh between all
# machines in your cluster prior to running this script.


# Required variables
export WORKLOAD_NAME=EXAMPLE              # A short name for this type of workload
export DESCRIPTION="Sweep CPU load on 2 hosts"  # A description of this particular workload

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages

# To run on hosts other than the local node, export the "HOSTS" variable
# We will simulate this by running on "localhost" and the string returned by 
# the "hostname" command
export HOSTS="localhost $(hostname)"    # space delimited

# For sweeps, create a run directory where all files will be saved
# Specify it directly, like this:
#export RUNDIR=path/to/your/directory
# or use this python script to create one automatically (recommended)
export RUNDIR=`./create-rundir.sh`

for CPU in 1 2 4; do
  export WORKLOAD_CMD="./load_cpu.sh $CPU"   # The workload to run
  export RUN_ID="NUM_CPU=$CPU"               # Unique for this run
  ./run-and-measure.sh
done

