
resource "aws_lb" "ecs_cluster_alb" {
  name                             = "${var.cluster_name}-ALB"
  internal                         = false
  load_balancer_type               = "application"
  subnets                          = module.infrastructure.public_subnets
  security_groups = [aws_security_group.ecs_alb_security_group[0].id]
}

resource "aws_alb_listener" "ecs_alb_https_listener" {
  load_balancer_arn = aws_lb.ecs_cluster_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.ecs_domain_certificate.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_default_target_group.arn
  }

  depends_on = [aws_lb_target_group.ecs_default_target_group]
}

resource "aws_lb_target_group" "ecs_default_target_group" {
  name     = "saa-test-vpces-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.infrastructure.vpc_id

  health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    protocol            = "HTTP"
  }
}


