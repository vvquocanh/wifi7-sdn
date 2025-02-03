#!/bin/bash

LOG_FILE="network_diagnostics.log"
> $LOG_FILE  # Clear previous log

echo "Time,Source,Destination,Bandwidth,Latency,Packet Loss" >> $LOG_FILE

# List of stations
stations=(sta11 sta12 sta13 sta21 sta22 sta23 sta31 sta32 sta33)

# Start iperf servers on each station
for sta in "${stations[@]}"; do
    mn --wifi "${sta} iperf -s &"
done

sleep 2  # Give time for servers to start

# Perform iperf tests
for src in "${stations[@]}"; do
    for dst in "${stations[@]}"; do
        if [ "$src" != "$dst" ]; then
            OUTPUT=$(mn --wifi "$src iperf -c $dst -t 5 -y C")
            
            BANDWIDTH=$(echo "$OUTPUT" | awk -F ',' '{print $9}')
            LATENCY=$(echo "$OUTPUT" | awk -F ',' '{print $8}')
            PACKET_LOSS=$(echo "$OUTPUT" | awk -F ',' '{print $11}')
            
            echo "$(date +%s),$src,$dst,$BANDWIDTH,$LATENCY,$PACKET_LOSS" >> $LOG_FILE
        fi
    done
done

echo "Diagnostics complete. Results saved in $LOG_FILE"
