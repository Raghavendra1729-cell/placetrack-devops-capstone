variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "cluster_name" {
  type    = string
  default = "placetrack"
}

variable "kubernetes_version" {
  type    = string
  default = "1.31"
}

variable "node_instance_type" {
  type    = string
  default = "t3.small"
}

variable "api_access_cidrs" {
  type        = list(string)
  description = "CIDR blocks allowed to reach the EKS API (your own IP, e.g. [\"203.0.113.10/32\"])"
}
