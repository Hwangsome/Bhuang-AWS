locals {
  aws_subnet_tag = {
    Public = true
  }
}
data "aws_subnets" "subnets" {
  count = length(var.lb_subnet_ids) == 0 ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  tags = local.aws_subnet_tag
}



