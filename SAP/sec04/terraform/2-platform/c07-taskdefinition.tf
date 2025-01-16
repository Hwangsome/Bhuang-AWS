module "ecs_container_definition" {
  source = "../container-definition"

  name      = "example"
  cpu       = 512
  memory    = 1024
  essential = true
  image     = "public.ecr.aws/aws-containers/ecsdemo-frontend:776fd50"
  port_mappings = [
    {
      name          = "ecs-sample"
      containerPort = 80
      protocol      = "tcp"
    }
  ]

  # Example image used requires access to write to root filesystem
  readonly_root_filesystem = false

  memory_reservation = 100

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

output "task_definition" {
  value = module.ecs_container_definition.container_definition
}