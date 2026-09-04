#!/bin/bash

# Maintenance script for the portfolio website

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
LOG_FILE="maintenance.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Function to log messages
log_message() {
  echo "[$DATE] $1" >> $LOG_FILE
  echo "[$DATE] $1"
}

# Start maintenance
log_message "Starting maintenance..."

# Clean up the project
log_message "Cleaning up the project..."
npm run clean

# Verify assets
log_message "Verifying assets..."
npm run verify-assets

# Optimize assets
log_message "Optimizing assets..."
npm run optimize

# Refactor templates
log_message "Refactoring templates..."
npm run refactor

# Build the project
log_message "Building the project..."
npm run build

# Check for updates
log_message "Checking for updates..."
npm outdated

# End maintenance
log_message "Maintenance completed successfully!"
