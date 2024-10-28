# lambda 执行成功 的时候， 将消息发送到sns 的 success topic 中
# lambda 执行失败的时候， 将消息发送到sqs 的 fail topic 中
# Lambda Function (store package locally)
module "lambda_function_alb" {
  source = "terraform-aws-modules/lambda/aws"
  version = "7.10.0"
  function_name = "my-lambda1"
  description   = "My awesome lambda function"
  handler       = "awesome-lambda.lambda_handler"
  runtime       = "python3.12"

# 这是resource "aws_lambda_function_event_invoke_config" 的源码， 当 create_async_event_config 为true 的时候，才会创建这个资源
#  for_each = { for k, v in local.qualifiers : k => v if v != null && local.create && var.create_function && !var.create_layer && var.create_async_event_config }
  create_async_event_config = true
  destination_on_failure = module.sns-fail.topic_arn
  destination_on_success = module.sns-success.topic_arn

#  issue: https://github.com/terraform-aws-modules/terraform-aws-lambda/issues/36
#  create_current_version_allowed_triggers = false
#  publish = true



  source_path = "${path.module}/lambda"

  #  lambda tags
  tags = {
    Name = "my-lambda1"
  }
}




