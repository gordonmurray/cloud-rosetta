# Simple OVH test infrastructure
resource "ovh_cloud_project_compute_instance" "web" {
  service_name = "your-service-name"
  name         = "test-instance"
  flavor       = "d2-2"
  region       = "GRA11"
  image        = "Ubuntu 22.04"
}

resource "ovh_cloud_project_network_private" "network" {
  service_name = "your-service-name"
  name         = "test-network"
  regions      = ["GRA11"]
  vlan_id      = 42
}

resource "ovh_cloud_project_network_private_subnet" "subnet" {
  service_name = "your-service-name"
  network_id   = ovh_cloud_project_network_private.network.id
  region       = "GRA11"
  start        = "192.168.1.100"
  end          = "192.168.1.200"
  network      = "192.168.1.0/24"
  dhcp         = true
}