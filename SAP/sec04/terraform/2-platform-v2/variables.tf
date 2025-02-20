variable "ecs_service_name" {
    description = "The name of the ECS service"
    type        = string
}

variable "ecs_domain_name" {
    description = "The domain name of the ECS service"
    type        = string
}

variable "cluster_name" {
    description = "The name of the ECS cluster"
    type        = string
}

variable "container_name" {
    description = "The name of the container"
    type        = string
}

variable "container_port" {
    description = "The port of the container"
    type        = number
    default = 8080
}

variable "container_image" {
    description = "The image of the container"
    type        = string
}