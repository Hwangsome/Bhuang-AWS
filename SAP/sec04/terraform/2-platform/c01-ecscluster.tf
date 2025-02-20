# create ecs cluster
resource "aws_ecs_cluster" "this" {
  count = var.create ? 1 : 0

  name = var.cluster_name
}