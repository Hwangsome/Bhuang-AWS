# 创建证书资源

# aws_acm_certificate 是一个用于创建和管理 AWS Certificate Manager (ACM) 证书的 Terraform 资源
#  使用 aws_acm_certificate 创建证书的场景通常包括：
# HTTPS 加密：如果您要保护 Web 应用程序（例如在 Amazon ECS 上运行的应用程序）并允许 HTTPS 连接，就需要申请 SSL/TLS 证书。
# 负载均衡：在 AWS Elastic Load Balancer (ELB) 上使用 ACM 证书，简化证书的申请和管理过程。
# 安全性：使用通配符证书来覆盖多个子域，减少证书管理的复杂性。
resource"aws_acm_certificate" "ecs_domain_certificate" {
  # 指定要为其请求证书的域名。在这里，使用了通配符 * 和变量
  # * 表示通配符证书（Wildcard Certificate）。这意味着证书将适用于该域名下的所有子域。
  # 例如，如果 var.ecs_domain_name 的值为 example.com，那么证书适用于 *.example.com，同时也会保护 example.com 本身。
  domain_name       = "*.${var.ecs_domain_name}"
  validation_method = "DNS"

  tags = {
    Name = "${var.cluster_name}-Certificate"
  }
}

data "aws_route53_zone" "ecs_domain" {
  name         = var.ecs_domain_name
  private_zone = false
}

output "ecs_domain_name" {
  value = "${data.aws_route53_zone.ecs_domain.zone_id}- ${data.aws_route53_zone.ecs_domain.arn}- ${data.aws_route53_zone.ecs_domain.name} "
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for ecs in aws_acm_certificate.ecs_domain_certificate.domain_validation_options : ecs.domain_name => {
      name   = ecs.resource_record_name
      record = ecs.resource_record_value
      type   = ecs.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.ecs_domain.zone_id
}

resource "aws_acm_certificate_validation" "ecs_domain_certificate_validation" {
  certificate_arn         = aws_acm_certificate.ecs_domain_certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}