data "aws_subnets" "public" {
  filter {
    name   = "tag:Name"
    values = ["*public*"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

data "aws_vpc" "selected" {
  filter {
    name   = "tag:Name"
    values = ["ecs-cluster-vpc"]  # 使用精确的名称匹配
  }

  filter {
    name   = "state"
    values = ["available"]  # 只查找可用状态的 VPC
  }
}


output "vpc_id" {
  value = data.aws_vpc.selected.id
}

output "public_subnet_ids" {
  value = data.aws_subnets.public.ids
}



module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name = "ecs-alb"

  load_balancer_type = "application"

  vpc_id  = data.aws_vpc.selected.id
  subnets = data.aws_subnets.public.ids

  # For example only
  enable_deletion_protection = false

  # Security Group
  security_group_ingress_rules = {
    all_http = {
      from_port   = 80
      to_port     = 80
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
    }

    https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      #      cidr_ipv4   = module.vpc.vpc_cidr_block
      cidr_ipv4 = data.aws_vpc.selected.cidr_block
    }
  }

  listeners = {
    ex_http = {
      port     = 80
      protocol = "HTTP"

      forward = {
        target_group_key = "ex_ecs"
      }
    }

    ex_https = {
      port              = 443
      protocol          = "HTTPS"
      certificate_arn   = aws_acm_certificate.ecs_domain_certificate.arn
#      default is "ELBSecurityPolicy-TLS13-1-2-Res-2021-06"
#      ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-Res-2021-06"

      forward = {
        target_group_key = "ex_ecs"
      }

      rules = {
        ex-fixed-response = {
          priority = 3
          listener_key = "ex_https"
          actions = [{
            type         = "forward"
            target_group_key = "ex_ecs"
          }]

          conditions = [{
            host_header = {
              values           = ["${lower(var.ecs_service_name)}.${var.ecs_domain_name}"]
            }
          }]
        }
      }
    }
  }

  target_groups = {
    ex_ecs = {
      backend_protocol                  = "HTTP"
      backend_port                      = "80"
      target_type                       = "ip"
      deregistration_delay              = 5
      load_balancing_cross_zone_enabled = true

      health_check = {
        enabled             = true
        healthy_threshold   = 5
        interval            = 30
        matcher             = "200"
        path                = "/health"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
      }

      # There's nothing to attach here in this definition. Instead,
      # ECS will attach the IPs of the tasks to this target group
      create_attachment = false
    }
  }
}
