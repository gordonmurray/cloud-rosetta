# Cloud Rosetta Tests

This directory contains all testing files for Cloud Rosetta.

## Structure

```
tests/
├── README.md                 # This file
├── TESTING.md               # Detailed testing guide
├── quick_test.sh            # Fast verification (30s)
├── test_translation_logic.py # Unit tests for translation logic
├── test_rosetta.sh          # Full integration test suite
└── fixtures/                # Test Terraform files
    ├── test_simple_aws.tf    # AWS test infrastructure
    ├── test_simple_ovh.tf    # OVH test infrastructure
    └── test_simple_hetzner.tf # Hetzner test infrastructure
```

## Quick Start

```bash
# Run from project root directory
cd tests/

# Quick verification (30 seconds)
./quick_test.sh

# Unit tests (1 minute)
python3 test_translation_logic.py

# Full integration tests (5 minutes)
./test_rosetta.sh
```

## What Each Test Does

### `quick_test.sh`
- Tests core translation mappings
- Tests instance type mappings  
- Shows database statistics
- Verifies database connectivity

**Use when:** You want to quickly verify core functionality is working

### `test_translation_logic.py`
- Tests database operations
- Tests resource mappings
- Tests instance type mappings
- Tests module imports

**Use when:** You've made changes to translation logic or database

### `test_rosetta.sh`
- Tests full workflow with Terraform files
- Tests multiple cloud providers
- Tests resource translation
- Tests cost estimation

**Use when:** You want to test the complete user workflow

## Test Files (fixtures/)

### `test_simple_aws.tf`
Basic AWS infrastructure for testing:
- `aws_instance` with t3.micro
- `aws_vpc` with subnets
- `aws_ebs_volume` for storage

### `test_simple_ovh.tf`
Basic OVH infrastructure for testing:
- `ovh_cloud_project_compute_instance`
- `ovh_cloud_project_network_private`
- Network subnet

### `test_simple_hetzner.tf`
Basic Hetzner infrastructure for testing:
- `hcloud_server`
- `hcloud_network`
- `hcloud_volume`

## Running Tests

### From Project Root
```bash
# Quick test
tests/quick_test.sh

# Unit tests
python3 tests/test_translation_logic.py

# Integration tests
tests/test_rosetta.sh
```

### From tests/ Directory
```bash
cd tests/
./quick_test.sh
python3 test_translation_logic.py
./test_rosetta.sh
```

## Expected Results

When everything is working correctly:

```
Translation logic test completed!
Resource mappings: aws_instance -> openstack_compute_instance_v2
Instance mappings: t3.micro -> d2-2
Cost estimation: > $0.00 (not $0.00)
```

## Troubleshooting

If tests fail, check:
1. Database exists: `../db/cloud_rosetta.db`
2. Scripts directory exists: `../scripts/`
3. Python modules can be imported
4. Terraform/OpenTofu is installed
5. Infracost is installed (for integration tests)

## Adding New Tests

To add new test cases:
1. Create new `.tf` files in `fixtures/`
2. Add test logic to `test_rosetta.sh`
3. Update this README
4. Test manually first

See `TESTING.md` for detailed testing guide.