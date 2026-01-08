#!/bin/bash

# CAN Interface Configuration (vcan0)
echo "[INFO] Configuring Virtual CAN interface..."
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan 2>/dev/null || echo "[INFO] vcan0 already exists"
sudo ip link set up vcan0

# UART Virtual Bridge Configuration
# ttyV0: Test Suite endpoint | ttyV1: Simulator endpoint
echo "[INFO] Creating virtual UART bridge (/tmp/ttyV0 <-> /tmp/ttyV1)..."
socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0 &
SOCAT_PID=$!

echo "------------------------------------------------"
echo "SIMULATION ENVIRONMENT ACTIVE:"
echo " - CAN: vcan0"
echo " - UART Test Endpoint: /tmp/ttyV0"
echo " - UART Simulator Endpoint: /tmp/ttyV1"
echo " - Ethernet: Localhost (UDP)"
echo "------------------------------------------------"

# Store PID for cleanup
echo $SOCAT_PID > .socat.pid
echo "[INFO] To terminate the environment, run: kill \$(cat .socat.pid)"