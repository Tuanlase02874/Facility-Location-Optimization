#!/bin/bash
mkdir -p exp_training
ARRAY=(10 20 30 40 50)
TRANSACTION_DATA=(20 50 100 200)
for array in 10 20 30 40 50;do
    for transaction in 20 30 40 50; do
        echo location_${array}_4
        python3 src/generate_training_data.py location_${array}_4.txt $transaction
        cp training/location_${array}_4/Node_0 exp_training/location_${array}_4_a${transaction}
    done
done

