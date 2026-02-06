# Cloud Rosetta Testing Guide

This document explains how to test Cloud Rosetta to ensure the translation and cost estimation functionality works correctly.

## Quick Tests

### 1. Translation Logic Test
```bash
# Test core translation functionality
./quick_test.sh
```

This tests:
- PASSED Resource type mappings (aws_instance -> openstack_compute_instance_v2)
- PASSED Instance type mappings (t3.micro -> d2-2)  
- PASSED Database connectivity
- PASSED Statistics generation

### 2. Unit Tests
```bash
# Test detailed translation logic
python3 test_translation_logic.py
```

This tests:
- PASSED Database operations
- PASSED Resource mappings
- PASSED Instance type mappings
- PASSED Module imports

## Integration Tests

### Test with AWS Resources
Create a directory with AWS Terraform resources and test translation:

```bash
# 1. Create test directory
mkdir test_aws && cd test_aws

# 2. Create simple AWS infrastructure
cat > main.tf << EOF
resource "aws_instance" "test" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t3.micro"
}

resource "aws_ebs_volume" "storage" {
  size = 20
  type = "gp3"
}
EOF

# 3. Test translation to different providers
../rosetta --provider aws      # Baseline AWS costs
../rosetta --provider ovh      # Translate to OVH
../rosetta --provider hetzner  # Translate to Hetzner
```

## Expected Results

### Working Translation
When translation works correctly, you should see:

```
PASSED Resource mappings found:
  aws_instance -> ovh: openstack_compute_instance_v2
  aws_ebs_volume -> ovh: openstack_blockstorage_volume_v3

PASSED Instance mappings found:
  aws t3.micro -> ovh: d2-2 (1 vCPU, 2GB RAM)

PASSED Cost estimation: > $0.00 (actual costs, not $0.00)
```

### Common Issues

#### FAILED $0.00 Costs
If you see `$0.00` in cost estimation:
1. Check that resources are being translated (run `quick_test.sh`)
2. Verify the source Terraform has AWS resources (not OVH/OpenStack)
3. Check that Infracost recognizes the translated resources

#### FAILED Translation Errors
If resources aren't being mapped:
1. Run `python3 test_translation_logic.py` to check database
2. Verify resource exists in `resource_mappings` table
3. Check that resource type names match exactly

#### FAILED Import Errors
If modules can't be imported:
1. Check that `scripts/` directory contains all Python files
2. Verify file permissions (`chmod +x rosetta`)
3. Run basic syntax check: `python3 -m py_compile rosetta`

## Test Files Included

- `test_simple_aws.tf` - Basic AWS infrastructure
- `test_simple_ovh.tf` - Basic OVH infrastructure  
- `test_simple_hetzner.tf` - Basic Hetzner infrastructure
- `test_rosetta.sh` - Full integration test suite
- `quick_test.sh` - Fast translation logic verification
- `test_translation_logic.py` - Unit tests for translation logic

## Pre-commit Testing

Before committing code changes:

```bash
# 1. Check Python syntax
find scripts/ -name "*.py" -exec python3 -m py_compile {} \;
python3 -m py_compile rosetta

# 2. Test core functionality
./quick_test.sh

# 3. Test translation logic
python3 test_translation_logic.py

# 4. Test with sample AWS project (optional)
./test_rosetta.sh
```

## Troubleshooting

### Database Issues
```bash
# Check database contents
python3 -c "
import sqlite3
conn = sqlite3.connect('db/cloud_rosetta.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM resource_mappings')
print('Resource mappings:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(*) FROM instance_types')  
print('Instance types:', cursor.fetchone()[0])
conn.close()
"
```

### Translation Issues
```bash
# Test specific resource mapping
python3 -c "
import sys; sys.path.append('scripts')
from database_manager import CloudRosettaDB
db = CloudRosettaDB('db/cloud_rosetta.db')
print('aws_instance ->', db.map_resource_type('aws_instance', 'ovh'))
db.close()
"
```

### Infracost Issues
```bash
# Test Infracost directly
echo '{}' | infracost diff --path - --format json
```

## Adding New Tests

To add a new test case:

1. Create a `.tf` file with the resources to test
2. Add test logic to `test_rosetta.sh`
3. Update this documentation
4. Test the new scenario manually
5. Add to automated test suite

Example test case:
```bash
# In test_rosetta.sh
run_test "New Feature Test" "test_new_feature.tf" "ovh" "expected_resource"
```