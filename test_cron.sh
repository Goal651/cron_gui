#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$DIR/cron_test.log"

# Write timestamp to log file
echo "Cron job executed at: $(date)" >> "$LOG_FILE"
