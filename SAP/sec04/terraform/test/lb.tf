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

data "aws_vpc" "selected" {
  filter {
    name   = "tag:Name"
    values = ["admin"]  # 使用精确的名称匹配
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
#
#resource "aws_lb" "ecs_cluster_alb" {
#  name                             = "${var.cluster_name}-ALB"
#  internal                         = false
#  load_balancer_type               = "application"
#  subnets                          = data.aws_subnets.public.ids
#  security_groups = [aws_security_group.this["lb_security_group"].id]
#}
#
#resource "aws_alb_listener" "ecs_alb_https_listener" {
#  load_balancer_arn = aws_lb.ecs_cluster_alb.arn
#  port              = 443
#  protocol          = "HTTPS"
#  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
#  certificate_arn   = aws_acm_certificate.ecs_domain_certificate.arn
#
#  default_action {
#    type             = "forward"
#    target_group_arn = aws_lb_target_group.ecs_default_target_group.arn
#  }
#
#  depends_on = [aws_lb_target_group.ecs_default_target_group]
#}
#
#
#resource "aws_lb_target_group" "ecs_default_target_group" {
#  name     = "saa-test-vpces-tg"
#  port     = 80
#  protocol = "HTTP"
#  vpc_id   = data.aws_vpc.selected.id
#
#  health_check {
#    healthy_threshold   = 3
#    unhealthy_threshold = 2
#    timeout             = 5
#    interval            = 30
#    path                = "/"
#    protocol            = "HTTP"
#  }
#}

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
        path                = "/info"
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


