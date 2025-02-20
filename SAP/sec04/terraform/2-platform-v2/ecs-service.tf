locals {
  container_name = var.container_name
  container_port = var.container_port
  region         = "us-east-1"
  name           = var.ecs_service_name
}

# create ecs cluster and ecs service with fargate
module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "5.12.0"

  cluster_name = var.cluster_name

  services = {
    springboot-app = {
      enable_execute_command = true
      cpu    = 1024
      memory = 4096

      container_definitions = {
        springboot-app = {
          cpu       = 512
          memory    = 1024
          essential = true
          image     = var.container_image

          port_mappings = [
            {
              containerPort = local.container_port
              hostPort      = local.container_port
              protocol      = "tcp"
            }
          ]

          readonly_root_filesystem = false
          enable_cloudwatch_logging = false
#          log_configuration = {
#            logDriver = "awslogs"
#            options = {
#              awslogs-group         = "/ecs/springboot-app"
#              awslogs-region        = local.region
#              awslogs-stream-prefix = "ecs"
#            }
#          }
        }
      }

      load_balancer = {
        service = {
          target_group_arn = module.alb.target_groups["ex_ecs"].arn
          container_name   = local.container_name
          container_port   = local.container_port
        }
      }

      tasks_iam_role_name        = "${local.name}-tasks"
      tasks_iam_role_description = "Example tasks IAM role for ${local.name}"
      tasks_iam_role_policies    = {
        ReadOnlyAccess = "arn:aws:iam::aws:policy/ReadOnlyAccess"
      }
      tasks_iam_role_statements = [
        {
          actions   = ["s3:List*"]
          resources = ["arn:aws:s3:::*"]
        }
      ]

      subnet_ids           = data.aws_subnets.private.ids
      security_group_ids   = [aws_security_group.app_security_group.id]
    }
  }
}

resource "aws_security_group" "app_security_group" {
  name        = "app-security-group"
  description = "Security group for application"
  vpc_id      = data.aws_vpc.selected.id

  ingress {
    description = "HTTPS Traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Custom Application Port"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "app-security-group"
  }
}
