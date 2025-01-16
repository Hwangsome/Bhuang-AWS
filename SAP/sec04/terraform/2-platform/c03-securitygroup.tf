locals {
  create_security_group = var.create && var.create_security_group && var.network_mode == "awsvpc"
  security_group_name   = try(coalesce(var.security_group_name, var.name), "")
  security_group_use_name_prefix = var.cluster_name
  ecs_alb_security_group = "alb-sg"
}

data "aws_vpc" "ecs_vpc" {
  count = local.create_security_group ? 1 : 0
  # 使用 VPC 的标签（tags）检索
  filter {
    name   = "tag:Name"  # 这里使用的标签是 Name
    values = ["ecs-cluster-vpc"]
  }
}
# create security group
resource "aws_security_group" "ecs_alb_security_group" {
  count = local.create_security_group ? 1 : 0
  name        = "${local.security_group_use_name_prefix}-${local.ecs_alb_security_group}"
  description = var.security_group_description
  vpc_id      = data.aws_vpc.ecs_vpc[0].id

  ingress {
    description = "Allow Port 443"
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = [var.internet_cidr_block]
  }

  egress {
    description = "Allow all ip and ports outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.internet_cidr_block]
  }

  tags = merge(
    var.tags,
    { "Name" = local.security_group_name },
    var.security_group_tags
  )

  lifecycle {
    create_before_destroy = true
  }
}