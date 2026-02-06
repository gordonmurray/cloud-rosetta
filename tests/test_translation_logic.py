#!/usr/bin/env python3
"""
Unit tests for Cloud Rosetta translation logic
Tests database mappings and resource translation
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(script_dir))

def test_database_connectivity():
    """Test basic database operations"""
    try:
        from database_manager import CloudRosettaDB
        
        # Test database initialization
        db = CloudRosettaDB("../db/cloud_rosetta.db")
        
        # Test basic queries
        providers = db.get_providers()
        print(f"PASSED Database connectivity: Found {len(providers)} providers: {', '.join(providers)}")
        
        # Test instance mapping
        aws_instance = db.find_equivalent_instance("aws", "t3.micro", "ovh")
        print(f"PASSED Instance mapping: AWS t3.micro -> OVH {aws_instance}")
        
        # Test resource mapping
        ovh_resource = db.map_resource_type("aws_instance", "ovh")
        print(f"PASSED Resource mapping: aws_instance -> {ovh_resource}")
        
        db.close()
        return True
    except Exception as e:
        print(f"FAILED Database test failed: {e}")
        return False

def test_resource_mappings():
    """Test resource type mappings in database"""
    try:
        conn = sqlite3.connect("../db/cloud_rosetta.db")
        cursor = conn.cursor()
        
        # Test compute resource mappings
        cursor.execute("""
            SELECT aws_type, ovh_type, hetzner_type 
            FROM resource_mappings 
            WHERE resource_category = 'compute'
            LIMIT 5
        """)
        
        mappings = cursor.fetchall()
        print(f"PASSED Compute mappings: Found {len(mappings)} compute resource mappings")
        
        for aws, ovh, hetzner in mappings[:3]:
            print(f"    {aws} -> {ovh} -> {hetzner}")
        
        # Test that key resources exist
        key_resources = ["aws_instance", "aws_vpc", "aws_ebs_volume"]
        for resource in key_resources:
            cursor.execute("SELECT COUNT(*) FROM resource_mappings WHERE aws_type = ?", (resource,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"PASSED Key resource {resource}: Found in mappings")
            else:
                print(f"FAILED Key resource {resource}: NOT found in mappings")
        
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED Resource mapping test failed: {e}")
        return False

def test_translator_import():
    """Test translator module import and basic functionality"""
    try:
        from translator import RosettaTranslator
        
        # Create a simple test plan
        test_plan = {
            "terraform_version": "1.0.0",
            "planned_values": {
                "root_module": {
                    "resources": [
                        {
                            "address": "aws_instance.test",
                            "type": "aws_instance",
                            "values": {
                                "instance_type": "t3.micro",
                                "ami": "ami-12345"
                            }
                        }
                    ]
                }
            }
        }
        
        translator = RosettaTranslator(test_plan, "../db/cloud_rosetta.db")
        print("PASSED Translator import: Successfully created RosettaTranslator instance")
        
        # Test source provider detection
        source_provider = translator.detect_source_provider()
        print(f"PASSED Provider detection: Detected source provider as '{source_provider}'")
        
        return True
    except Exception as e:
        print(f"FAILED Translator test failed: {e}")
        return False

def test_instance_type_mappings():
    """Test instance type mappings"""
    try:
        conn = sqlite3.connect("../db/cloud_rosetta.db")
        cursor = conn.cursor()
        
        # Test AWS instances exist
        cursor.execute("SELECT COUNT(*) FROM instance_types WHERE provider = 'aws'")
        aws_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM instance_types WHERE provider = 'ovh'")
        ovh_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM instance_types WHERE provider = 'hetzner'")
        hetzner_count = cursor.fetchone()[0]
        
        print(f"PASSED Instance types: AWS({aws_count}), OVH({ovh_count}), Hetzner({hetzner_count})")
        
        # Test specific instances
        test_instances = [
            ("aws", "t3.micro"),
            ("ovh", "d2-2"), 
            ("hetzner", "cx11")
        ]
        
        for provider, instance_type in test_instances:
            cursor.execute(
                "SELECT vcpu, memory_gb FROM instance_types WHERE provider = ? AND instance_type = ?",
                (provider, instance_type)
            )
            result = cursor.fetchone()
            if result:
                vcpu, memory = result
                print(f"PASSED {provider} {instance_type}: {vcpu} vCPU, {memory}GB RAM")
            else:
                print(f"FAILED {provider} {instance_type}: NOT found")
        
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED Instance type test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("TESTING Cloud Rosetta Translation Logic Tests")
    print("=========================================")
    
    tests = [
        test_database_connectivity,
        test_resource_mappings,
        test_instance_type_mappings,
        test_translator_import,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n--- Running {test.__name__} ---")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"FAILED Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\nTEST RESULTS:")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\nSUCCESS: All tests passed!")
        return 0
    else:
        print(f"\nERROR: {failed} test(s) failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())