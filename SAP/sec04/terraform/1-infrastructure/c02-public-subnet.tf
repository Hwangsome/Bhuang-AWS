################################################################################
# Publiс Subnets
#cidrsubnet(local.vpc_cidr, 8, k + 4):
#cidrsubnet 是一个Terraform函数，用于从给定的CIDR块生成新的子网CIDR。
#第一个参数 local.vpc_cidr 是VPC的CIDR块（例如 10.0.0.0/16）。
#第二个参数 8 表示要增加8位用于生成子网CIDR。
#第三个参数 k + 4 是在索引的基础上进行偏移，以生成不同的子网。例如，当 k=0 时，k + 4 的值为4；
################################################################################
locals {
  public_subnets = [for k, v in var.azs : cidrsubnet(var.cidr, 8, k + 4)]
  create_public_subnets = var.create_vpc && max(length(local.public_subnets), length(var.public_subnet_ipv6_prefixes)) > 0
  vpc_id = try(aws_vpc.this[0].id, "")
  len_public_subnets      = max(length(local.public_subnets), length(var.public_subnet_ipv6_prefixes))
  #  是否创建多个公共路由表，默认只创建1个
  num_public_route_tables = var.create_multiple_public_route_tables ? local.len_public_subnets : 1
}

# for debug
output "public_subnets" {
  value = local.public_subnets
}

resource "aws_subnet" "public" {
  count = local.create_public_subnets && (!var.one_nat_gateway_per_az || local.len_public_subnets >= length(var.azs)) ? local.len_public_subnets : 0

  #  在子网创建时是否分配IPv6地址，默认是不创建的。
  assign_ipv6_address_on_creation                = var.enable_ipv6 && var.public_subnet_ipv6_native ? true : var.public_subnet_assign_ipv6_address_on_creation
  #  从var.azs 的变量（通常是一个包含AWS可用区名称的列表）中根据当前的 count.index 值获取对应的元素。遍历var.azs列表，根据count.index值获取对应的元素。
  availability_zone                              = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id                           = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null
  #  如果子网配置为原生IPv6子网（即 var.public_subnet_ipv6_native 为 true），则不需要CIDR块配置，因此返回 null。
  #  如果子网不是原生IPv6子网（即 var.public_subnet_ipv6_native 为 false），则从 var.public_subnets 列表中提取对应的CIDR块。
  cidr_block                                     = var.public_subnet_ipv6_native ? null : element(concat(local.public_subnets, [""]), count.index)
  #  enable_ipv6 default is false
  enable_dns64                                   = var.enable_ipv6 && var.public_subnet_enable_dns64
  enable_resource_name_dns_aaaa_record_on_launch = var.enable_ipv6 && var.public_subnet_enable_resource_name_dns_aaaa_record_on_launch
  enable_resource_name_dns_a_record_on_launch    = !var.public_subnet_ipv6_native && var.public_subnet_enable_resource_name_dns_a_record_on_launch
  #  ipv6_cidr_block & ipv6_native 用于配置原生IPv6子网。默认不配置
  ipv6_cidr_block                                = var.enable_ipv6 && length(var.public_subnet_ipv6_prefixes) > 0 ? cidrsubnet(aws_vpc.this[0].ipv6_cidr_block, 8, var.public_subnet_ipv6_prefixes[count.index]) : null
  ipv6_native                                    = var.enable_ipv6 && var.public_subnet_ipv6_native
  map_public_ip_on_launch                        = var.map_public_ip_on_launch
  private_dns_hostname_type_on_launch            = var.public_subnet_private_dns_hostname_type_on_launch
  vpc_id                                         = local.vpc_id

  tags = merge(
    {
      Name = try(
        var.public_subnet_names[count.index],
        format("${var.name}-${var.public_subnet_suffix}-%s", element(var.azs, count.index))
      )
    },
    var.tags,
    var.public_subnet_tags,
    lookup(var.public_subnet_tags_per_az, element(var.azs, count.index), {})
  )
}

resource "aws_route_table" "public" {
  count = local.create_public_subnets ? local.num_public_route_tables : 0

  vpc_id = local.vpc_id

  tags = merge(
    {
      "Name" = var.create_multiple_public_route_tables ? format(
        "${var.name}-${var.public_subnet_suffix}-%s",
        element(var.azs, count.index),
      ) : "${var.name}-${var.public_subnet_suffix}"
    },
    var.tags,
    var.public_route_table_tags,
  )
}

# Provides a resource to create an association between a route table and a subnet or a route table and an internet gateway or virtual private gateway.
# 显式的进行子网和路由表进行关联
resource "aws_route_table_association" "public" {
  count = local.create_public_subnets ? local.len_public_subnets : 0

  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = element(aws_route_table.public[*].id, var.create_multiple_public_route_tables ? count.index : 0)
}

# Provides a resource to create a routing table entry (a route) in a VPC routing table.
# 在路由表中 创建一条route
resource "aws_route" "public_internet_gateway" {
  count = local.create_public_subnets && var.create_igw ? local.num_public_route_tables : 0

  route_table_id         = aws_route_table.public[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this[0].id

  timeouts {
    create = "5m"
  }
}