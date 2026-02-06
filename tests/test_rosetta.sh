#!/bin/bash

# Cloud Rosetta Integration Test Script
# Tests basic functionality with simple infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROSETTA="${SCRIPT_DIR}/../rosetta"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "TESTING Cloud Rosetta Integration Tests"
echo "=================================="

# Function to run test
run_test() {
    local test_name="$1"
    local tf_file="$2"
    local provider="$3"
    local expected_resources="$4"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    echo "File: $tf_file"
    echo "Provider: $provider"
    
    # Create test directory
    local test_dir="/tmp/rosetta_test_${provider}"
    rm -rf "$test_dir"
    mkdir -p "$test_dir"
    
    # Copy terraform file
    cp "$tf_file" "$test_dir/main.tf"
    cd "$test_dir"
    
    # Initialize terraform
    echo "  Initializing terraform..."
    terraform init -no-color > /dev/null 2>&1 || {
        echo -e "  ${RED}FAILED Terraform init failed${NC}"
        return 1
    }
    
    # Test rosetta
    echo "  Running rosetta --provider $provider..."
    local output
    if output=$($ROSETTA --provider $provider 2>&1); then
        echo -e "  ${GREEN}PASSED Rosetta executed successfully${NC}"
        
        # Check if cost was calculated (not $0.00)
        if echo "$output" | grep -q "OVERALL TOTAL.*\$0\.00"; then
            echo -e "  ${YELLOW}WARNING: Cost estimate is $0.00 - might indicate translation issues${NC}"
        else
            echo -e "  ${GREEN}PASSED Cost estimation appears to be working${NC}"
        fi
        
        # Check for expected resources in output
        if [ -n "$expected_resources" ]; then
            local found=0
            IFS=',' read -ra RESOURCES <<< "$expected_resources"
            for resource in "${RESOURCES[@]}"; do
                if echo "$output" | grep -q "$resource"; then
                    ((found++))
                fi
            done
            
            if [ $found -eq ${#RESOURCES[@]} ]; then
                echo -e "  ${GREEN}PASSED All expected resources found in output${NC}"
            else
                echo -e "  ${YELLOW}WARNING: Only $found/${#RESOURCES[@]} expected resources found${NC}"
            fi
        fi
        
        return 0
    else
        echo -e "  ${RED}FAILED Rosetta failed${NC}"
        echo "  Error output:"
        echo "$output" | sed 's/^/    /'
        return 1
    fi
}

# Test AWS baseline
echo -e "\n${YELLOW}=== AWS Tests (Baseline) ===${NC}"
run_test "AWS Simple Infrastructure" "$SCRIPT_DIR/fixtures/test_simple_aws.tf" "aws" "aws_instance,aws_vpc,aws_subnet"

# Test OVH translation
echo -e "\n${YELLOW}=== OVH Tests (Translation) ===${NC}"
run_test "OVH Simple Infrastructure" "$SCRIPT_DIR/fixtures/test_simple_ovh.tf" "ovh" "ovh_cloud_project_compute_instance"

# Test translation from AWS to OVH
echo -e "\n${YELLOW}=== Translation Tests ===${NC}"
run_test "AWS to OVH Translation" "$SCRIPT_DIR/fixtures/test_simple_aws.tf" "ovh" "aws_instance"

# Test translation from AWS to Hetzner
run_test "AWS to Hetzner Translation" "$SCRIPT_DIR/fixtures/test_simple_aws.tf" "hetzner" "aws_instance"

# Test Hetzner native
echo -e "\n${YELLOW}=== Hetzner Tests ===${NC}"
run_test "Hetzner Simple Infrastructure" "$SCRIPT_DIR/fixtures/test_simple_hetzner.tf" "hetzner" "hcloud_server"

echo -e "\n${GREEN}SUCCESS: Integration tests completed!${NC}"
echo -e "\n${YELLOW}TIPS:${NC}"
echo "  - If tests show \$0.00 costs, check resource translation logic"
echo "  - Missing resources in output might indicate mapping issues"
echo "  - Check logs for detailed error information"
echo ""
echo "To run individual tests:"
echo "  ./rosetta --provider aws    # Test AWS baseline"
echo "  ./rosetta --provider ovh    # Test OVH translation"
echo "  ./rosetta --provider hetzner # Test Hetzner translation"