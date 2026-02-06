#!/bin/bash

echo "Quick Cloud Rosetta Test"
echo "==========================="

# Test the translation logic directly
echo "Testing resource translation logic..."

python3 -c "
import sys
sys.path.append('../scripts')
from database_manager import CloudRosettaDB

db = CloudRosettaDB('../db/cloud_rosetta.db')

print('Testing resource mappings:')
test_resources = [
    ('aws_instance', 'ovh'),
    ('aws_instance', 'hetzner'),
    ('aws_vpc', 'ovh'),
    ('aws_ebs_volume', 'ovh'),
    ('aws_ebs_volume', 'hetzner')
]

for resource, provider in test_resources:
    mapped = db.map_resource_type(resource, provider)
    print(f'  {resource} -> {provider}: {mapped}')

print('')
print('Testing instance type mappings:')
test_instances = [
    ('aws', 't3.micro', 'ovh'),
    ('aws', 't3.small', 'hetzner'),
    ('aws', 'm5.large', 'ovh')
]

for source_prov, instance, target_prov in test_instances:
    mapped = db.find_equivalent_instance(source_prov, instance, target_prov)
    print(f'  {source_prov} {instance} -> {target_prov}: {mapped}')

db.close()
print('')
print('Translation logic test completed!')
"

echo ""
echo "Database Statistics:"
cd .. && python3 scripts/generate_stats.py | head -20 && cd tests

echo ""
echo "Quick test completed! If you see mappings above, the core logic is working."
echo ""
echo "To test full workflow:"
echo "1. Create a directory with simple AWS terraform files"
echo "2. Run: ./rosetta --provider ovh"
echo "3. Check that resources are translated and costs estimated"