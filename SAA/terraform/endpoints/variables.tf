variable "service_name" {
    type        = string
    description = "service name"
}

variable "ep_subnet_ids" {
  type        = list(string)
  description = ""
  default     = []
}

variable "vpc_id" {
  type        = string
  description = "vpc id"
}

variable "service_type" {
    type        = string
    description = "service type"
}