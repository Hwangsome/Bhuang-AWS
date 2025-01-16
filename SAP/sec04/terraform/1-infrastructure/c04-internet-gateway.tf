

################################################################################
# Internet Gateway
################################################################################
locals {
  max_subnet_length = max(
    local.len_private_subnets,
    local.len_public_subnets
  )
}
resource "aws_internet_gateway" "this" {
  count = local.create_public_subnets && var.create_igw ? 1 : 0

  vpc_id = local.vpc_id

  tags = merge(
    { "Name" = var.name },
    var.tags,
    var.igw_tags,
  )
}

# aws_egress_only_internet_gateway 是AWS（Amazon Web Services）中的一种网络组件，
# 专门用于支持IPv6流量的VPC（Virtual Private Cloud）架构。它允许VPC中的实例通过IPv6地址发送出站流量到Internet，但禁止反向（入站）流量向这些实例返回
#resource "aws_egress_only_internet_gateway" "this" {
#  count = var.create_vpc && var.create_egress_only_igw && var.enable_ipv6 && local.max_subnet_length > 0 ? 1 : 0
#
#  vpc_id = local.vpc_id
#
#  tags = merge(
#    { "Name" = var.name },
#    var.tags,
#    var.igw_tags,
#  )
#}

