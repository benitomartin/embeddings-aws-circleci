#!/bin/bash

# Exit immediately if a command fails
set -e

# Define script paths
SCRIPT1="scripts/create_roles.sh"
SCRIPT2="scripts/create_image.sh"
SCRIPT3="scripts/create_lambda.sh"

# Ensure scripts are executable
chmod +x $SCRIPT1 $SCRIPT2 $SCRIPT3

# Run the scripts sequentially
echo "Running Script 1..."
$SCRIPT1

echo "Running Script 2..."
$SCRIPT2

echo "Running Script 3..."
$SCRIPT3

echo "All scripts executed successfully!"
