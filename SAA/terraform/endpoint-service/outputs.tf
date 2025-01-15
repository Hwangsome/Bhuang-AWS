output "lb_arn" {
  description = "ARN of the LB"
  value       = aws_lb.lb.arn
}

output "lb_name" {
  description = "Name of the LB"
  value       = aws_lb.lb.name
}

output "lb_dns_name" {
  description = "DNS name of the LB"
  value       = aws_lb.lb.dns_name
}

output "lb_private_ips" {
  description = "Private IPs of the LB"
  value       = [for mapping in aws_lb.lb.subnet_mapping : mapping.private_ipv4_address]
}

output "lb_target_group_arn" {
  description = "ARN of the LBs target group"
  value       = aws_lb_target_group.target_group.arn
}

output "vpc_endpoint_service_arn" {
  description = "ARN of the VPC endpoint service"
  value       = aws_vpc_endpoint_service.service.arn
}

output "vpc_endpoint_service_id" {
  description = "ID of the VPC endpoint service"
  value       = aws_vpc_endpoint_service.service.id
}

output "vpc_endpoint_service_service_name" {
  description = "Name of the VPC endpoint service"
  value       = aws_vpc_endpoint_service.service.service_name
}

output "vpc_endpoint_service_service_type" {
  description = "Type of the VPC endpoint service"
  value       = aws_vpc_endpoint_service.service.service_type
}

output "vpc_endpoint_service_availability_zones" {
  description = "AZs of the VPC endpoint service"
  value       = aws_vpc_endpoint_service.service.availability_zones
}