locals {
  data_subnets = try(data.aws_subnets.subnets[0].ids, [])
  subnet_ids   = coalescelist(tolist(local.data_subnets), var.lb_subnet_ids)
}


resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow HTTP traffic on port 80"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 允许所有 IP 地址访问
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # 允许所有出站流量
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "lb" {
  name                             = "saa-test-vpces"
  internal                         = true
  load_balancer_type               = "network"
  subnets                          = local.subnet_ids
  enable_deletion_protection       = var.lb_enable_deletion_protection
  enable_cross_zone_load_balancing = var.lb_enable_cross_zone_load_balancing
  security_groups = [aws_security_group.allow_http.id]

  tags = {
    SAA = "true"
  }
}

resource "aws_lb_target_group" "target_group" {
  name     = "saa-test-vpces-tg"
  port     = var.lb_target_group_port
  protocol = "TCP"
  vpc_id   = var.vpc_id

  health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"  # 指定您服务的健康检查路径
    protocol            = "HTTP"
  }
  tags = {
    SAA = "true"
  }
}


resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.lb.arn
  port              = 80
  protocol          = "TCP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }

  tags = {
    SAA = "true"
  }
}

resource "aws_vpc_endpoint_service" "service" {
  acceptance_required        = var.endpoint_service_acceptance_required
  network_load_balancer_arns = [aws_lb.lb.arn]
  allowed_principals         = var.endpoint_service_allowed_principals

  tags = {
    SAA = "true"
  }
}