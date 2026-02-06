# Simple Hetzner test infrastructure
resource "hcloud_server" "web" {
  name        = "test-server"
  image       = "ubuntu-22.04"
  server_type = "cx11"
  location    = "nbg1"
}

resource "hcloud_network" "main" {
  name     = "test-network"
  ip_range = "192.168.0.0/16"
}

resource "hcloud_network_subnet" "main" {
  type         = "cloud"
  network_id   = hcloud_network.main.id
  network_zone = "eu-central"
  ip_range     = "192.168.1.0/24"
}

resource "hcloud_volume" "storage" {
  name     = "test-volume"
  size     = 20
  location = "nbg1"
}