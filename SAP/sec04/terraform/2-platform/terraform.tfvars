
container_definitions = {
  go-simplehttp-blue-green = {
#    The name of a container. If you're linking multiple containers together in a task definition, the name of one container can be entered in the links of another container to connect the containers. Up to 255 letters (uppercase and lowercase), numbers, underscores, and hyphens are allowed
    name = "go-simplehttp-blue-green"
#    The number of cpu units to reserve for the container. This is optional for tasks using Fargate launch type and the total amount of `cpu` of all containers in a task will need to be lower than the task-level cpu value
    #    cpu          = 256

#    The dependencies defined for container startup and shutdown.
#    dependencies = [{
#        containerName = "go-simplehttp-blue-green"
#        condition     = "SUCCESS"
#
#    }]

#    A container can contain multiple dependencies. When a dependency is defined for container startup, for container shutdown it is reversed. The condition can be one of START, COMPLETE, SUCCESS or HEALTHY
#    command = ["echo", "hello"]
    docker_labels = {"app" = "go-simplehttp-blue-green"}
#    If the `essential` parameter of a container is marked as `true`, and that container fails or stops for any reason, all other containers that are part of the task are stopped
    essential = true
#    A list of strings to provide custom labels for SELinux and AppArmor multi-level security systems. This field isn't valid for containers in tasks using the Fargate launch type
#    docker_security_options = [{"no-new-privileges" = ""}]
    environment = [
      {
        name  = "app"
        value = "go-simple-app"
      }
    ]
    cpu = 1
    memory = 512
    image = "058264261029.dkr.ecr.us-east-1.amazonaws.com/bhuang-devops/go-simplehttp-blue-green:8a13fc30176753952165ce1b4863c4e6d0fc49aa"
#    default is true
    create_cloudwatch_log_group = true
#    cloudwatch_log_group_name =  /aws/ecs/${var.service}/${var.name}
    service = "go-simplehttp-blue-green"
    name = "go-simplehttp-blue-green"
    port_mappings = [
      {
        name          = "go-simplehttp"
        containerPort = 80
        hostPort      = 80
        protocol      = "tcp"
      }
    ]
#    "Container repository credentials; required when using a private repo.  This map currently supports a single key; \"credentialsParameter\", which should be the ARN of a Secrets Manager's secret holding the credentials"
    #    repository_credentials = ""
  }
}

family = "go-simplehttp-blue-green"

name = "go-simplehttp-blue-green"


# sg

security_group_rules = {
  "ecs_ingress_8080" = {
    security_group_name = "ecs_security_group"  # 对应 security_group_config 中的 name
    type               = "ingress"
    from_port         = 8080
    to_port           = 8080
    protocol          = "tcp"
    cidr_blocks       = ["0.0.0.0/0"]
  }
  "ecs_egress_all" = {
    security_group_name = "ecs_security_group"  # 对应 security_group_config 中的 name
    type               = "ingress"
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    cidr_blocks       = ["0.0.0.0/0"]
  }
  "lb_ingress_443" = {
    security_group_name = "lb_security_group"
    type               = "ingress"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    description       = "Allow Port 443"
    cidr_blocks       = ["0.0.0.0/0"]
  }
  "lb_ingress_80" = {
    security_group_name = "lb_security_group"
    type               = "ingress"
    from_port         = 80
    to_port           = 80
    protocol          = "tcp"
    description       = "Allow Port 80"
    cidr_blocks       = ["0.0.0.0/0"]
  }

  "lb_egress_all" = {
    security_group_name = "lb_security_group"
    type               = "egress"
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    description       = "Allow all ip and ports outbound"
    cidr_blocks       = ["0.0.0.0/0"]
  }
}


# ecs
cluster_name = "ecs-example"
ecs_domain_name = "codewithbhuang-bytes.top"
assign_public_ip = true
load_balancer = {
  service = {
    container_name = "go-simplehttp-blue-green"
    container_port = 80
    target_group_arn = "arn:aws:elasticloadbalancing:us-east-1:058264261029:targetgroup/tf-20250123082854768400000001/a9d870151af3ca7a"
  }
}