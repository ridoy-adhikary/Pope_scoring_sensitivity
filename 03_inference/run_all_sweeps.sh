#!/bin/bash
# Automate the full Qwen sweep across all 4 templates
source ~/.bashrc_project
cd ~/Ridoy/Other_Projects/pope-audit

echo "========================================="
echo "Starting automated sweep sequence at $(date)"
echo "========================================="

for TEMPLATE in P1 P3 P5 P6; do
    echo ""
    echo ">>> Starting Template: $TEMPLATE at $(date) <<<"
    
    # Run the python script. The --resume logic inside the script will 
    # skip any questions that are already done.
    python 03_inference/run_sweep.py --template $TEMPLATE
    
    echo ">>> Finished Template: $TEMPLATE at $(date) <<<"
    echo "-----------------------------------------"
done

echo "========================================="
echo "ALL SWEEPS COMPLETE at $(date)"
echo "You can now run the scoring script."
echo "========================================="
