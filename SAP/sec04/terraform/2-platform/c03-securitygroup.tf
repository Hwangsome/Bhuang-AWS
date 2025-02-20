locals {
  create_security_group = var.create && var.create_security_group && var.network_mode == "awsvpc"
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

data "aws_subnet" "this" {
  count = local.create_security_group ? 1 : 0

  id = data.aws_subnets.public.ids[0]
}


resource "aws_security_group" "this" {
  #  构建一个用于 for_each 的映射（map），它决定了哪个安全组资源会被创建。
  #  group.name => group 这是映射的形式。它将 group.name 的值作为键，group 作为值存入新的映射中。
  #  如果当前的 group 是 { name = "ecs-sg", description = "Security Group for ECS service" }，那么它将会在新映射中生成一项："ecs-sg" => { name = "ecs-sg", description = "Security Group for ECS service" }。
  #  if var.create_security_groups[group.name] != null:  只在满足条件时才将当前的 group 加入到最终的映射中
  #  在 Terraform 的上下文中，var.create_security_groups[group.name] 如果没有找到对应的键会导致错误。
  #  因此，我们使用 != null 来确保只有当该键存在时才会进一步处理该 group。
  for_each = { for group in var.security_group_config : group.name => group if var.create_security_groups[group.name] }

  name        = each.value.name
  description = each.value.description
  vpc_id      = data.aws_subnet.this[0].vpc_id


  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = each.value.name
  }
}


resource "aws_security_group_rule" "this" {
  for_each = { for k, v in var.security_group_rules : k => v if local.create_security_group }

  # Required
  security_group_id = aws_security_group.this[each.value.security_group_name].id
  protocol          = each.value.protocol
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  type              = each.value.type

  # Optional
  description              = lookup(each.value, "description", null)
  cidr_blocks              = lookup(each.value, "cidr_blocks", null)
  ipv6_cidr_blocks         = lookup(each.value, "ipv6_cidr_blocks", null)
  prefix_list_ids          = lookup(each.value, "prefix_list_ids", null)
  self                     = lookup(each.value, "self", null)
  source_security_group_id = lookup(each.value, "source_security_group_id", null)
}

