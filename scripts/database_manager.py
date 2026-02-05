#!/usr/bin/env python3
"""
Cloud Rosetta Database Manager
Universal cloud resource mapping database for cost estimation
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

@dataclass
class InstanceMapping:
    """Represents an instance type mapping between clouds"""
    provider: str
    instance_type: str
    vcpu: int
    memory_gb: float
    family: str
    generation: str
    
@dataclass
class RegionMapping:
    """Represents a region mapping between clouds"""
    provider: str
    region_code: str
    region_name: str
    latitude: float
    longitude: float
    

class CloudRosettaDB:
    """Manages the cloud resource mapping database"""
    
    def __init__(self, db_path: str = "cloud_rosetta.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_schema()
        
    def _create_schema(self):
        """Create database schema if it doesn't exist"""
        
        # Instance types table - stores all instance types from all providers
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS instance_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                instance_type TEXT NOT NULL,
                vcpu INTEGER NOT NULL,
                memory_gb REAL NOT NULL,
                family TEXT,  -- general, compute, memory, etc
                generation TEXT,  -- current, previous, etc
                network_performance TEXT,
                storage_type TEXT,
                storage_gb INTEGER,
                gpu_count INTEGER DEFAULT 0,
                gpu_type TEXT,
                hourly_price REAL,  -- optional, for reference
                notes TEXT,
                UNIQUE(provider, instance_type)
            )
        """)
        
        # Regions table - stores all regions from all providers
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                region_code TEXT NOT NULL,
                region_name TEXT NOT NULL,
                country TEXT,
                continent TEXT,
                latitude REAL,
                longitude REAL,
                UNIQUE(provider, region_code)
            )
        """)
        
        # Resource types mapping table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_category TEXT NOT NULL,  -- compute, storage, network, etc
                terraform_type TEXT,  -- The actual Terraform resource type
                UNIQUE(provider, terraform_type)
            )
        """)
        
        # Images/OS mapping table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                image_name TEXT NOT NULL,
                os_family TEXT NOT NULL,  -- ubuntu, debian, centos, windows, etc
                os_version TEXT,
                architecture TEXT DEFAULT 'x86_64',
                UNIQUE(provider, image_name)
            )
        """)
        
        # Create indexes for better query performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_instance_specs 
            ON instance_types(vcpu, memory_gb, family)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_region_location 
            ON regions(latitude, longitude)
        """)
        
        self.conn.commit()
    
    def populate_initial_data(self):
        """Populate database with initial mappings"""
        
        # Instance types - OVH
        ovh_instances = [
            # d2 series (flex/development)
            ("ovh", "d2-2", 1, 2, "general", "current", None, "ssd", 20, 0, None, 0.0084),
            ("ovh", "d2-4", 2, 4, "general", "current", None, "ssd", 40, 0, None, 0.0168),
            ("ovh", "d2-8", 4, 8, "general", "current", None, "ssd", 80, 0, None, 0.0337),
            
            # b2 series (balanced)
            ("ovh", "b2-7", 2, 7, "general", "current", "moderate", "ssd", 50, 0, None, 0.0278),
            ("ovh", "b2-15", 4, 15, "general", "current", "high", "ssd", 100, 0, None, 0.0556),
            ("ovh", "b2-30", 8, 30, "general", "current", "high", "ssd", 200, 0, None, 0.1111),
            ("ovh", "b2-60", 16, 60, "general", "current", "high", "ssd", 400, 0, None, 0.2222),
            ("ovh", "b2-120", 32, 120, "general", "current", "very-high", "ssd", 400, 0, None, 0.4444),
            
            # c2 series (compute optimized)
            ("ovh", "c2-7", 2, 7, "compute", "current", "moderate", "ssd", 50, 0, None, 0.0417),
            ("ovh", "c2-15", 4, 15, "compute", "current", "high", "ssd", 100, 0, None, 0.0833),
            ("ovh", "c2-30", 8, 30, "compute", "current", "high", "ssd", 200, 0, None, 0.1667),
            ("ovh", "c2-60", 16, 60, "compute", "current", "very-high", "ssd", 400, 0, None, 0.3333),
            
            # r2 series (memory optimized)
            ("ovh", "r2-15", 2, 15, "memory", "current", "moderate", "ssd", 50, 0, None, 0.0556),
            ("ovh", "r2-30", 4, 30, "memory", "current", "high", "ssd", 100, 0, None, 0.1111),
            ("ovh", "r2-60", 8, 60, "memory", "current", "high", "ssd", 200, 0, None, 0.2222),
            ("ovh", "r2-120", 16, 120, "memory", "current", "very-high", "ssd", 400, 0, None, 0.4444),
        ]
        
        # Instance types - AWS (subset for mapping)
        aws_instances = [
            # t3 series (burstable)
            ("aws", "t3.nano", 2, 0.5, "burstable", "current", "low", "ebs", None, 0, None, 0.0052),
            ("aws", "t3.micro", 2, 1, "burstable", "current", "low", "ebs", None, 0, None, 0.0104),
            ("aws", "t3.small", 2, 2, "burstable", "current", "low", "ebs", None, 0, None, 0.0208),
            ("aws", "t3.medium", 2, 4, "burstable", "current", "moderate", "ebs", None, 0, None, 0.0416),
            ("aws", "t3.large", 2, 8, "burstable", "current", "moderate", "ebs", None, 0, None, 0.0832),
            
            # m5 series (general purpose)
            ("aws", "m5.large", 2, 8, "general", "current", "moderate", "ebs", None, 0, None, 0.096),
            ("aws", "m5.xlarge", 4, 16, "general", "current", "high", "ebs", None, 0, None, 0.192),
            ("aws", "m5.2xlarge", 8, 32, "general", "current", "high", "ebs", None, 0, None, 0.384),
            ("aws", "m5.4xlarge", 16, 64, "general", "current", "very-high", "ebs", None, 0, None, 0.768),
            ("aws", "m5.8xlarge", 32, 128, "general", "current", "10gbps", "ebs", None, 0, None, 1.536),
            
            # c5 series (compute optimized)
            ("aws", "c5.large", 2, 4, "compute", "current", "moderate", "ebs", None, 0, None, 0.085),
            ("aws", "c5.xlarge", 4, 8, "compute", "current", "high", "ebs", None, 0, None, 0.17),
            ("aws", "c5.2xlarge", 8, 16, "compute", "current", "high", "ebs", None, 0, None, 0.34),
            ("aws", "c5.4xlarge", 16, 32, "compute", "current", "very-high", "ebs", None, 0, None, 0.68),
            
            # r5 series (memory optimized)
            ("aws", "r5.large", 2, 16, "memory", "current", "moderate", "ebs", None, 0, None, 0.126),
            ("aws", "r5.xlarge", 4, 32, "memory", "current", "high", "ebs", None, 0, None, 0.252),
            ("aws", "r5.2xlarge", 8, 64, "memory", "current", "high", "ebs", None, 0, None, 0.504),
            ("aws", "r5.4xlarge", 16, 128, "memory", "current", "very-high", "ebs", None, 0, None, 1.008),
        ]
        
        # Instance types - Hetzner
        hetzner_instances = [
            ("hetzner", "cx11", 1, 2, "general", "current", "20TB", "ssd", 20, 0, None, 0.0052),
            ("hetzner", "cx21", 2, 4, "general", "current", "20TB", "ssd", 40, 0, None, 0.0089),
            ("hetzner", "cx31", 2, 8, "general", "current", "20TB", "ssd", 80, 0, None, 0.0137),
            ("hetzner", "cx41", 4, 16, "general", "current", "20TB", "ssd", 160, 0, None, 0.0274),
            ("hetzner", "cx51", 8, 32, "general", "current", "20TB", "ssd", 240, 0, None, 0.0548),
            
            ("hetzner", "cpx11", 2, 2, "general", "current", "20TB", "ssd", 40, 0, None, 0.0068),
            ("hetzner", "cpx21", 3, 4, "general", "current", "20TB", "ssd", 80, 0, None, 0.0116),
            ("hetzner", "cpx31", 4, 8, "general", "current", "20TB", "ssd", 160, 0, None, 0.0219),
            ("hetzner", "cpx41", 8, 16, "general", "current", "20TB", "ssd", 240, 0, None, 0.0438),
        ]
        
        # Insert instance types
        for instance in ovh_instances + aws_instances + hetzner_instances:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO instance_types 
                    (provider, instance_type, vcpu, memory_gb, family, generation, 
                     network_performance, storage_type, storage_gb, gpu_count, gpu_type, hourly_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, instance)
            except sqlite3.IntegrityError:
                pass  # Ignore duplicates
        
        # Regions
        regions = [
            # OVH regions
            ("ovh", "GRA9", "Gravelines, France", "France", "Europe", 50.987, 2.762),
            ("ovh", "GRA11", "Gravelines, France", "France", "Europe", 50.987, 2.762),
            ("ovh", "SBG5", "Strasbourg, France", "France", "Europe", 48.573, 7.752),
            ("ovh", "RBX", "Roubaix, France", "France", "Europe", 50.694, 3.174),
            ("ovh", "DE1", "Frankfurt, Germany", "Germany", "Europe", 50.110, 8.682),
            ("ovh", "UK1", "London, UK", "UK", "Europe", 51.507, -0.127),
            ("ovh", "WAW1", "Warsaw, Poland", "Poland", "Europe", 52.229, 21.012),
            ("ovh", "BHS5", "Beauharnois, Canada", "Canada", "North America", 45.315, -73.874),
            ("ovh", "SGP1", "Singapore", "Singapore", "Asia", 1.352, 103.819),
            ("ovh", "SYD1", "Sydney, Australia", "Australia", "Oceania", -33.868, 151.209),
            
            # AWS regions (subset)
            ("aws", "us-east-1", "N. Virginia, USA", "USA", "North America", 38.747, -77.517),
            ("aws", "us-west-2", "Oregon, USA", "USA", "North America", 45.523, -122.676),
            ("aws", "eu-west-1", "Ireland", "Ireland", "Europe", 53.349, -6.260),
            ("aws", "eu-west-2", "London, UK", "UK", "Europe", 51.507, -0.127),
            ("aws", "eu-west-3", "Paris, France", "France", "Europe", 48.856, 2.352),
            ("aws", "eu-central-1", "Frankfurt, Germany", "Germany", "Europe", 50.110, 8.682),
            ("aws", "ap-southeast-1", "Singapore", "Singapore", "Asia", 1.352, 103.819),
            ("aws", "ap-southeast-2", "Sydney, Australia", "Australia", "Oceania", -33.868, 151.209),
            ("aws", "ca-central-1", "Montreal, Canada", "Canada", "North America", 45.501, -73.567),
            
            # Hetzner regions
            ("hetzner", "nbg1", "Nuremberg, Germany", "Germany", "Europe", 49.452, 11.077),
            ("hetzner", "fsn1", "Falkenstein, Germany", "Germany", "Europe", 50.478, 12.337),
            ("hetzner", "hel1", "Helsinki, Finland", "Finland", "Europe", 60.169, 24.938),
            ("hetzner", "ash", "Ashburn, USA", "USA", "North America", 39.043, -77.487),
        ]
        
        for region in regions:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO regions 
                    (provider, region_code, region_name, country, continent, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, region)
            except sqlite3.IntegrityError:
                pass
        
        # Resource type mappings
        resource_types = [
            # OVH/OpenStack
            ("ovh", "compute", "compute", "openstack_compute_instance_v2"),
            ("ovh", "keypair", "compute", "openstack_compute_keypair_v2"),
            ("ovh", "volume", "storage", "openstack_blockstorage_volume_v3"),
            ("ovh", "loadbalancer", "network", "openstack_lb_loadbalancer_v2"),
            ("ovh", "floating_ip", "network", "openstack_networking_floatingip_v2"),
            ("ovh", "network", "network", "openstack_networking_network_v2"),
            ("ovh", "subnet", "network", "openstack_networking_subnet_v2"),
            ("ovh", "security_group", "network", "openstack_networking_secgroup_v2"),
            ("ovh", "object_storage", "storage", "openstack_objectstorage_container_v1"),
            
            # AWS
            ("aws", "compute", "compute", "aws_instance"),
            ("aws", "keypair", "compute", "aws_key_pair"),
            ("aws", "volume", "storage", "aws_ebs_volume"),
            ("aws", "loadbalancer", "network", "aws_lb"),
            ("aws", "floating_ip", "network", "aws_eip"),
            ("aws", "network", "network", "aws_vpc"),
            ("aws", "subnet", "network", "aws_subnet"),
            ("aws", "security_group", "network", "aws_security_group"),
            ("aws", "object_storage", "storage", "aws_s3_bucket"),
            
            # Hetzner
            ("hetzner", "compute", "compute", "hcloud_server"),
            ("hetzner", "keypair", "compute", "hcloud_ssh_key"),
            ("hetzner", "volume", "storage", "hcloud_volume"),
            ("hetzner", "loadbalancer", "network", "hcloud_load_balancer"),
            ("hetzner", "floating_ip", "network", "hcloud_floating_ip"),
            ("hetzner", "network", "network", "hcloud_network"),
            ("hetzner", "subnet", "network", "hcloud_network_subnet"),
        ]
        
        for rt in resource_types:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO resource_types 
                    (provider, resource_type, resource_category, terraform_type)
                    VALUES (?, ?, ?, ?)
                """, rt)
            except sqlite3.IntegrityError:
                pass
        
        # OS/Image mappings
        images = [
            # OVH
            ("ovh", "Ubuntu 24.04", "ubuntu", "24.04"),
            ("ovh", "Ubuntu 22.04", "ubuntu", "22.04"),
            ("ovh", "Ubuntu 20.04", "ubuntu", "20.04"),
            ("ovh", "Debian 12", "debian", "12"),
            ("ovh", "Debian 11", "debian", "11"),
            ("ovh", "CentOS 8", "centos", "8"),
            ("ovh", "Rocky Linux 8", "rocky", "8"),
            ("ovh", "AlmaLinux 8", "almalinux", "8"),
            
            # AWS (AMI placeholders)
            ("aws", "ami-ubuntu-24.04", "ubuntu", "24.04"),
            ("aws", "ami-ubuntu-22.04", "ubuntu", "22.04"),
            ("aws", "ami-ubuntu-20.04", "ubuntu", "20.04"),
            ("aws", "ami-debian-12", "debian", "12"),
            ("aws", "ami-debian-11", "debian", "11"),
            ("aws", "ami-centos-8", "centos", "8"),
            
            # Hetzner
            ("hetzner", "ubuntu-24.04", "ubuntu", "24.04"),
            ("hetzner", "ubuntu-22.04", "ubuntu", "22.04"),
            ("hetzner", "ubuntu-20.04", "ubuntu", "20.04"),
            ("hetzner", "debian-12", "debian", "12"),
            ("hetzner", "debian-11", "debian", "11"),
            ("hetzner", "centos-8", "centos", "8"),
            ("hetzner", "rocky-8", "rocky", "8"),
            ("hetzner", "almalinux-8", "almalinux", "8"),
        ]
        
        for img in images:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO images 
                    (provider, image_name, os_family, os_version, architecture)
                    VALUES (?, ?, ?, ?, 'x86_64')
                """, img)
            except sqlite3.IntegrityError:
                pass
        
            self.conn.commit()
            total_items = self.cursor.execute("SELECT COUNT(*) FROM instance_types").fetchone()[0]
            logger.info(f"Database populated successfully with {total_items} instance types")
        except sqlite3.Error as e:
            logger.error(f"Failed to populate database: {e}")
            self.conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error populating database: {e}")
            raise
    
    def find_equivalent_instance(self, source_provider: str, source_type: str, 
                                target_provider: str) -> Optional[str]:
        """Find equivalent instance type in target provider"""
        
        # First, get specs of source instance
        self.cursor.execute("""
            SELECT vcpu, memory_gb, family 
            FROM instance_types 
            WHERE provider = ? AND instance_type = ?
        """, (source_provider, source_type))
        
        source = self.cursor.fetchone()
        if not source:
            return None
        
        vcpu, memory_gb, family = source
        
        # Find best match in target provider
        # Priority: exact match > same family > closest specs
        self.cursor.execute("""
            SELECT instance_type,
                   ABS(vcpu - ?) + ABS(memory_gb - ?) * 0.5 as diff
            FROM instance_types
            WHERE provider = ?
              AND vcpu >= ? * 0.5 AND vcpu <= ? * 2
              AND memory_gb >= ? * 0.5 AND memory_gb <= ? * 2
            ORDER BY 
                CASE WHEN family = ? THEN 0 ELSE 1 END,
                diff
            LIMIT 1
        """, (vcpu, memory_gb, target_provider, 
              vcpu, vcpu, memory_gb, memory_gb, family))
            
            result = self.cursor.fetchone()
            instance = result[0] if result else None
            if instance:
                logger.debug(f"Found match: {instance}")
            else:
                logger.warning(f"No equivalent found for {source_provider}:{source_type} in {target_provider}")
            return instance
        except sqlite3.Error as e:
            logger.error(f"Database error finding equivalent instance: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding equivalent instance: {e}")
            return None
    
    def find_nearest_region(self, source_provider: str, source_region: str,
                           target_provider: str) -> Optional[str]:
        """Find nearest region in target provider based on geographic location"""
        
        # Get source region coordinates
        self.cursor.execute("""
            SELECT latitude, longitude, continent
            FROM regions
            WHERE provider = ? AND region_code = ?
        """, (source_provider, source_region))
        
        source = self.cursor.fetchone()
        if not source:
            return None
        
        lat, lon, continent = source
        
        # Find nearest region in target provider
        # Using simplified distance calculation (good enough for this purpose)
        self.cursor.execute("""
            SELECT region_code,
                   ((latitude - ?) * (latitude - ?) + 
                    (longitude - ?) * (longitude - ?)) as dist_sq
            FROM regions
            WHERE provider = ?
            ORDER BY 
                CASE WHEN continent = ? THEN 0 ELSE 1 END,
                dist_sq
            LIMIT 1
        """, (lat, lat, lon, lon, target_provider, continent))
        
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def map_resource_type(self, source_terraform_type: str, target_provider: str) -> Optional[str]:
        """Map a Terraform resource type to equivalent in target provider"""
        
        # First get the resource category from source
        self.cursor.execute("""
            SELECT resource_category
            FROM resource_types
            WHERE terraform_type = ?
        """, (source_terraform_type,))
        
        result = self.cursor.fetchone()
        if not result:
            return None
        
        category = result[0]
        
        # Find equivalent in target provider
        self.cursor.execute("""
            SELECT terraform_type
            FROM resource_types
            WHERE provider = ? AND resource_category = ?
            LIMIT 1
        """, (target_provider, category))
        
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_providers(self) -> List[str]:
        """Get list of all providers in database"""
        self.cursor.execute("SELECT DISTINCT provider FROM instance_types")
        return [row[0] for row in self.cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Cloud Rosetta Database Manager")
    parser.add_argument("command", choices=["init", "map-instance", "map-region", "map-resource", "list-providers"],
                       help="Command to execute")
    parser.add_argument("--source-provider", help="Source cloud provider")
    parser.add_argument("--source-type", help="Source instance type or region")
    parser.add_argument("--target-provider", help="Target cloud provider")
    parser.add_argument("--db", default="cloud_rosetta.db", help="Database file path")
    
    args = parser.parse_args()
    
    db = CloudRosettaDB(args.db)
    
    if args.command == "init":
        print("Initializing Cloud Rosetta database...")
        db.populate_initial_data()
        print("Done: Database initialized with mappings for OVH, AWS, and Hetzner")
        
    elif args.command == "list-providers":
        providers = db.get_providers()
        print("Available cloud providers:")
        for provider in providers:
            print(f"  • {provider}")
            
    elif args.command == "map-instance":
        if not all([args.source_provider, args.source_type, args.target_provider]):
            print("Error: --source-provider, --source-type, and --target-provider required")
            return
        
        result = db.find_equivalent_instance(args.source_provider, args.source_type, args.target_provider)
        if result:
            print(f"{args.source_provider} {args.source_type} → {args.target_provider} {result}")
        else:
            print(f"No mapping found for {args.source_provider} {args.source_type}")
            
    elif args.command == "map-region":
        if not all([args.source_provider, args.source_type, args.target_provider]):
            print("Error: --source-provider, --source-type (region), and --target-provider required")
            return
        
        result = db.find_nearest_region(args.source_provider, args.source_type, args.target_provider)
        if result:
            print(f"{args.source_provider} {args.source_type} → {args.target_provider} {result}")
        else:
            print(f"No mapping found for {args.source_provider} {args.source_type}")
            
    elif args.command == "map-resource":
        if not all([args.source_type, args.target_provider]):
            print("Error: --source-type (terraform type) and --target-provider required")
            return
        
        result = db.map_resource_type(args.source_type, args.target_provider)
        if result:
            print(f"{args.source_type} → {result}")
        else:
            print(f"No mapping found for {args.source_type}")
    
    db.close()


if __name__ == "__main__":
    main()