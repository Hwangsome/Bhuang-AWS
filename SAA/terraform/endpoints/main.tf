locals {
  data_subnets = try(data.aws_subnets.subnets[0].ids, [])
  subnet_ids   = coalescelist(tolist(local.data_subnets), var.ep_subnet_ids)
}
resource "aws_vpc_endpoint" "example" {
  service_name      = var.service_name
  subnet_ids        = local.subnet_ids
  vpc_endpoint_type = var.service_type
  vpc_id            = var.vpc_id
}