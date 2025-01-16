resource "aws_route53_record" "ecs_load_balancer_record" {
  name = "*.${var.ecs_domain_name}"
  type = "A"
  zone_id = data.aws_route53_zone.ecs_domain.zone_id

  alias {
    evaluate_target_health  = false
    name                    = aws_lb.ecs_cluster_alb.dns_name
    zone_id                 = aws_lb.ecs_cluster_alb.zone_id
  }
}