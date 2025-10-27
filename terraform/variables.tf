variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "ku-gcp-hackathon"  # Set your default project ID
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "student-portal"
}