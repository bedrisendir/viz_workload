# Currently available measurements
Here's a description of the currently available measurements.
I'll add more measurements over time.

##sys-summary
This measurement is enabled by default.

Summarizes system behavior in 4 charts:

1. System CPU [%]
2. System memory usage
3. System IO usage
4. System network usage

##cpu-heatmap 
Heatmap of all cpu threads vs. time

##interrupts  
Heatmap of interrupts summed for each cpu thread vs. time

##gpu
For systems with Nvidia GPU's and CUDA installed.

Creates 4 charts:

1. Avg GPU/MEMORY utilization
2. Power of each GPU
3. Detail GPU utilization (heatmap)
4. Detail GPU memory utilization (heatmap)

##ycsb (Yahoo Cloud Serving Benchmark)

Visualization tool considers that user might run multiple instances of YCSB. It collects data from all benchmark instances and constructs the timeline.


Place YCSB stderr/stdout files as follows:

To setup YCSB:
mkdir -p $RUNDIR/data/raw/ycsb
2>$RUNDIR/data/raw/ycsb/${RUN_ID}.${HOSTNAME}.ycsb${INSTANCE_ID}.err.txt 
1>$RUNDIR/data/raw/ycsb/${RUN_ID}.${HOSTNAME}.ycsb${INSTANCE_ID}.out.txt

Example (2 benchmark instances:
$RUNDIR/data/raw/${RUN_ID}.${HOSTNAME}.ycsb0.err.txt 
$RUNDIR/data/raw/${RUN_ID}.${HOSTNAME}.ycsb1.err.txt 
$RUNDIR/data/raw/${RUN_ID}.${HOSTNAME}.ycsb0.out.txt 
$RUNDIR/data/raw/${RUN_ID}.${HOSTNAME}.ycsb1.out.txt 

-- If there are multiple iterations for the same setting, ${RUN_ID} can be constructed in order to group experiments on the summary chart.


Creates 3 charts:

Assuming that all benchmark YCSB instances started simultaneously, parse script combines timeline and average throughput data from each instance.

1. Throughput timeline. Includes different type of operations such as (TOTAL,INSERT,READ,UPDATE,READ-MODIFY-WRITE etc.)

2. Latency timeline. Includes different type of operations such as (INSERT,READ,UPDATE,READ-MODIFY-WRITE etc.)

3. Summary of average throughputs


#How to enable measurements
Only 'sys-summary' is enabled by default. To enable more measurements in your 
script, export the MEASUREMENTS variable as shown below.

Examples:
```
export MEASUREMENTS="sys-summary cpu-heatmap interrupts"
```
```
export MEASUREMENTS="sys-summary gpu"
```
```
export MEASUREMENTS="sys-summary cpu-heatmap ycsb"
```