#!/bin/bash

# Exit on error
set -e

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    docker-compose down
}

# Set up trap to ensure cleanup runs even if script fails
trap cleanup EXIT

# Install test dependencies if they don't exist
if [ ! -f "requirements-test.txt" ]; then
    echo "Test requirements not found. Please ensure requirements-test.txt exists."
    exit 1
fi

# Build and start the test container
echo "Building and starting test container..."
docker-compose build test

# Run the tests
echo "Running tests..."
docker-compose run --rm test pytest "$@"

echo "Tests completed."
