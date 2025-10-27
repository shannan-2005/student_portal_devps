variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "future-grove-439612-s8"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "The name of the GKE cluster"
  type        = string
  default     = "student-devops-cluster"
}

variable "node_count" {
  description = "Number of nodes in the cluster"
  type        = number
  default     = 1
}