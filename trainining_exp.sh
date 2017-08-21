#!/bin/bash
mkdir -p exp_training_log
for entry in `ls exp_training`; do
    ts=$(date +%s%N)
    ./estimate/FL exp_training/$entry | tee exp_training_log/$entry.log
    end=`date +%s`
    tt=$((($(date +%s%N) - $ts)/1000000))
    echo $entry : $tt >> training_running_time.log
done