#locals {
#  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-external.html
#  is_external_deployment = try(var.deployment_controller.type, null) == "EXTERNAL"
#  is_daemon              = var.scheduling_strategy == "DAEMON"
#  is_fargate             = var.launch_type == "FARGATE"
#
#  # Flattened `network_configuration`
#  network_configuration = {
#    assign_public_ip = var.assign_public_ip
#    security_groups  = flatten(concat([try(aws_security_group.this[0].id, [])], var.security_group_ids))
#    subnets          = var.subnet_ids
#  }
#
#  create_service = var.create && var.create_service
#}
#
#resource "aws_ecs_service" "this" {
#  count = local.create_service && !var.ignore_task_definition_changes ? 1 : 0
#
#  dynamic "alarms" {
#    for_each = length(var.alarms) > 0 ? [var.alarms] : []
#
#    content {
#      alarm_names = alarms.value.alarm_names
#      enable      = try(alarms.value.enable, true)
#      rollback    = try(alarms.value.rollback, true)
#    }
#  }
#
#  dynamic "capacity_provider_strategy" {
#    # Set by task set if deployment controller is external
#    for_each = { for k, v in var.capacity_provider_strategy : k => v if !local.is_external_deployment }
#
#    content {
#      base              = try(capacity_provider_strategy.value.base, null)
#      capacity_provider = capacity_provider_strategy.value.capacity_provider
#      weight            = try(capacity_provider_strategy.value.weight, null)
#    }
#  }
#
#  cluster = var.cluster_arn
#
#  dynamic "deployment_circuit_breaker" {
#    for_each = length(var.deployment_circuit_breaker) > 0 ? [var.deployment_circuit_breaker] : []
#
#    content {
#      enable   = deployment_circuit_breaker.value.enable
#      rollback = deployment_circuit_breaker.value.rollback
#    }
#  }
#
#  dynamic "deployment_controller" {
#    for_each = length(var.deployment_controller) > 0 ? [var.deployment_controller] : []
#
#    content {
#      type = try(deployment_controller.value.type, null)
#    }
#  }
#
#  deployment_maximum_percent         = local.is_daemon || local.is_external_deployment ? null : var.deployment_maximum_percent
#  deployment_minimum_healthy_percent = local.is_daemon || local.is_external_deployment ? null : var.deployment_minimum_healthy_percent
#  desired_count                      = local.is_daemon || local.is_external_deployment ? null : var.desired_count
#  enable_ecs_managed_tags            = var.enable_ecs_managed_tags
#  enable_execute_command             = var.enable_execute_command
#  force_new_deployment               = local.is_external_deployment ? null : var.force_new_deployment
#  health_check_grace_period_seconds  = var.health_check_grace_period_seconds
#  iam_role                           = local.iam_role_arn
#  launch_type                        = local.is_external_deployment || length(var.capacity_provider_strategy) > 0 ? null : var.launch_type
#
#  dynamic "load_balancer" {
#    # Set by task set if deployment controller is external
#    for_each = { for k, v in var.load_balancer : k => v if !local.is_external_deployment }
#
#    content {
#      container_name   = load_balancer.value.container_name
#      container_port   = load_balancer.value.container_port
#      elb_name         = try(load_balancer.value.elb_name, null)
#      target_group_arn = try(load_balancer.value.target_group_arn, null)
#    }
#  }
#
#  name = var.name
#
#  dynamic "network_configuration" {
#    # Set by task set if deployment controller is external
#    for_each = var.network_mode == "awsvpc" && !local.is_external_deployment ? [local.network_configuration] : []
#
#    content {
#      assign_public_ip = network_configuration.value.assign_public_ip
#      security_groups  = network_configuration.value.security_groups
#      subnets          = network_configuration.value.subnets
#    }
#  }
#
#  dynamic "ordered_placement_strategy" {
#    for_each = var.ordered_placement_strategy
#
#    content {
#      field = try(ordered_placement_strategy.value.field, null)
#      type  = ordered_placement_strategy.value.type
#    }
#  }
#
#  dynamic "placement_constraints" {
#    for_each = var.placement_constraints
#
#    content {
#      expression = try(placement_constraints.value.expression, null)
#      type       = placement_constraints.value.type
#    }
#  }
#
#  # Set by task set if deployment controller is external
#  platform_version    = local.is_fargate && !local.is_external_deployment ? var.platform_version : null
#  scheduling_strategy = local.is_fargate ? "REPLICA" : var.scheduling_strategy
#
#  dynamic "service_connect_configuration" {
#    for_each = length(var.service_connect_configuration) > 0 ? [var.service_connect_configuration] : []
#
#    content {
#      enabled = try(service_connect_configuration.value.enabled, true)
#
#      dynamic "log_configuration" {
#        for_each = try([service_connect_configuration.value.log_configuration], [])
#
#        content {
#          log_driver = try(log_configuration.value.log_driver, null)
#          options    = try(log_configuration.value.options, null)
#
#          dynamic "secret_option" {
#            for_each = try(log_configuration.value.secret_option, [])
#
#            content {
#              name       = secret_option.value.name
#              value_from = secret_option.value.value_from
#            }
#          }
#        }
#      }
#
#      namespace = lookup(service_connect_configuration.value, "namespace", null)
#
#      dynamic "service" {
#        for_each = try([service_connect_configuration.value.service], [])
#
#        content {
#
#          dynamic "client_alias" {
#            for_each = try([service.value.client_alias], [])
#
#            content {
#              dns_name = try(client_alias.value.dns_name, null)
#              port     = client_alias.value.port
#            }
#          }
#
#          discovery_name        = try(service.value.discovery_name, null)
#          ingress_port_override = try(service.value.ingress_port_override, null)
#          port_name             = service.value.port_name
#        }
#      }
#    }
#  }
#
#  dynamic "service_registries" {
#    # Set by task set if deployment controller is external
#    for_each = length(var.service_registries) > 0 ? [{ for k, v in var.service_registries : k => v if !local.is_external_deployment }] : []
#
#    content {
#      container_name = try(service_registries.value.container_name, null)
#      container_port = try(service_registries.value.container_port, null)
#      port           = try(service_registries.value.port, null)
#      registry_arn   = service_registries.value.registry_arn
#    }
#  }
#
#  task_definition       = local.task_definition
#  triggers              = var.triggers
#  wait_for_steady_state = var.wait_for_steady_state
#
#  propagate_tags = var.propagate_tags
#  tags           = merge(var.tags, var.service_tags)
#
#  timeouts {
#    create = try(var.timeouts.create, null)
#    update = try(var.timeouts.update, null)
#    delete = try(var.timeouts.delete, null)
#  }
#
#  depends_on = [
#    aws_iam_role_policy_attachment.service
#  ]
#
#  lifecycle {
#    ignore_changes = [
#      desired_count, # Always ignored
#    ]
#  }
#}