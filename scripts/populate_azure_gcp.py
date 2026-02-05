#!/usr/bin/env python3
"""
Azure and GCP Database Population
Adds comprehensive Azure and GCP resource mappings
"""

import sqlite3
from datetime import datetime

class AzureGCPPopulator:
    def __init__(self, db_path: str = "db/cloud_rosetta.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def populate_azure_gcp_instances(self):
        """Add Azure and GCP instance types"""
        
        # Azure instance types
        azure_instances = [
            # B-series (Burstable)
            ("azure", "Standard_B1s", 1, 1, "burstable", "current", "moderate", "ssd", 4, 0, None, 0.0052),
            ("azure", "Standard_B1ms", 1, 2, "burstable", "current", "moderate", "ssd", 4, 0, None, 0.0104),
            ("azure", "Standard_B2s", 2, 4, "burstable", "current", "moderate", "ssd", 8, 0, None, 0.0208),
            ("azure", "Standard_B2ms", 2, 8, "burstable", "current", "moderate", "ssd", 16, 0, None, 0.0416),
            ("azure", "Standard_B4ms", 4, 16, "burstable", "current", "moderate", "ssd", 32, 0, None, 0.0832),
            ("azure", "Standard_B8ms", 8, 32, "burstable", "current", "moderate", "ssd", 64, 0, None, 0.1664),
            
            # D-series v4 (General Purpose)
            ("azure", "Standard_D2s_v4", 2, 8, "general", "current", "moderate", "ssd", 75, 0, None, 0.096),
            ("azure", "Standard_D4s_v4", 4, 16, "general", "current", "high", "ssd", 150, 0, None, 0.192),
            ("azure", "Standard_D8s_v4", 8, 32, "general", "current", "high", "ssd", 300, 0, None, 0.384),
            ("azure", "Standard_D16s_v4", 16, 64, "general", "current", "high", "ssd", 600, 0, None, 0.768),
            ("azure", "Standard_D32s_v4", 32, 128, "general", "current", "very-high", "ssd", 1200, 0, None, 1.536),
            ("azure", "Standard_D48s_v4", 48, 192, "general", "current", "very-high", "ssd", 1800, 0, None, 2.304),
            ("azure", "Standard_D64s_v4", 64, 256, "general", "current", "very-high", "ssd", 2400, 0, None, 3.072),
            
            # F-series (Compute Optimized)
            ("azure", "Standard_F2s_v2", 2, 4, "compute", "current", "moderate", "ssd", 16, 0, None, 0.085),
            ("azure", "Standard_F4s_v2", 4, 8, "compute", "current", "high", "ssd", 32, 0, None, 0.169),
            ("azure", "Standard_F8s_v2", 8, 16, "compute", "current", "high", "ssd", 64, 0, None, 0.338),
            ("azure", "Standard_F16s_v2", 16, 32, "compute", "current", "high", "ssd", 128, 0, None, 0.677),
            ("azure", "Standard_F32s_v2", 32, 64, "compute", "current", "very-high", "ssd", 256, 0, None, 1.353),
            ("azure", "Standard_F48s_v2", 48, 96, "compute", "current", "very-high", "ssd", 384, 0, None, 2.03),
            ("azure", "Standard_F72s_v2", 72, 144, "compute", "current", "very-high", "ssd", 576, 0, None, 3.045),
            
            # E-series v4 (Memory Optimized)
            ("azure", "Standard_E2s_v4", 2, 16, "memory", "current", "moderate", "ssd", 32, 0, None, 0.126),
            ("azure", "Standard_E4s_v4", 4, 32, "memory", "current", "high", "ssd", 64, 0, None, 0.252),
            ("azure", "Standard_E8s_v4", 8, 64, "memory", "current", "high", "ssd", 128, 0, None, 0.504),
            ("azure", "Standard_E16s_v4", 16, 128, "memory", "current", "high", "ssd", 256, 0, None, 1.008),
            ("azure", "Standard_E32s_v4", 32, 256, "memory", "current", "very-high", "ssd", 512, 0, None, 2.016),
            ("azure", "Standard_E48s_v4", 48, 384, "memory", "current", "very-high", "ssd", 768, 0, None, 3.024),
            ("azure", "Standard_E64s_v4", 64, 512, "memory", "current", "very-high", "ssd", 1024, 0, None, 4.032),
            
            # NC-series (GPU)
            ("azure", "Standard_NC6s_v3", 6, 112, "gpu", "current", "high", "ssd", 736, 1, "V100", 3.06),
            ("azure", "Standard_NC12s_v3", 12, 224, "gpu", "current", "high", "ssd", 1474, 2, "V100", 6.12),
            ("azure", "Standard_NC24s_v3", 24, 448, "gpu", "current", "very-high", "ssd", 2948, 4, "V100", 12.24),
        ]
        
        # GCP instance types
        gcp_instances = [
            # e2 series (Cost-optimized)
            ("gcp", "e2-micro", 2, 1, "burstable", "current", "low", "pd-standard", 0, 0, None, 0.00628),
            ("gcp", "e2-small", 2, 2, "burstable", "current", "low", "pd-standard", 0, 0, None, 0.01256),
            ("gcp", "e2-medium", 2, 4, "burstable", "current", "moderate", "pd-standard", 0, 0, None, 0.02512),
            
            # n2 series (General Purpose)
            ("gcp", "n2-standard-2", 2, 8, "general", "current", "moderate", "pd-standard", 0, 0, None, 0.0971),
            ("gcp", "n2-standard-4", 4, 16, "general", "current", "high", "pd-standard", 0, 0, None, 0.1943),
            ("gcp", "n2-standard-8", 8, 32, "general", "current", "high", "pd-standard", 0, 0, None, 0.3886),
            ("gcp", "n2-standard-16", 16, 64, "general", "current", "high", "pd-standard", 0, 0, None, 0.7773),
            ("gcp", "n2-standard-32", 32, 128, "general", "current", "very-high", "pd-standard", 0, 0, None, 1.5545),
            ("gcp", "n2-standard-48", 48, 192, "general", "current", "very-high", "pd-standard", 0, 0, None, 2.3318),
            ("gcp", "n2-standard-64", 64, 256, "general", "current", "very-high", "pd-standard", 0, 0, None, 3.1091),
            ("gcp", "n2-standard-80", 80, 320, "general", "current", "very-high", "pd-standard", 0, 0, None, 3.8863),
            
            # n2d series (AMD General Purpose)
            ("gcp", "n2d-standard-2", 2, 8, "general", "current", "moderate", "pd-standard", 0, 0, None, 0.0843),
            ("gcp", "n2d-standard-4", 4, 16, "general", "current", "high", "pd-standard", 0, 0, None, 0.1686),
            ("gcp", "n2d-standard-8", 8, 32, "general", "current", "high", "pd-standard", 0, 0, None, 0.3373),
            ("gcp", "n2d-standard-16", 16, 64, "general", "current", "high", "pd-standard", 0, 0, None, 0.6745),
            ("gcp", "n2d-standard-32", 32, 128, "general", "current", "very-high", "pd-standard", 0, 0, None, 1.349),
            
            # c2 series (Compute Optimized)
            ("gcp", "c2-standard-4", 4, 16, "compute", "current", "high", "pd-standard", 0, 0, None, 0.1668),
            ("gcp", "c2-standard-8", 8, 32, "compute", "current", "high", "pd-standard", 0, 0, None, 0.3336),
            ("gcp", "c2-standard-16", 16, 64, "compute", "current", "high", "pd-standard", 0, 0, None, 0.6672),
            ("gcp", "c2-standard-30", 30, 120, "compute", "current", "very-high", "pd-standard", 0, 0, None, 1.251),
            ("gcp", "c2-standard-60", 60, 240, "compute", "current", "very-high", "pd-standard", 0, 0, None, 2.502),
            
            # m2 series (Memory Optimized)
            ("gcp", "m2-ultramem-208", 208, 5888, "memory", "current", "very-high", "pd-standard", 0, 0, None, 25.026),
            ("gcp", "m2-ultramem-416", 416, 11776, "memory", "current", "very-high", "pd-standard", 0, 0, None, 50.052),
            ("gcp", "m2-megamem-416", 416, 5888, "memory", "current", "very-high", "pd-standard", 0, 0, None, 31.266),
            
            # n2-highmem series (High Memory)
            ("gcp", "n2-highmem-2", 2, 16, "memory", "current", "moderate", "pd-standard", 0, 0, None, 0.1308),
            ("gcp", "n2-highmem-4", 4, 32, "memory", "current", "high", "pd-standard", 0, 0, None, 0.2617),
            ("gcp", "n2-highmem-8", 8, 64, "memory", "current", "high", "pd-standard", 0, 0, None, 0.5234),
            ("gcp", "n2-highmem-16", 16, 128, "memory", "current", "high", "pd-standard", 0, 0, None, 1.0468),
            ("gcp", "n2-highmem-32", 32, 256, "memory", "current", "very-high", "pd-standard", 0, 0, None, 2.0936),
            
            # a2 series (GPU - A100)
            ("gcp", "a2-highgpu-1g", 12, 85, "gpu", "current", "high", "pd-standard", 0, 1, "A100", 3.673),
            ("gcp", "a2-highgpu-2g", 24, 170, "gpu", "current", "high", "pd-standard", 0, 2, "A100", 7.346),
            ("gcp", "a2-highgpu-4g", 48, 340, "gpu", "current", "very-high", "pd-standard", 0, 4, "A100", 14.692),
            ("gcp", "a2-highgpu-8g", 96, 680, "gpu", "current", "very-high", "pd-standard", 0, 8, "A100", 29.384),
            
            # t2d series (Tau - ARM)
            ("gcp", "t2d-standard-1", 1, 4, "general", "current", "moderate", "pd-standard", 0, 0, None, 0.042),
            ("gcp", "t2d-standard-2", 2, 8, "general", "current", "moderate", "pd-standard", 0, 0, None, 0.084),
            ("gcp", "t2d-standard-4", 4, 16, "general", "current", "high", "pd-standard", 0, 0, None, 0.168),
            ("gcp", "t2d-standard-8", 8, 32, "general", "current", "high", "pd-standard", 0, 0, None, 0.336),
        ]
        
        print(f"- Populating Azure and GCP instance types...")
        
        for instance in azure_instances + gcp_instances:
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
        print(f"Done: Added {len(azure_instances)} Azure and {len(gcp_instances)} GCP instances")
    
    def populate_azure_gcp_regions(self):
        """Add Azure and GCP regions"""
        
        regions = [
            # Azure regions
            ("azure", "eastus", "East US", "USA", "North America", 37.3688, -79.8336),
            ("azure", "eastus2", "East US 2", "USA", "North America", 36.6681, -78.3889),
            ("azure", "westus", "West US", "USA", "North America", 37.7898, -122.3942),
            ("azure", "westus2", "West US 2", "USA", "North America", 47.2333, -119.8522),
            ("azure", "centralus", "Central US", "USA", "North America", 41.5908, -93.6208),
            ("azure", "northeurope", "North Europe", "Ireland", "Europe", 53.3478, -6.2597),
            ("azure", "westeurope", "West Europe", "Netherlands", "Europe", 52.3667, 4.9000),
            ("azure", "uksouth", "UK South", "UK", "Europe", 50.941, -0.799),
            ("azure", "ukwest", "UK West", "UK", "Europe", 53.427, -3.084),
            ("azure", "francecentral", "France Central", "France", "Europe", 46.3772, 2.3730),
            ("azure", "germanywestcentral", "Germany West Central", "Germany", "Europe", 50.110, 8.682),
            ("azure", "switzerlandnorth", "Switzerland North", "Switzerland", "Europe", 47.451, 8.564),
            ("azure", "northcentralus", "North Central US", "USA", "North America", 41.8819, -87.6278),
            ("azure", "canadacentral", "Canada Central", "Canada", "North America", 43.653, -79.383),
            ("azure", "canadaeast", "Canada East", "Canada", "North America", 46.813, -71.208),
            ("azure", "japaneast", "Japan East", "Japan", "Asia", 35.68, 139.77),
            ("azure", "japanwest", "Japan West", "Japan", "Asia", 34.69, 135.50),
            ("azure", "koreacentral", "Korea Central", "South Korea", "Asia", 37.5665, 126.9780),
            ("azure", "southeastasia", "Southeast Asia", "Singapore", "Asia", 1.283, 103.833),
            ("azure", "eastasia", "East Asia", "Hong Kong", "Asia", 22.267, 114.188),
            ("azure", "australiaeast", "Australia East", "Australia", "Oceania", -33.86, 151.20),
            ("azure", "australiasoutheast", "Australia Southeast", "Australia", "Oceania", -37.83, 144.98),
            ("azure", "centralindia", "Central India", "India", "Asia", 18.5822, 73.9197),
            ("azure", "southindia", "South India", "India", "Asia", 12.9822, 80.1636),
            ("azure", "brazilsouth", "Brazil South", "Brazil", "South America", -23.55, -46.633),
            
            # GCP regions
            ("gcp", "us-central1", "Iowa, USA", "USA", "North America", 41.2619, -95.8608),
            ("gcp", "us-east1", "South Carolina, USA", "USA", "North America", 33.1761, -80.2408),
            ("gcp", "us-east4", "Virginia, USA", "USA", "North America", 37.3719, -78.8444),
            ("gcp", "us-west1", "Oregon, USA", "USA", "North America", 43.8041, -120.5542),
            ("gcp", "us-west2", "Los Angeles, USA", "USA", "North America", 34.0522, -118.2437),
            ("gcp", "us-west3", "Salt Lake City, USA", "USA", "North America", 40.7608, -111.8910),
            ("gcp", "us-west4", "Las Vegas, USA", "USA", "North America", 36.1699, -115.1398),
            ("gcp", "northamerica-northeast1", "Montreal, Canada", "Canada", "North America", 45.5017, -73.5673),
            ("gcp", "northamerica-northeast2", "Toronto, Canada", "Canada", "North America", 43.6532, -79.3832),
            ("gcp", "europe-west1", "Belgium", "Belgium", "Europe", 50.8503, 4.3517),
            ("gcp", "europe-west2", "London, UK", "UK", "Europe", 51.5074, -0.1278),
            ("gcp", "europe-west3", "Frankfurt, Germany", "Germany", "Europe", 50.1109, 8.6821),
            ("gcp", "europe-west4", "Netherlands", "Netherlands", "Europe", 52.3676, 4.9041),
            ("gcp", "europe-west6", "Zurich, Switzerland", "Switzerland", "Europe", 47.3769, 8.5417),
            ("gcp", "europe-north1", "Finland", "Finland", "Europe", 60.1699, 24.9384),
            ("gcp", "europe-central2", "Warsaw, Poland", "Poland", "Europe", 52.2297, 21.0122),
            ("gcp", "asia-east1", "Taiwan", "Taiwan", "Asia", 25.0330, 121.5654),
            ("gcp", "asia-east2", "Hong Kong", "Hong Kong", "Asia", 22.3193, 114.1694),
            ("gcp", "asia-northeast1", "Tokyo, Japan", "Japan", "Asia", 35.6895, 139.6917),
            ("gcp", "asia-northeast2", "Osaka, Japan", "Japan", "Asia", 34.6937, 135.5023),
            ("gcp", "asia-northeast3", "Seoul, South Korea", "South Korea", "Asia", 37.5665, 126.9780),
            ("gcp", "asia-south1", "Mumbai, India", "India", "Asia", 19.0760, 72.8777),
            ("gcp", "asia-south2", "Delhi, India", "India", "Asia", 28.6139, 77.2090),
            ("gcp", "asia-southeast1", "Singapore", "Singapore", "Asia", 1.3521, 103.8198),
            ("gcp", "asia-southeast2", "Jakarta, Indonesia", "Indonesia", "Asia", -6.2088, 106.8456),
            ("gcp", "australia-southeast1", "Sydney, Australia", "Australia", "Oceania", -33.8688, 151.2093),
            ("gcp", "australia-southeast2", "Melbourne, Australia", "Australia", "Oceania", -37.8136, 144.9631),
            ("gcp", "southamerica-east1", "Sao Paulo, Brazil", "Brazil", "South America", -23.5505, -46.6333),
        ]
        
        print(f"- Populating Azure and GCP regions...")
        
        for region in regions:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO regions 
                    (provider, region_code, region_name, country, continent, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, region)
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
        print(f"Done: Added {len([r for r in regions if r[0] == 'azure'])} Azure and {len([r for r in regions if r[0] == 'gcp'])} GCP regions")
    
    def populate_azure_gcp_resources(self):
        """Add Azure and GCP resource mappings"""
        
        # Extended resource mappings including Azure and GCP
        resource_mappings = [
            # Compute
            ("aws_instance", "openstack_compute_instance_v2", "hcloud_server", "azurerm_linux_virtual_machine", "google_compute_instance", "compute", "instance"),
            ("aws_launch_template", "openstack_compute_instance_v2", None, "azurerm_virtual_machine", "google_compute_instance_template", "compute", "template"),
            ("aws_autoscaling_group", None, None, "azurerm_virtual_machine_scale_set", "google_compute_instance_group_manager", "compute", "autoscaling"),
            
            # Key Pairs
            ("aws_key_pair", "openstack_compute_keypair_v2", "hcloud_ssh_key", "azurerm_ssh_public_key", "google_compute_project_metadata_item", "compute", "keypair"),
            
            # Storage - Block
            ("aws_ebs_volume", "openstack_blockstorage_volume_v3", "hcloud_volume", "azurerm_managed_disk", "google_compute_disk", "storage", "block"),
            ("aws_ebs_snapshot", "openstack_blockstorage_snapshot_v3", "hcloud_snapshot", "azurerm_snapshot", "google_compute_snapshot", "storage", "snapshot"),
            
            # Storage - Object
            ("aws_s3_bucket", "openstack_objectstorage_container_v1", None, "azurerm_storage_account", "google_storage_bucket", "storage", "object"),
            ("aws_s3_bucket_policy", None, None, "azurerm_storage_account_network_rules", "google_storage_bucket_iam_policy", "storage", "object_policy"),
            
            # Storage - File Systems
            ("aws_efs_file_system", None, None, "azurerm_storage_share", "google_filestore_instance", "storage", "filesystem"),
            
            # Networking - VPC/Network
            ("aws_vpc", "openstack_networking_network_v2", "hcloud_network", "azurerm_virtual_network", "google_compute_network", "network", "vpc"),
            ("aws_subnet", "openstack_networking_subnet_v2", "hcloud_network_subnet", "azurerm_subnet", "google_compute_subnetwork", "network", "subnet"),
            ("aws_internet_gateway", "openstack_networking_router_v2", None, "azurerm_virtual_network_gateway", "google_compute_router", "network", "gateway"),
            ("aws_nat_gateway", "openstack_networking_router_v2", None, "azurerm_nat_gateway", "google_compute_router_nat", "network", "nat"),
            
            # Networking - Security
            ("aws_security_group", "openstack_networking_secgroup_v2", "hcloud_firewall", "azurerm_network_security_group", "google_compute_firewall", "network", "security_group"),
            ("aws_security_group_rule", "openstack_networking_secgroup_rule_v2", None, "azurerm_network_security_rule", "google_compute_firewall", "network", "security_rule"),
            
            # Networking - IP Addresses
            ("aws_eip", "openstack_networking_floatingip_v2", "hcloud_floating_ip", "azurerm_public_ip", "google_compute_address", "network", "elastic_ip"),
            
            # Load Balancing
            ("aws_lb", "openstack_lb_loadbalancer_v2", "hcloud_load_balancer", "azurerm_lb", "google_compute_backend_service", "network", "load_balancer"),
            ("aws_lb_target_group", "openstack_lb_pool_v2", "hcloud_load_balancer_target", "azurerm_lb_backend_address_pool", "google_compute_instance_group", "network", "lb_target"),
            
            # Database
            ("aws_db_instance", "openstack_db_instance_v1", None, "azurerm_mssql_database", "google_sql_database_instance", "database", "instance"),
            ("aws_db_cluster", "openstack_db_cluster_v1", None, "azurerm_mssql_server", "google_sql_database_instance", "database", "cluster"),
            ("aws_elasticache_cluster", None, None, "azurerm_redis_cache", "google_redis_instance", "database", "cache"),
            
            # Containers
            ("aws_ecs_cluster", "openstack_containerinfra_cluster_v1", None, "azurerm_container_group", "google_container_cluster", "container", "cluster"),
            ("aws_eks_cluster", "openstack_containerinfra_cluster_v1", None, "azurerm_kubernetes_cluster", "google_container_cluster", "container", "kubernetes"),
            ("aws_ecr_repository", "openstack_imageservice_image_v2", "hcloud_image", "azurerm_container_registry", "google_artifact_registry_repository", "container", "registry"),
            
            # Serverless
            ("aws_lambda_function", None, None, "azurerm_function_app", "google_cloudfunctions_function", "serverless", "function"),
            ("aws_api_gateway_rest_api", None, None, "azurerm_api_management", "google_api_gateway_api", "serverless", "api_gateway"),
            
            # Messaging
            ("aws_sqs_queue", None, None, "azurerm_servicebus_queue", "google_pubsub_topic", "messaging", "queue"),
            ("aws_sns_topic", None, None, "azurerm_servicebus_topic", "google_pubsub_topic", "messaging", "topic"),
            
            # Identity & Access
            ("aws_iam_role", None, None, "azurerm_role_definition", "google_service_account", "iam", "role"),
            ("aws_iam_policy", None, None, "azurerm_role_definition", "google_iam_policy", "iam", "policy"),
            ("aws_iam_user", "openstack_identity_user_v3", None, "azuread_user", "google_service_account", "iam", "user"),
            
            # Monitoring
            ("aws_cloudwatch_metric_alarm", None, None, "azurerm_monitor_metric_alert", "google_monitoring_alert_policy", "monitoring", "alarm"),
            ("aws_cloudwatch_log_group", None, None, "azurerm_log_analytics_workspace", "google_logging_project_sink", "monitoring", "log_group"),
            
            # DNS
            ("aws_route53_zone", "openstack_dns_zone_v2", None, "azurerm_dns_zone", "google_dns_managed_zone", "network", "dns_zone"),
            ("aws_route53_record", "openstack_dns_recordset_v2", None, "azurerm_dns_a_record", "google_dns_record_set", "network", "dns_record"),
        ]
        
        print(f"- Populating Azure and GCP resource mappings...")
        
        # First, let's extend the resource_mappings table to support Azure and GCP
        try:
            self.cursor.execute("ALTER TABLE resource_mappings ADD COLUMN azure_type TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            self.cursor.execute("ALTER TABLE resource_mappings ADD COLUMN gcp_type TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Insert the mappings
        for mapping in resource_mappings:
            aws, ovh, hetzner, azure, gcp, category, subcategory = mapping
            try:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO resource_mappings 
                    (aws_type, ovh_type, hetzner_type, azure_type, gcp_type, resource_category, subcategory)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (aws, ovh, hetzner, azure, gcp, category, subcategory))
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
        print(f"Done: Added comprehensive Azure and GCP resource mappings")
    
    def populate_azure_gcp_images(self):
        """Add Azure and GCP OS images"""
        
        images = [
            # Azure images
            ("azure", "Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest", "ubuntu", "20.04"),
            ("azure", "Canonical:0001-com-ubuntu-server-jammy:22_04-lts:latest", "ubuntu", "22.04"),
            ("azure", "Canonical:0001-com-ubuntu-server-lunar:23_04:latest", "ubuntu", "23.04"),
            ("azure", "Debian:debian-11:11:latest", "debian", "11"),
            ("azure", "Debian:debian-12:12:latest", "debian", "12"),
            ("azure", "OpenLogic:CentOS:8_5:latest", "centos", "8.5"),
            ("azure", "RedHat:RHEL:8-lvm:latest", "rhel", "8"),
            ("azure", "RedHat:RHEL:9-lvm:latest", "rhel", "9"),
            ("azure", "MicrosoftWindowsServer:WindowsServer:2022-datacenter:latest", "windows", "2022"),
            ("azure", "MicrosoftWindowsServer:WindowsServer:2019-datacenter:latest", "windows", "2019"),
            
            # GCP images
            ("gcp", "ubuntu-2004-focal-v20240307", "ubuntu", "20.04"),
            ("gcp", "ubuntu-2204-jammy-v20240307", "ubuntu", "22.04"),
            ("gcp", "ubuntu-2404-noble-amd64-v20240307", "ubuntu", "24.04"),
            ("gcp", "debian-11-bullseye-v20240307", "debian", "11"),
            ("gcp", "debian-12-bookworm-v20240307", "debian", "12"),
            ("gcp", "centos-stream-8-v20240307", "centos", "8"),
            ("gcp", "centos-stream-9-v20240307", "centos", "9"),
            ("gcp", "rocky-linux-8-optimized-gcp-v20240307", "rocky", "8"),
            ("gcp", "rocky-linux-9-optimized-gcp-v20240307", "rocky", "9"),
            ("gcp", "windows-server-2022-dc-v20240307", "windows", "2022"),
            ("gcp", "windows-server-2019-dc-v20240307", "windows", "2019"),
        ]
        
        print(f"- Populating Azure and GCP OS images...")
        
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
        print(f"Done: Added Azure and GCP OS images")
    
    def update_version(self):
        """Update database version"""
        version = datetime.now().strftime("%Y%m%d.%H%M%S")
        
        self.cursor.execute("""
            INSERT INTO db_version 
            (version, updated_at, notes)
            VALUES (?, CURRENT_TIMESTAMP, ?)
        """, (version, "Added comprehensive Azure and GCP support"))
        
        self.conn.commit()
        print(f"Version: Database version updated to: {version}")
    
    def close(self):
        self.conn.close()


def main():
    print("> Adding Azure and GCP support to Cloud Rosetta...")
    
    populator = AzureGCPPopulator()
    
    # Populate all data
    populator.populate_azure_gcp_instances()
    populator.populate_azure_gcp_regions()
    populator.populate_azure_gcp_resources()
    populator.populate_azure_gcp_images()
    populator.update_version()
    
    populator.close()
    
    print("\nDone: Azure and GCP support added successfully!")
    print("- Database now includes comprehensive 5-cloud support:")
    print("   • AWS")
    print("   • OVH")
    print("   • Hetzner")
    print("   • Azure")
    print("   • Google Cloud Platform")


if __name__ == "__main__":
    main()