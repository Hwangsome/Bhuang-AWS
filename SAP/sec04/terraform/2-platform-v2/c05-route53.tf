resource "aws_route53_record" "alb_record" {
  zone_id = data.aws_route53_zone.ecs_domain.zone_id
  name    = "*.${var.ecs_domain_name}"
  type    = "A"

  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = false
  }
}