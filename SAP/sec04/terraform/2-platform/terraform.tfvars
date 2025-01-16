#vpc_id = "vpc-0f9ad46144d94a92c"
cluster_name = "ecs-example"
ecs_domain_name = "codewithbhuang-bytes.top"
container_definitions = {
  go-simplehttp-blue-green = {
    image = "058264261029.dkr.ecr.us-east-1.amazonaws.com/bhuang-devops/go-simplehttp-blue-green:8a13fc30176753952165ce1b4863c4e6d0fc49aa"
    create_cloudwatch_log_group = false
    port_mappings = [
      {
        name          = "go-simplehttp"
        containerPort = 80
        hostPort      = 80
        protocol      = "tcp"
      }
    ]
  }
}