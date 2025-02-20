module "ecs-codepipeline" {
  source  = "cloudposse/ecs-codepipeline/aws"
  version = "0.34.2"

  image_repo_name  = "springbootapp"
  region           = "us-east-1"
  repo_name        = "springboot-app-test-aws-cicd"
  repo_owner       = "Hwangsome"

  name                  = "springboot-app"
  namespace             = "bhuang"
  stage                 = "dev"
  branch                = "master"
  service_name          = "springboot-app"
  ecs_cluster_name      = "ecs-test-cluster"
  privileged_mode       = "true"
#  codestar_connection_arn = aws_codestarconnections_connection.github_connection.arn
  codestar_connection_arn = var.codestar_connection_arn
  webhook_enabled = false
}

resource "aws_codestarconnections_connection" "github_connection" {
  name          = "codepipeline-codestar-connection"
  provider_type = "GitHub"
}
#
output "connection_arn" {
  value = aws_codestarconnections_connection.github_connection.arn
}