module "ecs-codepipeline" {
  source  = "./codepipeline"

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
  webhook_enabled = false
  deploy_provider = var.deploy_provider
  image1_artifact_name = "ImageArtifact"
  image1_container_name = "springboot-app"
  task_definition_template_artifact = "DefinitionArtifact"
  appspec_template_artifact = "DefinitionArtifact"
}

resource "aws_codestarconnections_connection" "github_connection" {
  name          = "codepipeline-codestar-connection"
  provider_type = "GitHub"
}
#
output "connection_arn" {
  value = aws_codestarconnections_connection.github_connection.arn
}