data "aws_subnets" "subnets" {
  count = length(var.ep_subnet_ids) == 0 ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}
