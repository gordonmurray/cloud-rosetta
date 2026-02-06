#!/usr/bin/env python3
"""
Rosetta Stone for Cloud Infrastructure v2
Database-driven translation of Terraform plans between cloud providers
"""

import json
import sys
import argparse
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('translator')

try:
    from database_manager import CloudRosettaDB
except ImportError:
    logger.error("Failed to import CloudRosettaDB from database_manager")
    sys.exit(1)


class RosettaTranslator:
    """Database-driven translator for Terraform plans between cloud providers"""
    
    def __init__(self, plan_data: Dict[str, Any], db_path: str = "cloud_rosetta.db"):
        try:
            self.plan_data = plan_data
            self.translated_plan = json.loads(json.dumps(plan_data))  # Deep copy
            logger.info(f"Initializing translator with database: {db_path}")
            self.db = CloudRosettaDB(db_path)
            self.source_provider = None
            self.target_provider = None
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            raise
        
    def detect_source_provider(self) -> str:
        """Detect the source cloud provider from the plan"""
        # Check provider names in configuration
        if "configuration" in self.plan_data:
            if "provider_config" in self.plan_data["configuration"]:
                providers = self.plan_data["configuration"]["provider_config"]
                
                if "openstack" in providers or "openstack.ovh" in providers:
                    return "ovh"
                elif "aws" in providers:
                    return "aws"
                elif "hcloud" in providers:
                    return "hetzner"
                elif "azurerm" in providers:
                    return "azure"
                elif "google" in providers:
                    return "gcp"
        
        # Check resource types as fallback
        if "resource_changes" in self.plan_data:
            for change in self.plan_data["resource_changes"]:
                if change["type"].startswith("openstack_"):
                    return "ovh"
                elif change["type"].startswith("aws_"):
                    return "aws"
                elif change["type"].startswith("hcloud_"):
                    return "hetzner"
                elif change["type"].startswith("azurerm_"):
                    return "azure"
                elif change["type"].startswith("google_"):
                    return "gcp"
        
        return "unknown"
    
    def translate_instance_values(self, values: Dict[str, Any], 
                                 original_type: str) -> Dict[str, Any]:
        """Translate instance values using database mappings"""
        translated = {}
        
        # Map instance type/flavor
        if "flavor_name" in values:  # OVH
            flavor = values["flavor_name"]
            instance_type = self.db.find_equivalent_instance(
                self.source_provider, flavor, self.target_provider
            )
            if instance_type:
                if self.target_provider == "aws":
                    translated["instance_type"] = instance_type
                elif self.target_provider == "hetzner":
                    translated["server_type"] = instance_type
                print(f"  Mapped {self.source_provider} '{flavor}' → {self.target_provider} '{instance_type}'", 
                      file=sys.stderr)
        elif "instance_type" in values:  # AWS
            instance_type = values["instance_type"]
            mapped_type = self.db.find_equivalent_instance(
                self.source_provider, instance_type, self.target_provider
            )
            if mapped_type:
                if self.target_provider == "ovh":
                    translated["flavor_name"] = mapped_type
                elif self.target_provider == "hetzner":
                    translated["server_type"] = mapped_type
                print(f"  Mapped {self.source_provider} '{instance_type}' → {self.target_provider} '{mapped_type}'",
                      file=sys.stderr)
        elif "server_type" in values:  # Hetzner
            server_type = values["server_type"]
            mapped_type = self.db.find_equivalent_instance(
                self.source_provider, server_type, self.target_provider
            )
            if mapped_type:
                if self.target_provider == "aws":
                    translated["instance_type"] = mapped_type
                elif self.target_provider == "ovh":
                    translated["flavor_name"] = mapped_type
                print(f"  Mapped {self.source_provider} '{server_type}' → {self.target_provider} '{mapped_type}'",
                      file=sys.stderr)
        
        # Map region
        region_field = None
        if "region" in values:
            region_field = "region"
        elif "location" in values:
            region_field = "location"
        elif "availability_zone" in values:
            region_field = "availability_zone"
        
        if region_field:
            source_region = values[region_field]
            # For AWS availability zones, extract region
            if self.source_provider == "aws" and source_region.endswith(('a', 'b', 'c', 'd')):
                source_region = source_region[:-1]
            
            target_region = self.db.find_nearest_region(
                self.source_provider, source_region, self.target_provider
            )
            if target_region:
                if self.target_provider == "aws":
                    translated["availability_zone"] = f"{target_region}a"
                elif self.target_provider == "hetzner":
                    translated["location"] = target_region
                else:
                    translated["region"] = target_region
                print(f"  Mapped region '{values[region_field]}' → '{target_region}'", 
                      file=sys.stderr)
        
        # Map image/OS
        if "image_name" in values:  # OVH
            # Query database for equivalent image
            self.db.cursor.execute("""
                SELECT i2.image_name 
                FROM images i1
                JOIN images i2 ON i1.os_family = i2.os_family 
                              AND i1.os_version = i2.os_version
                WHERE i1.provider = ? AND i1.image_name = ?
                  AND i2.provider = ?
                LIMIT 1
            """, (self.source_provider, values["image_name"], self.target_provider))
            result = self.db.cursor.fetchone()
            if result:
                if self.target_provider == "aws":
                    translated["ami"] = result[0]
                elif self.target_provider == "hetzner":
                    translated["image"] = result[0]
                else:
                    translated["image_name"] = result[0]
                print(f"  Mapped image '{values['image_name']}' → '{result[0]}'", 
                      file=sys.stderr)
        
        # Direct mappings that work across providers
        if "name" in values:
            if self.target_provider == "aws":
                translated["tags"] = {"Name": values["name"]}
            else:
                translated["name"] = values["name"]
        
        if "key_pair" in values:
            if self.target_provider == "aws":
                translated["key_name"] = values["key_pair"]
            elif self.target_provider == "hetzner":
                translated["ssh_keys"] = [values["key_pair"]]
        
        if "user_data" in values:
            translated["user_data"] = values["user_data"]
        
        # Network configuration
        if "network" in values and len(values["network"]) > 0:
            if self.target_provider == "aws":
                translated["associate_public_ip_address"] = True
        
        # Security groups (AWS specific)
        if "security_groups" in values and self.target_provider == "aws":
            translated["vpc_security_group_ids"] = values["security_groups"]
        
        return translated
    
    def translate_provider_name(self, provider: str) -> str:
        """Translate provider names"""
        provider_map = {
            "ovh": "registry.terraform.io/hashicorp/aws",
            "aws": "registry.terraform.io/hashicorp/aws",
            "hetzner": "registry.terraform.io/hetznercloud/hcloud",
            "azure": "registry.terraform.io/hashicorp/azurerm",
            "gcp": "registry.terraform.io/hashicorp/google"
        }
        
        if "openstack" in provider.lower():
            return provider_map.get(self.target_provider, provider)
        elif "aws" in provider.lower():
            return provider_map.get(self.target_provider, provider)
        elif "hcloud" in provider.lower():
            return provider_map.get(self.target_provider, provider)
        
        return provider
    
    def translate(self, target_provider: str) -> Dict[str, Any]:
        """Main translation method"""
        try:
            self.source_provider = self.detect_source_provider()
            self.target_provider = target_provider
            
            logger.info(f"Starting translation from {self.source_provider} to {target_provider}")
            print(f"Translating from {self.source_provider.upper()} to {target_provider.upper()}...", 
                  file=sys.stderr)
            
            # Translate planned values resources
            if "planned_values" in self.translated_plan:
                if "root_module" in self.translated_plan["planned_values"]:
                    if "resources" in self.translated_plan["planned_values"]["root_module"]:
                        for resource in self.translated_plan["planned_values"]["root_module"]["resources"]:
                            original_type = resource["type"]
                            
                            # Map resource type using database
                            new_type = self.db.map_resource_type(original_type, target_provider)
                            if new_type:
                                resource["type"] = new_type
                                resource["provider_name"] = self.translate_provider_name(resource["provider_name"])
                                
                                print(f"\nProcessing: {resource['address']}", file=sys.stderr)
                                print(f"  Resource type: {original_type} → {new_type}", file=sys.stderr)
                                
                                # Translate values for compute instances
                                if "compute" in original_type or "instance" in original_type or "server" in original_type:
                                    resource["values"] = self.translate_instance_values(
                                        resource["values"], original_type
                                    )
                                
                                # Clean up provider-specific fields
                                self.cleanup_values(resource["values"])
            
            # Translate resource changes
            if "resource_changes" in self.translated_plan:
                for change in self.translated_plan["resource_changes"]:
                    original_type = change["type"]
                    
                    # Map resource type using database
                    new_type = self.db.map_resource_type(original_type, target_provider)
                    if new_type:
                        change["type"] = new_type
                        change["provider_name"] = self.translate_provider_name(change["provider_name"])
                        
                        if "change" in change and "after" in change["change"]:
                            print(f"\nProcessing change: {change['address']}", file=sys.stderr)
                            print(f"  Resource type: {original_type} → {new_type}", file=sys.stderr)
                            
                            # Translate values for compute instances
                            if "compute" in original_type or "instance" in original_type or "server" in original_type:
                                change["change"]["after"] = self.translate_instance_values(
                                    change["change"]["after"], original_type
                                )
                            
                            # Clean up provider-specific fields
                            self.cleanup_values(change["change"]["after"])
            
            # Update provider configuration
            self.update_provider_config()
            
            logger.info("Translation completed successfully")
            print("\nDone: Translation complete!", file=sys.stderr)
            return self.translated_plan
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def cleanup_values(self, values: Dict[str, Any]):
        """Remove provider-specific fields that don't translate"""
        if not values:
            return
        
        # Fields to remove based on source provider
        ovh_specific = ["flavor_name", "image_name", "region", "network", "metadata",
                       "power_state", "admin_pass", "personality", "vendor_options",
                       "scheduler_hints", "network_mode", "config_drive",
                       "availability_zone_hints", "block_device", "force_delete",
                       "stop_before_destroy"]
        
        aws_specific = ["instance_type", "ami", "availability_zone", "tags",
                       "key_name", "associate_public_ip_address", 
                       "vpc_security_group_ids"]
        
        hetzner_specific = ["server_type", "image", "location", "ssh_keys",
                           "datacenter", "firewall_ids", "placement_group_id"]
        
        # Remove fields based on source provider
        if self.source_provider == "ovh":
            fields_to_remove = ovh_specific
        elif self.source_provider == "aws":
            fields_to_remove = aws_specific
        elif self.source_provider == "hetzner":
            fields_to_remove = hetzner_specific
        else:
            fields_to_remove = []
        
        for field in fields_to_remove:
            values.pop(field, None)
    
    def update_provider_config(self):
        """Update provider configuration for target provider"""
        if "configuration" not in self.translated_plan:
            return
        
        if "provider_config" not in self.translated_plan["configuration"]:
            return
        
        # Set appropriate provider config based on target
        if self.target_provider == "aws":
            self.translated_plan["configuration"]["provider_config"] = {
                "aws": {
                    "name": "aws",
                    "full_name": "registry.terraform.io/hashicorp/aws",
                    "version_constraint": "~> 5.0",
                    "expressions": {
                        "region": {"constant_value": "us-east-1"}
                    }
                }
            }
        elif self.target_provider == "hetzner":
            self.translated_plan["configuration"]["provider_config"] = {
                "hcloud": {
                    "name": "hcloud",
                    "full_name": "registry.terraform.io/hetznercloud/hcloud",
                    "version_constraint": "~> 1.42",
                    "expressions": {}
                }
            }
        elif self.target_provider == "ovh":
            self.translated_plan["configuration"]["provider_config"] = {
                "openstack": {
                    "name": "openstack",
                    "full_name": "registry.terraform.io/terraform-provider-openstack/openstack",
                    "version_constraint": "~> 1.49",
                    "expressions": {
                        "auth_url": {"constant_value": "https://auth.cloud.ovh.net/v3"},
                        "domain_name": {"constant_value": "Default"}
                    }
                }
            }
        elif self.target_provider == "azure":
            self.translated_plan["configuration"]["provider_config"] = {
                "azurerm": {
                    "name": "azurerm",
                    "full_name": "registry.terraform.io/hashicorp/azurerm",
                    "version_constraint": "~> 3.0",
                    "expressions": {
                        "features": {"constant_value": {}}
                    }
                }
            }
        elif self.target_provider == "gcp":
            self.translated_plan["configuration"]["provider_config"] = {
                "google": {
                    "name": "google",
                    "full_name": "registry.terraform.io/hashicorp/google",
                    "version_constraint": "~> 5.0",
                    "expressions": {
                        "project": {"constant_value": "my-project"},
                        "region": {"constant_value": "us-central1"}
                    }
                }
            }
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Cloud Rosetta Translator v2 - Database-driven cloud plan translation"
        )
        parser.add_argument("input_file", help="Input Terraform plan JSON file")
        parser.add_argument("-t", "--target", required=True, 
                           choices=["aws", "ovh", "hetzner"],
                           help="Target cloud provider")
        parser.add_argument("-o", "--output", help="Output file (default: stdout)")
        parser.add_argument("--db", default="cloud_rosetta.db", 
                           help="Database file path")
        
        args = parser.parse_args()
        
        # Set logging level
        if hasattr(args, 'verbose') and args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Read input plan
        logger.info(f"Reading input plan: {args.input_file}")
        with open(args.input_file, 'r') as f:
            plan_data = json.load(f)
    
        # Translate
        translator = RosettaTranslatorV2(plan_data, args.db)
        translated_plan = translator.translate(args.target)
    
        # Output
        output_json = json.dumps(translated_plan, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            logger.info(f"Translated plan saved to: {args.output}")
            print(f"\nTranslated plan saved to: {args.output}", file=sys.stderr)
        else:
            print(output_json)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {e}")
        print(f"ERROR: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()