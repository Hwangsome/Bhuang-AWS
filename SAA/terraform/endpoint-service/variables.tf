variable "endpoint_service_acceptance_required" {
  type        = bool
  description = "Whether or not a consumer of this service needs to be accepted"
  default     = false
}

variable "endpoint_service_allowed_principals" {
  type        = set(string)
  description = "Principals allowed to access this VPC endpoint service"
  default     = []
}

variable "lb_enable_cross_zone_load_balancing" {
  type        = bool
  description = "Whether or not to enable cross zone load balancing for the load balancer"
  default     = true
}

variable "lb_enable_deletion_protection" {
  type        = bool
  description = "Whether or not to enable deletion protection for the load balancer"
  default     = false
}

variable "lb_target_group_port" {
  type        = number
  description = "Port to listen on"
  default     = 80
}

variable "lb_subnets_tags" {
  type        = map(string)
  description = "Map with tags to filter for subnets that the load balancer should be available in (when lb_subnet_ids is not set)"
  default = {
    Type = "private"
  }
}

variable "lb_subnet_ids" {
  type        = list(string)
  description = "Set of subnet ids to use for the load balancer"
  default     = []
}

variable "vpc_id" {
  type        = string
  description = "VPC id to filter for discovering private subnets"
}