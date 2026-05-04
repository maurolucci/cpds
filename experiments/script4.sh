#!/bin/bash

TIMEOUT=900
NRUN=5
MAXNODES=15000
declare -a SOLVERS=("brimkov")
CASES="instances.csv"
BIN="../cpds"
INPUT="../inputs/"
OUTPUT="../outputs/exp4/"

mkdir -p $OUTPUT 

tail -n +2 $CASES | while read -r line 
do
    IFS=',' read -r index name vertices degree <<< $line
    if [ $vertices -gt $MAXNODES ]
    then
        continue
    fi
    # solve
    for solver in "${SOLVERS[@]}"
    do
        for omega in $(seq 0 $degree)
        do
            date
            time $BIN -s $solver -k $omega -f $INPUT$name -n $NRUN -t $TIMEOUT -o $OUTPUT --out-prop
        done
    done
done
