#!/bin/bash

# Quick script to check LAFAN training status

echo "==================================================================="
echo "LAFAN1 Imitation Learning Training Status"
echo "==================================================================="
echo ""

# Check if training is running
if ps aux | grep -v grep | grep train_deepmimic > /dev/null; then
    echo "✅ Training is RUNNING"
    echo ""
    echo "Process:"
    ps aux | grep -v grep | grep train_deepmimic | awk '{print "  PID: "$2", CPU: "$3"%, MEM: "$4"%"}'
    echo ""
else
    echo "❌ Training is NOT running"
    echo ""
fi

# Show recent log output
if [ -f training_lafan.log ]; then
    echo "Recent log (last 15 lines):"
    echo "-------------------------------------------------------------------"
    tail -15 training_lafan.log
    echo "-------------------------------------------------------------------"
    echo ""
    echo "Full log: training_lafan.log"
else
    echo "No log file found yet"
fi

echo ""
echo "Commands:"
echo "  Monitor: tail -f training_lafan.log"
echo "  TensorBoard: tensorboard --logdir src/g1_imitation/checkpoints/"
echo "  Stop: pkill -f train_deepmimic"
echo ""
