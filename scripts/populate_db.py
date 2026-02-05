#!/usr/bin/env python3
"""
Comprehensive Cloud Resource Database Population
Populates the database with extensive AWS, OVH, and Hetzner resource mappings
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Tuple

class ComprehensiveDBPopulator:
    def __init__(self, db_path: str = "cloud_rosetta.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._extend_schema()
        
    def _extend_schema(self):
        """Extend schema with version tracking and more resource types"""
        try:
            logger.debug("Extending database schema")
            
            # Add version tracking table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version (
                id INTEGER PRIMARY KEY,
                version TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aws_prices_updated TIMESTAMP,
                ovh_prices_updated TIMESTAMP,
                hetzner_prices_updated TIMESTAMP,
                resource_count INTEGER,
                notes TEXT
            )
        """)
        
        # Extend resource_types table with more detailed mappings
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aws_type TEXT,
                ovh_type TEXT,
                hetzner_type TEXT,
                resource_category TEXT NOT NULL,
                subcategory TEXT,
                notes TEXT,
                UNIQUE(aws_type, ovh_type, hetzner_type)
            )
        """)
        
        # Add pricing history table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                price REAL,
                price_unit TEXT,
                currency TEXT DEFAULT 'USD',
                effective_date DATE,
                region TEXT
            )
        """)
        
        self.conn.commit()
    
    def populate_comprehensive_resources(self):
        """Populate all resource mappings"""
        
        # Comprehensive resource mappings
        # Format: (aws_type, ovh_type, hetzner_type, category, subcategory)
        resource_mappings = [
            # ===== COMPUTE =====
            ("aws_instance", "openstack_compute_instance_v2", "hcloud_server", "compute", "instance"),
            ("aws_launch_template", "openstack_compute_instance_v2", None, "compute", "template"),
            ("aws_autoscaling_group", None, None, "compute", "autoscaling"),
            ("aws_ec2_fleet", None, None, "compute", "fleet"),
            ("aws_spot_instance_request", None, None, "compute", "spot"),
            ("aws_placement_group", None, "hcloud_placement_group", "compute", "placement"),
            
            # ===== KEY PAIRS =====
            ("aws_key_pair", "openstack_compute_keypair_v2", "hcloud_ssh_key", "compute", "keypair"),
            
            # ===== STORAGE - BLOCK =====
            ("aws_ebs_volume", "openstack_blockstorage_volume_v3", "hcloud_volume", "storage", "block"),
            ("aws_ebs_snapshot", "openstack_blockstorage_snapshot_v3", "hcloud_snapshot", "storage", "snapshot"),
            ("aws_volume_attachment", "openstack_compute_volume_attach_v2", "hcloud_volume_attachment", "storage", "attachment"),
            
            # ===== STORAGE - OBJECT =====
            ("aws_s3_bucket", "openstack_objectstorage_container_v1", None, "storage", "object"),
            ("aws_s3_bucket_policy", "openstack_objectstorage_container_v1", None, "storage", "object_policy"),
            ("aws_s3_bucket_versioning", None, None, "storage", "versioning"),
            ("aws_s3_bucket_lifecycle_configuration", None, None, "storage", "lifecycle"),
            ("aws_s3_bucket_replication_configuration", None, None, "storage", "replication"),
            ("aws_s3_bucket_encryption", None, None, "storage", "encryption"),
            
            # ===== STORAGE - FILE SYSTEMS =====
            ("aws_efs_file_system", None, None, "storage", "efs"),
            ("aws_efs_mount_target", None, None, "storage", "efs_mount"),
            ("aws_fsx_lustre_file_system", None, None, "storage", "fsx"),
            
            # ===== NETWORKING - VPC/NETWORK =====
            ("aws_vpc", "openstack_networking_network_v2", "hcloud_network", "network", "vpc"),
            ("aws_subnet", "openstack_networking_subnet_v2", "hcloud_network_subnet", "network", "subnet"),
            ("aws_internet_gateway", "openstack_networking_router_v2", None, "network", "gateway"),
            ("aws_nat_gateway", "openstack_networking_router_v2", None, "network", "nat"),
            ("aws_route_table", "openstack_networking_router_route_v2", "hcloud_network_route", "network", "routing"),
            ("aws_route", "openstack_networking_router_route_v2", "hcloud_network_route", "network", "route"),
            ("aws_vpc_peering_connection", None, None, "network", "peering"),
            
            # ===== NETWORKING - SECURITY =====
            ("aws_security_group", "openstack_networking_secgroup_v2", "hcloud_firewall", "network", "security_group"),
            ("aws_security_group_rule", "openstack_networking_secgroup_rule_v2", None, "network", "security_rule"),
            ("aws_network_acl", None, None, "network", "acl"),
            ("aws_network_acl_rule", None, None, "network", "acl_rule"),
            
            # ===== NETWORKING - IP ADDRESSES =====
            ("aws_eip", "openstack_networking_floatingip_v2", "hcloud_floating_ip", "network", "elastic_ip"),
            ("aws_eip_association", "openstack_networking_floatingip_associate_v2", "hcloud_floating_ip_assignment", "network", "ip_association"),
            
            # ===== NETWORKING - DNS =====
            ("aws_route53_zone", "openstack_dns_zone_v2", None, "network", "dns_zone"),
            ("aws_route53_record", "openstack_dns_recordset_v2", None, "network", "dns_record"),
            
            # ===== LOAD BALANCING =====
            ("aws_lb", "openstack_lb_loadbalancer_v2", "hcloud_load_balancer", "network", "load_balancer"),
            ("aws_lb_target_group", "openstack_lb_pool_v2", "hcloud_load_balancer_target", "network", "lb_target"),
            ("aws_lb_listener", "openstack_lb_listener_v2", None, "network", "lb_listener"),
            ("aws_lb_listener_rule", "openstack_lb_l7policy_v2", None, "network", "lb_rule"),
            ("aws_alb", "openstack_lb_loadbalancer_v2", "hcloud_load_balancer", "network", "app_load_balancer"),
            ("aws_nlb", "openstack_lb_loadbalancer_v2", "hcloud_load_balancer", "network", "net_load_balancer"),
            
            # ===== DATABASE =====
            ("aws_db_instance", "openstack_db_instance_v1", None, "database", "instance"),
            ("aws_db_cluster", "openstack_db_cluster_v1", None, "database", "cluster"),
            ("aws_db_subnet_group", None, None, "database", "subnet_group"),
            ("aws_db_parameter_group", "openstack_db_configuration_v1", None, "database", "parameter_group"),
            ("aws_db_snapshot", None, None, "database", "snapshot"),
            ("aws_rds_cluster", None, None, "database", "rds_cluster"),
            ("aws_db_proxy", None, None, "database", "proxy"),
            
            # ===== CACHING =====
            ("aws_elasticache_cluster", None, None, "database", "cache_cluster"),
            ("aws_elasticache_replication_group", None, None, "database", "cache_replication"),
            ("aws_elasticache_subnet_group", None, None, "database", "cache_subnet"),
            
            # ===== CONTAINERS =====
            ("aws_ecs_cluster", "openstack_containerinfra_cluster_v1", None, "container", "cluster"),
            ("aws_ecs_service", None, None, "container", "service"),
            ("aws_ecs_task_definition", None, None, "container", "task"),
            ("aws_ecr_repository", "openstack_imageservice_image_v2", "hcloud_image", "container", "registry"),
            ("aws_eks_cluster", "openstack_containerinfra_cluster_v1", None, "container", "kubernetes"),
            
            # ===== SERVERLESS =====
            ("aws_lambda_function", None, None, "serverless", "function"),
            ("aws_lambda_layer_version", None, None, "serverless", "layer"),
            ("aws_api_gateway_rest_api", None, None, "serverless", "api_gateway"),
            ("aws_apigatewayv2_api", None, None, "serverless", "api_gateway_v2"),
            
            # ===== MESSAGE QUEUING =====
            ("aws_sqs_queue", None, None, "messaging", "queue"),
            ("aws_sns_topic", None, None, "messaging", "topic"),
            ("aws_sns_topic_subscription", None, None, "messaging", "subscription"),
            
            # ===== IDENTITY & ACCESS =====
            ("aws_iam_role", None, None, "iam", "role"),
            ("aws_iam_policy", None, None, "iam", "policy"),
            ("aws_iam_user", "openstack_identity_user_v3", None, "iam", "user"),
            ("aws_iam_group", "openstack_identity_group_v3", None, "iam", "group"),
            ("aws_iam_instance_profile", None, None, "iam", "instance_profile"),
            
            # ===== MONITORING =====
            ("aws_cloudwatch_metric_alarm", None, None, "monitoring", "alarm"),
            ("aws_cloudwatch_dashboard", None, None, "monitoring", "dashboard"),
            ("aws_cloudwatch_log_group", None, None, "monitoring", "log_group"),
            ("aws_cloudwatch_log_stream", None, None, "monitoring", "log_stream"),
            
            # ===== CDN =====
            ("aws_cloudfront_distribution", None, None, "cdn", "distribution"),
            ("aws_cloudfront_origin_access_identity", None, None, "cdn", "origin_access"),
            
            # ===== BACKUP =====
            ("aws_backup_plan", None, None, "backup", "plan"),
            ("aws_backup_vault", None, None, "backup", "vault"),
            ("aws_backup_selection", None, None, "backup", "selection"),
            
            # ===== VPN =====
            ("aws_vpn_connection", "openstack_vpnaas_ipsec_policy_v2", None, "vpn", "connection"),
            ("aws_vpn_gateway", "openstack_vpnaas_service_v2", None, "vpn", "gateway"),
            ("aws_customer_gateway", "openstack_vpnaas_endpoint_group_v2", None, "vpn", "customer_gateway"),
        ]
        
        print(f"- Populating {len(resource_mappings)} resource type mappings...")
        
        for mapping in resource_mappings:
            aws_type, ovh_type, hetzner_type, category, subcategory = mapping
            try:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO resource_mappings 
                    (aws_type, ovh_type, hetzner_type, resource_category, subcategory)
                    VALUES (?, ?, ?, ?, ?)
                """, (aws_type, ovh_type, hetzner_type, category, subcategory))
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
        print(f"Done: Added {len(resource_mappings)} resource mappings")
    
    def populate_extended_instances(self):
        """Add more comprehensive instance types"""
        
        # Extended AWS instance types
        aws_instances = [
            # T3 series (Burstable)
            ("aws", "t3.nano", 2, 0.5, "burstable", "current", "low", "ebs", None, 0, None, 0.0052),
            ("aws", "t3.micro", 2, 1, "burstable", "current", "low", "ebs", None, 0, None, 0.0104),
            ("aws", "t3.small", 2, 2, "burstable", "current", "low", "ebs", None, 0, None, 0.0208),
            ("aws", "t3.medium", 2, 4, "burstable", "current", "moderate", "ebs", None, 0, None, 0.0416),
            ("aws", "t3.large", 2, 8, "burstable", "current", "moderate", "ebs", None, 0, None, 0.0832),
            ("aws", "t3.xlarge", 4, 16, "burstable", "current", "moderate", "ebs", None, 0, None, 0.1664),
            ("aws", "t3.2xlarge", 8, 32, "burstable", "current", "moderate", "ebs", None, 0, None, 0.3328),
            
            # M5 series (General Purpose)
            ("aws", "m5.large", 2, 8, "general", "current", "moderate", "ebs", None, 0, None, 0.096),
            ("aws", "m5.xlarge", 4, 16, "general", "current", "high", "ebs", None, 0, None, 0.192),
            ("aws", "m5.2xlarge", 8, 32, "general", "current", "high", "ebs", None, 0, None, 0.384),
            ("aws", "m5.4xlarge", 16, 64, "general", "current", "high", "ebs", None, 0, None, 0.768),
            ("aws", "m5.8xlarge", 32, 128, "general", "current", "10gbps", "ebs", None, 0, None, 1.536),
            ("aws", "m5.12xlarge", 48, 192, "general", "current", "10gbps", "ebs", None, 0, None, 2.304),
            ("aws", "m5.16xlarge", 64, 256, "general", "current", "20gbps", "ebs", None, 0, None, 3.072),
            ("aws", "m5.24xlarge", 96, 384, "general", "current", "25gbps", "ebs", None, 0, None, 4.608),
            
            # M6i series (Latest Gen General Purpose)
            ("aws", "m6i.large", 2, 8, "general", "latest", "moderate", "ebs", None, 0, None, 0.1008),
            ("aws", "m6i.xlarge", 4, 16, "general", "latest", "high", "ebs", None, 0, None, 0.2016),
            ("aws", "m6i.2xlarge", 8, 32, "general", "latest", "high", "ebs", None, 0, None, 0.4032),
            
            # C5 series (Compute Optimized)
            ("aws", "c5.large", 2, 4, "compute", "current", "moderate", "ebs", None, 0, None, 0.085),
            ("aws", "c5.xlarge", 4, 8, "compute", "current", "high", "ebs", None, 0, None, 0.17),
            ("aws", "c5.2xlarge", 8, 16, "compute", "current", "high", "ebs", None, 0, None, 0.34),
            ("aws", "c5.4xlarge", 16, 32, "compute", "current", "high", "ebs", None, 0, None, 0.68),
            ("aws", "c5.9xlarge", 36, 72, "compute", "current", "10gbps", "ebs", None, 0, None, 1.53),
            ("aws", "c5.12xlarge", 48, 96, "compute", "current", "12gbps", "ebs", None, 0, None, 2.04),
            ("aws", "c5.18xlarge", 72, 144, "compute", "current", "25gbps", "ebs", None, 0, None, 3.06),
            ("aws", "c5.24xlarge", 96, 192, "compute", "current", "25gbps", "ebs", None, 0, None, 4.08),
            
            # R5 series (Memory Optimized)
            ("aws", "r5.large", 2, 16, "memory", "current", "moderate", "ebs", None, 0, None, 0.126),
            ("aws", "r5.xlarge", 4, 32, "memory", "current", "high", "ebs", None, 0, None, 0.252),
            ("aws", "r5.2xlarge", 8, 64, "memory", "current", "high", "ebs", None, 0, None, 0.504),
            ("aws", "r5.4xlarge", 16, 128, "memory", "current", "high", "ebs", None, 0, None, 1.008),
            ("aws", "r5.8xlarge", 32, 256, "memory", "current", "10gbps", "ebs", None, 0, None, 2.016),
            ("aws", "r5.12xlarge", 48, 384, "memory", "current", "10gbps", "ebs", None, 0, None, 3.024),
            ("aws", "r5.16xlarge", 64, 512, "memory", "current", "20gbps", "ebs", None, 0, None, 4.032),
            ("aws", "r5.24xlarge", 96, 768, "memory", "current", "25gbps", "ebs", None, 0, None, 6.048),
            
            # P3 series (GPU)
            ("aws", "p3.2xlarge", 8, 61, "gpu", "current", "10gbps", "ebs", None, 1, "V100", 3.06),
            ("aws", "p3.8xlarge", 32, 244, "gpu", "current", "10gbps", "ebs", None, 4, "V100", 12.24),
            ("aws", "p3.16xlarge", 64, 488, "gpu", "current", "25gbps", "ebs", None, 8, "V100", 24.48),
        ]
        
        # Extended OVH instances
        ovh_instances = [
            # Discovery series (d2)
            ("ovh", "d2-2", 1, 2, "general", "current", None, "ssd", 25, 0, None, 0.0084),
            ("ovh", "d2-4", 2, 4, "general", "current", None, "ssd", 50, 0, None, 0.0168),
            ("ovh", "d2-8", 4, 8, "general", "current", None, "ssd", 50, 0, None, 0.0337),
            
            # Balanced series (b2)
            ("ovh", "b2-7", 2, 7, "general", "current", "moderate", "ssd", 50, 0, None, 0.0278),
            ("ovh", "b2-15", 4, 15, "general", "current", "high", "ssd", 100, 0, None, 0.0556),
            ("ovh", "b2-30", 8, 30, "general", "current", "high", "ssd", 200, 0, None, 0.1111),
            ("ovh", "b2-60", 16, 60, "general", "current", "high", "ssd", 400, 0, None, 0.2222),
            ("ovh", "b2-120", 32, 120, "general", "current", "very-high", "ssd", 400, 0, None, 0.4444),
            ("ovh", "b2-240", 60, 240, "general", "current", "very-high", "ssd", 400, 0, None, 0.8889),
            
            # Compute series (c2)
            ("ovh", "c2-7", 2, 7, "compute", "current", "moderate", "ssd", 50, 0, None, 0.0417),
            ("ovh", "c2-15", 4, 15, "compute", "current", "high", "ssd", 100, 0, None, 0.0833),
            ("ovh", "c2-30", 8, 30, "compute", "current", "high", "ssd", 200, 0, None, 0.1667),
            ("ovh", "c2-60", 16, 60, "compute", "current", "very-high", "ssd", 400, 0, None, 0.3333),
            ("ovh", "c2-120", 32, 120, "compute", "current", "very-high", "ssd", 400, 0, None, 0.6667),
            
            # Memory series (r2)
            ("ovh", "r2-15", 2, 15, "memory", "current", "moderate", "ssd", 50, 0, None, 0.0556),
            ("ovh", "r2-30", 4, 30, "memory", "current", "high", "ssd", 100, 0, None, 0.1111),
            ("ovh", "r2-60", 8, 60, "memory", "current", "high", "ssd", 200, 0, None, 0.2222),
            ("ovh", "r2-120", 16, 120, "memory", "current", "very-high", "ssd", 400, 0, None, 0.4444),
            ("ovh", "r2-240", 32, 240, "memory", "current", "very-high", "ssd", 400, 0, None, 0.8889),
            
            # GPU series (g1)
            ("ovh", "g1-15", 4, 15, "gpu", "current", "high", "ssd", 200, 1, "GTX_1070", 0.5),
            ("ovh", "g1-30", 8, 30, "gpu", "current", "high", "ssd", 200, 1, "GTX_1070", 0.7),
            
            # Storage optimized (i1)
            ("ovh", "i1-45", 8, 45, "storage", "current", "high", "nvme", 1800, 0, None, 0.3333),
            ("ovh", "i1-90", 16, 90, "storage", "current", "very-high", "nvme", 3600, 0, None, 0.6667),
            ("ovh", "i1-180", 32, 180, "storage", "current", "very-high", "nvme", 7200, 0, None, 1.3333),
        ]
        
        # Extended Hetzner instances
        hetzner_instances = [
            # Cloud series (cx)
            ("hetzner", "cx11", 1, 2, "general", "current", "20TB", "local-ssd", 20, 0, None, 0.0052),
            ("hetzner", "cx21", 2, 4, "general", "current", "20TB", "local-ssd", 40, 0, None, 0.0089),
            ("hetzner", "cx31", 2, 8, "general", "current", "20TB", "local-ssd", 80, 0, None, 0.0137),
            ("hetzner", "cx41", 4, 16, "general", "current", "20TB", "local-ssd", 160, 0, None, 0.0274),
            ("hetzner", "cx51", 8, 32, "general", "current", "20TB", "local-ssd", 240, 0, None, 0.0548),
            
            # Dedicated vCPU (cpx)
            ("hetzner", "cpx11", 2, 2, "general", "current", "20TB", "local-ssd", 40, 0, None, 0.0068),
            ("hetzner", "cpx21", 3, 4, "general", "current", "20TB", "local-ssd", 80, 0, None, 0.0116),
            ("hetzner", "cpx31", 4, 8, "general", "current", "20TB", "local-ssd", 160, 0, None, 0.0219),
            ("hetzner", "cpx41", 8, 16, "general", "current", "20TB", "local-ssd", 240, 0, None, 0.0438),
            ("hetzner", "cpx51", 16, 32, "general", "current", "20TB", "local-ssd", 360, 0, None, 0.0877),
            
            # Dedicated vCPU Memory optimized (ccx)
            ("hetzner", "ccx11", 2, 8, "memory", "current", "20TB", "local-ssd", 80, 0, None, 0.0164),
            ("hetzner", "ccx21", 4, 16, "memory", "current", "20TB", "local-ssd", 160, 0, None, 0.0329),
            ("hetzner", "ccx31", 8, 32, "memory", "current", "20TB", "local-ssd", 240, 0, None, 0.0658),
            ("hetzner", "ccx41", 16, 64, "memory", "current", "20TB", "local-ssd", 360, 0, None, 0.1315),
            ("hetzner", "ccx51", 32, 128, "memory", "current", "20TB", "local-ssd", 600, 0, None, 0.2630),
        ]
        
        print(f"- Populating extended instance types...")
        
        # Insert all instances
        for instance in aws_instances + ovh_instances + hetzner_instances:
            try:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO instance_types 
                    (provider, instance_type, vcpu, memory_gb, family, generation, 
                     network_performance, storage_type, storage_gb, gpu_count, gpu_type, hourly_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, instance)
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
        print(f"Done: Added {len(aws_instances)} AWS, {len(ovh_instances)} OVH, {len(hetzner_instances)} Hetzner instances")
    
    def update_db_version(self):
        """Update database version information"""
        version = datetime.now().strftime("%Y%m%d.%H%M%S")
        
        # Count resources
        self.cursor.execute("SELECT COUNT(*) FROM resource_mappings")
        resource_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            INSERT INTO db_version 
            (version, updated_at, aws_prices_updated, resource_count, notes)
            VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)
        """, (version, resource_count, "Comprehensive resource mappings added"))
        
        self.conn.commit()
        print(f"Version: Database version updated to: {version}")
        print(f"Stats: Total resource mappings: {resource_count}")
    
    def close(self):
        self.conn.close()


def main():
    print("> Populating comprehensive cloud resource database...")
    
    populator = ComprehensiveDBPopulator()
    
    # Populate all data
    populator.populate_comprehensive_resources()
    populator.populate_extended_instances()
    populator.update_db_version()
    
    populator.close()
    
    print("\nDone: Database population complete!")
    print("- Database ready for use with comprehensive AWS, OVH, and Hetzner mappings")


if __name__ == "__main__":
    main()