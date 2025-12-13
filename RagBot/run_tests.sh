#!/bin/bash

# 1. Clear previous coverage data to start fresh
coverage erase

# 2. Loop through every test file
for f in tests/test_*.py; do
    echo "Running test file: $f"

    # 3. Run pytest for the specific file
    # --cov-append: Adds this file's coverage to the total, rather than overwriting
    # We DO NOT generate the xml report in the loop, only the raw .coverage data
    pytest "$f" --cov=src --cov-append --junitxml="test-results-$(basename $f).xml"

    # Check for failure and exit immediately if you want strictly clean runs
    if [ $? -ne 0 ]; then
        echo "Tests failed in $f"
        exit 1
    fi
done

# 4. Generate the single coverage XML report from the accumulated data
coverage xml -o coverage.xml