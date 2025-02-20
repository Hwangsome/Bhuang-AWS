#subnet_ids = ["subnet-0976cd1580502bd90"]
#
#security_group_rules = {
#  "ecs_ingress_80" = {
#    security_group_name = "ecs_security_group"  # 对应 security_group_config 中的 name
#    type               = "ingress"
#    from_port         = 80
#    to_port           = 80
#    protocol          = "tcp"
#    cidr_blocks       = ["0.0.0.0/0"]
#  }
#  "lb_ingress_443" = {
#    security_group_name = "lb_security_group"
#    type               = "ingress"
#    from_port         = 443
#    to_port           = 443
#    protocol          = "tcp"
#    description       = "Allow Port 443"
#    cidr_blocks       = [var.internet_cidr_block]
#  }
#  "lb_ingress_80" = {
#    security_group_name = "lb_security_group"
#    type               = "ingress"
#    from_port         = 80
#    to_port           = 80
#    protocol          = "tcp"
#    description       = "Allow Port 80"
#    cidr_blocks       = [var.internet_cidr_block]
#  }
#
#  "lb_egress_all" = {
#    security_group_name = "lb_security_group"
#    type               = "egress"
#    from_port         = 0
#    to_port           = 0
#    protocol          = "-1"
#    description       = "Allow all ip and ports outbound"
#    cidr_blocks       = [var.internet_cidr_block]
#  }
#}