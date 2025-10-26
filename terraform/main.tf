terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create Google Container Registry
resource "google_container_registry" "main" {
  project  = var.project_id
  location = "US"
}

# Create GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "${var.cluster_name}-cluster"
  location = var.region
  
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = "default"
  subnetwork = "default"
}

# Node pool for GKE cluster
resource "google_container_node_pool" "primary_nodes" {
  name       = "${google_container_cluster.primary.name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  
  node_count = var.node_count

  node_config {
    preemptible  = true
    machine_type = "e2-small"
    disk_size_gb = 20

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}